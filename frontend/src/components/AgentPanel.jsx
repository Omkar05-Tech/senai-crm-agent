import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import { Terminal, BrainCircuit, Activity, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function AgentPanel({ email }) {
  const [logs, setLogs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchLogs = async () => {
      if (!email) return;
      setIsLoading(true);
      try {
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

  if (!email) {
    return (
      <div className="flex flex-col h-full items-center justify-center bg-transparent">
        <BrainCircuit className="w-12 h-12 text-slate-200 mb-3" />
        <p className="text-slate-400 font-bold tracking-tight">Agent Telemetry Offline</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white font-sans">
      
      {/* Premium Terminal Header */}
      <div className="p-5 border-b border-slate-800 bg-slate-900 text-white shadow-md z-10 relative">
        <div className="flex items-center space-x-2 mb-1">
          <Terminal className="w-5 h-5 text-emerald-400" />
          <h2 className="text-lg font-extrabold tracking-tight">ReAct Engine Log</h2>
        </div>
        <p className="text-xs text-slate-400 flex items-center mt-1 font-medium tracking-wide">
          <Activity className="w-3 h-3 mr-1.5 animate-pulse text-emerald-500" />
          Live session telemetry
        </p>
      </div>

      {/* Log Feed */}
      <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50">
        {isLoading ? (
          <div className="text-sm font-medium text-slate-500 flex items-center justify-center h-20">
            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-3"></div>
            Extracting memory trace...
          </div>
        ) : logs.length === 0 ? (
          <div className="text-sm font-medium text-slate-400 italic text-center mt-10 border border-dashed border-slate-300 p-6 rounded-xl bg-white">
            No agent actions recorded for this email.
          </div>
        ) : (
          <div className="space-y-6">
            {logs.map((actionRecord, idx) => {
              const reasoningSteps = actionRecord.agent_reasoning_log || [];

              return (
                <div key={idx} className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-slate-200 before:via-slate-200 before:to-transparent">
                  
                  {reasoningSteps.map((step, stepIdx) => (
                    <div key={stepIdx} className="relative flex items-start space-x-4 mb-6 bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm transition-all hover:shadow-[0_4px_20px_rgba(0,0,0,0.03)] hover:-translate-y-0.5">
                      
                      {/* Left Timeline Dot */}
                      <div className="relative flex-shrink-0 w-8 h-8 bg-gradient-to-br from-slate-100 to-slate-200 text-slate-600 rounded-full flex items-center justify-center font-extrabold text-xs ring-4 ring-white shadow-sm z-10">
                        {step.step + 1}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        {step.thought && (
                          <div className="mb-4 text-[14px] text-slate-600 leading-relaxed">
                            <span className="font-bold text-slate-800 mr-2">Thought:</span>
                            "{step.thought}"
                          </div>
                        )}
                        
                        {step.action && (
                          <div className="mb-4">
                            <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-100/50">
                              Function Call: {step.action}()
                            </span>
                            {step.input && (
                              <div className="mt-2 ml-2 text-xs font-mono text-slate-500 bg-slate-50 p-2.5 rounded-lg border border-slate-200/60 shadow-inner">
                                {step.input}
                              </div>
                            )}
                          </div>
                        )}

                        {step.observation && (
                          <div className="mt-3 text-sm bg-slate-900 text-emerald-400 p-4 rounded-xl font-mono leading-relaxed overflow-x-auto border border-slate-800 shadow-inner">
                            <span className="text-slate-500 mr-2 text-[10px] uppercase tracking-widest font-bold block mb-1.5">System Observation:</span>
                            {step.observation}
                          </div>
                        )}
                        
                        {step.error && (
                          <div className="mt-3 text-sm bg-red-50 text-red-700 p-4 rounded-xl font-mono border border-red-100 flex items-start shadow-sm">
                            <AlertTriangle className="w-4 h-4 mr-2.5 flex-shrink-0 mt-0.5 text-red-500" />
                            {step.error}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Final Output Badge */}
                  {actionRecord.action_type && (
                    <div className="flex items-center justify-center mt-8 z-10 relative">
                       <div className="bg-gradient-to-r from-emerald-50 to-emerald-100 text-emerald-800 px-5 py-2.5 rounded-full text-[13px] font-extrabold flex items-center shadow-sm border border-emerald-200">
                         <CheckCircle2 className="w-4 h-4 mr-2 text-emerald-600" />
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