import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import EmailList from '../components/EmailList';
import ThreadView from '../components/ThreadView';
import AgentPanel from '../components/AgentPanel';
import Analytics from '../components/Analytics';
import { LayoutDashboard, Inbox, BarChart2 } from 'lucide-react';

export default function Dashboard() {
  // State to hold our data
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeView, setActiveView] = useState('inbox');

  // Fetch emails from the FastAPI backend when the page loads
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
    <div className="flex h-screen bg-gray-100 font-sans overflow-hidden">
      
      {/* MAIN WRAPPER 
        We use w-full and flex to align our workspace layout
      */}
      <div className="flex w-full">
        
        {/* COLUMN 1: LEFT SIDEBAR (Inbox List & Global Navigation) - 25% Width */}
        <div className="w-1/4 bg-white border-r border-gray-200 flex flex-col">
          
          {/* Header containing the App Title and View Switches */}
          <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <LayoutDashboard className="w-5 h-5 text-blue-600" />
              <h1 className="text-lg font-bold text-gray-800 tracking-tight">Mission Control</h1>
            </div>
            
            {/* Navigation Toggles */}
            <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg">
              <button 
                onClick={() => setActiveView('inbox')}
                title="Inbox View"
                className={`p-1.5 rounded-md transition-all ${
                  activeView === 'inbox' 
                    ? 'bg-white shadow-sm text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Inbox className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setActiveView('analytics')}
                title="Analytics View"
                className={`p-1.5 rounded-md transition-all ${
                  activeView === 'analytics' 
                    ? 'bg-white shadow-sm text-blue-600' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <BarChart2 className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          {/* Scrollable Email List Area */}
          <div className="flex-1 overflow-y-auto">
            <EmailList 
              emails={emails} 
              selectedEmail={selectedEmail} 
              onSelect={setSelectedEmail} 
              />
          </div>
        </div>

        {/* --- DYNAMIC WORKSPACE CONTENT --- */}
        {activeView === 'analytics' ? (
          
          /* Full Screen Metrics Workspace (Occupies the remaining 75% width) */
          <Analytics />
          
        ) : (
          
          /* Live Triage Workspace (Split Layout) */
          <>
            {/* COLUMN 2: CENTER PANE (Email Reading) - 40% Width */}
            <div className="w-2/5 bg-[#f8fafc] border-r border-gray-200 flex flex-col shadow-inner">
               <ThreadView email={selectedEmail} />
            </div>

            {/* COLUMN 3: RIGHT PANE (AI Intelligence Log) - 35% Width */}
            <div className="w-[35%] bg-white flex flex-col">
               <AgentPanel email={selectedEmail} />
            </div>
          </>
          
        )}

      </div>
    </div>
  );
}