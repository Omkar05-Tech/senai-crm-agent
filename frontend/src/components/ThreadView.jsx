import React from 'react';
import { Clock, Reply, Mail, User } from 'lucide-react';

export default function ThreadView({ email }) {
  // 1. The Empty State
  if (!email) {
    return (
      <div className="flex flex-col h-full items-center justify-center bg-transparent">
        <div className="bg-slate-100 p-6 rounded-full shadow-sm mb-4 border border-slate-200/60">
          <Mail className="w-12 h-12 text-slate-300" strokeWidth={1.5} />
        </div>
        <p className="text-lg font-bold text-slate-400 tracking-tight">Select a conversation</p>
        <p className="text-sm text-slate-400 mt-1">Choose an email from the inbox to read.</p>
      </div>
    );
  }

  const formattedDate = new Date(email.timestamp).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric', 
    hour: 'numeric', minute: '2-digit'
  });

  return (
    <div className="flex flex-col h-full bg-white shadow-[0_2px_24px_rgba(0,0,0,0.04)] m-4 rounded-2xl border border-slate-200/60 overflow-hidden relative">
      
      {/* Header */}
      <div className="p-8 border-b border-slate-100 bg-white z-10 relative">
        <h2 className="text-2xl font-extrabold text-slate-900 mb-6 leading-tight tracking-tight">
          {email.subject || "No Subject"}
        </h2>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Premium Gradient Avatar */}
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-md shadow-blue-200">
              {email.sender.charAt(0).toUpperCase()}
            </div>
            <div>
              <div className="text-[15px] font-bold text-slate-900">{email.sender}</div>
              <div className="text-[13px] font-medium text-slate-500 flex items-center mt-0.5">
                <Clock className="w-3.5 h-3.5 mr-1.5 opacity-70" />
                {formattedDate}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Body Area */}
      <div className="p-8 flex-1 overflow-y-auto bg-slate-50/30">
        <div className="text-slate-700 whitespace-pre-wrap leading-relaxed text-[15px] max-w-3xl">
          {email.body}
        </div>
      </div>

      {/* Floating Action Footer */}
      <div className="p-5 border-t border-slate-100 bg-white flex justify-end">
         <button className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-sm font-bold text-white hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md shadow-blue-500/20 hover:shadow-lg hover:-translate-y-0.5">
           <Reply className="w-4 h-4" />
           <span>Reply to Customer</span>
         </button>
      </div>
    </div>
  );
}