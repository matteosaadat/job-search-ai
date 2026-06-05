# Job Hunt — AI-Assisted Workflow Guide
> One assistant, 16 workflows, dump-first approach
> Owner: Mahdi Saadat | May 2026

---

## The Core Philosophy

You don't pre-sort mail before handing it to an assistant.
You hand them the pile. They sort it, flag what matters, and brief you.

This system works the same way. Dump raw content — articles, emails, job boards, LinkedIn posts, recruiter messages, anything. The AI reads it once and extracts everything useful across all 16 workflows simultaneously.

**You never have to say "this is a job listing" or "this is market data."**
The AI figures out what's in the pile and routes it correctly.

---

## The Universal Dump — Use This First

Before any workflow-specific prompt, start with this whenever you have raw content.

```
Here's some content I'm dumping. Read it and extract everything useful 
for my job hunt. In one pass, pull out:

- Job listings → score each against my profile and rules
- Companies mentioned → any intelligence signals (hiring, culture, news)
- Market signals → skill trends, role demand, salary/rate data
- Leads → people or companies worth reaching out to
- Anything else relevant to my search

Flag the top 2-3 things I should act on from this dump.

[paste anything here]
```

**Works for:** Indeed digest emails, LinkedIn feed screenshots, industry newsletters,
recruiter emails with multiple roles, blog posts with hiring trends, any raw paste.

**One dump → multiple workflows updated simultaneously.**

---

## WF-01 — Market Intelligence

**Manual:** Read industry articles, track hiring trends, maintain a spreadsheet of skills
and rates. Takes 2–3 hours per week to do properly. Most people don't do it consistently.

**AI-assisted:** Dump content, AI extracts patterns. Takes 5 minutes.

**Prompts:**

```
# After a Universal Dump, ask:
What market patterns are you seeing across everything I've shared this week?
Specifically: which skills are appearing repeatedly, what contract lengths
dominate, and are rates trending up or down for my profile?
```

```
# Monthly synthesis:
Based on all the jobs and market content I've shared this month,
what 3 skills should I prioritize developing? Rank by:
market frequency × impact on my hirability × effort to close.
```

```
# Specific trend research:
I keep seeing "system thinking" mentioned in senior eng postings.
Is this a real shift or buzzword? How does my profile speak to it?
What should I emphasize?
```

**What you get:** Skill trends, rate data, company hiring patterns, role demand signals —
extracted from content you were already reading anyway.

---

## WF-02 — Job Discovery

**Manual:** Browse 5–6 platforms daily, save interesting postings in browser bookmarks
or a spreadsheet. 45–60 min/day. Easy to miss good postings or forget to follow up.

**AI-assisted:** Forward emails, paste job board pages. AI scores and surfaces the best ones.

**Prompts:**

```
# Forward an Indeed/LinkedIn digest email:
Here's my job alert email. Go through every listing.
For each: extract title, company, location, rate if stated, contract vs full-time.
Score each against my profile (1-10). Flag anything scoring 7+
with a one-line reason why.

[paste email content]
```

```
# After browsing a job board:
Here are 8 job postings I just captured. Score each for fit.
For the top 3: tell me which resume group fits best and flag
any location or rate concerns based on my rules.

[paste JDs]
```

```
# Prioritization:
I have 12 saved jobs I haven't acted on. Here they are.
Which 3 should I work on first given my 2-month runway?
[paste list]
```

**Time saved:** 45 min/day → 10 min/day. You browse, AI filters.

---

## WF-03 — Job Digestion & Scoring

**Manual:** Read each JD carefully, highlight requirements, honestly assess your fit,
estimate rate alignment. 20–30 min per job.

**AI-assisted:** Paste JD, get structured record and score in 60 seconds.

**Prompts:**

```
# Standard digest:
Digest this JD completely. Extract:
- Title, company, location, remote policy, contract type, duration, rate
- Required vs nice-to-have skills
- Key responsibilities
- Red flags (vague, unrealistic, scope creep signals)
- Culture signals from the language they use
- Application method

Then score fit against my profile. Give me:
- Overall score (0-100)
- Skill match breakdown
- Location/rate flag
- Recommendation: apply / monitor / pass / stretch
- The one thing that makes this worth applying to (or not)

[paste JD]
```

```
# Quick gut-check:
One paragraph: is this job worth my time? Yes/no and why.
[paste JD]
```

**Time saved:** 20–30 min → 2 min. Every time.

---

## WF-04 — Company Research

