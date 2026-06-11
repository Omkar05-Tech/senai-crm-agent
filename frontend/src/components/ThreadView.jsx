import React from 'react';
import { Clock, Reply, Mail } from 'lucide-react';

export default function ThreadView({ email }) {
  // 1. The Empty State: What to show before the user clicks an email
  if (!email) {
    return (
      <div className="flex flex-col h-full items-center justify-center bg-[#f8fafc]">
        <div className="bg-white p-6 rounded-full shadow-sm mb-4 border border-gray-100">
          <Mail className="w-12 h-12 text-gray-300" strokeWidth={1.5} />
        </div>
        <p className="text-lg font-medium text-gray-600">Select a conversation</p>
        <p className="text-sm text-gray-400 mt-1">Choose an email from the inbox to read.</p>
      </div>
    );
  }

  // Helper to format the raw database timestamp into a readable date
  const formattedDate = new Date(email.timestamp).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric', 
    hour: 'numeric', minute: '2-digit'
  });

  // 2. The Active State: What to show when an email is selected
  return (
    <div className="flex flex-col h-full bg-white shadow-sm m-4 rounded-xl border border-gray-200 overflow-hidden">
      
      {/* Header: Subject Line and Metadata */}
      <div className="p-6 border-b border-gray-100 bg-gray-50/50">
        <h2 className="text-2xl font-bold text-gray-900 mb-5 leading-tight">
          {email.subject || "No Subject"}
        </h2>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {/* Auto-generated Avatar based on the sender's email letter */}
            <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-lg shadow-inner">
              {email.sender.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-sm font-bold text-gray-900">{email.sender}</div>
              <div className="text-xs text-gray-500 flex items-center mt-1">
                <Clock className="w-3.5 h-3.5 mr-1.5 opacity-70" />
                {formattedDate}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Body: The actual email text */}
      <div className="p-6 flex-1 overflow-y-auto">
        <div className="text-gray-800 whitespace-pre-wrap leading-relaxed text-[15px]">
          {email.body}
        </div>
      </div>

      {/* Footer: Visual Reply Button (No logic attached yet) */}
      <div className="p-4 border-t border-gray-100 bg-gray-50 flex justify-end">
         <button className="flex items-center space-x-2 px-5 py-2.5 bg-white border border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-50 hover:text-blue-600 transition-all shadow-sm">
           <Reply className="w-4 h-4" />
           <span>Reply to Customer</span>
         </button>
      </div>
    </div>
  );
}