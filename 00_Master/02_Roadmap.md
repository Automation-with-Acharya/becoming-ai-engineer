# ROADMAP.md — Execution Plan for ₹13 LPA → ₹50+ LPA in 12–18 Months

**Companion file to MASTER_CONTEXT.md and RULES.md.** MASTER_CONTEXT.md is the "what" (facts and targets). RULES.md is the "how the AI should behave." This file is the "what to physically do, and when" — the week-by-week and month-by-month execution calendar. Paste all three files together at the start of any planning/review session.

**Start date:** 2 July 2026 (Week 1, Day 1)
**Jump 1 hard deadline:** 2 January 2027 (end of Month 6 / Week 26)
**Jump 2 hard deadline:** 2 January 2028 (end of Month 18)
**Last updated:** 3 July 2026

---

## 0. THE TIME BUDGET — THE CONSTRAINT EVERYTHING ELSE IS DESIGNED AROUND

| Day type | Hours/day | Days/week | Weekly total |
|---|---|---|---|
| Weekday (Mon–Fri) | 2h | 5 | 10h |
| Weekend (Sat–Sun) | 4h | 2 | 8h |
| **Nominal weekly total** | | | **18h/week** |

- **Realistic effective average: ~15h/week**, not 18h. This roadmap is built against 15h/week, not the optimistic nominal number, because holidays, festivals, trips, low-motivation days, and "life" are already priced in. Hitting 18h in a given week is a bonus, not the baseline expectation.
- **Annual effective hours at 15h/week:** ~780h/year → over 18 months, roughly **1,150–1,200 effective hours** total. This is genuinely enough to reach both milestones if the hours are spent on the right things in the right order — but there is no slack for spending them on the wrong things (see MASTER_CONTEXT.md Section 6D — deprioritize list).
- **Non-negotiable weekly floor:** even in a bad week, protect a minimum of **6 hours** (e.g., one weekend day only). Falling below this floor for 2+ consecutive weeks is an automatic trigger to flag it in the weekly review (RULES.md Section 2) and adjust the plan — not to silently let it slide.
- **Missed-day policy:** if a weekday is missed (holiday, travel, low mood, unavoidable commitment), do NOT try to "make it up" by cramming double hours the next day — this causes burnout and kills the habit. Instead, let the weekend absorb it: shift the missed content into the existing Saturday/Sunday blocks below. If an entire week is lost (festival week, vacation), it is written off — not guilt-tripped over — and the following week resumes at the normal pace. The 15h/week average already assumes several such weeks per year.

### Standard weekly template (repeats with content changing by phase — see Sections 2–6 below)

| Day | Hours | Default activity type |
|---|---|---|
| Monday | 2h | Deep skill-building (hands-on coding/learning — new concept) |
| Tuesday | 2h | Deep skill-building (continued / cloud cert study) |
| Wednesday | 2h | Applied project work (building the actual portfolio project) |
| Thursday | 2h | Applied project work (continued) |
| Friday | 2h | Light/low-energy day — job search admin: browse postings, shortlist, save for weekend, light flashcard/concept review |
| Saturday | 4h | Split: 2h applications + outreach, 2h project build or interview prep |
| Sunday | 4h | Split: 2h project build/cert study, 1h mock interview or networking, 1h weekly review + log update (see RULES.md Section 2) |

This template holds throughout the roadmap — only the *content* inside each slot changes by phase/month, detailed below. Having a fixed weekly skeleton is deliberate: it turns "did I do career work today" into a non-decision.

---

## 1. PHASE OVERVIEW

| Phase | Duration | Goal | Months |
|---|---|---|---|
| **Phase 1 — Foundation & Build** | Weeks 1–12 | Learn core AI/GenAI stack, ship 2 portfolio projects, get cloud cert, rebuild resume/LinkedIn | Months 1–3 |
| **Phase 2 — Jump 1 Search Intensifies** | Weeks 13–26 | Heavy applications, interviews, portfolio polish, close Jump 1 offer | Months 4–6 |
| **Phase 3 — Onboard + Jump 2 Foundation** | Weeks 27–39 | Settle into new role, keep learning cadence alive, build production-grade domain project | Months 7–9 |
| **Phase 4 — Jump 2 Deepening** | Weeks 40–52 | Advanced skills (fine-tuning, multi-agent at scale, K8s, system design), quiet networking | Months 10–12 |
| **Phase 5 — Jump 2 Search & Close** | Weeks 53–78 | Heavy applications for senior/architect/lead roles, interviews, negotiate, close Jump 2 | Months 13–18 |

---

