import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from app.agent.tools import search_knowledge_base, get_thread_history, escalate_to_human, draft_reply

def run_agent_loop(email_body: str, thread_id: str, db: Session, max_steps: int = 4) -> dict:
    """
    Runs the ReAct (Reason + Act) loop. 
    It forces the AI to Think -> Act -> Observe -> Repeat until resolved.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # The running memory of what the agent has done so far
    memory_trace = []
    
    # We explicitly tell the AI what tools it has and exactly how to format its output
    system_prompt = """
    You are an autonomous CRM Support Agent. You must resolve the user's email.
    You have access to these tools:
    1. search_knowledge_base(query: str): Searches company policies (e.g., 'refund rules').
    2. get_thread_history(thread_id: str): Gets the context of the conversation.
    3. escalate_to_human(reason: str): Use if it's a security threat, legal threat, or you are unsure.
    4. draft_reply(content: str): Use to write the final response to the user.

    You must respond in strict JSON format for EVERY step:
    {
      "thought": "Your step-by-step reasoning based on what you know.",
      "action": "The exact tool name to use, or 'none' if finished.",
      "action_input": "The input parameter for the tool",
      "is_final_answer": false
    }
    """
    
    # We add the new email to the prompt
    current_prompt = system_prompt + f"\n\nNew Email to process:\n{email_body}\nThread ID: {thread_id}\n\nStart your reasoning:"

    for step in range(max_steps):
        try:
            # 1. Ask the AI what to do next
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
            
            # 2. If it wants to stop or draft a reply, break the loop
            if action == "draft_reply" or action == "escalate_to_human" or is_final:
                memory_trace.append({"step": step, "thought": thought, "action": action, "input": action_input, "status": "Terminated"})
                return {
                    "final_action": action,
                    "proposed_content": action_input,
                    "reasoning_log": memory_trace
                }
                
            # 3. Execute the Tool the AI asked for
            if action == "search_knowledge_base":
                observation = search_knowledge_base(action_input, db)
            elif action == "get_thread_history":
                observation = get_thread_history(thread_id, db)
            else:
                observation = f"Tool {action} not recognized."

            # 4. Save the step to memory
            memory_trace.append({
                "step": step,
                "thought": thought,
                "action": action,
                "observation": observation
            })
            
            # 5. Add the observation back into the prompt so the AI can read it on the next loop
            current_prompt += f"\n\nObservation from {action}: {observation}\nWhat is your next step? Provide JSON."

        except Exception as e:
            # If the AI hallucinates bad JSON, we forcefully escalate to a human
            memory_trace.append({"error": str(e)})
            return {
                "final_action": "escalate_to_human",
                "proposed_content": "Agent loop failed. Manual review required.",
                "reasoning_log": memory_trace
            }

    # If it hits max_steps (loop limit) without finishing, force an escalation
    return {
        "final_action": "escalate_to_human",
        "proposed_content": "Max agent steps reached. Unresolved.",
        "reasoning_log": memory_trace
    }