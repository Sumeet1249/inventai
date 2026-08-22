'use client';

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1',
  timeout: 120000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // We can add JWT token here if needed in the future
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle global errors here
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ApiClient {
  static async startProject(name: string, ideaDescription: string): Promise<{ id: string, status: string }> {
    const response = await api.post('/projects', { name, idea_description: ideaDescription });
    return response.data;
  }

  static async getProjectStatus(projectId: string): Promise<{ status: string }> {
    const response = await api.get(`/projects/${projectId}/status`);
    return response.data;
  }
}