## 2. PHASE 1 — FOUNDATION & BUILD (Weeks 1–12 / Months 1–3)

**Phase goal:** By the end of Week 12, I must have: (1) working knowledge of LLM APIs, prompt engineering, RAG, and one agentic framework, (2) one deployed RAG project and one deployed agentic project on GitHub with live demos, (3) a rebuilt resume and LinkedIn reflecting the "Automation + AI-augmented Full-Stack Lead" positioning from MASTER_CONTEXT.md Section 3, (4) cloud certification study underway (exam by end of Month 3 or early Month 4), (5) applications already started from Week 3 onward — do NOT wait for the portfolio to be "ready" to start applying.

### Week 1 (2–6 July 2026) — Setup week, day-by-day
- **Mon (2h):** Set up dev environment. Create Anthropic/OpenAI API accounts. Read documentation on function/tool calling. Write first "hello world" LLM API call in Python.
- **Tue (2h):** Prompt engineering fundamentals — study structured prompting, few-shot examples, system prompts. Build 2–3 small scripts (summarizer, classifier).
- **Wed (2h):** Decide RAG project idea (recommendation: a searchable Q&A tool over BFSI/compliance-style documents — plays directly to your domain strength). Set up project repo.
- **Thu (2h):** Start resume rewrite using MASTER_CONTEXT.md Section 7 as the spec. Draft new bullet points with the Action + What + Tech + Metric format.
- **Fri (2h):** LinkedIn profile overhaul — headline, About section, experience section rewritten to match new positioning. Research and shortlist 15–20 target companies (from MASTER_CONTEXT.md Section 3 archetypes).
- **Sat (4h):** 2h — Finish resume v1, get it into a clean template. 2h — Start learning vector databases (pick one: Chroma or pgvector, since both are free/local-friendly).
- **Sun (4h):** 2h — Build basic embedding + retrieval pipeline for the RAG project. 1h — Research cloud certification options, register for AWS Solutions Architect Associate OR Azure AI Engineer Associate (decide by end of week — recommendation: Azure, given existing Azure DevOps exposure). 1h — Weekly review: log Week 1 in MASTER_CONTEXT.md Progress Log.

### Weeks 2–4 (Month 1 continued) — pattern
- **Weekdays:** Continue RAG pipeline build (chunking strategies, embedding quality, retrieval tuning) + start cloud cert coursework in parallel (alternate Mon/Tue between RAG concepts and cert modules).
- **Wed/Thu:** Keep building the RAG project until it has a working chat-style interface (simple Streamlit or Flask front end is enough — you already know Flask).
- **Fri:** Job search admin — by Week 3, start actually submitting 3–5 applications per week even with an imperfect portfolio. Do not wait for perfection; the market moves faster than your polish cycle.
- **Sat/Sun:** Applications + continued build + cert study + weekly review, per the standard template.
- **End of Month 1 checkpoint (Week 4 Sunday):** RAG project should be functionally complete (even if not polished). Resume v1 and LinkedIn should be live. 12–20 applications should be submitted cumulatively. Cloud cert coursework should be ~25% complete.

