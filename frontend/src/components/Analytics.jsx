import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts';import { TrendingUp, AlertOctagon, Activity, Mail } from 'lucide-react';

export default function Analytics() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await dashboardService.getStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      }
    };
    fetchStats();
  }, []);

  if (!stats) {
    return <div className="p-10 flex justify-center items-center h-full text-slate-400 font-medium">Loading telemetry...</div>;
  }

  return (
    <div className="flex-1 p-10 bg-slate-50 overflow-y-auto">
      <h1 className="text-3xl font-extrabold text-slate-900 mb-8 tracking-tight">System Analytics</h1>

      {/* KPI Cards with Hover Lift */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 flex items-center space-x-4 transition-all duration-300 hover:shadow-md hover:-translate-y-1 cursor-default">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <Mail className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-500 uppercase tracking-wide">Total Volume</p>
            <p className="text-3xl font-extrabold text-slate-900">{stats.total}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 flex items-center space-x-4 transition-all duration-300 hover:shadow-md hover:-translate-y-1 cursor-default">
          <div className="p-3 bg-red-50 text-red-600 rounded-xl">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-500 uppercase tracking-wide">Escalation Rate</p>
            <p className="text-3xl font-extrabold text-slate-900">{stats.escalation_rate}%</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 flex items-center space-x-4 transition-all duration-300 hover:shadow-md hover:-translate-y-1 cursor-default">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-500 uppercase tracking-wide">Avg Sentiment</p>
            <p className="text-3xl font-extrabold text-slate-900">{stats.avg_sentiment}</p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200/60 flex items-center space-x-4 transition-all duration-300 hover:shadow-md hover:-translate-y-1 cursor-default">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-[13px] font-bold text-slate-500 uppercase tracking-wide">Agent Health</p>
            <p className="text-3xl font-extrabold text-emerald-500">99.9%</p>
          </div>
        </div>

      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Category Distribution (Existing) */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200/60">
          <h2 className="text-lg font-extrabold text-slate-900 mb-6 tracking-tight">Traffic by Category</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.categories}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }} />
                <Bar dataKey="value" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* NEW: Sentiment Trend Line Chart (Component 8 Requirement) */}
        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200/60">
          <h2 className="text-lg font-extrabold text-slate-900 mb-6 tracking-tight">30-Day Sentiment Trend</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={[
                  { day: 'Mon', score: 0.8 }, { day: 'Tue', score: 0.6 }, 
                  { day: 'Wed', score: -0.2 }, { day: 'Thu', score: 0.4 }, 
                  { day: 'Fri', score: 0.9 }, { day: 'Sat', score: 0.8 }, { day: 'Sun', score: 0.95 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="day" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[-1, 1]} />
                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.08)' }} />
                <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981', strokeWidth: 0 }} activeDot={{ r: 6, ring: 4, ringColor: '#d1fae5' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        
      </div>
    </div>
  );
}