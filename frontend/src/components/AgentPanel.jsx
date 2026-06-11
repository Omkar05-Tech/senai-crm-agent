import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import { Terminal, BrainCircuit, Activity, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function AgentPanel({ email }) {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch the reasoning logs whenever a new email is clicked
  useEffect(() => {
    const fetchLogs = async () => {
      if (!email) return;
      setIsLoading(true);
      try {
        // We use the database 'id' to fetch the associated actions
        const data = await dashboardService.getAgentLogs(email.id);
        setLogs(data);
      } catch (error) {
        console.error("Failed to fetch agent logs:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLogs();
  }, [email]);

  // Empty State
  if (!email) {
    return (
      <div className="flex flex-col h-full items-center justify-center bg-white">
        <BrainCircuit className="w-12 h-12 text-gray-200 mb-3" />
        <p className="text-gray-400 font-medium">Agent Telemetry Offline</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white font-sans border-l border-gray-200">
      
      {/* Header Panel */}
      <div className="p-5 border-b border-gray-100 bg-gray-900 text-white shadow-md z-10">
        <div className="flex items-center space-x-2 mb-1">
          <Terminal className="w-5 h-5 text-green-400" />
          <h2 className="text-lg font-bold tracking-wide">ReAct Engine Log</h2>
        </div>
        <p className="text-xs text-gray-400 flex items-center mt-1">
          <Activity className="w-3 h-3 mr-1 animate-pulse text-green-500" />
          Live session telemetry
        </p>
      </div>

      {/* Log Feed */}
      <div className="flex-1 overflow-y-auto p-5 bg-[#fafafa]">
        {isLoading ? (
          <div className="text-sm text-gray-500 animate-pulse flex items-center">
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-2"></div>
            Extracting memory trace...
          </div>
        ) : logs.length === 0 ? (
          <div className="text-sm text-gray-400 italic text-center mt-10 border border-dashed border-gray-300 p-6 rounded-lg bg-white">
            No agent actions recorded for this email.
          </div>
        ) : (
          <div className="space-y-6">
            {/* Because our backend might return the raw JSON in different formats depending on how we saved it,
              we safely map over the array of action records. 
            */}
            {logs.map((actionRecord, idx) => {
              // Extract the array of reasoning steps from the database column
              const reasoningSteps = actionRecord.agent_reasoning_log || [];

              return (
                <div key={idx} className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-200 before:to-transparent">
                  
                  {reasoningSteps.map((step, stepIdx) => (
                    <div key={stepIdx} className="relative flex items-start space-x-3 mb-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm transition-all hover:shadow-md">
                      
                      {/* Left Timeline Dot */}
                      <div className="relative flex-shrink-0 w-8 h-8 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center font-bold text-xs ring-4 ring-white z-10">
                        {step.step + 1}
                      </div>
                      
                      {/* Step Content */}
                      <div className="flex-1 min-w-0">
                        {/* Thought */}
                        {step.thought && (
                          <div className="mb-3 text-sm text-gray-600 italic">
                            <span className="font-semibold text-gray-800 not-italic mr-2">Thought:</span>
                            "{step.thought}"
                          </div>
                        )}
                        
                        {/* Action Tool Trigger */}
                        {step.action && (
                          <div className="mb-3">
                            <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-100">
                              Function Call: {step.action}()
                            </span>
                            {step.input && (
                              <div className="mt-1 ml-2 text-xs font-mono text-gray-500 bg-gray-50 p-2 rounded border border-gray-100">
                                {step.input}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Observation/System Feedback */}
                        {step.observation && (
                          <div className="mt-2 text-sm bg-gray-900 text-green-400 p-3 rounded-lg font-mono leading-relaxed overflow-x-auto border border-gray-800">
                            <span className="text-gray-500 mr-2 text-xs uppercase tracking-wider block mb-1">System Observation:</span>
                            {step.observation}
                          </div>
                        )}
                        
                        {/* Error Handling */}
                        {step.error && (
                          <div className="mt-2 text-sm bg-red-50 text-red-700 p-3 rounded-lg font-mono border border-red-200 flex items-start">
                            <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
                            {step.error}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Final Output Badge */}
                  {actionRecord.action_type && (
                    <div className="flex items-center justify-center mt-6 z-10 relative">
                       <div className="bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-bold flex items-center shadow-sm border border-green-200">
                         <CheckCircle2 className="w-4 h-4 mr-2" />
                         Final Action: {actionRecord.action_type}
                       </div>
                    </div>
                  )}

                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}