import axios from 'axios';

// Ensure /api is strictly appended to whatever environment variable Vite loads
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = baseURL.endsWith('/api') ? baseURL : `${baseURL}/api`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardService = {
  // 1. Fetch the list of emails for the inbox
  getInbox: async () => {
    const response = await apiClient.get('/dashboard/inbox');
    return response.data;
  },
  
  // 2. Fetch the reasoning logs for a specific email
  getAgentLogs: async (emailId) => {
    const response = await apiClient.get(`/dashboard/logs/${emailId}`);
    return response.data;
  },

  // 3. Fire a test email into the system (so we can demo it live)
  ingestTestEmail: async (payload) => {
    const response = await apiClient.post('/ingest', payload);
    return response.data;
  },

  // 4. Fetch metrics for the Analytics page
  getStats: async () => {
    const response = await apiClient.get('/dashboard/stats');
    return response.data;
  }
};

export default apiClient;