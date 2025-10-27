# Email Reports Automation - Task Dependencies

## Project Overview
Build an automated email reporting system that processes 30 monthly Looker Studio PDF reports and generates personalized client emails. Develop locally on Windows, deploy to Linux server with cPanel.

## Current Status: Phase 3 In Progress ⏳

**Completed:**
- ✅ Phase 1: Environment Setup (100%)
- ✅ Phase 2: PDF Processing (100%)
  - ✅ collect_sample_pdfs
  - ✅ implement_pdf_extractor
  - ✅ setup_client_database
  - ✅ implement_client_database

**In Progress:**
- ⏳ Phase 3: Gmail Integration & Email Generation (25%)
  - ✅ implement_client_database (COMPLETE)
  - ⏳ implement_gmail_reader (next task)
  - ⏳ implement_email_generator
  - ⏳ implement_gmail_sender

## Task Dependency Graph

### Phase 1: Environment Setup ✅ COMPLETE

```
task: setup_local_environment ✅ COMPLETE
description: Set up local Windows development environment with Python and dependencies
dependencies: []
estimated_time: 30 minutes
deliverables:
  - Python 3.8+ installed on Windows
  - Virtual environment created at c:\Users\cscot\Documents\Apps\Email Reports\venv
  - All required packages installed (google-api-python-client, pdfplumber, Jinja2, RapidFuzz, premailer, python-dotenv)
  - requirements.txt file created
acceptance_criteria:
  - pip list shows all required packages
  - python --version shows 3.8 or higher
  - Virtual environment activates successfully
```

```
task: create_project_structure ✅ COMPLETE
description: Create folder structure for development
dependencies: [setup_local_environment]
estimated_time: 15 minutes
deliverables:
  - data/ folder for clients.csv and PDFs
  - logs/ folder for application logs
  - templates/ folder for email templates
  - config/ folder for configuration files
  - tests/ folder for unit tests
  - src/ folder for source code
acceptance_criteria:
  - All folders exist in project directory
  - .gitignore file created (excludes .env, venv/, data/, logs/, *.pyc, token.json)
```

```
task: setup_gmail_oauth ✅ COMPLETE
description: Configure Gmail API OAuth 2.0 credentials and generate token.pickle
dependencies: [setup_local_environment]
estimated_time: 45 minutes
manual_steps:
  1. Go to https://console.cloud.google.com
  2. Create new project: "Email Reports Automation"
  3. Enable Gmail API via APIs & Services > Library
  4. Configure OAuth consent screen:
     - User type: Internal (Google Workspace) or External
     - App name: "Email Reports Automation"
     - Add scopes: gmail.readonly, gmail.compose, gmail.send
  5. Create OAuth 2.0 Client ID:
     - Application type: Desktop app
     - Name: "Email Reports Desktop"
  6. Download credentials.json to project root
  7. Run initial OAuth flow: python test_auth.py
  8. Browser will open - sign in with Gmail account
  9. Grant permissions (read, compose, send)
  10. token.pickle file will be created
deliverables:
  - Google Cloud Console project created
  - Gmail API enabled
  - OAuth 2.0 desktop app credentials downloaded as credentials.json
  - token.pickle generated via initial OAuth flow on Windows
  - .env file created with configuration
acceptance_criteria:
  - credentials.json exists in project root
  - token.pickle generated successfully
  - Test script can authenticate and access Gmail API
  - .env file contains necessary configuration variables
  - Can list Gmail labels successfully (test API call)
```

### Phase 2: Core Functionality - PDF Processing ✅ COMPLETE

```
task: collect_sample_pdfs ✅ COMPLETE
description: Obtain sample Looker Studio PDFs for testing and development
dependencies: [create_project_structure]
estimated_time: 15 minutes
manual_steps:
  1. Access Gmail inbox with Looker Studio reports
  2. Download 5 PDF reports from previous months:
     - 3 SEO reports (from different clients)
     - 2 Google Ads reports (from different clients)
  3. Save to tests/fixtures/ folder
  4. Rename files descriptively:
     - sample_seo_1.pdf, sample_seo_2.pdf, sample_seo_3.pdf
     - sample_sem_1.pdf, sample_sem_2.pdf
  5. Verify PDFs open correctly
  6. Document any format variations observed
deliverables:
  - 5 sample Looker Studio PDFs in tests/fixtures/
  - Notes on PDF format variations (if any)
acceptance_criteria:
  - 3 SEO PDFs from different clients
  - 2 Google Ads PDFs from different clients
  - All PDFs open without errors
  - Files saved in tests/fixtures/ folder
```

