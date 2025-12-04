#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: Build a web application to visualize research paper data from a CSV file with an interactive world map showing papers by country, with drill-down navigation (Country -> University -> Author -> Papers), search functionality, year filtering, and Excel export features.

backend:
  - task: "Data Processing and Cleaning Pipeline"
    implemented: true
    working: true
    file: "/app/backend/data_cleaner.py, /app/backend/csv_processor.py"
    stuck_count: 4
    priority: "high"
    needs_retesting: false
    status_history:
        - working: false
          agent: "user"
          comment: "User reported: Data processing broken, showing incorrect statistics (wrong paper counts, country counts, author counts). The numbers got worse after attempting to support uncleaned dataset."
        - working: false
          agent: "main"
          comment: "Previous agent attempted multiple complex parsing strategies using hardcoded indices and keywords, all failed to handle variability in Authors with affiliations column."
        - working: true
          agent: "main"
          comment: "FIXED - Completely rewrote data parsing logic in data_cleaner.py. New approach: 1) Created _is_likely_country() method with comprehensive country list. 2) Created _is_likely_institution() to identify institution names. 3) Implemented _parse_author_affiliations() that splits by semicolon, identifies countries first, then extracts institutions before each country. 4) Added name normalization for matching authors to IDs. Tested standalone and full pipeline - now correctly parsing all data. Stats: 1668 papers, 49 countries, 807 universities, 3411 authors, 10333 citations."
        - working: true
          agent: "testing"
          comment: "VERIFIED - Comprehensive API testing confirms data processing is working correctly. /api/stats returns exact expected values: 1668 papers, 49 countries, 807 universities, 3411 authors, 10333 citations. All data structures are properly formatted and accessible through drill-down navigation."

  - task: "API Endpoints for Stats and Data"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "All API endpoints implemented: /api/stats, /api/data/countries, /api/data/country/{id}, /api/data/university/{country_id}/{uni_id}, /api/data/author/{country_id}/{uni_id}/{author_id}, /api/search, /api/export/{type}. Year filtering supported via query param. Need comprehensive testing."

  - task: "Year Filtering"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py, /app/backend/csv_processor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Year filtering implemented in csv_processor.py and exposed via query parameter in all API endpoints. Tested via curl: 2025 filter returns 388 papers correctly. Need comprehensive API testing with various year filters."

  - task: "Excel Export Functionality"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Excel export endpoints implemented for papers, authors, universities, and countries. Uses openpyxl library. Respects year filter. Need to test all export types with and without year filter."

frontend:
  - task: "Interactive Map with Country Markers"
    implemented: true
    working: true
    file: "/app/frontend/src/components/MapView.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "Verified via screenshot - Map loads correctly with 49 country markers displayed. Markers are clickable and open side panel."

  - task: "Drill-Down Navigation (Country -> University -> Author -> Papers)"
    implemented: true
    working: true
    file: "/app/frontend/src/components/SidePanel.js, /app/frontend/src/components/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "Verified via screenshot - Successfully navigated from Singapore country to Newcastle University Singapore to author Manoharan Aaruththiran to view paper details. Breadcrumb navigation visible and working."

  - task: "Year Filter with Apply Button"
    implemented: true
    working: true
    file: "/app/frontend/src/components/Header.js, /app/frontend/src/components/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
          agent: "main"
          comment: "Verified via screenshot - Year filter dropdown working, selected 2025, clicked Apply Filters button. Stats updated correctly from 1668 to 388 papers, 49 to 42 countries."

  - task: "Search Functionality"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/Header.js, /app/frontend/src/components/App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Search bar visible in UI with Apply button. Need to test search functionality for countries, universities, authors, and paper titles."

  - task: "Excel Export Button and Modal"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/Header.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Export Data button visible in header. Need to test export modal opens and all export types (papers, authors, universities, countries) work correctly with current filters."

metadata:
  created_by: "main_agent"
  version: "2.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Data Processing and Cleaning Pipeline"
    - "API Endpoints for Stats and Data"
    - "Year Filtering"
    - "Search Functionality"
    - "Excel Export Functionality"
  stuck_tasks:
    - "Data Processing and Cleaning Pipeline (stuck_count: 4 - but now fixed with new approach)"
  test_all: true
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "Fixed the critical data processing issue by completely rewriting the parser in data_cleaner.py. The new parser uses a robust country-detection approach and correctly handles the complex 'Authors with affiliations' field. Tested standalone and via curl - all stats are now accurate (1668 papers, 49 countries). Frontend verified via screenshots - map, drill-down navigation, and year filter all working. Need comprehensive backend API testing for all endpoints, year filters, search functionality, and Excel exports. Frontend search and export features also need testing."