**Manual:** Google the company, read Glassdoor, scan LinkedIn team page, look for
recent news. 45–60 min for a thorough research. Usually skipped or rushed.

**AI-assisted:** AI researches and briefs you in 2–3 minutes.

**Prompts:**

```
# Standard research brief:
I'm considering applying to [Company]. Give me a research brief covering:
- What they do and who their customers are
- Size, funding stage, and financial health signals
- Tech stack (if publicly known or inferable)
- Recent news (hiring, layoffs, product launches, acquisitions)
- Culture signals from their job posting language and any public reviews
- Red flags worth knowing before I engage
- Who is likely hiring for this role (title, LinkedIn search tips)
Keep it to a page. I need to make a decision, not a thesis.
```

```
# After dump mentions a company:
[Company] came up in something I dumped earlier.
What do I already know about them from context?
What should I find out before reaching out?
```

```
# Rate calibration:
What does [Company] typically pay for senior contract full-stack work?
What's the range I should expect and what floor should I anchor to?
```

**Time saved:** 45–60 min → 3–5 min. Always do this before applying.

---

## WF-05 — Document Generation

**Manual:** Rewrite resume for each job, draft cover letter from scratch, format everything.
1–3 hours per application. The biggest time sink in the whole process.

**AI-assisted:** Full package in under 2 minutes.

**Prompts:**

```
# Full application package:
Generate a full application package for the [Company] / [Title] job.

Use Group [A/B/C] framing.

Deliver:
1. Tailored resume — reorder sections and adjust language to mirror 
   this JD. Do not add any skill not in my master truth.
2. Cover letter — in my voice, direct, specific to this role.
   Apply my location rules automatically (Boston, remote preference).
   Lead with [fast learner narrative / Horse Platform / AI governance / 
   transformation story — pick the most relevant].
3. Interview prep — top 5 likely questions for this role with my 
   strongest answer angles.
```

```
# Cover letter only:
Write a cover letter for [role] at [company].
Their emphasis seems to be on [X].
My strongest proof point for that is [Y].
Keep it under 300 words. No "I am writing to apply" opener.
```

```
# Application field response:
This application has a field: "[Tell us about a time you improved 
a legacy system. 500 characters max.]"
Write a perfect response using real examples from my background.
Stay under 500 characters. Every word counts.
```

```
# Character-limited field (most common pain point):
Field: "[Why do you want to work here? 250 chars]"
Company: [X]
Role: [Y]
Draft 3 versions at exactly 250 characters. 
One confident, one warm, one direct. I'll pick.
```

**Time saved:** 1–3 hours → under 5 minutes. This alone justifies the whole system.

---

## WF-06 — Reach Out

**Manual:** Draft outreach emails and LinkedIn messages. Figure out the right tone.
Second-guess yourself. 20–45 min per message.

**AI-assisted:** Draft in 60 seconds, you edit and send.

**Prompts:**

```
# Cold LinkedIn message to hiring manager:
I'm applying to [role] at [Company].
The hiring manager appears to be [Name/Title from LinkedIn].
Draft a cold LinkedIn InMail — 5 lines max.
Goal: get a conversation, not deliver a resume.
Don't mention the application directly. Make it about shared interest.
```

```
# Cold email application:
Draft an email to send my application to [contact] at [company].
Subject line should be specific and scannable.
Body: 4 sentences. Who I am, what I built, why them, what I want.
Attach my resume and make that clear.
```

```
# Warm email (I know them):
I know [Name] — we [worked together at X / met at Y / connected over Z].
I'm applying to [company/role].
Draft a warm email that references our connection naturally,
expresses genuine specific interest, and asks for a conversation.
Not a favor request. A peer reaching out.
```

```
# Intro request:
I want an intro to [hiring manager/company].
[Contact name] might know them.
Draft a short message asking [Contact] to make the intro.
Include a forwarding paragraph they can send on my behalf.
Keep both messages to 3-4 lines.
```

**Time saved:** 20–45 min → 3–5 min per message.

---

## WF-07 — Network Activation

**Manual:** Think about who you know, awkwardly draft messages,
feel weird asking for things, put it off. Usually under-utilized.

**AI-assisted:** AI identifies relevant contacts for each opportunity and drafts
non-awkward messages.

**Prompts:**

```
# Quarterly activation:
I'm entering active search mode. I'm looking for a 3-6 month 
senior full-stack or AI contract starting August 2026.

Here are people in my network: [list names + context]
Which of these are worth activating for this search?
For each recommended contact: draft a message that's genuine,
references something real about our connection,
and naturally mentions my availability.
Don't make it feel like a mass email.
```

