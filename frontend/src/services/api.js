const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  async fetchStats() {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }
    return response.json();
  }

  async fetchCountries() {
    const response = await fetch(`${API_BASE_URL}/data/countries`);
    if (!response.ok) {
      throw new Error('Failed to fetch countries');
    }
    const data = await response.json();
    return data.countries;
  }

  async fetchCountry(countryId) {
    const response = await fetch(`${API_BASE_URL}/data/country/${countryId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch country');
    }
    const data = await response.json();
    return data.country;
  }

  async fetchUniversity(countryId, universityId) {
    const response = await fetch(`${API_BASE_URL}/data/university/${countryId}/${universityId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch university');
    }
    const data = await response.json();
    return data.university;
  }

  async fetchAuthor(countryId, universityId, authorId) {
    const response = await fetch(`${API_BASE_URL}/data/author/${countryId}/${universityId}/${authorId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch author');
    }
    const data = await response.json();
    return data.author;
  }

  async search(query, year) {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (year && year !== 'all') params.append('year', year);
    
    const response = await fetch(`${API_BASE_URL}/search?${params}`);
    if (!response.ok) {
      throw new Error('Failed to search');
    }
    const data = await response.json();
    return data.countries;
  }
}

export default new ApiService();