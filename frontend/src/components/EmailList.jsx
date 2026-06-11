import React from 'react';
import { Tag, ShieldAlert } from 'lucide-react';

export default function EmailList({ emails, selectedEmail, onSelect }) {
  // If the backend hasn't returned data yet, or the database is empty
  if (!emails || emails.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500 text-sm">
        No emails found in the database.
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {emails.map((email) => {
        // Check if this card is the currently clicked one
        const isSelected = selectedEmail?.message_id === email.message_id;
        
        // Dynamically style the urgency badge based on the AI's decision
        let urgencyColor = "bg-gray-100 text-gray-800 border-gray-200";
        if (email.urgency === "High") urgencyColor = "bg-orange-100 text-orange-800 border-orange-200";
        if (email.urgency === "Critical") urgencyColor = "bg-red-100 text-red-800 border-red-200";
        if (email.urgency === "Low") urgencyColor = "bg-green-100 text-green-800 border-green-200";

        return (
          <div 
            key={email.message_id}
            onClick={() => onSelect(email)}
            className={`p-4 cursor-pointer transition-colors duration-150 border-l-4 ${
              isSelected 
                ? 'bg-blue-50 border-blue-600' // Highlight if selected
                : 'bg-white border-transparent hover:bg-gray-50'
            }`}
          >
            {/* Top Row: Sender & Urgency Badge */}
            <div className="flex justify-between items-start mb-1">
              <div className="text-sm font-semibold text-gray-900 truncate pr-2">
                {email.sender}
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${urgencyColor}`}>
                {email.urgency || "Unrated"}
              </span>
            </div>
            
            {/* Subject Line */}
            <div className="text-sm text-gray-800 font-medium mb-2 truncate">
              {email.subject || "No Subject"}
            </div>
            
            {/* Bottom Row: AI Category & Escalate Warning */}
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded border border-gray-200">
                <Tag className="w-3 h-3 mr-1" />
                {email.category || "Uncategorized"}
              </span>
              
              {/* Only show this warning if the AI flagged it for a human */}
              {email.requires_human && (
                <span className="flex items-center text-xs text-red-600 font-bold">
                  <ShieldAlert className="w-3 h-3 mr-1" />
                  Human Req
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}