```
task: implement_pdf_extractor ✅ COMPLETE
description: Build PDF text and table extraction module using pdfplumber
dependencies: [collect_sample_pdfs]
estimated_time: 3 hours
completion_notes: |
  - Extracts business name, report date, report type (SEO/Google Ads)
  - Extracts all KPIs with values AND change percentages
  - SEO: 7 KPIs (Sessions, Active users, New users, Key events, Engagement rate, Bounce rate, Avg session duration)
  - Google Ads: 7 KPIs (Clicks, Impressions, CTR, Conversions, Conv. rate, Avg. CPC, Cost)
  - Handles time format (00:03:29), currency ($2.96), percentages (5.12%), N/A values
  - Tested with tgc_seo.pdf and tgc_google_ads.pdf - 100% accuracy
deliverables:
  - src/pdf_extractor.py module
  - Functions to extract business name from PDF header
  - Functions to extract report date/month
  - Functions to extract KPI table data (6 metrics)
  - Visual debugging capability for troubleshooting
acceptance_criteria:
  - Can extract business name from sample Looker Studio PDF
  - Can extract date in format suitable for email subject
  - Can extract KPI table with all 6 metrics (Sessions, Conversions, Active Users, Engagement Rate, Bounce Rate, Avg Session Duration)
  - Unit tests pass for all extraction functions
  - Handles errors gracefully (missing tables, malformed PDFs)
  - Tested successfully with all 5 sample PDFs
```

```
task: setup_client_database ✅ COMPLETE
description: Create initial client database CSV with real client data
dependencies: [create_project_structure]
estimated_time: 30 minutes
completion_notes: |
  - data/clients.csv exists with 30 client records
  - Has columns: Client-ID, Contact-Name, Business-Name, Contact-Email, Service-Type,
    SEO-Introduction, Google-Ads-Introduction, Active, Created-Date, Last-Modified-Date
manual_steps:
  1. Open data/clients.csv template
  2. Populate with 30 client records:
     - ClientID (1-30)
     - FirstName (client contact first name)
     - BusinessName (EXACT name as appears in Looker Studio PDFs)
     - Email (client email address)
     - ServiceType (SEO or SEM)
     - PersonalizedText (1-2 sentence custom note per client)
     - Active (TRUE for all initially)
     - CreatedDate (today's date)
     - LastModifiedDate (today's date)
  3. Save file as CSV
  4. Backup to Google Drive
deliverables:
  - data/clients.csv with 30 real client records
  - Backup copy in Google Drive
acceptance_criteria:
  - All 30 clients entered with complete data
  - Business names match Looker Studio PDF headers exactly
  - Email addresses valid and current
  - Service types correctly identified (SEO or SEM)
  - File opens correctly in Excel
```

```
task: implement_client_database ✅ COMPLETE
description: Build client database module with CSV reading and fuzzy matching
dependencies: [setup_client_database]
estimated_time: 2 hours
completion_notes: |
  - src/client_database.py module implemented with full CSV reading
  - Uses RapidFuzz library for fuzzy matching with token_sort_ratio (handles word order variations)
  - Fuzzy matching threshold: 85% (configurable)
  - Exact matching (case-insensitive) tries first for performance
  - Additional methods: find_all_matches, get_service_type, get_personalized_intro, validate_database
  - Comprehensive test suite: test_client_database.py with 8 test scenarios
  - Test results: 100% pass rate (8/8 tests passed)
  - Tests cover: CSV loading, exact matching, fuzzy matching, PDF extraction matching, edge cases, multiple matches, validation, service type detection
  - Successfully matches "The George Centre" from PDF extraction
  - Loaded 30 clients from data/clients.csv successfully
  - No critical issues found in database validation
  - Handles missing fields gracefully with warnings
deliverables:
  - src/client_database.py module
  - Functions to load client data from CSV
  - Fuzzy matching logic to match business names from PDFs to database
  - Client record validation
  - test_client_database.py comprehensive test suite
acceptance_criteria:
  - ✅ Can load clients.csv successfully (30 clients loaded)
  - ✅ Fuzzy matching correctly identifies client with 90%+ accuracy (100% on test cases)
  - ✅ Returns client contact name, email, service-specific intro text
  - ✅ Handles edge cases (no match found, multiple matches, empty database)
  - ✅ Unit tests pass (8/8 tests passed, 100% success rate)
```

### Phase 3: Gmail Integration

