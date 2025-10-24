# CLAUDE.md - SEO/SEM Client Report Automation System

## Executive Summary

### Project Vision
Build an automated email reporting system that transforms Looker Studio PDF reports into personalized, data-rich client emails with minimal manual intervention. The system will replace the current Relevance AI workflow, reducing costs while increasing automation flexibility and enabling future AI-powered insights.

### Strategic Context
This project addresses a critical operational bottleneck for a digital marketing agency managing 30 SEO and Google Ads clients. Currently, monthly client reporting requires manual PDF attachment, lacks Google Analytics integration, and incurs significant costs through Relevance AI. The new system will automate 90% of the reporting workflow while maintaining quality control through a streamlined approval process.

### Success Criteria
- **Time Efficiency:** Reduce report preparation time from hours to minutes per month
- **Quality Assurance:** Zero errors in KPI data extraction, personalization, or PDF attachments
- **Cost Reduction:** Eliminate Relevance AI subscription while maintaining or improving functionality
- **Delivery Success:** 100% successful delivery to all 30 clients monthly
- **User Adoption:** System maintainable by agency owner without external technical support

### Project Phases
**Phase 1 (MVP):** PDF extraction, KPI parsing, personalized email generation, approval workflow, Gmail draft creation
**Phase 2 (Future):** Google Analytics MCP integration, AI-generated insights, interactive dashboard, auto-send capability

---

## Press Release (External Positioning)

**FOR IMMEDIATE RELEASE**

**Local Digital Marketing Agency Launches Next-Generation Client Reporting System**

Today marks a significant milestone in client communication excellence as our agency unveils a sophisticated automated reporting system that delivers personalized, data-rich monthly performance reports with unprecedented speed and accuracy.

"Our clients deserve timely, personalized insights into their digital marketing performance," said the Agency Director. "This new system allows us to deliver beautiful, data-driven reports at the start of each month while freeing our team to focus on strategic analysis and optimization."

The new reporting system processes performance data from Looker Studio, extracting key metrics including sessions, conversions, user engagement, and bounce rates. Each report is personalized with the client's business name, customized commentary, and actionable insights, delivered as both an HTML email and comprehensive PDF attachment.

Unlike generic automated systems, this solution maintains the personal touch clients expect while ensuring data accuracy through a built-in approval workflow. Reports are sent in a measured cadence to ensure optimal inbox placement and client engagement.

**What This Means for Clients:**
- Consistent, timely reports at the start of each month
- Clear, visual presentation of key performance indicators
- Personalized insights specific to their business
- Professional HTML formatting optimized for all email clients
- Comprehensive PDF reports for detailed analysis

**What This Means for Our Agency:**
- Faster turnaround on monthly reporting
- Elimination of manual data entry errors
- Scalable infrastructure supporting business growth
- Foundation for AI-powered performance insights (coming soon)

The system represents a significant investment in client experience and operational efficiency, positioning the agency for continued growth while maintaining the personalized service that has defined our client relationships.

---

## Customer FAQ (User-Facing Concerns)

### Report Delivery & Timing

**Q: When will I receive my monthly report?**
A: Reports are sent during the first week of each month, covering the previous month's performance. You'll receive your report via email with both an HTML summary and PDF attachment.

**Q: What if I don't receive my report?**
A: Reports are sent from our business Gmail account. Please check your spam folder and add our email to your contacts. If you still don't receive it, contact us immediately and we'll resend.

**Q: Can I request my report earlier in the month?**
A: Reports are generated once Looker Studio compiles the complete monthly data. We send them as soon as the data is available, typically within the first few days of the new month.

### Report Content & Data

**Q: What metrics are included in my report?**
A: Your report includes six core KPIs: Sessions, Conversions, Active Users, Engagement Rate, Bounce Rate, and Average Session Duration. These metrics provide a comprehensive view of your website or campaign performance.

**Q: How is this data different from my Google Analytics dashboard?**
A: The data comes from the same source (Google Analytics or Google Ads), but is curated and presented specifically for your business. We include personalized commentary and context to help you understand what the numbers mean for your goals.

**Q: Can I request additional metrics?**
A: Absolutely. The current report includes the most important KPIs, but we can customize your report to include additional metrics based on your business objectives. Contact us to discuss customization options.

### Report Format & Access

**Q: Why do I receive both an HTML email and a PDF?**
A: The HTML email provides quick, at-a-glance insights you can read immediately in your inbox. The PDF is a comprehensive report you can save, print, or share with stakeholders.

**Q: Can I access previous months' reports?**
A: Yes, all PDF reports are saved to your email. We recommend creating a folder in your email client to archive these reports for easy reference.

**Q: Is the report mobile-friendly?**
A: Yes, the HTML email is designed to display beautifully on desktop, tablet, and mobile devices.

### Personalization & Customization

**Q: Why does my report include specific commentary about my business?**
A: We believe automated doesn't mean impersonal. Each report includes customized notes based on your business goals, ongoing campaigns, and strategic priorities.

**Q: Can the commentary be updated if my business priorities change?**
A: Yes, we review and update personalized commentary quarterly or upon request. Let us know if your business focus shifts and we'll adjust your report accordingly.

---

## Internal FAQ (Team & Stakeholder Concerns)

### Migration & Implementation

**Q: Why are we moving away from Relevance AI?**
A: Relevance AI served its purpose but has three critical limitations: (1) ongoing subscription costs that don't align with our usage, (2) inflexible automation requiring manual PDF attachment, and (3) lack of Google Analytics MCP integration for future AI-powered insights. The new system addresses all three issues while providing greater control and customization.

**Q: What's the migration plan?**
A: Phase 1 (MVP) replicates and improves current functionality: PDF extraction, KPI parsing, email generation, and approval workflow. We'll run parallel systems for one reporting cycle to ensure reliability before fully deprecating Relevance AI.

**Q: How long until the system is operational?**
A: No fixed deadline. We're prioritizing quality over speed, with a flexible timeline that allows thorough testing and refinement.

### Technical Architecture & Decisions

**Q: What are the deployment options being considered?**
A: Three primary approaches are under evaluation:
1. **Local Windows Application:** Runs on office workstation, full control, no hosting costs
2. **Cloud-Hosted Solution:** Runs on cloud infrastructure, accessible anywhere, recurring costs
3. **Hybrid Approach:** PDF processing local, email generation cloud-based

The plan-synthesizer will provide detailed pros/cons analysis for each option based on security, cost, reliability, and maintenance requirements.

**Q: How will PDF extraction work?**
A: Currently evaluating two approaches:
1. Continue using Make.com (existing integration, proven reliability)
2. Gmail API direct integration (eliminates third-party dependency, more control)

Decision will be based on complexity, cost, and maintenance overhead.

**Q: What database will store client information?**
A: Options under evaluation: CSV (simple, portable), SQLite (structured, no server), Google Sheets (collaborative, cloud-based). Selection criteria: ease of updates, backup reliability, and deployment environment compatibility.

**Q: How will we handle the approval workflow?**
A: Two approaches being researched:
1. **Email-based review:** Drafts sent to review address, managed via CSV tracking spreadsheet
2. **Preview interface:** Web-based interface showing exact email appearance before approval

If interface approach is chosen, it must render emails identically to how they'll appear when sent.

### Security & Compliance

**Q: How is client data secured?**
A: All API credentials and OAuth tokens stored in .env file (never committed to version control). No sensitive client data is involved—only business names, contact emails, and service types. PDFs are archived after processing, with copies retained in Google Drive.

**Q: What OAuth scopes are required for Gmail integration?**
A: Minimum required scopes: Gmail API read access (for PDF extraction), Gmail API draft creation, Gmail API send (for future auto-send). All OAuth credentials managed through Google Workspace admin console.

**Q: What happens if credentials are compromised?**
A: Credentials can be revoked and regenerated through Google Workspace console. System uses OAuth 2.0 with refresh tokens, allowing credential rotation without system reconfiguration.

### Workflow & Operations

**Q: What's the exact workflow from PDF receipt to sent email?**
A:
1. Looker Studio emails 30 PDFs to business Gmail (batch arrival over few hours, start of month)
2. System extracts PDFs from email (Make.com or Gmail API)
3. PDFs stored temporarily for processing
4. For each PDF:
   - Extract business name from report header
   - Extract date/month for subject line construction
   - Extract KPI table (6 metrics: Sessions, Conversions, Active Users, Engagement Rate, Bounce Rate, Avg Session Duration)
   - Match business name to client database
   - Retrieve: client first name, email, service type (SEO/SEM), predefined personalized text
5. Generate HTML email:
   - Subject: "Your [Month] SEO Report" or "Your [Month] Google Ads Report"
   - Greeting: "Hi [First Name],"
   - Opening: "Please see the data below for [Business Name]."
   - Personalized text (1-2 lines, predefined per client)
   - Standard paragraph about keyword rankings
   - KPI table (HTML formatted for email compatibility)
   - Standard closing paragraph
   - Attach original PDF report
6. Send all draft emails to review address OR present in approval interface
7. User reviews via CSV/spreadsheet tracking (client name, status, notes columns)
8. User marks approved/needs revision in tracking sheet
9. System creates Gmail drafts for all approved emails
10. User manually sends each draft from Gmail, spacing out sends (not all at once)

**Q: How many clients do we process monthly?**
A: 30 clients total: approximately 25 SEO reports and 5 Google Ads reports. All processed as monthly batch, not real-time.

**Q: What happens if a PDF is corrupted or data can't be extracted?**
A: System will flag extraction errors in approval workflow. User can manually review problem PDFs and decide whether to fix source data or manually create email for that client.

**Q: How are emails spaced out to avoid spam flags?**
A: User manually sends from Gmail drafts, naturally spacing sends. Future Phase 2 may introduce auto-send with configurable delays (e.g., 5-10 minutes between sends).

### Cost & Resources

**Q: What's the budget for this project?**
A: Free and open-source tools preferred. Willing to pay small amounts for premium tools if value is clearly justified. Primary cost savings goal: eliminate Relevance AI subscription.

