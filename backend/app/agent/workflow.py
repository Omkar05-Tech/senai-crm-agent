import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from app.agent.tools import (
    search_knowledge_base, get_thread_history, escalate_to_human, 
    draft_reply, check_account_status, flag_for_legal, send_auto_reply, create_internal_ticket
)
from app.services.scraper import WEB_CACHE

def run_agent_loop(email_body: str, thread_id: str, db: Session, sender_email: str, urgency: str = "Medium", is_dry_run: bool = False, max_steps: int = 6) -> dict:
    """
    Runs the dynamic ReAct (Reason + Act) loop using Gemini.
    """
    memory_trace = []
    
    # COMPONENT 4 REQUIREMENT: Must not auto-reply to emails marked Critical urgency
    if urgency == "Critical":
        memory_trace.append({
            "step": 0,
            "thought": "The email is marked as Critical urgency. Corporate policy prohibits auto-replies. I must immediately escalate.",
            "action": "escalate_to_human",
            "input": "Critical urgency override",
            "observation": "Escalated successfully."
        })
        return {
            "final_action": "escalate_to_human",
            "proposed_content": "Critical Urgency Override",
            "reasoning_log": memory_trace
        }

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # COMPONENT 5 REQUIREMENT: Inject market intelligence if available
    market_intel_block = ""
    if "SenAI" in WEB_CACHE:
        market_intel_block = f"\n\n--- LIVE MARKET INTELLIGENCE ---\n{json.dumps(WEB_CACHE['SenAI']['data'], indent=2)}\n--------------------------------\n"

    system_prompt = f"""
    You are an autonomous CRM Support Agent...
    {market_intel_block} You must resolve the user's email.
    You have access to these tools:
    1. search_knowledge_base(query: str): Searches company policies (e.g., 'SLA rules', 'refunds').
    2. get_thread_history(thread_id: str): Gets the context of the conversation.
    3. check_account_status(email: str): Check the user's billing tier and status.
    4. flag_for_legal(issue_type: str): Use immediately if the user mentions lawsuits or lawyers.
    5. escalate_to_human(reason: str): Use if you cannot resolve it automatically.
    6. draft_reply(content: str): Use to write the final response to the user.
    7. send_auto_reply(draft_id: str): Use to send the email.
    8. create_internal_ticket(title: str, body: str, assignee: str): Use to create a compliance or engineering ticket.

    You must respond in strict JSON format for EVERY step:
    {
      "thought": "Your step-by-step reasoning based on what you know.",
      "action": "The exact tool name to use, or 'none' if finished.",
      "action_input": "The input parameter for the tool",
      "is_final_answer": false
    }
    """
    
    current_prompt = system_prompt + f"\n\nSender Email: {sender_email}\nNew Email to process:\n{email_body}\nThread ID: {thread_id}\n\nStart your reasoning:"

    for step in range(max_steps):
        try:
            response = model.generate_content(
                current_prompt,
                generation_config=genai.GenerationConfig(response_mime_type="application/json", temperature=0.0)
            )
            
            ai_decision = json.loads(response.text)
            thought = ai_decision.get("thought", "")
            action = ai_decision.get("action", "none")
            action_input = ai_decision.get("action_input", "")
            is_final = ai_decision.get("is_final_answer", False)
            
            observation = ""
            
            if is_dry_run and action in ["draft_reply", "escalate_to_human", "flag_for_legal", "send_auto_reply"]:
                memory_trace.append({"step": step, "thought": thought, "action": action, "input": action_input, "observation": "[DRY RUN] Action blocked."})
                return {"final_action": "dry_run", "proposed_content": "Dry run complete.", "reasoning_log": memory_trace}

            if action == "draft_reply" or action == "escalate_to_human" or action == "create_internal_ticket" or is_final:
                memory_trace.append({"step": step, "thought": thought, "action": action, "input": action_input, "status": "Terminated"})
                return {"final_action": action, "proposed_content": action_input, "reasoning_log": memory_trace}
                
            # Execute the Tool
            if action == "search_knowledge_base":
                observation = search_knowledge_base(action_input, db)
            elif action == "get_thread_history":
                observation = get_thread_history(thread_id, db)
            elif action == "check_account_status":
                observation = check_account_status(action_input)
            elif action == "flag_for_legal":
                observation = flag_for_legal(action_input)
            elif action == "send_auto_reply":
                observation = send_auto_reply(action_input)
            else:
                observation = f"Tool {action} not recognized."

            memory_trace.append({
                "step": step,
                "thought": thought,
                "action": action,
                "input": action_input,
                "observation": observation
            })
            
            current_prompt += f"\n\nObservation from {action}: {observation}\nWhat is your next step? Provide JSON."

        except Exception as e:
            memory_trace.append({"error": str(e)})
            return {"final_action": "escalate_to_human", "proposed_content": "Agent loop failed. Manual review required.", "reasoning_log": memory_trace}

    return {"final_action": "escalate_to_human", "proposed_content": "Max agent steps reached. Unresolved.", "reasoning_log": memory_trace}