```
task: implement_gmail_reader
description: Build Gmail API integration to read emails and extract PDF attachments
dependencies: [setup_gmail_oauth]
estimated_time: 3 hours
deliverables:
  - src/gmail_reader.py module
  - Functions to authenticate with Gmail API
  - Functions to search for Looker Studio emails
  - Functions to download PDF attachments
  - Functions to mark emails as processed
acceptance_criteria:
  - Can authenticate using token.json
  - Can search for emails with query filter
  - Can download PDF attachments to data/ folder
  - Handles API rate limits and errors
  - Unit tests pass (using mocked Gmail API)
```

```
task: implement_email_generator
description: Build HTML email generation module using Jinja2 templates
dependencies: [create_project_structure, implement_client_database, implement_pdf_extractor]
estimated_time: 4 hours
deliverables:
  - templates/email_template.html (Jinja2 template)
  - src/email_generator.py module
  - Functions to render personalized HTML emails
  - Functions to inline CSS using premailer
  - Functions to generate email subject lines with dates
  - HTML email styling to match sample format
acceptance_criteria:
  - Generates valid HTML email with personalized greeting
  - Includes predefined text from client database
  - Includes KPI table with extracted data
  - Subject line formatted as "Your [Month] [SEO/Google Ads] Report"
  - CSS properly inlined for email client compatibility
  - Unit tests pass
```

```
task: implement_gmail_sender
description: Build Gmail API integration to create drafts and send emails
dependencies: [setup_gmail_oauth, implement_email_generator]
estimated_time: 3 hours
deliverables:
  - src/gmail_sender.py module
  - Functions to create Gmail drafts with attachments
  - Functions to send preview emails
  - Functions to implement sending delays (spaced out sending)
acceptance_criteria:
  - Can create Gmail draft with HTML body
  - Can attach PDF to draft
  - Can send email via Gmail API
  - Implements rate limiting for spaced-out sending
  - Handles errors and retries
  - Unit tests pass (using mocked Gmail API)
```

### Phase 4: Approval Workflow

```
task: implement_approval_workflow
description: Build CSV-based approval tracking system
dependencies: [implement_email_generator]
estimated_time: 2 hours
deliverables:
  - data/approval_tracking.csv template
  - src/approval_tracker.py module
  - Functions to generate approval tracking CSV
  - Functions to read approval status from CSV
  - Functions to filter approved vs. needs-revision emails
acceptance_criteria:
  - Generates approval_tracking.csv with all clients
  - Can read and parse approval status
  - Returns list of approved client IDs
  - Handles missing or malformed CSV
  - Unit tests pass
```

### Phase 5: Main Orchestration

```
task: implement_main_orchestrator
description: Build main application logic that coordinates all modules
dependencies: [implement_pdf_extractor, implement_client_database, implement_gmail_reader, implement_email_generator, implement_gmail_sender, implement_approval_workflow]
estimated_time: 4 hours
deliverables:
  - src/main.py main application file
  - Workflow: fetch emails → extract PDFs → match clients → generate emails → send previews → read approvals → create drafts
  - Command-line arguments for different modes (full_run, preview_only, drafts_only)
  - Comprehensive logging throughout workflow
  - Error handling and rollback capability
acceptance_criteria:
  - Can execute full workflow end-to-end
  - Logs all activities to logs/ folder
  - Handles errors gracefully without crashing
  - Can run in different modes via CLI arguments
  - Integration tests pass with sample data
```

```
task: implement_logging_system
description: Build comprehensive logging and error tracking
dependencies: [create_project_structure]
estimated_time: 1.5 hours
deliverables:
  - src/logger.py logging configuration
  - Log file rotation (daily logs)
  - Different log levels (DEBUG, INFO, WARNING, ERROR)
  - Structured log format with timestamps
acceptance_criteria:
  - Logs written to logs/ folder with date-based filenames
  - Console output shows INFO and above
  - File logs capture DEBUG and above
  - Log rotation works correctly
  - Errors include stack traces
```

### Phase 6: Testing & Documentation

```
task: write_unit_tests
description: Write comprehensive unit tests for all modules
dependencies: [implement_main_orchestrator]
estimated_time: 4 hours
deliverables:
  - tests/test_pdf_extractor.py
  - tests/test_client_database.py
  - tests/test_gmail_reader.py
  - tests/test_email_generator.py
  - tests/test_gmail_sender.py
  - tests/test_approval_tracker.py
  - Sample test data and fixtures
test_coverage_requirements:
  - PDF extraction: Test with all 5 sample PDFs (3 SEO, 2 SEM)
  - Business name extraction: 100% accuracy required
  - KPI extraction: All 6 metrics extracted correctly
  - Fuzzy matching: Test with typos (85%+ threshold)
  - Email generation: Validate HTML structure and CSS inlining
  - Gmail API: Mock API calls, test error handling
acceptance_criteria:
  - All modules have >80% code coverage
  - Tests use mocking for external APIs (Gmail API)
  - Tests can run independently (no order dependency)
  - All tests pass with pytest
  - pytest configured and working
  - Test execution time < 30 seconds
```