**Q: What ongoing maintenance is required?**
A: User (agency owner) will maintain system themselves. Documentation must focus on "how to use" rather than deep technical architecture. Key maintenance tasks: updating client database, reviewing/approving emails, handling extraction errors.

**Q: What skills are required for maintenance?**
A: User is comfortable with technical setup and following documentation. System should require minimal coding knowledge for routine operations (updating client data, running monthly process, handling common errors).

### Future Roadmap (Phase 2)

**Q: What's planned for Phase 2?**
A:
1. **Google Analytics MCP Integration:** Direct connection to Google Analytics for real-time data access
2. **AI-Generated Insights:** Claude-powered analysis identifying trends, anomalies, and opportunities
3. **Interactive Dashboard:** Web-based approval interface replacing CSV spreadsheet
4. **Auto-Send Capability:** Automated sending with spacing after approval (vs. manual Gmail sending)

**Q: When will Phase 2 features be implemented?**
A: Phase 2 timeline is undefined and depends on Phase 1 success, user feedback, and business priorities. Each Phase 2 feature can be implemented independently.

**Q: Will AI insights replace personalized text?**
A: No. AI insights will augment, not replace, the predefined personalized text. The system will combine human-written custom notes (relationship context, ongoing initiatives) with AI-generated performance analysis (trend identification, anomaly detection, recommendations).

---

## Core Definitions & Glossary

### Business Entities

**Client:** Digital marketing service customer receiving monthly SEO or Google Ads reports. Total: 30 clients (~25 SEO, ~5 Google Ads).

**Business Name:** Official company/organization name as it appears on Looker Studio reports. Used for matching PDF to client database record.

**Service Type:** Either "SEO" or "SEM" (Google Ads). Determines report type, subject line, and content template.

### Technical Components

**Looker Studio:** Google's data visualization platform that generates monthly PDF reports from Google Analytics and Google Ads data. Reports are automatically emailed to business Gmail account.

**KPI (Key Performance Indicator):** Six metrics extracted from PDF reports:
1. **Sessions:** Total number of website visits
2. **Conversions:** Completed goal actions (form submissions, purchases, etc.)
3. **Active Users:** Unique visitors who engaged with the site
4. **Engagement Rate:** Percentage of sessions with meaningful interaction
5. **Bounce Rate:** Percentage of single-page sessions
6. **Average Session Duration:** Mean time spent on site per session

**Predefined Email Text:** 1-2 lines of customized commentary stored in client database, specific to each client's business context, ongoing campaigns, or strategic priorities.

**HTML Email:** Formatted email content with proper styling, tables, and structure. Must render consistently across email clients (Gmail, Outlook, Apple Mail, etc.).

**PDF Attachment:** Original Looker Studio report attached to email. File naming convention: `[Business Name] - [Month] [Year] [Report Type].pdf`

### Workflow Stages

**PDF Extraction:** Process of retrieving PDF files from Gmail inbox. Two approaches under evaluation: Make.com automation or Gmail API direct integration.

**KPI Parsing:** Extracting structured data (business name, date, six metrics) from PDF text/tables. Requires PDF parsing library capable of handling Looker Studio's format.

**Database Matching:** Comparing extracted business name against client database to retrieve personalization data (first name, email, service type, custom text).

**Email Generation:** Combining template, personalized data, KPI table, and PDF attachment into complete email draft.

**Approval Workflow:** User review process before sending. Options: email preview with CSV tracking or web-based interface showing exact email rendering.

**Draft Creation:** Generating Gmail draft messages via Gmail API for user to send manually.

**Spaced Sending:** Distributing email sends over time (not all at once) to avoid spam flags and improve deliverability.

### System States

**Batch Processing:** All 30 PDFs processed together monthly (not real-time individual processing).

**Approval Pending:** Email generated and awaiting user review before draft creation.

**Approved:** Email cleared for Gmail draft creation and sending.

**Needs Revision:** Email flagged by user for manual correction (data extraction error, wrong client match, etc.).

**Sent:** Email successfully delivered to client.

---

## Technical Architecture & Constraints

### Current Environment

**Working Directory:** `c:\Users\cscot\Documents\Apps\Email Reports`

**Platform:** Windows (local development and potential deployment target)

**Email Infrastructure:** Google Workspace business account

**Processing Model:** Monthly batch processing (30 PDFs arriving over few hours at start of month)

**Current Workflow:** Looker Studio → Email → Make.com → Google Drive → Relevance AI → Gmail drafts

### Technology Stack (To Be Determined by Plan-Synthesizer)

**RESEARCH REQUIREMENT:** The plan-synthesizer must evaluate and recommend optimal technology choices for:

1. **Deployment Architecture**
   - **Local Windows Application:** Runs on `c:\Users\cscot\Documents\Apps\Email Reports`
     - Pros: Full control, no hosting costs, direct file system access, works offline
     - Cons: Requires local machine running, no remote access, backup responsibility
   - **Cloud-Hosted Solution:** Runs on cloud platform (AWS Lambda, Google Cloud Functions, Heroku, etc.)
     - Pros: Accessible anywhere, automatic scaling, managed backups, reliable uptime
     - Cons: Ongoing hosting costs, internet dependency, slightly more complex deployment
   - **Hybrid Approach:** PDF processing local, email generation/approval cloud-based
     - Pros: Balances cost and accessibility, leverages local storage, cloud collaboration
     - Cons: Most complex architecture, requires synchronization between environments

2. **Email Ingestion Method**
   - **Make.com (Current):** Continue using existing Make.com scenario
     - Pros: Already configured, proven reliability, no new integration needed
     - Cons: Third-party dependency, ongoing subscription cost, less control
   - **Gmail API Direct:** Python/Node.js Gmail API integration
     - Pros: No third-party dependency, full control, free (within quotas), better error handling
     - Cons: Requires OAuth setup, more initial development, quota management

3. **Client Database Format**
   - **CSV File:** Simple text file with client records
     - Pros: Easy to edit (Excel/Sheets), portable, version control friendly, no database server
     - Cons: No data validation, concurrent access issues, manual backup
   - **SQLite:** Embedded relational database
     - Pros: Structured queries, data validation, ACID compliance, single file
     - Cons: Requires database tool for editing, binary format (not human-readable)
   - **Google Sheets:** Cloud spreadsheet via API
     - Pros: Collaborative editing, automatic backup, familiar interface, accessible anywhere
     - Cons: API quota limits, internet dependency, slightly slower access
   - **Recommendation Criteria:** Consider deployment model (local vs cloud), update frequency, user comfort with tools, backup requirements

4. **PDF Parsing Library**
   - **Python Options:** PyPDF2, pdfplumber, tabula-py, camelot-py
   - **Node.js Options:** pdf-parse, pdf2json, pdfjs-dist
   - **Evaluation Criteria:**
     - Ability to extract text from Looker Studio PDFs
     - Table extraction accuracy (KPI data is in table format)
     - Handling of formatted text (business name in header)
     - Ease of installation on Windows
     - Active maintenance and documentation

5. **Email Template System**
   - **Python Options:** Jinja2, email.mime (stdlib)
   - **Node.js Options:** Handlebars, EJS, Pug
   - **Requirements:**
     - Generate valid HTML email with CSS inlining
     - Support for dynamic tables
     - Consistent rendering across email clients

6. **Gmail API Integration**
   - **Authentication:** OAuth 2.0 with refresh tokens
   - **Required Scopes:**
     - `gmail.readonly` or `gmail.modify` (for PDF extraction)
     - `gmail.compose` (for draft creation)
     - `gmail.send` (for future Phase 2 auto-send)
   - **Rate Limits:** 250 quota units per user per second (well within monthly batch requirements)

7. **Approval Workflow Interface**
   - **Option A: Email-Based Review**
     - Drafts sent to review email address
     - CSV/spreadsheet tracking (columns: Client Name, Business Name, Status, Notes, Extraction Errors)
     - User marks "Approved" or "Needs Revision" in spreadsheet
     - System reads spreadsheet to determine which emails to draft
     - Pros: Simple, no UI development, uses familiar tools
     - Cons: Less visual, requires manual spreadsheet management
   - **Option B: Web Preview Interface**
     - Local or cloud-hosted web app
     - Shows exact email rendering (must look identical to sent email)
     - Click to approve/reject each email
     - Notes field for revision comments
     - Pros: Visual verification, better UX, integrated experience
     - Cons: Requires web development, must perfectly replicate email rendering
   - **Decision Criteria:** User preference, development complexity, accuracy of email preview

### Security Requirements

**Credential Management:**
- All API keys, OAuth tokens, and credentials stored in `.env` file
- `.env` file never committed to version control (add to `.gitignore`)
- Use environment variable libraries (python-dotenv, dotenv for Node.js)

**Data Privacy:**
- No sensitive personal data (only business names, contact emails, service types)
- PDFs archived after processing (copies retained in Google Drive)
- Client database backup strategy needed (automatic or manual)

**OAuth Security:**
- Use OAuth 2.0 authorization code flow
- Store refresh tokens securely (encrypted or environment variables)
- Implement token rotation
- Restrict OAuth scopes to minimum required permissions

**Access Control:**
- Gmail API credentials restricted to business Google Workspace account
- No multi-user access required (single agency owner user)

### Performance Requirements

**Processing Speed:**
- Process 30 PDFs within 10-15 minutes (not time-critical, monthly batch)
- Email generation: < 30 seconds per email
- Total workflow: < 30 minutes from PDF extraction to draft creation

**Reliability:**
- 100% success rate on KPI extraction (with fallback error flagging)
- Zero data corruption or client mismatches
- Graceful error handling with clear error messages

**Scalability:**
- Support for 30 clients (MVP)
- Architecture should accommodate growth to 50-100 clients (Phase 2+)

### Integration Requirements

**Gmail Integration:**
- Read emails from specific sender (Looker Studio)
- Extract PDF attachments
- Create draft emails
- Attach PDF files to drafts
- (Phase 2) Send emails programmatically

**Google Drive (Existing):**
- PDFs already synced to Google Drive via Make.com
- System should archive processed PDFs
- No active integration required for MVP