### Weeks 5–8 (Month 2)
- **Focus:** Agentic orchestration (LangGraph or CrewAI — pick one, don't split attention across both). Build Project 2: a multi-step agent that does something domain-relevant (e.g., an agent that reads a compliance document, extracts obligations, and drafts a checklist — leverages your BFSI background directly).
- **Weekdays:** Mon/Tue — agentic framework concepts and small exercises. Wed/Thu — build Project 2 incrementally.
- **Fri:** Continue applications (aim for 5+/week from this point on). Track responses in the Progress Log.
- **Sat/Sun:** Split between project build, cert study, and — starting Week 6 — begin doing 1 mock interview every other Sunday (use ChatGPT/Claude itself to role-play a technical interviewer, or a peer if available).
- **End of Month 2 checkpoint (Week 8):** Project 2 functionally working. Cloud cert coursework ~60–70% complete. Cumulative applications: 35–50. First real recruiter screens/interview calls should start appearing — if zero calls by Week 8, this is a hard flag: revisit resume/targeting in the Week 8 review (see RULES.md Section 2 "Gap flag").

### Weeks 9–12 (Month 3)
- **Focus:** Polish both projects (clean READMEs, architecture diagrams, short demo videos/GIFs, deploy live if possible — Streamlit Cloud, Render, or Vercel are free-tier friendly). Take the cloud certification exam by the end of this phase.
- **Weekdays:** Mon/Tue — cert exam prep/practice tests. Wed/Thu — portfolio polish, GitHub README quality, case-study writeups (2–3 paragraphs per project: problem, approach, tech stack, quantified outcome or realistic estimate).
- **Fri:** Continue applications; start layering in 1–2 direct outreach messages per week to recruiters/hiring managers at target companies (LinkedIn).
- **Sat/Sun:** Interview prep ramps up — system design basics, behavioral story prep (the 6-person team leadership story, the automation impact story), plus continued applications.
- **End of Phase 1 checkpoint (Week 12 / end of Month 3):** Cloud cert earned. 2 polished, deployed, portfolio-ready projects live. Resume/LinkedIn fully reflecting new positioning. Cumulative applications: 60–80. At least a handful of interviews should be in progress. This is the mandatory 45-day-ish review point referenced in RULES.md — do a full honest diagnostic here.

---

## 3. PHASE 2 — JUMP 1 SEARCH INTENSIFIES (Weeks 13–26 / Months 4–6)

**Phase goal:** Convert the foundation built in Phase 1 into an actual ₹25–30 LPA offer by 2 January 2027.

### Month 4 (Weeks 13–17)
- **Shift in time allocation:** Learning time drops from ~50% to ~25% of weekly hours; applications + interview prep rises to ~60%; remaining ~15% stays on portfolio refinement based on interview feedback.
- **Weekdays:** Mon — system design study (focus on patterns relevant to automation/data platforms, not generic FAANG-style system design). Tue — mock technical interview or DSA-adjacent practice (light — your roles are less DSA-heavy, more system/architecture-heavy, so weight accordingly). Wed/Thu — applications, tailoring resume per role, follow-ups. Fri — networking/outreach.
- **Sat/Sun:** Heavier interview prep blocks, real interviews scheduled here as they come in, weekly review.
- **Target:** 8–10 applications/week sustained. First-round interviews should be regularly occurring by now.

### Month 5 (Weeks 18–21)
- **Focus:** This is peak interview season. Prioritize interview prep and live interviews over new learning — the portfolio and skills built in Phase 1 are the ammunition, this month is about firing it accurately.
- **Weekdays:** Interview-specific prep tailored to each upcoming interview's company/role (research the company, tailor behavioral answers, review relevant tech). Treat each interview as deserving dedicated prep time, pulled from the standard slots.
- **Sat/Sun:** Continue applications for backup pipeline (never stop applying just because one process looks promising — it can fall through), plus salary negotiation research (know the band for each target role before an offer conversation happens).
- **Target:** At least 2–3 active interview processes running in parallel at any time by mid-Month 5.

### Month 6 (Weeks 22–26)
- **Focus:** Close the process. Final rounds, offer negotiation, decision-making.
- **Weekdays/weekends:** Flex time allocation entirely toward whatever the live interview processes need — this is not the month to start new learning threads.
- **Negotiation reminder:** Use the salary bands in MASTER_CONTEXT.md Section 5 as your floor reference, not your ceiling — always negotiate up from the initial offer using the market data as justification.
- **Hard deadline: 2 January 2027.** If Jump 1 has not landed by this date, this triggers the mandatory full checkpoint in RULES.md Section 5 — an honest diagnostic on title mismatch, application volume, interview conversion rate, market conditions, or portfolio gaps, followed by a revised plan (not a redefinition of the goal itself, unless the diagnostic clearly warrants it).

---

## 4. PHASE 3 — ONBOARD + JUMP 2 FOUNDATION (Weeks 27–39 / Months 7–9)

**Phase goal:** Successfully transition into the new role while keeping the Jump 2 skill-build alive at a reduced but non-zero pace.

- **Reality check:** The first 2–4 weeks in a new job absorb extra cognitive energy. Time budget temporarily drops — protect a minimum of 6–8h/week (roughly the weekend blocks only) during onboarding, and resume the full 15h/week template by Week 31 or so.
- **Weekly content shifts to:**
  - Fine-tuning/PEFT/LoRA basics (conceptual + small hands-on exercises)
  - Model evaluation and guardrails/safety tooling
  - Multi-agent systems at production scale (tool use, memory, cost/latency optimization) — this is a natural extension of Project 2 from Phase 1
  - Domain specialization: start Project 3 — a production-grade AI system specifically in the "AI for regulated financial services" niche (fraud detection, compliance automation, or risk scoring), which is your most defensible differentiator per MASTER_CONTEXT.md Section 6C.
- **Sat/Sun:** Shift from active applications (paused during onboarding) to quiet groundwork — LinkedIn content/visibility building, staying warm with recruiters, continued Project 3 build.
- **End of Phase 3 checkpoint (Week 39 / end of Month 9):** Fully settled into new role. Project 3 in progress (30–50% complete). Fine-tuning/multi-agent concepts understood at a working level.

---

## 5. PHASE 4 — JUMP 2 DEEPENING (Weeks 40–52 / Months 10–12)

**Phase goal:** Build the specific credibility markers that justify a ₹45–50+ LPA offer: production-scale system design skill, a completed flagship domain project, and quiet market positioning.

- **Weekly content:**
  - Kubernetes/containerized deployment fundamentals (moves you from "developer" to "systems" credibility)
  - Advanced system design practice (distributed systems, scalability, increasingly asked even in AI-adjacent senior interviews)
  - Finish Project 3 (the BFSI/regulated-AI flagship project) to a fully polished, demo-ready state — this is the single most important artifact for Jump 2
  - Decide explicitly by Month 11: is the Jump 2 target the **Senior/Lead AI Engineer (IC)** track or the **Engineering Manager/Lead (GCC)** track? (See MASTER_CONTEXT.md Section 3.) This decision changes the interview prep focus for Phase 5 — don't leave it undecided going into the search phase.
- **Sat/Sun:** Start light, quiet networking for Jump 2 — reconnect with recruiters, update LinkedIn with Project 3 progress, no full application push yet (that's Phase 5).
- **End of Phase 4 checkpoint (Week 52 / end of Month 12):** Project 3 complete and polished. Track decision made (IC vs. EM). K8s and system design at working-interview level. Ready to enter full search mode.

---

## 6. PHASE 5 — JUMP 2 SEARCH & CLOSE (Weeks 53–78 / Months 13–18)

**Phase goal:** Land the ₹45–50+ LPA offer by 2 January 2028.

### Months 13–14 (Weeks 53–60)
- Full application push resumes — same intensity pattern as Phase 2 Month 4, but targeting senior/lead/architect titles this time (see MASTER_CONTEXT.md Section 3).
- Resume/LinkedIn refreshed again to lead with Project 3 and the now-completed AI/GenAI skill stack, plus the fact of having successfully executed Jump 1 (a market-tested compensation data point is itself a credibility signal — use it explicitly in interviews and negotiations).
- Target: 8–10 applications/week for senior-level roles (expect a lower volume of suitable postings than Jump 1, since these are more senior — quality of targeting matters more than raw volume here).

### Months 15–16 (Weeks 61–69)
- Peak interview season for Jump 2 — same discipline as Phase 2 Month 5: prioritize live interview prep over new learning, keep multiple processes running in parallel, never stop the applications pipeline until an offer is signed.
- Senior-level interviews will weight system design, architecture judgment, and leadership/behavioral scenarios heavily — prep accordingly using Project 3 and the team-leadership story as anchors.

### Months 17–18 (Weeks 70–78)
- Close the process — final rounds, negotiation, decision.
- **Hard deadline: 2 January 2028.** If this date arrives without a closed Jump 2 offer, trigger the same honest full-diagnostic protocol as the Jump 1 deadline (RULES.md Section 5) — this is not a failure state to hide from, it's a planned checkpoint with a built-in correction mechanism.
- Once Jump 2 closes: update MASTER_CONTEXT.md Section 9 (Change Log) and Section 8 (Progress Log) with the final outcome, and this document's job is done — the master goal is achieved.

---

## 7. WHAT SUCCESS LOOKS LIKE AT EACH CHECKPOINT (quick-reference table)

| Checkpoint | Date (approx) | Must be true |
|---|---|---|
| End of Month 1 | ~30 Jul 2026 | RAG project functional, resume/LinkedIn live, 12–20 apps sent |
| End of Month 2 | ~27 Aug 2026 | Agentic project functional, 35–50 apps sent, first interview calls |
| End of Month 3 | ~24 Sep 2026 | Cloud cert earned, 2 projects polished/deployed, 60–80 apps sent |
| End of Month 6 (Jump 1 deadline) | 2 Jan 2027 | ₹25–30 LPA offer signed |
| End of Month 9 | ~2 Apr 2027 | Settled in new role, Project 3 30–50% complete |
| End of Month 12 | ~2 Jul 2027 | Project 3 complete, IC-vs-EM track decided, K8s/system design working-level |
| End of Month 18 (Jump 2 deadline) | 2 Jan 2028 | ₹45–50+ LPA offer signed — master goal achieved |

---

## 8. CHANGE LOG

| Date | Change | Reason |
|---|---|---|
| 2026-07-03 | Initial version created, built against the 15h/week effective time budget (2h weekdays, 4h weekends) and the compressed 12–18 month timeline from MASTER_CONTEXT.md | Roadmap requested as a companion execution file |