```
task: write_integration_tests
description: Write end-to-end integration tests
dependencies: [implement_main_orchestrator, write_unit_tests]
estimated_time: 3 hours
deliverables:
  - tests/test_integration.py
  - Mock data for full workflow testing
  - Integration test scenarios (success, partial failure, full failure)
test_scenarios:
  1. Happy path: Process 5 PDFs end-to-end successfully
  2. PDF parsing failure: 1 corrupted PDF, 4 successful
  3. Database mismatch: Business name not found
  4. Approval workflow: Mix of approved/rejected emails
  5. Gmail API failure: Simulate network error, test retry
  6. Partial success: 3/5 emails process correctly
acceptance_criteria:
  - Can test full workflow with mock data
  - Tests cover happy path and error scenarios
  - All integration tests pass
  - Test execution time < 2 minutes
  - Each scenario logs appropriately
  - System continues processing after recoverable errors
```

```
task: create_user_documentation
description: Write user documentation for how to use the system
dependencies: [implement_main_orchestrator]
estimated_time: 2 hours
deliverables:
  - README.md with project overview and setup instructions
  - USAGE.md with step-by-step workflow guide
  - DEPLOYMENT.md with server deployment instructions
  - Sample .env.example file
acceptance_criteria:
  - README explains what the system does and how to install
  - USAGE explains monthly workflow step-by-step
  - DEPLOYMENT explains cPanel deployment process
  - Documentation is clear and includes examples
```

### Phase 7: Deployment Preparation

```
task: verify_agency_branding
description: Collect and configure agency branding information
dependencies: [create_project_structure]
estimated_time: 15 minutes
manual_steps:
  1. Confirm agency name (for email signature)
  2. Confirm agency email address (for signature)
  3. Confirm agency phone number (for signature)
  4. Confirm agency website URL (for signature)
  5. Confirm standard paragraph text for SEO reports
  6. Confirm standard paragraph text for Google Ads reports
  7. Confirm closing paragraph text
  8. Update .env file with all branding information
deliverables:
  - .env file with complete branding configuration
  - Sample email preview with actual branding
acceptance_criteria:
  - All branding fields populated in .env
  - Email signature displays correctly
  - Standard paragraphs match agency tone/voice
  - User approves email template appearance
```

```
task: prepare_server_deployment
description: Prepare application for Linux server deployment
dependencies: [write_integration_tests, create_user_documentation]
estimated_time: 2 hours
manual_prerequisites:
  - cPanel access credentials confirmed
  - Server Python version verified (3.8+)
  - SSH access confirmed (optional but helpful)
  - File upload method chosen (cPanel File Manager or FTP/SFTP)
deliverables:
  - requirements.txt verified for Linux compatibility
  - Deployment checklist document (DEPLOYMENT.md)
  - Server configuration notes (cron job examples, paths)
  - Migration script to help transfer files to server
  - Server path mapping (Windows paths → Linux paths)
acceptance_criteria:
  - requirements.txt lists all dependencies with versions
  - Deployment checklist covers all steps
  - Cron job example provided for monthly automation
  - Clear instructions for uploading token.pickle and .env to server
  - Path conversion documented (c:\ → /home/username/)
```

```
task: test_cross_platform_compatibility
description: Verify code works on both Windows (dev) and Linux (prod)
dependencies: [prepare_server_deployment]
estimated_time: 1.5 hours
cross_platform_checklist:
  - Replace all hardcoded paths with pathlib.Path or os.path.join
  - Use forward slashes (/) in .env file paths (works on both systems)
  - Test path handling with sample Windows and Linux paths
  - Verify pickle/JSON files are binary-safe
  - Check line endings (use \n, not \r\n)
  - Confirm no Windows-specific library dependencies
deliverables:
  - Cross-platform compatibility verification report
  - Path handling fixes (use os.path.join, pathlib)
  - Line ending fixes if necessary
  - Compatibility test results document
acceptance_criteria:
  - All file paths use cross-platform compatible methods (pathlib.Path)
  - No hardcoded Windows paths (backslashes) in code
  - .env file uses forward slashes for all paths
  - Tests pass on Windows
  - (If possible) Tests pass on Linux test environment
  - Code review confirms no platform-specific dependencies
```