**Google Analytics (Phase 2):**
- MCP (Model Context Protocol) integration for direct data access
- Real-time metric queries
- Enables AI-generated insights

### Development Constraints

**Platform:** Windows (`win32` environment)

**File System:** Windows path format (`c:\Users\...`)

**Maintenance:** User will self-maintain (clear documentation required)

**Documentation:** "How to use" focus, not deep technical architecture

**Cost:** Free/open-source preferred, small paid tools acceptable if justified

**Timeline:** Flexible, no hard deadline

---

## Success Metrics & Measurement Plan

### Primary Success Metrics

**1. Time Efficiency**
- **Metric:** Total time from PDF receipt to all emails sent
- **Baseline:** Current Relevance AI workflow time (estimate: 2-4 hours)
- **Target:** < 30 minutes for complete workflow (90%+ reduction)
- **Measurement:** Manual timing for first 3 monthly cycles, then quarterly spot checks

**2. Data Accuracy**
- **Metric:** Percentage of emails with zero errors
- **Error Types:** Wrong KPI data, incorrect client matching, missing attachments, wrong personalization
- **Target:** 100% error-free (30/30 emails correct)
- **Measurement:** Manual verification during approval workflow, client feedback tracking

**3. Cost Reduction**
- **Metric:** Monthly operational cost (tools, subscriptions, hosting)
- **Baseline:** Relevance AI subscription cost
- **Target:** 75%+ cost reduction
- **Measurement:** Monthly expense tracking

**4. Delivery Success**
- **Metric:** Successful delivery to all clients
- **Target:** 100% delivery rate (30/30 sent and received)
- **Measurement:** Gmail sent confirmation, client acknowledgment, bounce tracking

**5. User Adoption**
- **Metric:** System usability without external support
- **Target:** Zero support requests after first month
- **Measurement:** Support ticket tracking, user feedback

### Secondary Success Metrics

**6. Processing Reliability**
- **Metric:** Percentage of PDFs successfully extracted and parsed
- **Target:** 95%+ automatic success, 5% flagged for manual review
- **Measurement:** Error logs, approval workflow flags

**7. Email Rendering Consistency**
- **Metric:** Proper display across email clients (Gmail, Outlook, Apple Mail)
- **Target:** 100% consistent rendering
- **Measurement:** Test sends to multiple email clients, client feedback

**8. Maintenance Effort**
- **Metric:** Time spent on monthly system operation
- **Target:** < 15 minutes per month (excluding email review/approval)
- **Measurement:** User time tracking for database updates, error handling, system checks

### Measurement Schedule

**Weekly (During Implementation):**
- Development progress against milestones
- Blocker identification and resolution

**Monthly (First 3 Months Post-Launch):**
- All primary metrics (time, accuracy, cost, delivery, adoption)
- Error pattern analysis
- User feedback collection

**Quarterly (Ongoing):**
- Primary metrics review
- Cost-benefit analysis
- Phase 2 readiness assessment

### Success Criteria for MVP Launch

**Must Have (Go/No-Go Criteria):**
- [ ] 100% accurate KPI extraction from test PDFs
- [ ] Zero client mismatches in test runs
- [ ] All emails render correctly in Gmail, Outlook, Apple Mail
- [ ] PDF attachments successfully included in all drafts
- [ ] User can complete full workflow in < 30 minutes
- [ ] Documentation sufficient for user self-maintenance

**Should Have (Quality Indicators):**
- [ ] Graceful error handling with clear messages
- [ ] Automated backup of client database
- [ ] Comprehensive logging for troubleshooting
- [ ] Rollback capability if issues arise

**Nice to Have (Future Enhancements):**
- [ ] Automated testing suite
- [ ] Dashboard showing processing statistics
- [ ] Email preview before approval (if not core feature)

---

## Feature Specifications & User Stories

### Feature 1: PDF Extraction from Gmail

**User Story:**
As a user, I want the system to automatically extract all Looker Studio PDF reports from my Gmail inbox so that I don't have to manually download and organize 30 files each month.

**Acceptance Criteria:**
- [ ] System connects to Gmail using OAuth 2.0 credentials from .env file
- [ ] System identifies emails from Looker Studio sender (specific email address to be configured)
- [ ] System extracts all PDF attachments from identified emails
- [ ] System saves PDFs to temporary processing directory with original filenames
- [ ] System handles batch arrival (PDFs arriving over few hours)
- [ ] System logs extraction status for each PDF (success/failure)
- [ ] System gracefully handles missing attachments or corrupted files

**Technical Notes:**
- Decision needed: Make.com (existing) vs Gmail API direct integration
- Gmail API approach requires `gmail.readonly` or `gmail.modify` scope
- Must handle Gmail API pagination if > 100 emails (unlikely for monthly batch)
- Consider marking processed emails as read or applying label to prevent reprocessing

**Edge Cases:**
- Email arrives without PDF attachment → Flag for manual review
- PDF is corrupted or unreadable → Flag for manual review
- Multiple PDFs in single email → Extract all
- Duplicate PDFs (same business, same month) → Flag duplicate, process most recent

---

### Feature 2: KPI Data Extraction from PDFs

**User Story:**
As a user, I want the system to extract business name, date, and six KPI metrics from each PDF so that I can populate email templates with accurate data without manual entry.

**Acceptance Criteria:**
- [ ] System extracts **Business Name** from top of report (exact location may vary by report)
- [ ] System extracts **Date/Month** for subject line (format: "Month Year" e.g., "January 2025")
- [ ] System extracts KPI table with six metrics:
  - Sessions (integer)
  - Conversions (integer)
  - Active Users (integer)
  - Engagement Rate (percentage, e.g., "45.2%")
  - Bounce Rate (percentage, e.g., "32.1%")
  - Average Session Duration (time format, e.g., "2m 34s" or "0:02:34")
- [ ] System validates that all six KPIs were successfully extracted
- [ ] System flags PDFs with missing or malformed data for manual review
- [ ] System logs extraction results (success/failure, values extracted)

**Technical Notes:**
- Requires PDF parsing library evaluation (PyPDF2, pdfplumber, tabula-py for Python; pdf-parse for Node.js)
- Looker Studio PDF format must be analyzed to determine extraction strategy (text positions, table structure)
- May require OCR if PDFs are image-based (unlikely for Looker Studio)
- Metrics may be formatted with commas (e.g., "1,234" sessions) requiring parsing
- Percentage and time formats need standardization for email display

**Edge Cases:**
- Business name contains special characters → Handle encoding properly
- KPI table structure differs between SEO and Google Ads reports → Support multiple table formats
- Metric value is "N/A" or missing → Flag for manual review
- Decimal precision varies (e.g., "45%" vs "45.2%") → Preserve original precision

**Validation Rules:**
- Sessions: Non-negative integer
- Conversions: Non-negative integer
- Active Users: Non-negative integer
- Engagement Rate: 0-100% (decimal allowed)
- Bounce Rate: 0-100% (decimal allowed)
- Average Session Duration: Valid time format (minutes/seconds)

---

### Feature 3: Client Database Matching

**User Story:**
As a user, I want the system to match each PDF's business name to my client database so that the correct personalization data (first name, email, custom text) is used for each email.

**Acceptance Criteria:**
- [ ] System loads client database (CSV, SQLite, or Google Sheets - format TBD)
- [ ] System compares extracted business name to database records
- [ ] System performs fuzzy matching to handle minor variations (e.g., "ABC Corp" vs "ABC Corporation")
- [ ] System retrieves for matched client:
  - Client first name
  - Client email address
  - Service type (SEO or SEM)
  - Predefined personalized email text
- [ ] System flags PDFs with no database match for manual review
- [ ] System flags PDFs with multiple potential matches for manual review
- [ ] System logs all matching attempts and results

**Technical Notes:**
- Database schema:
  ```
  Client ID | First Name | Business Name | Email | Service Type | Personalized Text
  1         | John       | ABC Corp      | john@abc.com | SEO | Great work on the content updates last month.
  ```
- Fuzzy matching library needed (e.g., fuzzywuzzy, Levenshtein distance)
- Matching threshold: 85%+ similarity (configurable)
- Case-insensitive matching
- Handle punctuation differences ("ABC Corp." vs "ABC Corp")

**Edge Cases:**
- Business name has minor typo in PDF → Fuzzy matching should catch
- Business name completely different → Flag as no match
- Two clients with similar business names → Flag as multiple matches
- Database missing client → Flag as no match
- Database has duplicate business names → Flag as data integrity error

**Database Format Decision (Research Required):**
- **CSV:** Easy to edit in Excel, version control friendly, portable
- **SQLite:** Structured queries, data validation, single file
- **Google Sheets:** Collaborative, cloud backup, accessible anywhere
- **Recommendation needed from plan-synthesizer based on deployment model**

---

### Feature 4: HTML Email Generation

**User Story:**
As a user, I want the system to generate professional, personalized HTML emails with KPI tables and PDF attachments so that my clients receive beautiful, data-rich reports that reflect my agency's quality standards.

**Acceptance Criteria:**
- [ ] System generates HTML email with proper structure (DOCTYPE, meta tags, inline CSS)
- [ ] **Subject Line:** "Your [Month] SEO Report" or "Your [Month] Google Ads Report" (based on service type)
- [ ] **Email Body Structure:**
  1. Personalized greeting: "Hi [First Name],"
  2. Opening line: "Please see the data below for [Business Name]."
  3. Predefined personalized text (1-2 lines, from database)
  4. Standard paragraph about keyword rankings (template text)
  5. HTML-formatted KPI table with six metrics
  6. Standard closing paragraph (template text)
  7. Signature (agency name, contact info - template)
- [ ] **PDF Attachment:** Original Looker Studio PDF attached with descriptive filename
- [ ] Email renders consistently across email clients (Gmail, Outlook, Apple Mail, mobile)
- [ ] All dynamic fields correctly populated (no missing [placeholders])
- [ ] HTML validates and passes email rendering tests (Litmus/Email on Acid equivalent)