```
# Company-specific:
I'm applying to [Company]. 
Who in my network might have a connection there?
Draft an intro request I can send to [Name] who might know someone.
```

```
# Nextmark network (high value — 10 years):
I want to reach out to former Nextmark colleagues.
Here's what I know about them: [list]
Who's most likely to have leads in my target areas?
Draft a personalized note for each — reference something specific
about our time at Nextmark, not generic "hope you're well."
```

**Time saved:** Most people skip this entirely. AI makes it easy enough to actually do.

---

## WF-08 — Follow Up

**Manual:** Remember who you applied to, when, and when to follow up.
Forget half of them. Feel unsure about timing and tone.

**AI-assisted:** AI tracks and drafts. You send.

**Prompts:**

```
# Post-application follow-up (day 5):
I applied to [role] at [Company] on [date].
No response yet. Draft a short follow-up email to [contact if known].
5-day follow-up — keep it to 2 sentences.
Reference something specific about the role. No "just checking in."
```

```
# Post-interview thank you (within 24 hours):
I just interviewed with [Name] at [Company] for [role].
Key things we talked about: [brief notes]
Draft a thank-you email. 3 sentences. Warm but professional.
Reference one specific thing from our conversation.
```

```
# Final close-out (day 20, no response):
I've followed up twice with [Company] for [role].
Draft a final "closing the loop" message.
Tone: no pressure, leaves door open, moves on professionally.
One sentence.
```

```
# Warm lead re-ping (company you liked, wrong timing):
I was interested in [Company] 2 months ago but timing didn't work.
Draft a re-engagement message for [contact].
Brief, genuine, references what's changed (Horse Platform launched, etc.)
```

---

## WF-09 — Platform Profile Maintenance

**Manual:** Update each platform separately, rewrite descriptions, feel like
you're writing the same thing 5 times. Profiles get stale.

**AI-assisted:** Generate fresh content for each platform from master truth in one session.

**Prompts:**

```
# LinkedIn headline + about section:
Write my LinkedIn headline and about section for contract search mode.
Headline: 120 chars max, lead with what I do + what I build.
About: 3 paragraphs. Problem I solve, proof (Horse Platform + Smart Form + SAM),
what I'm looking for. First person, direct voice. No buzzwords.
```

```
# Toptal profile:
Write my Toptal profile bio and project descriptions.
Toptal audience: CTOs and senior hiring managers looking for elite contractors.
Lead with Horse Platform (full-stack SaaS, solo, live in production).
Include SAM (AI governance — this differentiates me on Toptal).
Keep each project description to 100 words.
```

```
# Contra profile:
Write my Contra profile.
Contra audience: startups and small teams.
Emphasize: end-to-end ownership, fast delivery, AI-assisted velocity.
Mention availability: August 2026, 3-6 month contracts preferred.
```

```
# Portfolio case study (Smart Form):
Write a case study for Smart Form for my portfolio site.
Structure: the real-world problem → the insight → the solution → live demo.
Audience: technical hiring managers. Show both product thinking and engineering.
500 words max.
```

---

## WF-10 — Path Optimization

**Manual:** Periodically reflect on what skills are in demand, make vague plans
to "learn Docker someday", never execute because there's no urgency signal.

**AI-assisted:** Market data drives specific, prioritized actions.

**Prompts:**

```
# Monthly roadmap refresh:
Based on all the market content, jobs, and application outcomes 
I've shared this month, what are the top 3 things I should build 
or learn to increase my hirability?

For each: which resume group it helps, how long it takes,
and what specifically I'd build or ship to prove it.
Be specific — not "learn Docker" but "add a Dockerfile to 
Horse Platform and deploy to a $5 Fly.io instance."
```

```
# Rejected or passed on — extract learning:
I was passed on for [role] at [Company].
Here's the JD and any feedback I got: [paste]
What does this tell me about a gap in my profile?
Is it worth closing or is this just not my target market?
```

```
# Skill gap for a specific target:
I want to be competitive for Group C (AI Systems) roles.
Here are 5 Group C JDs I've seen recently: [paste]
What's the delta between my current profile and what these jobs need?
What's the fastest path to close that delta?
```

---

## WF-11 — Exposure (LinkedIn + Content)

**Manual:** Writing LinkedIn posts takes 2–3 hours. Most engineers don't post
because it feels unnatural and time-consuming.

