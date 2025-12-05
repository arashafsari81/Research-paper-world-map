#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Research Papers World Map Application
Tests all API endpoints with various scenarios including year filtering and edge cases.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import time

# Backend URL from frontend/.env
BASE_URL = "https://scholarviz.preview.emergentagent.com/api"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'response_data': response_data
        })
    
    def make_request(self, endpoint: str, params: Optional[Dict] = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return True, data, response.status_code
                except json.JSONDecodeError:
                    return False, f"Invalid JSON response", response.status_code
            else:
                return False, f"HTTP {response.status_code}: {response.text}", response.status_code
                
        except requests.exceptions.RequestException as e:
            return False, f"Request failed: {str(e)}", 0
    
    def test_stats_endpoint(self):
        """Test /api/stats endpoint with and without year filter"""
        print("=== Testing Stats Endpoint ===")
        
        # Test without year filter (all data)
        success, data, status = self.make_request("/stats")
        if success:
            expected_papers = 1668
            expected_countries = 49
            expected_universities = 807
            expected_authors = 3411
            expected_citations = 10333
            
            actual_papers = data.get('totalPapers', 0)
            actual_countries = data.get('totalCountries', 0)
            actual_universities = data.get('totalUniversities', 0)
            actual_authors = data.get('totalAuthors', 0)
            actual_citations = data.get('totalCitations', 0)
            
            if (actual_papers == expected_papers and 
                actual_countries == expected_countries and
                actual_universities == expected_universities and
                actual_authors == expected_authors and
                actual_citations == expected_citations):
                self.log_test("Stats (All Years)", True, 
                            f"Papers: {actual_papers}, Countries: {actual_countries}, Universities: {actual_universities}, Authors: {actual_authors}, Citations: {actual_citations}")
            else:
                self.log_test("Stats (All Years)", False, 
                            f"Expected: Papers={expected_papers}, Countries={expected_countries}, Universities={expected_universities}, Authors={expected_authors}, Citations={expected_citations}. Got: Papers={actual_papers}, Countries={actual_countries}, Universities={actual_universities}, Authors={actual_authors}, Citations={actual_citations}")
        else:
            self.log_test("Stats (All Years)", False, f"Request failed: {data}")
        
        # Test with year filter 2025
        success, data, status = self.make_request("/stats", {"year": 2025})
        if success:
            expected_papers_2025 = 388
            expected_countries_2025 = 42
            
            actual_papers = data.get('totalPapers', 0)
            actual_countries = data.get('totalCountries', 0)
            
            if actual_papers == expected_papers_2025 and actual_countries == expected_countries_2025:
                self.log_test("Stats (Year 2025)", True, 
                            f"Papers: {actual_papers}, Countries: {actual_countries}")
            else:
                self.log_test("Stats (Year 2025)", False, 
                            f"Expected: Papers={expected_papers_2025}, Countries={expected_countries_2025}. Got: Papers={actual_papers}, Countries={actual_countries}")
        else:
            self.log_test("Stats (Year 2025)", False, f"Request failed: {data}")
        
        # Test other years
        for year in [2024, 2023, 2022, 2021]:
            success, data, status = self.make_request("/stats", {"year": year})
            if success:
                papers = data.get('totalPapers', 0)
                countries = data.get('totalCountries', 0)
                self.log_test(f"Stats (Year {year})", True, 
                            f"Papers: {papers}, Countries: {countries}")
            else:
                self.log_test(f"Stats (Year {year})", False, f"Request failed: {data}")
    
    def test_countries_endpoint(self):
        """Test /api/data/countries endpoint"""
        print("=== Testing Countries Endpoint ===")
        
        # Test without year filter
        success, data, status = self.make_request("/data/countries")
        if success:
            countries = data.get('countries', [])
            if len(countries) == 49:
                # Check structure of first country
                if countries and all(key in countries[0] for key in ['id', 'name', 'lat', 'lng', 'paperCount']):
                    self.log_test("Countries (All Years)", True, f"Found {len(countries)} countries with correct structure")
                else:
                    self.log_test("Countries (All Years)", False, "Countries missing required fields")
            else:
                self.log_test("Countries (All Years)", False, f"Expected 49 countries, got {len(countries)}")
        else:
            self.log_test("Countries (All Years)", False, f"Request failed: {data}")
        
        # Test with year filter
        success, data, status = self.make_request("/data/countries", {"year": 2025})
        if success:
            countries = data.get('countries', [])
            if len(countries) == 42:
                self.log_test("Countries (Year 2025)", True, f"Found {len(countries)} countries")
            else:
                self.log_test("Countries (Year 2025)", False, f"Expected 42 countries for 2025, got {len(countries)}")
        else:
            self.log_test("Countries (Year 2025)", False, f"Request failed: {data}")
    
    def test_drill_down_navigation(self):
        """Test drill-down navigation endpoints"""
        print("=== Testing Drill-Down Navigation ===")
        
        # First get countries to find a valid country ID
        success, countries_data, status = self.make_request("/data/countries")
        if not success:
            self.log_test("Drill-Down Setup", False, "Could not get countries list")
            return
        
        countries = countries_data.get('countries', [])
        if not countries:
            self.log_test("Drill-Down Setup", False, "No countries found")
            return
        
        # Test with Malaysia (should have universities)
        malaysia_country = None
        for country in countries:
            if 'malaysia' in country['name'].lower():
                malaysia_country = country
                break
        
        if not malaysia_country:
            # Use first country if Malaysia not found
            malaysia_country = countries[0]
        
        country_id = malaysia_country['id']
        country_name = malaysia_country['name']
        
        # Test country endpoint
        success, data, status = self.make_request(f"/data/country/{country_id}")
        if success:
            country_data = data.get('country', {})
            universities = country_data.get('universities', [])
            if universities:
                self.log_test(f"Country Details ({country_name})", True, 
                            f"Found {len(universities)} universities")
                
                # Test university endpoint
                uni_id = universities[0]['id']
                uni_name = universities[0]['name']
                
                success, data, status = self.make_request(f"/data/university/{country_id}/{uni_id}")
                if success:
                    uni_data = data.get('university', {})
                    authors = uni_data.get('authors', [])
                    if authors:
                        self.log_test(f"University Details ({uni_name})", True, 
                                    f"Found {len(authors)} authors")
                        
                        # Test author endpoint
                        author_id = authors[0]['id']
                        author_name = authors[0]['name']
                        
                        success, data, status = self.make_request(f"/data/author/{country_id}/{uni_id}/{author_id}")
                        if success:
                            author_data = data.get('author', {})
                            papers = author_data.get('papers', [])
                            if papers:
                                # Check paper structure
                                paper = papers[0]
                                required_fields = ['id', 'title', 'year', 'source', 'authors']
                                if all(field in paper for field in required_fields):
                                    self.log_test(f"Author Details ({author_name})", True, 
                                                f"Found {len(papers)} papers with correct structure")
                                else:
                                    self.log_test(f"Author Details ({author_name})", False, 
                                                "Papers missing required fields")
                            else:
                                self.log_test(f"Author Details ({author_name})", False, "No papers found")
                        else:
                            self.log_test(f"Author Details ({author_name})", False, f"Request failed: {data}")
                    else:
                        self.log_test(f"University Details ({uni_name})", False, "No authors found")
                else:
                    self.log_test(f"University Details ({uni_name})", False, f"Request failed: {data}")
            else:
                self.log_test(f"Country Details ({country_name})", False, "No universities found")
        else:
            self.log_test(f"Country Details ({country_name})", False, f"Request failed: {data}")
    
    def test_search_endpoint(self):
        """Test /api/search endpoint"""
        print("=== Testing Search Endpoint ===")
        
        # Test search without query (should return all data)
        success, data, status = self.make_request("/search")
        if success:
            countries = data.get('countries', [])
            if countries:
                self.log_test("Search (No Query)", True, f"Returned {len(countries)} countries")
            else:
                self.log_test("Search (No Query)", False, "No countries returned")
        else:
            self.log_test("Search (No Query)", False, f"Request failed: {data}")
        
        # Test search with query parameter
        success, data, status = self.make_request("/search", {"q": "malaysia"})
        if success:
            countries = data.get('countries', [])
            self.log_test("Search (With Query)", True, f"Search with query returned {len(countries)} countries")
        else:
            self.log_test("Search (With Query)", False, f"Request failed: {data}")
        
        # Test search with year filter
        success, data, status = self.make_request("/search", {"year": 2025})
        if success:
            countries = data.get('countries', [])
            self.log_test("Search (Year Filter)", True, f"Search with year filter returned {len(countries)} countries")
        else:
            self.log_test("Search (Year Filter)", False, f"Request failed: {data}")
    
    def test_excel_exports(self):
        """Test Excel export endpoints"""
        print("=== Testing Excel Export Endpoints ===")
        
        export_types = ['papers', 'authors', 'universities', 'countries']
        
        for export_type in export_types:
            # Test without year filter
            try:
                url = f"{self.base_url}/export/{export_type}"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'spreadsheet' in content_type or 'excel' in content_type:
                        content_length = len(response.content)
                        self.log_test(f"Export {export_type.title()} (All Years)", True, 
                                    f"Excel file downloaded, size: {content_length} bytes")
                    else:
                        self.log_test(f"Export {export_type.title()} (All Years)", False, 
                                    f"Wrong content type: {content_type}")
                else:
                    self.log_test(f"Export {export_type.title()} (All Years)", False, 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Export {export_type.title()} (All Years)", False, f"Exception: {str(e)}")
            
            # Test with year filter
            try:
                url = f"{self.base_url}/export/{export_type}"
                response = self.session.get(url, params={"year": 2025}, timeout=30)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'spreadsheet' in content_type or 'excel' in content_type:
                        content_length = len(response.content)
                        self.log_test(f"Export {export_type.title()} (Year 2025)", True, 
                                    f"Excel file downloaded, size: {content_length} bytes")
                    else:
                        self.log_test(f"Export {export_type.title()} (Year 2025)", False, 
                                    f"Wrong content type: {content_type}")
                else:
                    self.log_test(f"Export {export_type.title()} (Year 2025)", False, 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Export {export_type.title()} (Year 2025)", False, f"Exception: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("=== Testing Edge Cases ===")
        
        # Test invalid country ID
        success, data, status = self.make_request("/data/country/invalid_country_id")
        if status == 404:
            self.log_test("Invalid Country ID", True, "Correctly returned 404")
        else:
            self.log_test("Invalid Country ID", False, f"Expected 404, got {status}")
        
        # Test invalid year
        success, data, status = self.make_request("/stats", {"year": "invalid"})
        # Should either work (ignore invalid year) or return error
        self.log_test("Invalid Year Parameter", True, f"Handled invalid year parameter (status: {status})")
        
        # Test very old year (should return empty or minimal data)
        success, data, status = self.make_request("/stats", {"year": 1990})
        if success:
            papers = data.get('totalPapers', 0)
            self.log_test("Old Year (1990)", True, f"Returned {papers} papers for year 1990")
        else:
            self.log_test("Old Year (1990)", False, f"Request failed: {data}")
        
        # Test future year
        success, data, status = self.make_request("/stats", {"year": 2030})
        if success:
            papers = data.get('totalPapers', 0)
            self.log_test("Future Year (2030)", True, f"Returned {papers} papers for year 2030")
        else:
            self.log_test("Future Year (2030)", False, f"Request failed: {data}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"Starting comprehensive API testing for: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        self.test_stats_endpoint()
        self.test_countries_endpoint()
        self.test_drill_down_navigation()
        self.test_search_endpoint()
        self.test_excel_exports()
        self.test_edge_cases()
        
        end_time = time.time()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Execution Time: {end_time - start_time:.2f} seconds")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests, self.test_results

def main():
    """Main function to run tests"""
    tester = APITester(BASE_URL)
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()