**Technical Notes:**
- Use table-based layout for email client compatibility (not CSS Grid/Flexbox)
- Inline all CSS (many email clients strip `<style>` tags)
- Use web-safe fonts (Arial, Helvetica, Georgia, Times New Roman)
- KPI table styling: borders, padding, alternating row colors (subtle)
- Responsive design for mobile (use `@media` queries)
- Test on Gmail (web, iOS, Android), Outlook (desktop, web), Apple Mail

**Email Template Structure:**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your [Month] [Service Type] Report</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
  <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
    <p>Hi [First Name],</p>
    <p>Please see the data below for [Business Name].</p>
    <p>[Personalized Text from Database]</p>
    <p>[Standard Paragraph about Keyword Rankings]</p>

    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
      <thead>
        <tr style="background-color: #f4f4f4;">
          <th style="border: 1px solid #ddd; padding: 12px; text-align: left;">Metric</th>
          <th style="border: 1px solid #ddd; padding: 12px; text-align: right;">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Sessions</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">[Sessions Value]</td>
        </tr>
        <!-- Repeat for all 6 KPIs -->
      </tbody>
    </table>

    <p>[Standard Closing Paragraph]</p>
    <p>Best regards,<br>[Agency Name]</p>
  </div>
</body>
</html>
```

**Edge Cases:**
- Business name contains special HTML characters (&, <, >) → Properly escape
- Personalized text contains line breaks → Convert to `<br>` tags
- KPI values too long for table cell → Handle text wrapping
- Email client blocks images → No critical images used (text-only design)

**Standard Text Templates (To Be Provided):**
- Standard paragraph about keyword rankings (same for all SEO reports)
- Standard closing paragraph (same for all reports)
- Agency signature block

---

### Feature 5: Approval Workflow

**User Story:**
As a user, I want to review all generated emails before they're sent so that I can catch any errors, verify personalization, and ensure quality control before client delivery.

**Acceptance Criteria:**
- [ ] System presents all generated emails for review (method TBD: email preview or web interface)
- [ ] For each email, user can see:
  - Client name and business name
  - Full email preview (subject line, body, KPI data)
  - PDF attachment confirmation
  - Any extraction errors or warnings
- [ ] User can mark each email as:
  - **Approved:** Ready for draft creation
  - **Needs Revision:** Requires manual correction
- [ ] User can add notes for emails needing revision
- [ ] System tracks approval status (spreadsheet or database)
- [ ] System only creates Gmail drafts for approved emails
- [ ] System provides summary: X approved, Y need revision, Z total

**Technical Notes:**
- **Option A: Email-Based Review**
  - System sends all draft emails to review address (e.g., owner@agency.com)
  - User reviews in Gmail inbox
  - User updates CSV/Google Sheets with approval status
  - Columns: Client Name | Business Name | Status | Notes | Extraction Errors
  - System reads spreadsheet to determine which to draft

- **Option B: Web Preview Interface**
  - Local or cloud-hosted web app
  - Shows email exactly as it will appear when sent
  - Approve/Reject buttons for each email
  - Notes field for revision comments
  - Must render email identically to final version (critical requirement)

**Decision Criteria:**
- User preference (which workflow is more comfortable?)
- Development complexity (web interface requires more dev time)
- Accuracy of preview (can web interface perfectly replicate email rendering?)

**Edge Cases:**
- All emails approved → Proceed directly to draft creation
- All emails need revision → Provide manual workflow instructions
- User forgets to update approval spreadsheet → System prompts/reminds
- Approval status file corrupted → System creates new blank template

---

### Feature 6: Gmail Draft Creation

**User Story:**
As a user, I want the system to create Gmail drafts for all approved emails so that I can review them one final time in Gmail and send them manually at my preferred pace.

**Acceptance Criteria:**
- [ ] System reads approval status (from spreadsheet or database)
- [ ] System creates Gmail draft for each approved email using Gmail API
- [ ] Each draft includes:
  - To: Client email address
  - Subject: Properly formatted subject line
  - Body: Complete HTML email
  - Attachment: Original PDF report
- [ ] Drafts appear in Gmail "Drafts" folder
- [ ] Drafts are labeled/organized for easy identification (optional: apply Gmail label "Monthly Reports - [Month]")
- [ ] System provides confirmation: "Created X drafts successfully"
- [ ] System logs any draft creation errors

**Technical Notes:**
- Gmail API `users.drafts.create` method
- Required scope: `gmail.compose`
- Draft format: MIME multipart (text/html + PDF attachment)
- Attachment encoding: Base64
- Gmail API quota: 250 units/user/second (30 drafts well within limit)

**Draft Creation Process:**
1. For each approved email:
   - Load HTML email body
   - Load PDF file from processing directory
   - Construct MIME message:
     ```
     Content-Type: multipart/mixed
       - Part 1: text/html (email body)
       - Part 2: application/pdf (PDF attachment)
     ```
   - Base64 encode MIME message
   - Call Gmail API `users.drafts.create`
   - Log success/failure

2. Error handling:
   - Gmail API rate limit exceeded → Implement exponential backoff
   - PDF file not found → Log error, skip draft, notify user
   - Network error → Retry up to 3 times

**Edge Cases:**
- Gmail API authentication expires → Refresh OAuth token automatically
- PDF file too large (Gmail limit: 25MB per message) → Flag oversized PDFs
- Draft creation partially fails (e.g., 28/30 succeed) → Report which failed, allow retry
- Drafts already exist from previous run → Option to replace or skip

---

### Feature 7: Manual Sending with Spacing Guidance

**User Story:**
As a user, I want clear guidance on manually sending Gmail drafts with appropriate spacing so that I avoid spam flags and ensure optimal deliverability.

**Acceptance Criteria:**
- [ ] System provides instructions for manual sending process
- [ ] Instructions include recommended spacing (e.g., "Send 5-10 emails per hour")
- [ ] System identifies drafts to be sent (by Gmail label or folder)
- [ ] (Optional) System provides checklist: "Sent [0/30]" for user to track progress
- [ ] Documentation includes best practices for avoiding spam flags

**Technical Notes:**
- This is MVP approach; Phase 2 will introduce auto-send with programmatic spacing
- Manual sending ensures user maintains full control during early deployment
- User can use Gmail's native "Send" button for each draft

**Sending Best Practices (Documentation):**
- Space sends 5-10 minutes apart (not critical, but recommended)
- Send in batches: 10 emails, then 15-minute break, then next 10
- Monitor Gmail's "Sent" folder to confirm successful delivery
- Check for bounce-backs or delivery failures
- Send during business hours (9 AM - 5 PM local time) for better engagement

**Edge Cases:**
- User sends all drafts at once → Not ideal, but won't break system (deliverability risk only)
- User forgets to send some drafts → Drafts remain in Gmail; user can send later
- Sent emails bounce back → User manually follows up with client

---

### Feature 8: Error Handling & Logging

**User Story:**
As a user, I want clear error messages and comprehensive logs so that I can troubleshoot issues independently and understand what happened when something goes wrong.

**Acceptance Criteria:**
- [ ] System logs all major operations: PDF extraction, KPI parsing, database matching, email generation, draft creation
- [ ] Logs include timestamps, operation type, success/failure status, error messages
- [ ] Errors categorized by severity:
  - **Critical:** System cannot proceed (e.g., Gmail API auth failure)
  - **Warning:** Recoverable issue (e.g., single PDF extraction failed)
  - **Info:** Normal operation (e.g., "Processing PDF 5 of 30")
- [ ] Error messages are user-friendly, not technical stack traces
- [ ] System creates error summary report: "5 PDFs flagged for manual review: [List of business names]"
- [ ] Logs stored in dated files (e.g., `logs/2025-01-05.log`)

**Technical Notes:**
- Use logging library (Python: `logging`, Node.js: `winston` or `pino`)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation: Keep last 12 months of logs (monthly batch = 12 log files/year)
- Log format: `[2025-01-05 14:23:45] [INFO] [PDF_EXTRACTION] Successfully extracted report for ABC Corp`

**Error Scenarios & Messages:**

| Error Scenario | Severity | User-Friendly Message | Troubleshooting Hint |
|----------------|----------|----------------------|----------------------|
| Gmail API auth failure | CRITICAL | "Cannot connect to Gmail. Please check OAuth credentials in .env file." | Verify .env file exists, check token expiration |
| PDF extraction failed | WARNING | "Unable to extract PDF from email (Subject: [Subject]). Email may be missing attachment." | Manually check email for PDF |
| KPI parsing failed | WARNING | "Could not extract KPI data from [Business Name] report. Please verify PDF format." | Manually review PDF, check if format changed |
| No database match | WARNING | "Business name '[Name]' not found in client database. Please verify spelling." | Update database or check PDF business name |
| Draft creation failed | ERROR | "Failed to create Gmail draft for [Client Name]. Error: [API Error]" | Check Gmail API quota, network connection |

**Logging Examples:**
```
[2025-01-05 09:15:00] [INFO] [SYSTEM] Starting monthly report processing
[2025-01-05 09:15:05] [INFO] [PDF_EXTRACTION] Connected to Gmail API successfully
[2025-01-05 09:15:10] [INFO] [PDF_EXTRACTION] Found 30 emails from Looker Studio
[2025-01-05 09:15:15] [INFO] [PDF_EXTRACTION] Extracted report for ABC Corp (1/30)
[2025-01-05 09:15:45] [WARNING] [KPI_PARSING] Missing 'Bounce Rate' in XYZ Company report
[2025-01-05 09:16:00] [ERROR] [DATABASE_MATCHING] No match found for business name "Unknown Business LLC"
[2025-01-05 09:20:00] [INFO] [EMAIL_GENERATION] Generated 28 emails successfully, 2 flagged for review
[2025-01-05 09:25:00] [INFO] [DRAFT_CREATION] Created 28 Gmail drafts
[2025-01-05 09:25:05] [INFO] [SYSTEM] Processing complete. 28 approved, 2 need review.
```

---

### Feature 9: Documentation & User Guide

**User Story:**
As a user, I want clear "how to use" documentation so that I can operate the system independently without external technical support.

**Acceptance Criteria:**
- [ ] Documentation covers complete monthly workflow (end-to-end)
- [ ] Documentation includes:
  - Initial setup (OAuth, .env file, client database)
  - Running monthly process (commands, expected outputs)
  - Approval workflow steps
  - Sending drafts from Gmail
  - Updating client database (adding/removing clients, changing personalized text)
  - Troubleshooting common errors
  - FAQ section
- [ ] Documentation uses screenshots where helpful
- [ ] Documentation written in plain language (not technical jargon)
- [ ] Documentation organized in logical sequence (setup → monthly use → troubleshooting)

**Technical Notes:**
- Format: Markdown (README.md) or simple HTML page
- Location: `c:\Users\cscot\Documents\Apps\Email Reports\DOCUMENTATION.md`
- Not deep technical architecture (no code explanations unless necessary for troubleshooting)

**Documentation Outline:**
1. **Getting Started**
   - System requirements
   - Initial setup (OAuth credentials, .env file configuration)
   - Client database setup (format, required fields)
   - First-time Gmail API authorization

2. **Monthly Workflow**
   - Step 1: Wait for Looker Studio PDFs to arrive
   - Step 2: Run report processing script
   - Step 3: Review generated emails (approval workflow)
   - Step 4: Mark approvals in tracking spreadsheet
   - Step 5: Generate Gmail drafts
   - Step 6: Send drafts manually from Gmail
   - Step 7: Archive/cleanup

3. **Managing Client Database**
   - Adding new clients
   - Updating personalized text
   - Changing email addresses
   - Removing clients
   - Database backup recommendations

4. **Troubleshooting**
   - "System can't connect to Gmail" → Check OAuth credentials
   - "PDF extraction failed for some reports" → Manually review flagged PDFs
   - "Business name not found in database" → Check spelling, update database
   - "Gmail drafts not appearing" → Check Gmail API quota, verify draft creation logs
   - "Emails going to spam" → Review sending pace, check SPF/DKIM records

5. **FAQ**
   - How often should I back up the client database?
   - What if Looker Studio changes the PDF format?
   - Can I customize the email template?
   - How do I add a new KPI to the reports?
   - What if a client changes their email address mid-month?

---

## Development Principles & Testing Philosophy

### Core Development Principles

**1. Reliability Over Features**
- The system must work correctly 100% of the time for core functionality (PDF extraction, KPI parsing, email generation)
- Prefer simple, proven solutions over complex, cutting-edge approaches
- Extensive error handling and graceful degradation
- No silent failures—always log and notify user of issues

**2. User-Centric Design**
- Every feature must reduce user effort, not increase complexity
- Clear, actionable error messages (never expose stack traces to user)
- Workflow should feel intuitive, not require constant documentation reference
- User maintains control (approval step prevents automated mistakes)

**3. Maintainability First**
- Code must be readable and well-documented (inline comments for complex logic)
- Modular architecture: PDF extraction, KPI parsing, email generation, draft creation should be independent components
- Configuration over hardcoding (email templates, database paths, API endpoints in config files)
- User should be able to update templates and database without touching code

**4. Fail-Safe by Default**
- When in doubt, flag for manual review rather than proceeding with uncertain data
- Never send emails automatically without user approval (at least in MVP)
- Database backups before any updates
- Rollback capability if processing fails mid-workflow

**5. Cost-Conscious Architecture**
- Prefer free, open-source libraries with strong community support
- Minimize API calls (batch operations, cache where appropriate)
- Avoid unnecessary cloud infrastructure if local deployment suffices
- Only pay for tools that provide clear, measurable value

### Testing Philosophy

**Unit Testing (Component-Level)**
- Test each component independently:
  - PDF extraction: Test with sample Looker Studio PDFs (SEO and Google Ads variants)
  - KPI parsing: Test with various PDF formats, edge cases (missing metrics, formatting variations)
  - Database matching: Test fuzzy matching with intentional typos, case variations
  - Email generation: Test template rendering with all field combinations
  - Draft creation: Test MIME message construction, attachment encoding

**Integration Testing (Workflow-Level)**
- Test complete end-to-end workflow:
  - Start with 5 test PDFs (3 SEO, 2 Google Ads)
  - Verify all 5 emails generated correctly
  - Verify Gmail drafts created successfully
  - Manually send one test draft, verify receipt and rendering

**User Acceptance Testing (Real-World Validation)**
- First production run: Process all 30 PDFs, user reviews each email manually
- Compare generated emails to manually-created emails (previous months)
- Verify KPI data accuracy by spot-checking against original PDFs (sample 10 reports)
- Send test emails to user's own email addresses across different clients (Gmail, Outlook, Apple Mail)

**Regression Testing (Ongoing)**
- Maintain test PDF library (representative samples from each month)
- Re-run tests when Looker Studio changes PDF format
- Re-test after any code changes or dependency updates

**Error Simulation Testing**
- Missing PDF attachments in emails
- Corrupted PDF files
- Business names not in database
- Malformed KPI data
- Gmail API authentication failures
- Network interruptions during draft creation

### Quality Assurance Checklist (Before Production Use)

**Data Accuracy:**
- [ ] KPI extraction matches PDF data exactly (100% accuracy on 10 sample PDFs)
- [ ] Business name matching works with intentional typos (< 85% similarity threshold)
- [ ] Personalization data (first name, email, custom text) correctly populated
- [ ] Subject lines accurately reflect month and service type

**Email Rendering:**
- [ ] HTML emails render correctly in Gmail (web, mobile)
- [ ] HTML emails render correctly in Outlook (desktop, web)
- [ ] HTML emails render correctly in Apple Mail (desktop, mobile)
- [ ] KPI tables display properly (borders, alignment, readability)
- [ ] PDF attachments open correctly from received emails

**Workflow Integrity:**
- [ ] All 30 PDFs extracted successfully
- [ ] Approval workflow allows flagging emails for revision
- [ ] Only approved emails generate Gmail drafts
- [ ] Drafts contain correct recipient, subject, body, attachment

**Error Handling:**
- [ ] Missing PDF attachment triggers warning, not crash
- [ ] Unmatched business name flagged in approval workflow
- [ ] Draft creation failure logged with clear error message
- [ ] System completes processing even if some PDFs fail

**Documentation:**
- [ ] User can complete setup following documentation alone
- [ ] User can run monthly workflow without external help
- [ ] Troubleshooting guide addresses observed errors during testing

---

## Migration Strategy from Relevance AI

### Current State Analysis

**Existing Workflow:**
1. Looker Studio → Email → Make.com → Google Drive → Relevance AI → Gmail drafts

**Pain Points:**
- Relevance AI subscription cost
- Manual PDF attachment required
- No Google Analytics integration for AI insights
- Limited customization flexibility

**What's Working:**
- Make.com reliably extracts PDFs to Google Drive
- Looker Studio PDFs arrive consistently each month
- Gmail drafts approach provides review before sending

### Migration Approach

**Phase 1: Parallel Operation (Recommended)**
- Run new system alongside Relevance AI for one monthly cycle
- Compare outputs (email quality, data accuracy, time efficiency)
- User comfort level with new workflow
- Fallback to Relevance AI if critical issues arise

**Phase 2: Full Cutover**
- Disable Relevance AI workflow
- Use new system exclusively
- Monitor first two production cycles closely
- Maintain Relevance AI account (paused) for 90 days as emergency backup

**Phase 3: Full Deprecation**
- Cancel Relevance AI subscription after 90-day successful operation
- Archive Relevance AI configurations and documentation
- Fully commit to new system

### Migration Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| New system fails to extract KPIs correctly | High (clients receive incorrect data) | Medium | Parallel operation for first cycle, manual verification |
| User unfamiliar with new workflow | Medium (delayed reporting) | Low | Clear documentation, training session |
| Looker Studio changes PDF format | High (system breaks) | Low | PDF parsing fallback, alert user to format changes |
| Gmail API quota exceeded | Medium (drafts not created) | Very Low | Monitor quota usage, well within limits for 30 emails |
| Cost higher than expected | Low (budget overrun) | Low | Free/open-source focus, approve all paid tools in advance |

### Rollback Plan

**If critical issues arise:**
1. Re-enable Relevance AI workflow (Make.com → Relevance AI → Gmail)
2. Manually process month's reports using old system
3. Investigate and fix new system issues without time pressure
4. Re-attempt migration following month

**Rollback Triggers:**
- > 5 emails with incorrect KPI data
- System completely fails to process PDFs
- User unable to complete workflow within reasonable timeframe (< 1 hour)
- Critical security or privacy issue discovered

---

## Research Requirements for Plan-Synthesizer

The following decisions require detailed research and recommendation from the plan-synthesizer agent before development begins:

### 1. Deployment Architecture
**Question:** Should the system run locally (Windows), cloud-hosted, or hybrid?

**Research Requirements:**
- **Local Windows Application:**
  - Pros: Full control, no hosting costs, offline capability, direct file system access
  - Cons: Single point of failure (user's machine), no remote access, manual backups
  - Technical considerations: Windows task scheduler for automation, local storage for PDFs, database location

- **Cloud-Hosted Solution:**
  - Pros: Accessible anywhere, automatic backups, managed uptime, scalable
  - Cons: Ongoing costs, internet dependency, more complex deployment
  - Platform options: AWS Lambda, Google Cloud Functions, Heroku, DigitalOcean
  - Cost estimate for 30 emails/month workload

- **Hybrid Approach:**
  - Pros: Balance cost and flexibility, local storage with cloud processing
  - Cons: Most complex, synchronization challenges
  - Architecture: Local PDF storage + cloud email generation + cloud approval interface

**Recommendation Criteria:**
- Total cost of ownership (setup + monthly operation)
- User technical comfort (deployment, maintenance)
- Reliability requirements
- Backup and disaster recovery

**Required Output:** Detailed pros/cons comparison table with cost estimates and final recommendation

---

### 2. Email Ingestion Method
**Question:** Continue using Make.com or switch to Gmail API direct integration?

**Research Requirements:**
- **Make.com (Current):**
  - Existing scenario already configured
  - Proven reliability over past months
  - Cost: Current subscription level
  - Integration effort: Minimal (keep existing)
  - Dependency: Third-party service (Make.com uptime)

- **Gmail API Direct:**
  - Full control over extraction logic
  - No third-party dependency
  - Cost: Free (within Gmail API quotas)
  - Integration effort: OAuth setup, API integration code
  - Quota limits: Gmail API read operations (well within limits for 30 emails/month)
  - Python library: `google-api-python-client` or Node.js library: `googleapis`

**Recommendation Criteria:**
- Total cost (Make.com subscription vs. development time)
- Reliability and control
- Maintenance complexity
- Integration with overall system architecture

**Required Output:** Side-by-side comparison with cost analysis and final recommendation

---

### 3. Client Database Format
**Question:** CSV file, SQLite database, or Google Sheets API?

**Research Requirements:**
- **CSV File:**
  - Editing: Excel, Google Sheets (export to CSV), any text editor
  - Backup: Manual file copy, version control (Git)
  - Concurrent access: Not safe (file locking issues)
  - Validation: None (user can enter invalid data)
  - Library: Python `csv` module, Node.js `csv-parser`
  - Deployment fit: Best for local deployment

- **SQLite Database:**
  - Editing: DB Browser for SQLite, command-line tools, custom UI
  - Backup: Single file copy, WAL mode for safety
  - Concurrent access: Safe read-only, limited concurrent writes
  - Validation: Schema enforcement, constraints, foreign keys
  - Library: Python `sqlite3`, Node.js `better-sqlite3`
  - Deployment fit: Good for local or cloud

- **Google Sheets API:**
  - Editing: Google Sheets web interface (familiar, collaborative)
  - Backup: Automatic (Google Drive versioning)
  - Concurrent access: Safe (Google handles conflicts)
  - Validation: Data validation rules in Google Sheets
  - Library: Python `gspread`, Node.js `google-spreadsheet`
  - Deployment fit: Best for cloud, requires internet for local
  - Cost: Free (within Google Sheets API quotas)

**Database Schema (All Formats):**
```
Client ID (auto-increment)
First Name (text, required)
Business Name (text, required, unique)
Email (text, required, valid email format)
Service Type (text, required, values: "SEO" or "SEM")
Personalized Text (text, optional, max 500 characters)
Active (boolean, default true) - for disabling clients without deleting
Created Date (date)
Last Modified Date (date)
```

**Recommendation Criteria:**
- User comfort with editing interface
- Backup and disaster recovery
- Deployment model compatibility
- Future collaboration needs (single user vs. team)

**Required Output:** Comparison table with user experience mockups (how user edits data) and final recommendation

---

### 4. PDF Parsing Library
**Question:** Which library best extracts text and tables from Looker Studio PDFs?

**Research Requirements:**
- **Python Options:**
  - **PyPDF2:** Basic text extraction, limited table support
  - **pdfplumber:** Excellent table extraction, handles layouts well
  - **tabula-py:** Java dependency, strong table extraction
  - **camelot-py:** Advanced table extraction, good for complex layouts
  - **PyMuPDF (fitz):** Fast, comprehensive, good text extraction

- **Node.js Options:**
  - **pdf-parse:** Simple text extraction, basic
  - **pdf2json:** Structured JSON output, moderate table support
  - **pdfjs-dist:** Mozilla's PDF.js, robust but complex

**Evaluation Criteria:**
- Successful extraction from sample Looker Studio PDFs (must test with actual PDFs)
- Table extraction accuracy (KPI table critical)
- Ease of installation on Windows
- Active maintenance and community support
- Documentation quality

**Testing Protocol:**
- Obtain 3-5 sample Looker Studio PDFs (SEO and Google Ads variants)
- Attempt extraction with top 2-3 libraries
- Measure: Business name extraction success, KPI table extraction accuracy, code complexity

**Required Output:** Test results showing extraction accuracy per library, code snippet examples, final recommendation

---

### 5. Approval Workflow Interface
**Question:** Email-based review with CSV tracking or web-based preview interface?

**Research Requirements:**
- **Option A: Email-Based Review**
  - Workflow:
    1. System sends all generated emails to review address (e.g., `owner@agency.com`)
    2. User opens each email in Gmail, reviews content
    3. User updates CSV or Google Sheets with approval status
       - Columns: Client Name | Business Name | Status (Approved/Needs Revision) | Notes | Extraction Errors
    4. System reads tracking file, creates drafts for "Approved" emails
  - Pros: Simple, no UI development, uses familiar tools (Gmail, Excel/Sheets)
  - Cons: Less visual, manual spreadsheet management, potential for errors in status tracking

- **Option B: Web Preview Interface**
  - Workflow:
    1. System generates preview URLs or launches local web app
    2. Web interface shows each email exactly as it will appear when sent
    3. User clicks "Approve" or "Needs Revision" for each
    4. User adds notes for revisions
    5. System tracks approvals in database/file
    6. System creates drafts for approved emails
  - Pros: Visual verification, integrated experience, better UX
  - Cons: Development time, must perfectly replicate email rendering (critical), local server or cloud hosting needed
  - Email Rendering Challenge: HTML email in web browser ≠ HTML email in email client
    - Must inline all CSS
    - Must account for email client quirks (Outlook, Gmail rendering differences)
    - May need to use iframe or email testing service API
  - Technology options:
    - Local: Flask/Django (Python) or Express (Node.js) web server
    - Cloud: Simple static site with email previews
    - Email Testing Integration: Litmus API, Email on Acid API (costs $$)

**Recommendation Criteria:**
- User preference (which workflow is more comfortable?)
- Development time vs. value
- Accuracy of email preview (can web interface truly replicate email client rendering?)
- Long-term usability (will user prefer visual interface after initial learning curve?)

**Required Output:** Mockups or wireframes for both options, detailed pros/cons, user preference survey, final recommendation

---

### 6. Technology Stack Recommendation
**Question:** Python or Node.js? Which libraries and frameworks?

**Research Requirements:**
- **Python Stack:**
  - Gmail API: `google-api-python-client`
  - PDF parsing: `pdfplumber` or `camelot-py`
  - Email templating: `Jinja2`
  - Database: `sqlite3` (stdlib), `csv` (stdlib), or `gspread` (Google Sheets)
  - Fuzzy matching: `fuzzywuzzy` or `thefuzz`
  - MIME message: `email.mime` (stdlib)
  - Environment variables: `python-dotenv`
  - Logging: `logging` (stdlib)
  - Pros: Excellent PDF libraries, strong data processing, user may be familiar
  - Cons: Windows installation sometimes complex (C dependencies)

- **Node.js Stack:**
  - Gmail API: `googleapis`
  - PDF parsing: `pdf-parse` or `pdfjs-dist`
  - Email templating: `handlebars` or `ejs`
  - Database: `better-sqlite3`, `csv-parser`, or `google-spreadsheet`
  - Fuzzy matching: `fuzzball` or `fuse.js`
  - MIME message: `nodemailer`
  - Environment variables: `dotenv`
  - Logging: `winston` or `pino`
  - Pros: Excellent async handling, good for web interfaces, npm ecosystem
  - Cons: PDF parsing libraries less mature than Python

**Recommendation Criteria:**
- PDF parsing quality (most critical component)
- User's existing technical familiarity
- Windows compatibility and ease of setup
- Library maturity and community support
- Long-term maintenance (which ecosystem is better for user self-maintenance?)

**Required Output:** Full stack recommendation with library versions, installation instructions for Windows, sample code snippets

---

### 7. OAuth Setup & Credential Management
**Question:** How should OAuth credentials and tokens be securely stored and managed?

**Research Requirements:**
- Gmail API OAuth 2.0 flow:
  1. Create project in Google Cloud Console
  2. Enable Gmail API
  3. Create OAuth 2.0 credentials (Desktop app type)
  4. Download `credentials.json`
  5. Run authorization flow (opens browser, user grants permissions)
  6. Receive `token.json` (contains access token + refresh token)
  7. Store `token.json` securely
  8. System uses refresh token to get new access tokens (expire every hour)

- Required Gmail API Scopes:
  - `https://www.googleapis.com/auth/gmail.readonly` or `gmail.modify` (read emails, extract PDFs)
  - `https://www.googleapis.com/auth/gmail.compose` (create drafts)
  - `https://www.googleapis.com/auth/gmail.send` (Phase 2: auto-send)