**AI-assisted:** Draft in 15 minutes. You edit into your voice and post.

**Prompts:**

```
# Project post (Horse Platform launch):
Write a LinkedIn post about launching Horse Platform.
Audience: engineering and startup community.
Angle: what it felt like to build a production SaaS solo in 3 months —
the real architectural decisions, not a product announcement.
Tone: peer-to-peer, not self-promotional. Show the thinking.
500 words max. Hook in the first line.
```

```
# Opinion/thought leadership post:
Write a LinkedIn post about AI governance in engineering.
My specific angle: "using AI" is not the same as "governing AI."
SAM is my proof. The post should make people think, not just nod.
Don't mention I'm job hunting. This is pure value.
```

```
# Fast learner narrative post:
Write a LinkedIn post about going from 10 years of legacy frontend
to full-stack + AI + Java in 12 months after a layoff.
Honest, specific, no toxic positivity.
Real talk about what was hard and what the foundation from Nextmark 
actually gave me that made it faster.
```

```
# Shorter engagement post (3x/week format):
Give me 5 short LinkedIn post ideas (50-100 words each) 
based on what I've been building this week.
I'll pick one and we'll develop it.
Context: [what you worked on this week]
```

**Time saved:** 2–3 hours → 15–20 minutes. Post 3x more often.

---

## WF-12 — Interview Execution

**Manual:** Prep notes from memory, practice generic answers,
forget key talking points in the moment.

**AI-assisted:** Custom prep doc for every interview. Walk in ready.

**Prompts:**

```
# Full interview prep:
I have an interview for [role] at [Company] on [date].
Interviewer: [name + title if known]

Generate an interview prep doc:
1. Top 7 questions they'll likely ask for this specific role
2. My strongest answer angle for each — drawn from my real experience
3. The 3 talking points I should land no matter what (most relevant to this role)
4. Likely objections to my profile and how to handle them
5. 3 smart questions I should ask them
6. One-paragraph company brief so I can reference their context naturally
```

```
# Handling a specific weakness:
In interviews for this type of role, they'll probably ask about
[Docker / cloud experience / formal leadership].
I don't have a strong answer for this.
Help me reframe it honestly — not avoiding the gap but positioning
my actual experience in a way that's credible.
```

```
# Post-interview debrief:
I just finished the interview. Here's what happened: [notes]
What should my thank-you email say?
What signals did I pick up about their decision timeline?
Should I do anything differently in the next round?
```

---

## WF-13 — Negotiation

**Manual:** Accept the first number because it feels awkward to counter.
Leave money on the table every time.

**AI-assisted:** Research-backed counter, in the right tone.

**Prompts:**

```
# Counter offer:
[Company] offered me [rate]/hr for a [duration] contract starting [date].
My floor is $[X]/hr.
Market rate for this type of work (based on what I've seen) is $[Y]-$[Z]/hr.

Draft a counter email. Tone: confident and collegial, not apologetic.
Anchor to market rate and the value I bring, not what I need.
Counter at $[target].
```

```
# Terms negotiation (not just rate):
The rate is acceptable but the terms concern me:
- [Net 60 payment / IP clause / non-compete / termination at will]
Draft a response that accepts the offer conditionally and
asks to revise these specific terms. Friendly but clear.
```

```
# Offer evaluation before responding:
Here's what they offered: [details]
My rules: [paste relevant rules config section]
Is this worth countering or accepting?
What's my leverage in this negotiation?
What's the risk of countering?
```

---

## WF-14 — Contract Review

**Manual:** Read dense contract language, miss important clauses,
sign something you regret. Or pay a lawyer $300 to review a $15k contract.

**AI-assisted:** Flagged summary in 3 minutes. Know exactly what to ask about.

**Prompts:**

```
# Full contract review:
Review this contract. Flag every clause I should pay attention to.
Specifically look for:
- IP ownership (do they own everything I build, including side projects?)
- Non-compete scope, duration, and geography
- Non-solicitation terms
- Payment terms (net days, milestone triggers)
- Termination clause (how much notice on either side?)
- Indemnification — what am I personally liable for?
- Rate and hours — does it match what was verbally agreed?

For each flag: plain English explanation + severity (must negotiate / should discuss / just be aware).

[paste contract]
```

```
# Specific clause:
What does this clause actually mean in plain English?
Is it standard or should I push back?
[paste clause]
```

---

## WF-15 — Relationship Maintenance

