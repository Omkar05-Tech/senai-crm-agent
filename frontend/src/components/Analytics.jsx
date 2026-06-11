import React, { useState, useEffect } from 'react';
import { dashboardService } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertOctagon, Activity, Mail } from 'lucide-react';

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
    return <div className="p-10 flex justify-center items-center h-full">Loading telemetry...</div>;
  }

  return (
    <div className="flex-1 p-8 bg-gray-50 overflow-y-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">System Analytics</h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        
        {/* Total Volume */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
            <Mail className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Total Volume</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          </div>
        </div>

        {/* Escalation Rate */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-red-100 text-red-600 rounded-lg">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Escalation Rate</p>
            <p className="text-2xl font-bold text-gray-900">{stats.escalation_rate}%</p>
          </div>
        </div>

        {/* Avg Sentiment */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-green-100 text-green-600 rounded-lg">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Avg Sentiment</p>
            <p className="text-2xl font-bold text-gray-900">{stats.avg_sentiment}</p>
          </div>
        </div>
        
        {/* API Health */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center space-x-4">
          <div className="p-3 bg-indigo-100 text-indigo-600 rounded-lg">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Agent Health</p>
            <p className="text-2xl font-bold text-green-500">99.9%</p>
          </div>
        </div>

      </div>

      {/* Charts Section */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-lg font-bold text-gray-800 mb-6">Traffic by Category</h2>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={stats.categories}>
              <XAxis dataKey="name" stroke="#8884d8" />
              <YAxis />
              <Tooltip cursor={{ fill: '#f3f4f6' }} />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}