- Security Best Practices:
  - Store `credentials.json` and `token.json` in `.env` file or secure directory
  - Add to `.gitignore` (never commit to version control)
  - Use environment variables for sensitive paths
  - Encrypt tokens at rest (optional, OS-level encryption)
  - Implement token rotation (refresh tokens can be revoked)

- Credential Management Options:
  - **Option A:** Store as files (`credentials.json`, `token.json`) in project directory
  - **Option B:** Store in `.env` file as environment variables (serialized JSON)
  - **Option C:** Use OS keyring/credential manager (Windows Credential Manager)

**Required Output:** Step-by-step OAuth setup guide, credential storage recommendation, security checklist

---

## Phase 2 Features (Future Enhancements)

### Google Analytics MCP Integration

**Objective:** Direct connection to Google Analytics for real-time data access, enabling AI-generated insights.

**Capabilities:**
- Query Google Analytics 4 (GA4) for current month data (in-progress month insights)
- Compare current metrics to historical trends
- Access granular data (page-level, source/medium, user demographics)
- Enable Claude Code (via MCP) to analyze trends and generate insights

**Technical Requirements:**
- MCP (Model Context Protocol) server for Google Analytics
- GA4 API credentials (separate from Gmail API)
- OAuth scopes for read-only GA4 access
- Data caching to minimize API calls

