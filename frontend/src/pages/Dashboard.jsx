import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import EmailList from '../components/EmailList';
import ThreadView from '../components/ThreadView';
import AgentPanel from '../components/AgentPanel';
import { LayoutDashboard, Inbox } from 'lucide-react';

export default function Dashboard() {
  // State to hold our data
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);

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
        We use w-full and flex to align our 3 columns 
      */}
      <div className="flex w-full">
        
        {/* COLUMN 1: LEFT SIDEBAR (Inbox List) - 25% Width */}
        <div className="w-1/4 bg-white border-r border-gray-200 flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center gap-3">
            <LayoutDashboard className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold text-gray-800 tracking-tight">Mission Control</h1>
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

        {/* COLUMN 2: CENTER PANE (Email Reading) - 40% Width */}
        <div className="w-2/5 bg-[#f8fafc] border-r border-gray-200 flex flex-col shadow-inner">
           <ThreadView email={selectedEmail} />
        </div>

        {/* COLUMN 3: RIGHT PANE (AI Intelligence Log) - 35% Width */}
        <div className="w-[35%] bg-white flex flex-col">
           <AgentPanel email={selectedEmail} />
        </div>

      </div>
    </div>
  );
}