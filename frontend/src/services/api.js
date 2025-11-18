import axios from 'axios';

// Use REACT_APP_BACKEND_URL from environment, which contains the full backend URL
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

class ApiService {
  async getStats() {
    try {
      const response = await axios.get(`${API_BASE}/stats`);
      return response.data;
    } catch (error) {
      console.error('Error fetching stats:', error);
      throw error;
    }
  }

  async getCountries() {
    try {
      const response = await axios.get(`${API_BASE}/data/countries`);
      return response.data.countries;
    } catch (error) {
      console.error('Error fetching countries:', error);
      throw error;
    }
  }

  async getCountry(countryId) {
    try {
      const response = await axios.get(`${API_BASE}/data/country/${countryId}`);
      return response.data.country;
    } catch (error) {
      console.error('Error fetching country:', error);
      throw error;
    }
  }

  async getUniversity(countryId, universityId) {
    try {
      const response = await axios.get(`${API_BASE}/data/university/${countryId}/${universityId}`);
      return response.data.university;
    } catch (error) {
      console.error('Error fetching university:', error);
      throw error;
    }
  }

  async getAuthor(countryId, universityId, authorId) {
    try {
      const response = await axios.get(`${API_BASE}/data/author/${countryId}/${universityId}/${authorId}`);
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