**Use Cases:**
- "Sessions are up 25% compared to last month's average"
- "Top performing page this month: /services/seo (30% of conversions)"
- "Traffic from organic search increased 15% week-over-week"

**Implementation Timeline:** Post-MVP, dependent on Phase 1 success

---

### AI-Generated Insights

**Objective:** Claude-powered analysis of client data, generating positive, actionable insights for each email.

**Insight Categories:**
1. **Trend Identification:**
   - "Your engagement rate has increased steadily over the past 3 months"
   - "Bounce rate improved by 12% compared to the previous quarter"

2. **Anomaly Detection:**
   - "Conversions spiked 40% in the third week—this coincides with your new landing page launch"
   - "Sessions dipped on weekends, suggesting opportunity for weekend-specific campaigns"

3. **Comparative Analysis:**
   - "Your average session duration (3m 45s) exceeds industry average (2m 30s)"
   - "Engagement rate is 20% higher than your own 6-month average"

4. **Recommendations:**
   - "With bounce rate declining, consider expanding content on your top-performing pages"
   - "Mobile traffic now represents 60% of sessions—prioritize mobile UX improvements"

**AI Prompt Strategy:**
- Provide Claude with: client's current month data, previous 3-6 months data, industry benchmarks (if available)
- Instruction: "Identify 2-3 positive, actionable insights. Focus on trends, improvements, or opportunities. Avoid generic statements."
- Tone: Professional, optimistic, consultative
- Length: 2-4 sentences per insight

