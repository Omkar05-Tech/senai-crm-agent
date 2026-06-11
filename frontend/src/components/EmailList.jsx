import React from 'react';
import { Tag, ShieldAlert } from 'lucide-react';

export default function EmailList({ emails, selectedEmail, onSelect }) {
  if (!emails || emails.length === 0) {
    return (
      <div className="p-10 flex flex-col items-center justify-center text-slate-400">
        <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-3">
          <Tag className="w-5 h-5 text-slate-300" />
        </div>
        <p className="text-sm font-medium">Inbox is empty.</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-slate-100 p-2 space-y-1">
      {emails.map((email) => {
        const isSelected = selectedEmail?.message_id === email.message_id;
        
        // Refined Badge Colors
        let urgencyColor = "bg-slate-100 text-slate-600 border-slate-200/60";
        if (email.urgency === "High") urgencyColor = "bg-orange-50 text-orange-700 border-orange-200/60 ring-1 ring-orange-600/10";
        if (email.urgency === "Critical") urgencyColor = "bg-red-50 text-red-700 border-red-200/60 ring-1 ring-red-600/10 shadow-sm shadow-red-100";
        if (email.urgency === "Low") urgencyColor = "bg-emerald-50 text-emerald-700 border-emerald-200/60";

        return (
          <div 
            key={email.message_id}
            onClick={() => onSelect(email)}
            // Here is the magic Tailwind transition: hover:shadow-md and hover:-translate-y-0.5
            className={`p-4 rounded-xl cursor-pointer transition-all duration-200 ease-out border ${
              isSelected 
                ? 'bg-blue-50/80 border-blue-200 ring-1 ring-blue-500/20 shadow-sm' 
                : 'bg-white border-transparent hover:border-slate-200 hover:shadow-[0_4px_12px_rgba(0,0,0,0.03)] hover:-translate-y-0.5'
            }`}
          >
            <div className="flex justify-between items-start mb-1.5">
              <div className="text-[13px] font-bold text-slate-900 truncate pr-2 tracking-tight">
                {email.sender}
              </div>
              <span className={`text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold ${urgencyColor}`}>
                {email.urgency || "Unrated"}
              </span>
            </div>
            
            <div className={`text-[14px] mb-3 truncate leading-snug ${isSelected ? 'text-blue-900 font-semibold' : 'text-slate-600 font-medium'}`}>
              {email.subject || "No Subject"}
            </div>
            
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center text-[11px] font-medium text-slate-500 bg-slate-50 px-2 py-1 rounded-md border border-slate-200/60">
                <Tag className="w-3 h-3 mr-1.5 opacity-70" />
                {email.category || "Uncategorized"}
              </span>
              
              {email.requires_human && (
                <span className="flex items-center text-[11px] text-red-600 font-bold bg-red-50 px-2 py-1 rounded-md border border-red-100">
                  <ShieldAlert className="w-3 h-3 mr-1.5" />
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