**Manual:** Means to reach out to people, never does.
Relationships go cold. By the time you need them, it's been 2 years.

**AI-assisted:** Draft touchpoints that don't feel like cold asks.

**Prompts:**

```
# Quarterly activation sweep:
Here are people I should stay warm with:
[Name] — [context: former colleague at Nextmark, worked on X]
[Name] — [context: client from 2023, built Y for them]
[Name] — [context: recruiter who placed me at Z]

For each: draft a genuine touchpoint.
Reference something real about our connection or their work.
Not "hope you're well." Something they'd actually want to read.
I'm not asking for anything yet — just staying visible.
```

```
# End of contract re-engagement:
My contract at Beta Technology is ending in 2 months.
Draft a message to my Beta contact that:
- Appreciates the engagement professionally
- Mentions I'm wrapping up and will be available
- Leaves the door open for future work without being needy
```

```
# Referral ask (after re-engagement):
I've been back in touch with [Name] for a couple of weeks.
I want to ask if they know anyone who might need a senior contract engineer.
Draft a natural referral ask — peer tone, not favor-begging.
```

---

## WF-16 — Pipeline Timing Management

**Manual:** Stressful mental juggling. Things collide. You rush a decision
because something else has a deadline. Or you lose momentum because nothing is moving.

**AI-assisted:** Weekly briefing. Clear picture. Clear next actions.

**Prompts:**

```
# Weekly pipeline review:
Here's where my applications stand:
[Company A] — applied [date], no response
[Company B] — interview scheduled [date]
[Company C] — offer received, expires [date]
[Company D] — warm lead, haven't reached out yet
[Company E] — referral intro pending

My availability: [date]
My runway: 2 months

What should I do in the next 48 hours?
Flag any timing conflicts or things that need acceleration.
```

```
# Offer timing conflict:
[Company A] made an offer, expires in 48 hours.
[Company B] is my top choice but their decision is 2 weeks out.
How do I handle this? Draft the message to [Company B] asking for their timeline.
```

```
# Pipeline is thin:
I only have 2 active applications and nothing warm.
My target start is 8 weeks away.
What channels should I hit hard right now?
In what order?
```

---

## The Dump-First Habit

The most powerful habit this system gives you is **the daily dump.**

Before you do any of the 16 workflows explicitly, paste whatever you read that day.
An email. A job board page. A LinkedIn article. A recruiter message.

```
Daily dump — [date]

[paste everything you came across today]

Extract anything useful for my job hunt. Update me on:
- Any new leads or jobs worth scoring
- Market signals
- Companies I should know about
- Anything I should act on today
```

5 minutes in the morning. Your assistant has context by the time you're working.
Over time, patterns emerge without you having to go looking for them.

---

---

## The Review Loop — Stage, Refine, Commit

Every dump goes through three stages before anything is finalized.
Nothing is permanent until you say so.

```
DUMP → EXTRACT → [REVIEW LOOP] → COMMIT → DOCUMENTS UPDATED
                      ↑____refine, exclude, expand_____|
```

---

### Stage 1 — Extract (AI runs automatically)

After a dump, AI presents a structured staged report — one section per
workflow that had relevant content. Everything is draft. Nothing is written yet.

Example output after one dump:

```
STAGED REPORT — May 29 dump
─────────────────────────────────────────────

[WF-01 MARKET INTELLIGENCE — 3 signals found]
  → Signal A: "System thinking" appearing in 60% of senior eng postings
  → Signal B: Average contract rate for AI engineer roles: $130-160/hr
  → Signal C: Two companies (Acme, Bravo) announced expansion hiring

[WF-02 JOB DISCOVERY — 4 jobs found]
  → Job 1: Senior Full-Stack, Acme Corp, Remote, $140/hr — Score: 88 ✓
  → Job 2: AI Systems Eng, Bravo Inc, Boston hybrid, $500k salary — Score: 72
  → Job 3: Frontend Lead, Delta GmbH, Berlin, €90k — Score: 31
  → Job 4: Contract Dev, Echo Ltd, NYC, 6 months — Score: 65

[WF-04 COMPANY INTELLIGENCE — 2 companies found]
  → Acme Corp: 120 employees, Series B, React + Node stack, hiring 8 engineers
  → Delta GmbH: Berlin-based, no US presence

─────────────────────────────────────────────
Nothing committed. Review and tell me what to change.
```

---

### Stage 2 — Review Loop (you and AI talk)