**Integration into Email:**
- Insert AI insights after predefined personalized text, before KPI table
- Section header: "Key Insights This Month"
- Clearly distinguish AI insights from human-written custom text

**Technical Requirements:**
- Claude API access (Anthropic API key)
- Prompt template system
- Data formatting for Claude (JSON or structured text)
- Insight validation (ensure positive tone, avoid hallucinations)

**Implementation Timeline:** Post-MVP, after Google Analytics MCP integration

---

### Interactive Approval Dashboard

**Objective:** Replace CSV spreadsheet with web-based dashboard for reviewing and approving emails.

**Features:**
- Email preview showing exact rendering (HTML email in iframe or email testing service)
- Side-by-side comparison: generated email vs. previous month's email (for consistency check)
- Approve/Reject buttons with one-click action
- Notes field for revision comments
- Bulk actions: "Approve All," "Approve All SEO," etc.
- Filtering: Show only "Needs Review," "Approved," "Rejected"
- Summary statistics: "25 approved, 3 need revision, 2 pending"

**User Experience:**
1. User opens dashboard URL (local: `http://localhost:5000` or cloud-hosted)
2. Dashboard displays all 30 generated emails in list view
3. User clicks on email to expand preview
4. User reviews content, clicks "Approve" or "Needs Revision"
5. For revisions, user adds note explaining issue
6. User completes review, clicks "Create Drafts" button
7. System generates Gmail drafts for all approved emails

**Technical Requirements:**
- Web framework: Flask/Django (Python) or Express (Node.js)
- Frontend: Simple HTML/CSS/JavaScript (or React for richer UI)
- Email rendering: iframe with inline CSS or email testing API
- Database: Track approval status per email
- Authentication: Basic password protection (single user)

**Implementation Timeline:** Post-MVP, based on user feedback after using CSV workflow

---

### Auto-Send with Spacing

**Objective:** Programmatically send approved emails with configurable delays to avoid spam flags.

**Features:**
- User sets sending schedule: "Send 10 emails/hour" or "Space sends 5 minutes apart"
- User initiates auto-send (button or command)
- System sends emails in batches with delays
- Real-time progress tracking: "Sent 15/30 emails, next batch in 10 minutes"
- Pause/resume capability
- Error handling: If send fails, retry or skip and notify user

**Sending Strategy:**
- Delay between sends: Configurable (default: 5-10 minutes)
- Batch size: Configurable (default: 10 emails per batch, 15-minute break between batches)
- Sending hours: Configurable (default: 9 AM - 5 PM local time)
- Retry logic: If send fails, retry up to 3 times with exponential backoff

**Technical Requirements:**
- Gmail API scope: `gmail.send` (move from drafts to sent programmatically)
- Job scheduler: Python `schedule` library or Node.js `node-cron`
- Queue system: Track pending sends, mark complete
- Logging: Detailed send logs (timestamp, recipient, success/failure)

**Safety Features:**
- Confirmation prompt before auto-send: "About to send 30 emails. Proceed?"
- Daily send limit: Max 50 emails/day (safety cap)
- Manual override: User can cancel auto-send mid-process

**Implementation Timeline:** Post-MVP, after user comfort with manual sending workflow

---

## Project Constraints & Assumptions

### Constraints

**Technical Constraints:**
1. **Platform:** Windows environment (`c:\Users\cscot\Documents\Apps\Email Reports`)
2. **Email Provider:** Google Workspace (Gmail API required)
3. **Data Source:** Looker Studio PDFs (format controlled by Google, subject to change)
4. **Processing Model:** Monthly batch (not real-time streaming)
5. **User Access:** Single user (agency owner), no multi-user collaboration required
6. **Internet Dependency:** Gmail API requires internet connection
7. **API Quotas:** Gmail API quotas (250 units/user/second for drafts, 250 units/user/day for send)

**Business Constraints:**
1. **Budget:** Free/open-source preferred, small paid tools acceptable if justified
2. **Timeline:** Flexible, no hard deadline (quality over speed)
3. **Maintenance:** User self-maintains (no ongoing developer support)
4. **Client Count:** 30 clients (MVP), potential growth to 50-100 (future)
5. **Service Types:** SEO and Google Ads (two report types)
6. **Approval Requirement:** All emails must be reviewed before sending (at least in MVP)

**Data Constraints:**
1. **Client Database Size:** 30 records (small dataset)
2. **PDF Size:** Typically < 5MB per report (Gmail attachment limit: 25MB)
3. **KPI Count:** Six fixed metrics (may expand in future)
4. **Email Length:** HTML email ~500-800 words, KPI table, PDF attachment
5. **Personalization Data:** First name, business name, 1-2 lines custom text per client

### Assumptions

**About the Data:**
1. Looker Studio PDFs arrive reliably at start of each month
2. PDF format is consistent across months (text extractable, not image-based)
3. Business names in PDFs match client database with minor variations (fuzzy matching handles typos)
4. KPI table structure is consistent between SEO and Google Ads reports (or has identifiable variants)
5. All PDFs contain complete data (all six KPIs present)

**About the User:**
1. User has Google Workspace admin access (can create OAuth credentials)
2. User comfortable with basic technical setup (installing software, editing .env files)
3. User prefers control over full automation (approval workflow acceptable)
4. User has Windows machine available for running system (if local deployment chosen)
5. User can dedicate 30-60 minutes per month for approval workflow

