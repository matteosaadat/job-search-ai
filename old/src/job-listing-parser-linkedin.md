
# 🧠 ChatGPT Browser Instruction: LinkedIn Smart Job Listing Parser

---

## ✅ Task Overview

When given raw HTML or a scraped list of job postings from LinkedIn or similar platforms, extract the following information for each job card:

### Fields to Extract:
- **Job Title**
- **Company Name**
- **Location**
- **Remote/Onsite/Hybrid status**
- **Job URL** → Convert to full URL and make it clickable
- **Promoted?**
- **Easy Apply?**
- **Actively Reviewing Applicants?**

---

## ✅ Output Format (Markdown List)

Example:

---

### Frontend Developer  
**Company:** InterEx Group  
**Location:** United States (Remote)  
**Remote:** ✅  
**Job URL:** [https://www.linkedin.com/jobs/view/4268345422](https://www.linkedin.com/jobs/view/4268345422)  
**Details:**  
- ✅ Actively reviewing applicants  
- 🔴 Promoted  
- 🔴 Easy Apply  

**💡 Score:** 75/100  

---

## ✅ Scoring Rules (0–100)

| Condition                  | Score Adjustment |
|---------------------------|------------------|
| Not Remote                | –25              |
| Promoted                  | –15              |
| Easy Apply                | –10              |
| Actively Reviewing        | +10              |

---

## ✅ Notes

- Always extract the **full LinkedIn job URL**:  
  Format → `https://www.linkedin.com/jobs/view/{job-id}`  
  (Extract the numeric job ID from `data-job-id` or job card `href`)

- Render output as a Markdown **list**, not a table or grid.

- Focus on high-quality listings tailored to the user’s goals.