### Phase 8: Initial Deployment & Testing

```
task: deploy_to_server
description: Deploy application to Linux server via cPanel
dependencies: [test_cross_platform_compatibility]
estimated_time: 2 hours
manual_deployment_steps:
  1. Log in to cPanel
  2. Navigate to File Manager
  3. Create directory: /home/username/email_reports/
  4. Upload all files EXCEPT:
     - venv/ (recreate on server)
     - __pycache__/ (will regenerate)
     - logs/*.log (old logs)
     - data/pdfs/*.pdf (test PDFs)
  5. Upload .env file separately (contains config)
  6. Upload token.pickle file separately (contains OAuth tokens)
  7. Set file permissions:
     - Folders: 755
     - Python files: 644
     - .env: 600 (owner only)
     - token.pickle: 600 (owner only)
  8. Open SSH terminal (or use cPanel Python app)
  9. Create virtual environment: python3 -m venv venv
  10. Activate: source venv/bin/activate
  11. Install dependencies: pip install -r requirements.txt
  12. Test: python src/main.py --help
deliverables:
  - Application uploaded to /home/username/email_reports/
  - Virtual environment created on server
  - Dependencies installed on server
  - .env file configured on server (with Linux paths)
  - token.pickle uploaded to server
  - File permissions set correctly
acceptance_criteria:
  - All files present on server (verify with ls -la)
  - Python virtual environment activates successfully
  - Can run python src/main.py --help without errors
  - Logs directory is writable (test with touch logs/test.log)
  - Can access Gmail API from server (run test_auth.py)
  - .env file paths use Linux format (/home/username/...)
```

```
task: configure_cron_job
description: Set up cron job for monthly automated processing
dependencies: [deploy_to_server]
estimated_time: 30 minutes
deliverables:
  - Cron job configured in cPanel
  - Cron job script (if needed)
  - Test execution to verify cron job works
acceptance_criteria:
  - Cron job scheduled for 1st of month at 9am
  - Cron job executes Python script correctly
  - Logs confirm cron execution
  - Email notification on cron errors (optional)
```

```
task: conduct_parallel_run_testing
description: Run new system in parallel with Relevance AI for one month
dependencies: [configure_cron_job]
estimated_time: Ongoing (1 month)
deliverables:
  - Parallel run monitoring log
  - Comparison report (new system vs Relevance AI)
  - Bug fixes and adjustments based on real data
  - Performance metrics
acceptance_criteria:
  - Both systems process same 30 PDFs
  - New system produces identical or better results
  - No critical errors in new system
  - New system completes faster than manual process
  - All 30 emails sent successfully
```

## Phase 9: Cutover & Optimization

```
task: cutover_from_relevance
description: Disable Relevance AI and fully migrate to new system
dependencies: [conduct_parallel_run_testing]
estimated_time: 1 hour
deliverables:
  - Relevance AI disabled
  - Make.com scenario disabled (if using Gmail API)
  - New system as primary automation
  - Rollback plan documented
acceptance_criteria:
  - Only new system running
  - Backup plan ready in case of issues
  - User confirms successful operation
  - Documentation updated
```

```
task: monitor_and_optimize
description: Monitor first 3 months of operation and optimize
dependencies: [cutover_from_relevance]
estimated_time: Ongoing (3 months)
deliverables:
  - Monthly performance reports
  - Bug fixes and improvements
  - User feedback incorporation
  - Process refinements
acceptance_criteria:
  - System runs successfully for 3 consecutive months
  - No critical failures
  - User satisfaction confirmed
  - Time savings documented
```

## Success Criteria

- All 30 clients receive monthly reports automatically
- Workflow takes < 30 minutes from PDF arrival to approval
- 100% accuracy in KPI data extraction
- 100% email delivery success rate
- Zero manual intervention needed after approval
- Cost savings of $456-1,536/year achieved (Relevance AI + Make.com eliminated)

## Timeline Estimate

- Phase 1 (Environment Setup): 1.5 hours
- Phase 2 (Core Functionality): 5 hours
- Phase 3 (Gmail Integration): 10 hours
- Phase 4 (Approval Workflow): 2 hours
- Phase 5 (Main Orchestration): 5.5 hours
- Phase 6 (Testing & Docs): 9 hours
- Phase 7 (Deployment Prep): 3.5 hours
- Phase 8 (Deployment & Testing): 1 month + 4.5 hours
- Phase 9 (Cutover): 3 months ongoing

**Total Development Time: ~40 hours over 1-2 weeks**
**Total Testing & Validation: 4 months (parallel run + monitoring)**