**About the Workflow:**
1. Monthly reporting cadence is fixed (won't change to weekly or daily)
2. Client database changes infrequently (1-2 updates per month)
3. Email template changes infrequently (quarterly at most)
4. Sending all 30 emails over 2-3 hours is acceptable (not all within 5 minutes)
5. User reviews emails on desktop (not mobile)

**About the Technology:**
1. Gmail API will remain stable (Google's long-term support)
2. PDF parsing libraries can handle Looker Studio format (confirmed through testing)
3. HTML email rendering is consistent enough across email clients (with proper coding)
4. OAuth tokens can be refreshed automatically (no manual re-authorization monthly)
5. Local file system (Windows) is reliable for temporary PDF storage

**About Future Phases:**
1. Google Analytics MCP will be available and functional (in development by Anthropic/community)
2. User will want AI insights after seeing value in Phase 1
3. Interactive dashboard will be valued over CSV workflow (based on user feedback)
4. Auto-send will be safe and reliable (after successful manual sending period)

---

## Success Definition & Launch Criteria

### MVP Success Definition

**The MVP is considered successful if:**

1. **Data Accuracy:** 100% of emails contain correct KPI data, client personalization, and PDF attachments (zero errors across 30 emails for 2 consecutive months)

2. **Time Efficiency:** Complete workflow (PDF extraction → approval → draft creation) takes < 30 minutes (90%+ reduction from current Relevance AI workflow)

3. **Cost Reduction:** Operational costs reduced by 75%+ compared to Relevance AI subscription

4. **User Adoption:** User operates system independently without external support (zero support requests after first production month)

5. **Email Quality:** Clients receive professional, correctly-formatted emails that render properly in all major email clients

6. **Reliability:** System successfully processes all 30 PDFs for 3 consecutive months without critical failures

### MVP Launch Criteria (Go/No-Go Decision)

**Must-Have (Blockers if Missing):**
- [ ] 100% accurate KPI extraction from 10 sample PDFs (5 SEO, 5 Google Ads)
- [ ] Zero client mismatches in test runs (30 test emails matched correctly)
- [ ] HTML emails render correctly in Gmail, Outlook, Apple Mail (tested on all three)
- [ ] PDF attachments successfully included in all test drafts
- [ ] OAuth authentication works without errors
- [ ] Approval workflow functional (user can review, approve, reject)
- [ ] Gmail drafts created successfully for all approved emails
- [ ] User can complete end-to-end workflow following documentation alone
- [ ] Error handling prevents system crashes (graceful failures with clear messages)
- [ ] Logging provides visibility into all operations

**Should-Have (Important but Not Blockers):**
- [ ] Fuzzy matching handles business name variations (85%+ similarity threshold works)
- [ ] System completes processing in < 15 minutes (30-minute target with margin)
- [ ] Database backup process documented and tested
- [ ] Troubleshooting guide addresses all errors encountered in testing
- [ ] Email rendering tested on mobile devices
- [ ] System handles partial failures (e.g., 28/30 PDFs process successfully)

**Nice-to-Have (Post-Launch Improvements):**
- [ ] Automated testing suite (unit tests for each component)
- [ ] Performance monitoring dashboard
- [ ] Email preview interface (if not core feature, can add later)
- [ ] Batch processing optimization (parallel PDF parsing)

### Post-Launch Monitoring (First 3 Months)

**Week 1 (Parallel Operation):**
- Run new system alongside Relevance AI
- Compare outputs side-by-side
- User reviews 100% of emails manually
- Log all discrepancies or issues

**Month 1 (Primary System):**
- Use new system exclusively
- Maintain Relevance AI as emergency backup
- User reviews 100% of emails manually
- Track time spent on workflow
- Document all errors and resolutions

**Month 2 (Optimization):**
- Continue using new system
- User reviews 50% of emails in detail (spot-check others)
- Identify workflow improvements
- Measure time savings vs. baseline

**Month 3 (Steady State):**
- Full production use
- User reviews 10-20% of emails in detail (trust but verify)
- Measure all success metrics
- Decide on Relevance AI cancellation
- Plan Phase 2 features based on feedback

---

## Appendix: Email Template Examples

### SEO Report Email Template

**Subject Line:**
```
Your January 2025 SEO Report
```

**Email Body (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your January 2025 SEO Report</title>
</head>
<body style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
  <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">

    <!-- Greeting -->
    <p style="margin-bottom: 15px;">Hi John,</p>

    <!-- Opening -->
    <p style="margin-bottom: 15px;">Please see the data below for ABC Corporation.</p>

    <!-- Personalized Text (from database) -->
    <p style="margin-bottom: 15px; font-style: italic; color: #555;">
      Great work on the content updates last month. The new blog posts are already showing positive engagement.
    </p>

    <!-- Standard Paragraph about Keyword Rankings -->
    <p style="margin-bottom: 20px;">
      Your keyword rankings continue to improve across target search terms. We're monitoring performance closely and will continue optimizing your content strategy to maintain upward momentum.
    </p>

    <!-- KPI Table -->
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
      <thead>
        <tr style="background-color: #f4f4f4;">
          <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Metric</th>
          <th style="border: 1px solid #ddd; padding: 12px; text-align: right; font-weight: bold;">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Sessions</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">3,456</td>
        </tr>
        <tr style="background-color: #f9f9f9;">
          <td style="border: 1px solid #ddd; padding: 10px;">Conversions</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">127</td>
        </tr>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Active Users</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">2,890</td>
        </tr>
        <tr style="background-color: #f9f9f9;">
          <td style="border: 1px solid #ddd; padding: 10px;">Engagement Rate</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">45.2%</td>
        </tr>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Bounce Rate</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">38.7%</td>
        </tr>
        <tr style="background-color: #f9f9f9;">
          <td style="border: 1px solid #ddd; padding: 10px;">Average Session Duration</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">2m 34s</td>
        </tr>
      </tbody>
    </table>

    <!-- Standard Closing Paragraph -->
    <p style="margin-bottom: 20px;">
      Please review the attached PDF for your complete monthly report. If you have any questions or would like to discuss these results in more detail, don't hesitate to reach out.
    </p>

    <!-- Signature -->
    <p style="margin-bottom: 5px;">Best regards,</p>
    <p style="margin-bottom: 5px; font-weight: bold;">[Agency Name]</p>
    <p style="margin-bottom: 0; font-size: 13px; color: #666;">
      [Agency Email] | [Agency Phone] | [Agency Website]
    </p>

  </div>
</body>
</html>
```

**PDF Attachment:**
- Filename: `ABC Corporation - January 2025 SEO Report.pdf`
- Source: Original Looker Studio PDF

---

### Google Ads Report Email Template

**Subject Line:**
```
Your January 2025 Google Ads Report
```

**Email Body (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your January 2025 Google Ads Report</title>
</head>
<body style="font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0;">
  <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">

    <!-- Greeting -->
    <p style="margin-bottom: 15px;">Hi Sarah,</p>

    <!-- Opening -->
    <p style="margin-bottom: 15px;">Please see the data below for XYZ Services.</p>

    <!-- Personalized Text (from database) -->
    <p style="margin-bottom: 15px; font-style: italic; color: #555;">
      Your new ad copy is performing well. Conversion rate improved significantly this month.
    </p>

    <!-- Standard Paragraph (Google Ads specific) -->
    <p style="margin-bottom: 20px;">
      Your Google Ads campaigns continue to drive quality traffic and conversions. We're actively monitoring performance and making bid adjustments to maximize your ROI.
    </p>

    <!-- KPI Table -->
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px;">
      <thead>
        <tr style="background-color: #f4f4f4;">
          <th style="border: 1px solid #ddd; padding: 12px; text-align: left; font-weight: bold;">Metric</th>
          <th style="border: 1px solid #ddd; padding: 12px; text-align: right; font-weight: bold;">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Sessions</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">1,234</td>
        </tr>
        <tr style="background-color: #f9f9f9;">
          <td style="border: 1px solid #ddd; padding: 10px;">Conversions</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">89</td>
        </tr>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Active Users</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">1,102</td>
        </tr>
        <tr style="background-color: #f9f9f9;">
          <td style="border: 1px solid #ddd; padding: 10px;">Engagement Rate</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">52.8%</td>
        </tr>
        <tr>
          <td style="border: 1px solid #ddd; padding: 10px;">Bounce Rate</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">31.2%</td>
        </tr>
        <tr style="background-color: #f9f9f9;">
          <td style="border: 1px solid #ddd; padding: 10px;">Average Session Duration</td>
          <td style="border: 1px solid #ddd; padding: 10px; text-align: right;">3m 12s</td>
        </tr>
      </tbody>
    </table>

    <!-- Standard Closing Paragraph -->
    <p style="margin-bottom: 20px;">
      Please review the attached PDF for your complete monthly report. If you have any questions or would like to discuss these results in more detail, don't hesitate to reach out.
    </p>

    <!-- Signature -->
    <p style="margin-bottom: 5px;">Best regards,</p>
    <p style="margin-bottom: 5px; font-weight: bold;">[Agency Name]</p>
    <p style="margin-bottom: 0; font-size: 13px; color: #666;">
      [Agency Email] | [Agency Phone] | [Agency Website]
    </p>

  </div>
</body>
</html>
```

**PDF Attachment:**
- Filename: `XYZ Services - January 2025 Google Ads Report.pdf`
- Source: Original Looker Studio PDF

---

## Appendix: Client Database Example

### CSV Format Example

```csv
ClientID,FirstName,BusinessName,Email,ServiceType,PersonalizedText,Active,CreatedDate,LastModifiedDate
1,John,ABC Corporation,john@abccorp.com,SEO,"Great work on the content updates last month. The new blog posts are already showing positive engagement.",TRUE,2024-01-15,2025-01-05
2,Sarah,XYZ Services,sarah@xyzservices.com,SEM,"Your new ad copy is performing well. Conversion rate improved significantly this month.",TRUE,2024-02-20,2025-01-05
3,Michael,Tech Solutions LLC,michael@techsolutions.com,SEO,"The technical SEO improvements are paying off. Site speed has improved notably.",TRUE,2024-03-10,2024-12-15
4,Emily,Green Earth Landscaping,emily@greenearthlandscaping.com,SEO,"Seasonal content strategy is working well. Spring service pages are gaining traction.",TRUE,2024-04-05,2024-11-20
5,David,Elite Fitness Center,david@elitefitness.com,SEM,"New landing pages for class signups are converting well. Keep up the great work!",TRUE,2024-05-12,2025-01-03
```

### Google Sheets Format Example

**Sheet Name:** Client Database

| Client ID | First Name | Business Name | Email | Service Type | Personalized Text | Active | Created Date | Last Modified Date |
|-----------|------------|---------------|-------|--------------|-------------------|--------|--------------|-------------------|
| 1 | John | ABC Corporation | john@abccorp.com | SEO | Great work on the content updates last month. The new blog posts are already showing positive engagement. | TRUE | 2024-01-15 | 2025-01-05 |
| 2 | Sarah | XYZ Services | sarah@xyzservices.com | SEM | Your new ad copy is performing well. Conversion rate improved significantly this month. | TRUE | 2024-02-20 | 2025-01-05 |
| 3 | Michael | Tech Solutions LLC | michael@techsolutions.com | SEO | The technical SEO improvements are paying off. Site speed has improved notably. | TRUE | 2024-03-10 | 2024-12-15 |

**Data Validation Rules (Google Sheets):**
- Service Type: Dropdown (SEO, SEM)
- Email: Valid email format
- Active: Checkbox (TRUE/FALSE)
- Personalized Text: Character limit 500

---

## Next Steps: Handoff to Plan-Synthesizer

This CLAUDE.md document provides comprehensive project requirements for the SEO/SEM Client Report Automation System. The plan-synthesizer agent should:

1. **Review Research Requirements** (Section: Research Requirements for Plan-Synthesizer)
   - Evaluate all seven research questions
   - Provide detailed analysis with pros/cons comparisons
   - Make final recommendations for each decision point

2. **Design System Architecture**
   - Based on research recommendations, design complete technical architecture
   - Define component interactions and data flow
   - Specify technology stack (libraries, frameworks, versions)
   - Create deployment plan (local, cloud, or hybrid)

3. **Create Implementation Plan**
   - Break down development into phases and tasks
   - Define milestones and deliverables
   - Estimate effort for each component
   - Identify dependencies and critical path

4. **Specify Testing Strategy**
   - Define unit test requirements per component
   - Create integration test scenarios
   - Design user acceptance test plan
   - Establish quality gates for MVP launch

5. **Develop Documentation Structure**
   - Outline user documentation ("how to use" guide)
   - Define setup/installation instructions
   - Create troubleshooting guide framework
   - Specify FAQ content based on anticipated questions

6. **Address Security & Compliance**
   - Finalize OAuth setup procedure
   - Define credential storage approach
   - Establish backup and disaster recovery plan
   - Document security best practices

**Key Deliverables from Plan-Synthesizer:**
- Technology stack recommendation with justification
- System architecture diagram
- Database schema (final format)
- Email template specifications (with actual template code)
- Implementation roadmap with milestones
- Testing plan with success criteria
- Security and deployment guide
- Cost analysis (setup + ongoing operational costs)

**Priority Focus Areas:**
1. PDF parsing library selection (critical for MVP success)
2. Deployment architecture (local vs. cloud decision impacts everything)
3. Approval workflow interface (user experience critical)
4. Database format (user maintenance ease)

Once plan-synthesizer completes research and architecture design, development can begin with clear technical direction and minimal ambiguity.

---

**End of CLAUDE.md Document**

**Project:** SEO/SEM Client Report Automation System
**Version:** 1.0
**Date:** 2025-10-01
**Working Directory:** `c:\Users\cscot\Documents\Apps\Email Reports`
**Status:** Requirements Complete - Ready for Plan-Synthesizer Review
