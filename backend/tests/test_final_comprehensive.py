#!/usr/bin/env python3
"""
Final Comprehensive Testing for Research Papers World Map Application
Tests data parsing accuracy, drill-down navigation, year filtering, and edge cases.
"""

import requests
import json
import sys
import random
from typing import Dict, Any, Optional, List
import time

# Backend URL from frontend/.env
BASE_URL = "https://academy-mapper.preview.emergentagent.com/api"

class FinalComprehensiveTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.all_countries_data = None
        
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
    
    def test_data_parsing_verification(self):
        """Test 1: Data Parsing Verification (CRITICAL)"""
        print("=== 1. DATA PARSING VERIFICATION (CRITICAL) ===")
        
        # Test expected statistics
        success, data, status = self.make_request("/stats")
        if success:
            expected = {
                'totalPapers': 1668,
                'totalCountries': 82,
                'totalUniversities': 1041,
                'totalAuthors': 3508,
                'totalCitations': 10333
            }
            
            actual = {
                'totalPapers': data.get('totalPapers', 0),
                'totalCountries': data.get('totalCountries', 0),
                'totalUniversities': data.get('totalUniversities', 0),
                'totalAuthors': data.get('totalAuthors', 0),
                'totalCitations': data.get('totalCitations', 0)
            }
            
            all_match = True
            mismatches = []
            for key in expected:
                if actual[key] != expected[key]:
                    all_match = False
                    mismatches.append(f"{key}: expected {expected[key]}, got {actual[key]}")
            
            if all_match:
                self.log_test("Stats Verification", True, 
                            f"All statistics match expected values: Papers={actual['totalPapers']}, Countries={actual['totalCountries']}, Universities={actual['totalUniversities']}, Authors={actual['totalAuthors']}, Citations={actual['totalCitations']}")
            else:
                self.log_test("Stats Verification", False, 
                            f"Statistics mismatch: {'; '.join(mismatches)}")
        else:
            self.log_test("Stats Verification", False, f"Request failed: {data}")
        
        # Get all countries data for further testing
        success, countries_data, status = self.make_request("/data/countries")
        if success:
            self.all_countries_data = countries_data.get('countries', [])
            
            # Verify Niger (1 paper) and Brazil (3 papers)
            niger_found = False
            brazil_found = False
            niger_papers = 0
            brazil_papers = 0
            
            for country in self.all_countries_data:
                if 'niger' in country['name'].lower():
                    niger_found = True
                    niger_papers = country['paperCount']
                elif 'brazil' in country['name'].lower():
                    brazil_found = True
                    brazil_papers = country['paperCount']
            
            if niger_found and niger_papers == 1:
                self.log_test("Niger Country Verification", True, f"Niger found with {niger_papers} paper")
            else:
                self.log_test("Niger Country Verification", False, 
                            f"Niger not found or incorrect paper count (expected 1, got {niger_papers})")
            
            if brazil_found and brazil_papers == 3:
                self.log_test("Brazil Country Verification", True, f"Brazil found with {brazil_papers} papers")
            else:
                self.log_test("Brazil Country Verification", False, 
                            f"Brazil not found or incorrect paper count (expected 3, got {brazil_papers})")
            
            # Check for suspicious country names (departments/schools)
            suspicious_names = []
            department_keywords = ['department', 'school', 'faculty', 'college', 'institute', 'center', 'centre']
            
            for country in self.all_countries_data:
                country_name_lower = country['name'].lower()
                for keyword in department_keywords:
                    if keyword in country_name_lower:
                        suspicious_names.append(country['name'])
                        break
            
            if not suspicious_names:
                self.log_test("Country Names Validation", True, "No department/school names found as countries")
            else:
                self.log_test("Country Names Validation", False, 
                            f"Suspicious country names found: {', '.join(suspicious_names[:5])}")
        else:
            self.log_test("Countries Data Retrieval", False, f"Request failed: {data}")
    
    def test_spot_check_papers(self):
        """Spot-check 5 random papers for data accuracy"""
        print("=== SPOT-CHECK RANDOM PAPERS ===")
        
        if not self.all_countries_data:
            self.log_test("Spot Check Setup", False, "No countries data available")
            return
        
        # Select 5 random countries with papers
        countries_with_papers = [c for c in self.all_countries_data if c['paperCount'] > 0]
        if len(countries_with_papers) < 5:
            selected_countries = countries_with_papers
        else:
            selected_countries = random.sample(countries_with_papers, 5)
        
        papers_checked = 0
        for i, country in enumerate(selected_countries):
            if papers_checked >= 5:
                break
                
            # Get country details
            success, country_data, status = self.make_request(f"/data/country/{country['id']}")
            if not success:
                continue
            
            universities = country_data.get('country', {}).get('universities', [])
            if not universities:
                continue
            
            # Get first university
            uni = universities[0]
            success, uni_data, status = self.make_request(f"/data/university/{country['id']}/{uni['id']}")
            if not success:
                continue
            
            authors = uni_data.get('university', {}).get('authors', [])
            if not authors:
                continue
            
            # Get first author
            author = authors[0]
            success, author_data, status = self.make_request(f"/data/author/{country['id']}/{uni['id']}/{author['id']}")
            if not success:
                continue
            
            papers = author_data.get('author', {}).get('papers', [])
            if not papers:
                continue
            
            # Check first paper
            paper = papers[0]
            required_fields = ['id', 'title', 'year', 'source', 'authors']
            optional_fields = ['cited_by', 'doi']
            
            missing_required = [field for field in required_fields if field not in paper]
            has_optional = [field for field in optional_fields if field in paper]
            
            if not missing_required:
                papers_checked += 1
                self.log_test(f"Paper Spot Check #{papers_checked}", True, 
                            f"Paper '{paper['title'][:50]}...' has all required fields. Optional fields: {', '.join(has_optional) if has_optional else 'none'}")
            else:
                self.log_test(f"Paper Spot Check #{papers_checked + 1}", False, 
                            f"Paper missing required fields: {', '.join(missing_required)}")
        
        if papers_checked == 0:
            self.log_test("Paper Spot Check", False, "Could not access any papers for verification")
    
    def test_drill_down_navigation(self):
        """Test 2: Drill-Down Navigation (HIGH PRIORITY)"""
        print("=== 2. DRILL-DOWN NAVIGATION (HIGH PRIORITY) ===")
        
        if not self.all_countries_data:
            self.log_test("Drill-Down Setup", False, "No countries data available")
            return
        
        # Test Malaysia -> Asia Pacific University -> Random Author -> Papers
        malaysia_country = None
        for country in self.all_countries_data:
            if 'malaysia' in country['name'].lower():
                malaysia_country = country
                break
        
        if not malaysia_country:
            self.log_test("Malaysia Country Search", False, "Malaysia not found in countries list")
            return
        
        # Get Malaysia details
        success, country_data, status = self.make_request(f"/data/country/{malaysia_country['id']}")
        if not success:
            self.log_test("Malaysia Country Details", False, f"Request failed: {country_data}")
            return
        
        universities = country_data.get('country', {}).get('universities', [])
        apu_university = None
        
        for uni in universities:
            if 'asia pacific' in uni['name'].lower():
                apu_university = uni
                break
        
        if not apu_university:
            self.log_test("Asia Pacific University Search", False, 
                        f"Asia Pacific University not found. Available universities: {[u['name'] for u in universities[:3]]}")
            return
        
        self.log_test("Malaysia -> Asia Pacific University", True, 
                    f"Found Asia Pacific University with {apu_university['paperCount']} papers")
        
        # Get university details
        success, uni_data, status = self.make_request(f"/data/university/{malaysia_country['id']}/{apu_university['id']}")
        if not success:
            self.log_test("University Details", False, f"Request failed: {uni_data}")
            return
        
        authors = uni_data.get('university', {}).get('authors', [])
        if not authors:
            self.log_test("University Authors", False, "No authors found in Asia Pacific University")
            return
        
        # Select random author
        random_author = random.choice(authors)
        self.log_test("Asia Pacific University -> Random Author", True, 
                    f"Selected author: {random_author['name']} with {random_author['paperCount']} papers")
        
        # Get author details
        success, author_data, status = self.make_request(f"/data/author/{malaysia_country['id']}/{apu_university['id']}/{random_author['id']}")
        if not success:
            self.log_test("Author Details", False, f"Request failed: {author_data}")
            return
        
        papers = author_data.get('author', {}).get('papers', [])
        if papers:
            self.log_test("Random Author -> Papers", True, 
                        f"Found {len(papers)} papers for {random_author['name']}")
            
            # Verify paper structure
            paper = papers[0]
            required_fields = ['id', 'title', 'year', 'source', 'authors']
            missing_fields = [field for field in required_fields if field not in paper]
            
            if not missing_fields:
                self.log_test("Paper Data Structure", True, "Papers have all required fields")
            else:
                self.log_test("Paper Data Structure", False, f"Papers missing fields: {', '.join(missing_fields)}")
        else:
            self.log_test("Random Author -> Papers", False, f"No papers found for {random_author['name']}")
        
        # Test another country with fewer papers (Niger or Brazil)
        test_countries = ['niger', 'brazil']
        for country_name in test_countries:
            test_country = None
            for country in self.all_countries_data:
                if country_name in country['name'].lower():
                    test_country = country
                    break
            
            if test_country:
                success, country_data, status = self.make_request(f"/data/country/{test_country['id']}")
                if success:
                    universities = country_data.get('country', {}).get('universities', [])
                    self.log_test(f"{test_country['name']} Drill-Down", True, 
                                f"Successfully accessed {test_country['name']} with {len(universities)} universities")
                else:
                    self.log_test(f"{test_country['name']} Drill-Down", False, f"Request failed: {country_data}")
    
    def test_year_filtering(self):
        """Test 3: Year Filtering (HIGH PRIORITY)"""
        print("=== 3. YEAR FILTERING (HIGH PRIORITY) ===")
        
        years_to_test = [2021, 2022, 2023, 2024, 2025]
        year_results = {}
        
        for year in years_to_test:
            success, data, status = self.make_request("/stats", {"year": year})
            if success:
                papers = data.get('totalPapers', 0)
                countries = data.get('totalCountries', 0)
                year_results[year] = {'papers': papers, 'countries': countries}
                self.log_test(f"Year Filter {year}", True, 
                            f"Papers: {papers}, Countries: {countries}")
            else:
                self.log_test(f"Year Filter {year}", False, f"Request failed: {data}")
        
        # Test year filtering on drill-down endpoints
        if 2025 in year_results:
            # Test countries endpoint with year filter
            success, data, status = self.make_request("/data/countries", {"year": 2025})
            if success:
                countries_2025 = data.get('countries', [])
                expected_count = year_results[2025]['countries']
                if len(countries_2025) == expected_count:
                    self.log_test("Countries Year Filter", True, 
                                f"Countries endpoint correctly filtered to {len(countries_2025)} countries for 2025")
                else:
                    self.log_test("Countries Year Filter", False, 
                                f"Expected {expected_count} countries, got {len(countries_2025)}")
            else:
                self.log_test("Countries Year Filter", False, f"Request failed: {data}")
            
            # Test drill-down with year filter
            if self.all_countries_data:
                test_country = self.all_countries_data[0]
                success, data, status = self.make_request(f"/data/country/{test_country['id']}", {"year": 2025})
                if success:
                    self.log_test("Drill-Down Year Filter", True, "Country drill-down works with year filter")
                else:
                    self.log_test("Drill-Down Year Filter", False, f"Request failed: {data}")
    
    def test_search_endpoint(self):
        """Test 4: Search Endpoint"""
        print("=== 4. SEARCH ENDPOINT ===")
        
        # Test search without query
        success, data, status = self.make_request("/search")
        if success:
            countries = data.get('countries', [])
            if countries:
                # Verify data structure
                country = countries[0]
                required_fields = ['id', 'name', 'paperCount', 'universities']
                missing_fields = [field for field in required_fields if field not in country]
                
                if not missing_fields:
                    self.log_test("Search Data Structure", True, 
                                f"Search returns correct data structure with {len(countries)} countries")
                else:
                    self.log_test("Search Data Structure", False, 
                                f"Search data missing fields: {', '.join(missing_fields)}")
            else:
                self.log_test("Search Endpoint", False, "Search returned no countries")
        else:
            self.log_test("Search Endpoint", False, f"Request failed: {data}")
        
        # Test search with query parameter
        success, data, status = self.make_request("/search", {"q": "malaysia"})
        if success:
            self.log_test("Search with Query", True, "Search with query parameter works")
        else:
            self.log_test("Search with Query", False, f"Request failed: {data}")
    
    def test_excel_exports(self):
        """Test 5: Excel Export"""
        print("=== 5. EXCEL EXPORT ===")
        
        export_types = ['papers', 'authors', 'universities', 'countries']
        
        for export_type in export_types:
            # Test without year filter
            try:
                url = f"{self.base_url}/export/{export_type}"
                response = self.session.get(url, timeout=60)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'spreadsheet' in content_type or 'excel' in content_type:
                        content_length = len(response.content)
                        self.log_test(f"Export {export_type.title()} (All Years)", True, 
                                    f"Excel file downloaded, size: {content_length:,} bytes")
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
                response = self.session.get(url, params={"year": 2025}, timeout=60)
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'spreadsheet' in content_type or 'excel' in content_type:
                        content_length = len(response.content)
                        self.log_test(f"Export {export_type.title()} (Year 2025)", True, 
                                    f"Excel file downloaded, size: {content_length:,} bytes")
                    else:
                        self.log_test(f"Export {export_type.title()} (Year 2025)", False, 
                                    f"Wrong content type: {content_type}")
                else:
                    self.log_test(f"Export {export_type.title()} (Year 2025)", False, 
                                f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Export {export_type.title()} (Year 2025)", False, f"Exception: {str(e)}")
    
    def test_edge_cases(self):
        """Test 6: Edge Cases"""
        print("=== 6. EDGE CASES ===")
        
        # Test invalid country ID
        success, data, status = self.make_request("/data/country/invalid_country_id")
        if status == 404:
            self.log_test("Invalid Country ID", True, "Correctly returned 404 for invalid country ID")
        else:
            self.log_test("Invalid Country ID", False, f"Expected 404, got {status}")
        
        # Test invalid year values
        invalid_years = ["invalid", -1, 0, 3000]
        for invalid_year in invalid_years:
            success, data, status = self.make_request("/stats", {"year": invalid_year})
            # Should handle gracefully (either ignore or return error)
            if status in [200, 400, 422]:
                self.log_test(f"Invalid Year ({invalid_year})", True, 
                            f"Handled invalid year gracefully (status: {status})")
            else:
                self.log_test(f"Invalid Year ({invalid_year})", False, 
                            f"Unexpected status code: {status}")
        
        # Test invalid university/author IDs
        if self.all_countries_data:
            country_id = self.all_countries_data[0]['id']
            success, data, status = self.make_request(f"/data/university/{country_id}/invalid_uni_id")
            if status == 404:
                self.log_test("Invalid University ID", True, "Correctly returned 404 for invalid university ID")
            else:
                self.log_test("Invalid University ID", False, f"Expected 404, got {status}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"Starting Final Comprehensive Testing for: {self.base_url}")
        print("=" * 80)
        
        start_time = time.time()
        
        self.test_data_parsing_verification()
        self.test_spot_check_papers()
        self.test_drill_down_navigation()
        self.test_year_filtering()
        self.test_search_endpoint()
        self.test_excel_exports()
        self.test_edge_cases()
        
        end_time = time.time()
        
        # Summary
        print("=" * 80)
        print("FINAL COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Execution Time: {end_time - start_time:.2f} seconds")
        
        # Critical issues
        critical_failures = []
        for result in self.test_results:
            if not result['success']:
                if any(keyword in result['test'].lower() for keyword in ['stats verification', 'data parsing', 'country names']):
                    critical_failures.append(result)
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(critical_failures)}):")
            for result in critical_failures:
                print(f"❌ {result['test']}: {result['details']}")
        
        if failed_tests > 0:
            print(f"\nALL FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"❌ {result['test']}: {result['details']}")
        
        return passed_tests, failed_tests, self.test_results

def main():
    """Main function to run tests"""
    tester = FinalComprehensiveTester(BASE_URL)
    passed, failed, results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    sys.exit(1 if failed > 0 else 0)

if __name__ == "__main__":
    main()