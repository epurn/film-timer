const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Timer endpoints
  async getTimers() {
    return this.request('/api/v1/timers/');
  }

  async getTimer(id) {
    return this.request(`/api/v1/timers/${id}`);
  }

  async createTimer(timerData) {
    return this.request('/api/v1/timers/', {
      method: 'POST',
      body: JSON.stringify(timerData),
    });
  }

  async updateTimer(id, timerData) {
    return this.request(`/api/v1/timers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(timerData),
    });
  }

  async deleteTimer(id) {
    return this.request(`/api/v1/timers/${id}`, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

export default new ApiService();