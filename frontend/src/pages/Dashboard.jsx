import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import EmailList from '../components/EmailList';
import ThreadView from '../components/ThreadView';
import AgentPanel from '../components/AgentPanel';
import Analytics from '../components/Analytics';
import { LayoutDashboard, Inbox, BarChart2, Zap } from 'lucide-react';

export default function Dashboard() {
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeView, setActiveView] = useState('inbox');

  useEffect(() => {
    const fetchEmails = async () => {
      try {
        const data = await dashboardService.getInbox();
        setEmails(data);
      } catch (error) {
        console.error("Failed to fetch inbox:", error);
      }
    };
    fetchEmails();
  }, []);

  return (
    // 1. Upgraded to a soft slate background for the main canvas
    <div className="flex h-screen bg-slate-50 font-sans overflow-hidden text-slate-800">
      
      <div className="flex w-full">
        
        {/* COLUMN 1: LEFT SIDEBAR (Inbox) - 25% Width 
            Added z-20 and a custom soft shadow spreading to the right 
        */}
        <div className="w-1/4 bg-white border-r border-slate-200 flex flex-col z-20 shadow-[4px_0_24px_rgba(0,0,0,0.02)] relative">
          
          {/* Header - Increased padding and upgraded branding */}
          <div className="p-5 border-b border-slate-100 bg-white flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Brand Icon Box */}
              <div className="bg-gradient-to-br from-blue-600 to-indigo-600 p-2 rounded-xl shadow-sm shadow-blue-200">
                <Zap className="w-4 h-4 text-white" fill="currentColor" />
              </div>
              <h1 className="text-xl font-extrabold text-slate-900 tracking-tight">SenAI</h1>
            </div>
            
            {/* Tactile Navigation Toggles */}
            <div className="flex space-x-1 bg-slate-100/80 p-1 rounded-xl border border-slate-200/60">
              <button 
                onClick={() => setActiveView('inbox')}
                title="Inbox View"
                className={`p-2 rounded-lg transition-all duration-200 ease-in-out ${
                  activeView === 'inbox' 
                    ? 'bg-white shadow-sm text-blue-600 ring-1 ring-slate-900/5' 
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-200/50'
                }`}
              >
                <Inbox className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setActiveView('analytics')}
                title="Analytics View"
                className={`p-2 rounded-lg transition-all duration-200 ease-in-out ${
                  activeView === 'analytics' 
                    ? 'bg-white shadow-sm text-blue-600 ring-1 ring-slate-900/5' 
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-200/50'
                }`}
              >
                <BarChart2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {/* Email List Area */}
          <div className="flex-1 overflow-y-auto bg-slate-50/30">
            <EmailList 
              emails={emails} 
              selectedEmail={selectedEmail} 
              onSelect={setSelectedEmail} 
            />
          </div>
        </div>

        {/* --- DYNAMIC WORKSPACE CONTENT --- */}
        {activeView === 'analytics' ? (
          
          <div className="flex-1 bg-slate-50 overflow-y-auto">
            <Analytics />
          </div>
          
        ) : (
          
          <>
            {/* COLUMN 2: CENTER PANE (Thread) - 40% Width 
                Slightly darker background to recede behind the left/right panels 
            */}
            <div className="w-2/5 bg-slate-50/60 border-r border-slate-200 flex flex-col z-10 relative">
               <ThreadView email={selectedEmail} />
            </div>

            {/* COLUMN 3: RIGHT PANE (AI Log) - 35% Width 
                Added z-20 and a custom soft shadow spreading to the left 
            */}
            <div className="w-[35%] bg-white flex flex-col z-20 shadow-[-4px_0_24px_rgba(0,0,0,0.02)] relative">
               <AgentPanel email={selectedEmail} />
            </div>
          </>
          
        )}

      </div>
    </div>
  );
}