This is a conversation. You read the staged report and react.
AI refines, re-researches, filters, or expands based on your feedback.
The loop continues until you're satisfied.

**Example exchanges:**

```
You:  Job 2 — $500k salary seems off. Probably a data error. Exclude it.
AI:   Removed Job 2. That was likely a scraped LinkedIn total comp figure
      misread as hourly. Staging updated.

You:  Job 3 is a European company. Drop it and don't include European 
      companies from this source going forward.
AI:   Removed Job 3. Noted: Delta GmbH source = European, filter out.
      Added rule to staging filter for this session.

You:  Job 1 looks great. Before committing, find me 3 similar roles 
      to Acme Corp before we add it.
AI:   Searching for similar roles... Found:
      → Foxtrot SaaS: Senior FS, Remote, $130/hr — Score: 82
      → Golf Inc: Full-Stack Contract, Remote-first, $120/hr — Score: 79
      → Hotel Co: React + Node, 4mo contract, Boston hybrid, $135/hr — Score: 85
      Add any of these to staging?

You:  Add Hotel Co. Skip the others.
AI:   Hotel Co added to staging. Now 2 jobs staged for commit.

You:  Signal B rate data — is $130-160/hr for AI roles or all senior eng?
AI:   That was mixed. Specifically for AI Systems roles (Group C) the 
      range is $140-175/hr. For general senior full-stack it's $110-140/hr.
      Which should I record in market intelligence?

You:  Record both separately.
AI:   Updated. Two signals staged now: AI Systems $140-175/hr, 
      Full-Stack $110-140/hr.

You:  Looks good. Commit everything.
```

---

### Stage 3 — Commit

When you say commit (or "looks good", "save this", "update the docs"),
AI finalizes all staged items and tells you exactly what changed.

```
AI:  COMMITTED — here's what was updated:

     /jobs/digested/job_acme_20260529.md  ← created
     /jobs/digested/job_hotelco_20260529.md  ← created
     /strategy/market-patterns.md  ← 2 rate signals added
     /companies/acme-corp.md  ← created with Series B intel
     
     Excluded: Job 2 (data error), Job 3 (European), 
               Job 4 (below threshold)
     
     Nothing was written before you approved it.
```

In Claude Code: files are literally written to disk.
In this chat: AI gives you the exact content to paste into each file.

---

### Review Loop Prompt Patterns

```
# After any dump — open the loop:
Here's my dump. Extract everything relevant across all 16 workflows.
Present a staged report. Don't commit anything yet.
[paste content]
```

```
# Mid-review refinements:
Exclude [X] — reason: [Y]
Flag [X] for more research before committing
Find similar [jobs/companies/signals] to [X] before I decide
Apply this filter to all items: [condition]
Merge [A] and [B] — they're the same company
That number seems off — double-check it
```

```
# Expanding mid-loop:
While we're here, also check [X]
Add this to the same session: [new paste]
Before committing job 3, generate the cover letter so I can see 
if it's worth pursuing
```

```
# Closing the loop:
Commit everything approved
Commit jobs only, hold the market signals
Start over — discard this session's staging
What's still staged that I haven't reviewed?
```

---

### The Interface — Where This Runs

**Right now — this Claude Project**
You already have this. Dump here, review here, say commit.
AI tells you what to write where. Fully functional today.
No build required.

**Next step — Claude Code in your project folder**
Same conversation pattern, but Claude Code writes to your actual files.
You run `claude` in your `/job-hunt/` directory.
Dump content in the terminal or reference a file.
Say commit → files updated on disk instantly.
This is the natural next step once you have the folder structure set up.

**Later — simple chat UI**
A lightweight web interface over the same system.
Drag and drop files. See staged reports in a clean layout.
Only worth building once the conversation patterns are solid
and you know exactly what you need the UI to show.

---

## Evolution Path

```
Week 1-2:   Claude Project (this chat)
            Dump here. Review here. Commit = AI tells you what to write.
            No build. Learn the prompt patterns.

Month 1:    Claude Code in your project folder
            Same workflow, files actually write to disk.
            Add browser extension for job capture.

Month 2+:   Automate the highest-friction steps.
            Watcher script for truth chip ingestion.
            Scheduled market intelligence dump.
            Only build what you actually use daily.

Month 3+:   Optional UI layer if the terminal feels slow.
            The conversation logic doesn't change — just the interface.
```

You don't need the full SAM-like system on day one.
You need the prompts and the dump habit.
The system grows from what you actually use.
