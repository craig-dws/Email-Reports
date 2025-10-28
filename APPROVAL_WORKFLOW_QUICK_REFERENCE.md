# Approval Workflow Quick Reference

## 🚀 Quick Start

### 1. Generate Emails
```bash
venv\Scripts\python main.py --full
```

### 2. Review
Open: `data/approval_review.html`

### 3. Approve
Edit: `data/approval_tracking.csv`
- Change `Pending` → `Approved`
- Save file

### 4. Create Drafts
```bash
venv\Scripts\python main.py --create-drafts
```

### 5. Send
Open Gmail → Drafts → Send manually (with spacing)

---

## 📋 Status Values

| Status | Meaning | Color |
|--------|---------|-------|
| `Pending` | Ready for review | 🟢 Green |
| `Approved` | Ready to send | 🟡 Yellow |
| `Needs Revision` | Has errors | 🔴 Red |
| `Sent` | Already sent | 🔵 Blue |

---

## 🛠️ Commands

### Full Workflow
```bash
venv\Scripts\python main.py --full
```

### Process Stored PDFs Only
```bash
venv\Scripts\python main.py --process-pdfs
```

### Auto-Approve All (⚠️ Use with caution)
```bash
venv\Scripts\python main.py --approve-all
```

### Create Drafts
```bash
venv\Scripts\python main.py --create-drafts
```

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `data/approval_tracking.csv` | Approval status (edit this) |
| `data/approval_review.html` | Visual review (read-only) |
| `logs/YYYY-MM-DD.log` | Error messages |

---

## ✅ Approval Checklist

When reviewing each email:

- [ ] Business name matches client
- [ ] Email subject has correct month/year
- [ ] Report type correct (SEO vs Google Ads)
- [ ] No extraction errors listed
- [ ] KPI values look reasonable

---

## 🔧 Troubleshooting

### CSV changes not taking effect?
- Save the file after editing
- Check status is exactly `Approved` (case-sensitive)

### No drafts created?
- Verify at least one email has status `Approved`
- Check Gmail API credentials working

### Extraction errors?
- Mark as `Needs Revision`
- Check original PDF manually
- Add notes in Notes column

---

## 📊 CSV Format

```csv
ClientID,BusinessName,EmailSubject,Status,Notes,ExtractionErrors,CreatedDate,UpdatedDate
1,ABC Corp,Your January 2025 SEO Report,Pending,,,2025-01-05 09:15:00,2025-01-05 09:15:00
```

**To Approve:**
```csv
1,ABC Corp,Your January 2025 SEO Report,Approved,Looks good!,,2025-01-05 09:15:00,2025-01-05 09:15:00
```

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Generate emails | 5-10 min |
| Review HTML | 10-15 min |
| Approve in CSV | 5 min |
| Create drafts | 2-3 min |
| Send manually | 20-30 min |
| **TOTAL** | **40-60 min** |

---

## 🎯 Best Practices

### DO ✅
- Review at least 5-10 emails manually
- Check extraction errors first
- Save CSV after every change
- Space out sending (10-15 min between batches)

### DON'T ❌
- Don't auto-approve without spot-checking
- Don't edit CSV while system running
- Don't delete rows (mark as Needs Revision)
- Don't change CSV headers
- Don't send all drafts at once

---

## 📖 Full Documentation

- **User Guide:** `APPROVAL_WORKFLOW_GUIDE.md`
- **General Guide:** `README.md`
- **Technical Docs:** `APPROVAL_WORKFLOW_IMPLEMENTATION.md`

---

**Last Updated:** 2025-10-28
