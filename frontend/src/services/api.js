import axios from 'axios';

// Use REACT_APP_BACKEND_URL from environment
// If empty, use same origin (production setup with K8s ingress routing /api to backend)
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API_BASE = BACKEND_URL ? `${BACKEND_URL}/api` : '/api';

class ApiService {
  async getStats(year = null) {
    try {
      let params = {};
      if (year && year !== 'all') {
        if (typeof year === 'string' && year.includes('-')) {
          // Year range format: "2021-2024"
          const [start_year, end_year] = year.split('-').map(y => parseInt(y));
          params = { start_year, end_year };
        } else {
          // Single year
          params = { year: parseInt(year) };
        }
      }
      const response = await axios.get(`${API_BASE}/stats`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  }

  async getCountries(year = null) {
    try {
      let params = {};
      if (year && year !== 'all') {
        if (typeof year === 'string' && year.includes('-')) {
          const [start_year, end_year] = year.split('-').map(y => parseInt(y));
          params = { start_year, end_year };
        } else {
          params = { year: parseInt(year) };
        }
      }
      const response = await axios.get(`${API_BASE}/data/countries`, { params });
      return response.data.countries;
    } catch (error) {
      console.error('Error fetching countries:', error);
      throw error;
    }
  }

  async getCountry(countryId, year = null) {
    try {
      let params = {};
      if (year && year !== 'all') {
        if (typeof year === 'string' && year.includes('-')) {
          const [start_year, end_year] = year.split('-').map(y => parseInt(y));
          params = { start_year, end_year };
        } else {
          params = { year: parseInt(year) };
        }
      }
      const response = await axios.get(`${API_BASE}/data/country/${countryId}`, { params });
      return response.data.country;
    } catch (error) {
      console.error('Error fetching country:', error);
      throw error;
    }
  }

  async getUniversity(countryId, universityId, year = null) {
    try {
      let params = {};
      if (year && year !== 'all') {
        if (typeof year === 'string' && year.includes('-')) {
          const [start_year, end_year] = year.split('-').map(y => parseInt(y));
          params = { start_year, end_year };
        } else {
          params = { year: parseInt(year) };
        }
      }
      const response = await axios.get(`${API_BASE}/data/university/${countryId}/${universityId}`, { params });
      return response.data.university;
    } catch (error) {
      console.error('Error fetching university:', error);
      throw error;
    }
  }

  async getAuthor(countryId, universityId, authorId, year = null) {
    try {
      const params = year ? { year } : {};
      const response = await axios.get(`${API_BASE}/data/author/${countryId}/${universityId}/${authorId}`, { params });
      return response.data.author;
    } catch (error) {
      console.error('Error fetching author:', error);
      throw error;
    }
  }

  async search(query, year) {
    try {
      const params = {};
      if (query) params.q = query;
      if (year) params.year = year;
      
      const response = await axios.get(`${API_BASE}/search`, { params });
      return response.data.countries;
    } catch (error) {
      console.error('Error searching:', error);
      throw error;
    }
  }
}

export default new ApiService();
