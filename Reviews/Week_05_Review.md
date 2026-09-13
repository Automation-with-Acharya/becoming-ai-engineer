# Week 05 Review

> **Project ₹50L | Week 05**
>
> **Date Range:** 27 August 2026 – 09 September 2026

---

## Week

- **Week Number:** 05
- **Date Range:** 27 August 2026 – 09 September 2026

---

## Time Summary

- **Hours Planned:** ~16 Hours
- **Hours Completed:** ~14 Hours

### Notes on Schedule

#### What worked?

- Successfully completed the core Week 5 database-engineering and backend-reliability progression without changing the frozen roadmap.
- Continued evolving the same Student Management backend rather than creating disconnected tutorial projects.
- The strongest learning pattern this week was **measure → experiment → break deliberately → inspect → fix → verify**, especially during PostgreSQL performance and testing work.
- Day 31 received extra time because I explored execution plans, schemas, search paths, database sessions, pgAdmin behaviour, and a 2.5-million-row dataset rather than stopping at the nominal two-hour target.
- Day 32 continued the same experimentation-first approach with composite indexes, index-column ordering, selectivity, partial indexes, and measured before/after performance.
- Day 33–35 converted the backend from “tested code” into a more deliberate **test strategy**, including unit, integration, API, regression, smoke, coverage, and transaction-isolation thinking.
- The overall learning workflow remained consistent with the earlier weeks: learn from official material → implement immediately → experiment independently → document deeply → commit/push.

#### What shifted?

- The week was spread across a longer calendar period because of the Janmashtami/festival break and other personal commitments.
- Day 31 intentionally expanded to ~4 hours across two days because the concepts were new and the additional experiments substantially improved understanding.
- The independent AI-image Telegram bot project consumed some time outside Project ₹50L, but it also produced valuable real-world backend, deployment, GPU/VM, and end-to-end systems experience.
- I did not try to force all missed time back into subsequent sessions. This remains consistent with the roadmap's missed-day policy: preserve the long-term learning system rather than creating burnout through catch-up cramming.

---

## Topics Learned

### Key Concepts Covered

- Advanced SQL JOINs and relational query design.
- `INNER JOIN`, `LEFT JOIN`, `GROUP BY`, `COUNT`, `HAVING`, and multi-table relational queries.
- Many-to-many modelling using a junction table.
- PostgreSQL `EXPLAIN` and `EXPLAIN ANALYZE`.
- Execution-plan reading and query-planner mental models.
- Sequential Scan, Index Scan, Nested Loop, Hash Join, Merge Join, estimated vs actual rows, loops, execution time, and buffer activity.
- Composite / multicolumn indexes and B-tree leading-column behaviour.
- Selectivity and workload-driven index design.
- Partial indexes.
- Evidence-driven query optimization.
- Repository improvements and the practical value of Dependency Injection for testability.
- pytest unit tests, fixtures, `conftest.py`, `MagicMock`, `patch`, FastAPI `TestClient`, and dependency overrides.
- Database integration testing with real PostgreSQL.
- Transaction isolation, rollback, `TRUNCATE`, SAVEPOINT concepts, constraint-failure testing, atomicity verification, and test-order independence.
- pytest markers, parametrization, coverage measurement, regression tests, smoke tests, and risk-based test strategy.
- CI/CD-oriented thinking around fast smoke gates and broader regression suites.

### Resources Used

- PostgreSQL Official Documentation:
  - Table expressions / JOINs
  - `SELECT`
  - Aggregate functions
  - Indexes and multicolumn indexes
  - Partial indexes
  - `EXPLAIN` / `EXPLAIN ANALYZE`
  - Transactions and SAVEPOINTs
- pytest Official Documentation:
  - fixtures
  - markers
  - parametrization
  - good integration practices
- FastAPI Official Documentation:
  - testing
  - TestClient
  - dependency overrides
- Python Standard Library:
  - `unittest.mock`
- coverage.py documentation.
- Engineering Handbook (self-maintained).
- Hands-on PostgreSQL experimentation through pgAdmin / PostgreSQL sessions.
- Hands-on experiments using a **2.5-million-row student dataset**.
- Existing Dockerized Student Management backend and its integration-test environment.

### Insights / Takeaways

- SQL performance is not primarily about writing clever SQL syntax; it is about understanding how PostgreSQL will physically execute the query and validating assumptions with measurements.
- Index design must follow real query patterns. More indexes do not automatically produce a faster system.
- A composite index is a workload decision, not merely a combination of two single-column indexes.
- Database engineering and application architecture are tightly connected: Repository boundaries, transaction ownership, and dependency injection directly affect testability and reliability.
- Integration tests provide confidence that mocks cannot provide because they exercise real SQL, schema constraints, transactions, and PostgreSQL behaviour.
- Coverage is a map of exercised code, not a correctness score. Risk-based testing is more valuable than blindly chasing 100%.
- The biggest architectural payoff of the earlier Clean Architecture work is now becoming visible: the system can be tested at different boundaries without requiring every test to run the entire stack.
- Repeated real-world troubleshooting and experimentation are producing deeper understanding than passive tutorial consumption.

---

## Projects Built

### Student Management Backend — Database & Reliability Engineering Upgrade

**Summary**

The Student Management Backend moved through a substantial database and reliability-engineering upgrade during Week 5.

The project now demonstrates:

```text
FastAPI
   ↓
Router
   ↓
Service
   ↓
Repository
   ↓
Database Helper / Connection Pool
   ↓
PostgreSQL
```

with:

```text
Advanced SQL
+
JOINs
+
Transactions
+
Indexes
+
Execution Plans
+
Repository Abstraction
+
Unit Tests
+
Integration Tests
+
API Tests
+
Regression Tests
+
Smoke Tests
+
Coverage Analysis
```

By the end of Week 5, the project had a structured test strategy with:

- **23 unit tests**
- **17 integration tests**
- **11 API tests**
- **51 total tests**
- **6 smoke tests**
- **~73% measured code coverage**

The project also retained the ability to test real PostgreSQL behaviour, including constraints, transaction atomicity, rollback, and isolated integration-test state.

**Status**

✅ Active (Continuously Improving)

**What I Learned**

- A backend becomes significantly more trustworthy when testing is treated as an architectural system rather than a collection of individual test functions.
- Performance, persistence, and testability must be designed together.
- Database transactions are both application concerns and test-environment concerns.
- Repository boundaries create the isolation required for fast unit tests while still allowing real integration tests where infrastructure behaviour matters.

---

### Personal Telegram AI Image-Generation Bot Project — Independent Learning

**Summary**

Alongside Project ₹50L, I spent time building and deploying a personal AI image-generation Telegram bot system. It is intentionally **not part of the Project ₹50L GitHub portfolio** and remains a separate personal project.

Even though it is outside the formal curriculum, it provided real end-to-end systems experience:

```text
Telegram User
      ↓
Telegram Bot
      ↓
Backend / Orchestration Logic
      ↓
VM / Remote Compute Environment
      ↓
GPU Service
      ↓
AI Image Generation
      ↓
Result Delivery Back to Telegram
```

The project was built and operated with **₹0 direct infrastructure spend**, leveraging the available VM and GPU-service resources.

**Status**

✅ Personal project / Independent learning

**What I Learned**

- End-to-end AI application architecture becomes much clearer when the complete request lifecycle is implemented and deployed rather than only studied theoretically.
- Backend engineering decisions become more concrete when the system has to handle remote compute, GPU workloads, external messaging, deployment, and operational troubleshooting together.
- This project reinforced Docker/VM/networking/runtime concepts from the Project ₹50L curriculum in a different real-world context.
- The project provided additional confidence that the concepts learned in the Student Management backend are transferable beyond the educational project.

**Important boundary**

This project remains outside the formal Project ₹50L portfolio and its GitHub scope. Its value this week is primarily as **supplementary hands-on systems experience**.

---

## LeetCode

### Problems Solved

- No major increase in LeetCode volume during Week 5.
- The primary effort was deliberately concentrated on database engineering, testing, performance, and systems implementation.

### Difficulty Levels

- Limited additional practice documented this week.

### Techniques Practiced

- SQL reasoning
- Query analysis
- Relational reasoning
- Backend architecture
- Testing strategy
- Database performance thinking

### Assessment

This is currently a deliberate trade-off rather than a problem. The project objective at this stage is production/backend depth, and Week 5 delivered substantial progress there.

However, LeetCode / DSA must remain part of the broader career-transition plan and should not be allowed to disappear for multiple consecutive weeks.

---

## GitHub Activity

### Commits This Week

- Continued updating the `becoming-ai-engineer` repository with the Week 5 Student Management backend work.
- Added advanced SQL practice and relational-query work.
- Added execution-plan and query-optimization experiments.
- Added composite and partial indexing experiments.
- Added repository testing infrastructure.
- Added unit, integration, and API tests.
- Added database transaction/integration tests.
- Added pytest markers, parametrization, regression tests, smoke tests, and coverage analysis.
- Continued updating the Engineering Handbook alongside implementation.

### Pull Requests / Branches

- Main branch development continued.
- No separate PR/branch workflow was introduced for these learning sessions.

### Notes on Version Control Habits

- The GitHub repository increasingly tells a coherent engineering story:
  - Python → PostgreSQL → Clean Architecture → FastAPI → Security → Reliability → Docker → SQL Performance → Testing.
- Documentation and implementation continued to evolve together.
- The repository is becoming a portfolio artifact rather than merely a record of exercises.

---

## Wins

### What Went Well

- ✅ Completed the full advanced-database/testing progression planned for this stage.
- ✅ Worked with a realistic **2.5-million-row dataset**, turning query-performance concepts into measurable experiments.
- ✅ Learned to inspect PostgreSQL execution plans rather than treating query performance as guesswork.
- ✅ Demonstrated a substantial composite-index performance improvement through real measurement rather than theoretical assumptions.
- ✅ Built a layered 51-test backend test strategy instead of simply accumulating isolated test cases.
- ✅ Verified real PostgreSQL transaction behaviour, including constraint failures and atomicity.
- ✅ Learned to reason about transaction ownership rather than blindly applying rollback-based testing patterns.
- ✅ Added risk-based coverage analysis and identified real next testing priorities rather than chasing a 100% number.
- ✅ Built a six-test smoke layer suitable for fast CI/CD gating.
- ✅ Continued integrating every new concept into the same Student Management backend.
- ✅ Gained additional independent end-to-end AI application deployment experience through the personal Telegram bot project at ₹0 direct infrastructure cost.
- ✅ Returned from the festival/personal-project break without losing the larger roadmap.

### Milestones Reached

- ✅ Day 030 — Advanced SQL JOINs Completed
- ✅ Day 031 — EXPLAIN / EXPLAIN ANALYZE Completed
- ✅ Day 032 — Advanced Indexing & Query Optimization Completed
- ✅ Day 033 — Repository Improvements & Automated Testing Completed
- ✅ Day 034 — Database Integration Testing & Transaction Safety Completed
- ✅ Day 035 — Backend Test Strategy, Coverage & Reliability Completed
- ✅ Week 05 Successfully Completed

---

## Challenges

### Obstacles Faced

- Janmashtami/festival commitments interrupted the planned study cadence.
- Day 31 expanded to approximately four hours across two days because the execution-plan concepts were new and required extensive experimentation.
- Understanding PostgreSQL planner behaviour required moving beyond application-level thinking into database-internal reasoning.
- Database-test transaction ownership created a subtle architectural challenge: an external rollback cannot undo an independently committed repository transaction.
- Coverage analysis revealed that important parts of the backend remain weakly tested, especially search functionality and the authentication layer.
- Balancing the formal Project ₹50L roadmap with the separate Telegram AI bot project introduced an additional time allocation decision.

### What I Struggled With

- Interpreting execution-plan details with confidence.
- Understanding why PostgreSQL can legitimately choose a sequential scan even when indexes exist.
- Developing intuition for composite index ordering and selectivity.
- Reasoning about transaction ownership across application and test boundaries.
- Determining what should be tested at unit, integration, API, and smoke levels without over-testing implementation details.

### How I Plan to Overcome Them

- Keep using real measurements instead of relying on intuition for database performance.
- Continue validating query assumptions with `EXPLAIN ANALYZE`.
- Continue testing transaction behaviour against real PostgreSQL.
- Prioritize uncovered high-risk application areas rather than blindly increasing coverage.
- Keep the Student Management backend as the primary structured learning vehicle.
- Keep independent personal projects supplementary so they enrich the roadmap without displacing it.
- Preserve the missed-day policy: resume the roadmap normally rather than creating burnout through artificial catch-up.

---

## Questions

### Open Questions

- How should the Student Management backend implement pagination efficiently over very large datasets?
- How should `search_students()` be optimized, tested, and indexed as the dataset grows?
- How should authentication/JWT flows be brought up to the same testing maturity as the core student APIs?
- How should CI/CD execute unit, smoke, API, and PostgreSQL integration tests in a clean automated environment?
- At what point should local Docker Compose testing evolve toward a more production-like test environment?
- How should observability evolve from local structured logs toward metrics, tracing, and production alerting?
- How should transaction boundaries be represented when one service operation spans multiple repositories?

### Topics to Research Next

- Pagination strategies
- Sorting and filtering
- Keyset / cursor pagination
- Query optimization for large datasets
- Search indexing strategies
- Authentication and authorization testing
- CI/CD pipelines for containerized applications
- Test containers / disposable databases
- Observability
- Production-grade API performance

---

## Next Week Goals

### Focus Areas

- Transition into the next roadmap phase while preserving the Week 5 database/testing foundation.
- Begin frontend / full-stack direction only where the frozen contract calls for it.
- Continue strengthening the Student Management backend through targeted gaps rather than uncontrolled feature expansion.
- Maintain testing discipline as new layers are added.

### Specific Goals

- Start the next planned technology block from the frozen 12-week roadmap.
- Keep the existing Student Management backend as the integration point between frontend and backend learning.
- Add or plan pagination, filtering, and search improvements where the roadmap places them.
- Continue testing authentication and other currently under-covered areas.
- Preserve the Engineering Handbook workflow.
- Keep GitHub commits and documentation synchronized with actual implementation.
- Continue maintaining enough DSA/LeetCode exposure to avoid creating a long-term gap.

### Success Criteria

- Week 6 starts without rewriting the learning contract.
- The Student Management backend remains stable while new capabilities are layered on top.
- Existing tests remain green when new work is introduced.
- At least the highest-risk Week 5 coverage gaps are clearly identified and scheduled.
- Learning continues at a sustainable pace rather than relying on catch-up bursts.
- The independent Telegram bot project remains a useful side-learning asset without becoming a source of roadmap drift.

---

# Mentor Assessment

## Overall Verdict

**🟢 ON TRACK — STRONG PROGRESS — KEEP THE CURRENT OPERATING SYSTEM**

Week 5 is a meaningful milestone because the project has crossed from “production-style backend development” into **measurable database engineering and reliable software-engineering practice**.

The progression is now:

```text
Python + CLI
      ↓
PostgreSQL
      ↓
Clean Architecture
      ↓
FastAPI
      ↓
Authentication / Middleware / Logging
      ↓
Configuration / Transactions / Pooling
      ↓
Docker + Compose + Deployment
      ↓
Advanced SQL / JOINs
      ↓
Execution Plans
      ↓
Advanced Indexing
      ↓
Repository Testing
      ↓
Database Integration Testing
      ↓
Regression / Smoke / Coverage Strategy
```

That is a coherent engineering progression rather than a collection of unrelated tutorials.

## Biggest Achievements

### 1. Database performance became evidence-driven

You moved beyond:

```text
“Indexes make queries faster.”
```

to:

```text
Baseline
   ↓
EXPLAIN ANALYZE
   ↓
Index hypothesis
   ↓
Measure
   ↓
Compare
   ↓
Keep / remove
```

The 2.5-million-row experiments made this especially valuable because the performance differences became observable rather than theoretical.

### 2. Transaction knowledge became architectural

Day 20 taught ACID and transaction mechanics.

Day 34 forced the harder question:

> **Who owns the transaction?**

That is a major step beyond simply knowing `BEGIN`, `COMMIT`, and `ROLLBACK`.

### 3. Testing became a system

By Day 35 the project had:

```text
23 Unit
17 Integration
11 API
─────────
51 Tests
```

plus:

```text
6 Smoke Tests
~73% measured coverage
Parametrized validation
Regression protection
Marker-based execution
```

The stronger achievement is not the number 51. It is that you began designing a **test strategy**.

### 4. Real-world independent systems experience expanded

The personal Telegram AI image-generation bot was outside the formal contract, but it exposed you to a different class of real engineering problems:

```text
Telegram
   ↓
Backend / orchestration
   ↓
VM / remote compute
   ↓
GPU service
   ↓
AI generation
   ↓
Result delivery
```

You also achieved that at **₹0 direct infrastructure cost** by leveraging the available VM/GPU resources.

That should be treated as supplementary evidence that the backend and systems concepts are transferring beyond the Student Management project.

---

## Goods & Bads

### 🟢 Goods

- Same project continuously evolving.
- Architecture is becoming progressively cleaner instead of being rewritten every few days.
- Excellent hands-on experimentation.
- Strong willingness to debug difficult infrastructure/database failures.
- Official documentation remains the learning foundation.
- Documentation and implementation are being maintained together.
- GitHub is becoming a coherent engineering portfolio rather than a collection of tutorials.
- Increasingly strong “why?” questions and architectural reasoning.
- Independent AI project experience is reinforcing rather than contradicting the main backend curriculum.

### 🟡 Areas to Watch

#### 1. DSA / LeetCode is getting crowded out

That is understandable during a deep backend/database block, but it should not disappear for many consecutive weeks. Bring it back as a small recurring “sprinkle” rather than creating another major study track.

#### 2. Authentication coverage is now a visible gap

Week 5 coverage analysis identified JWT/auth components as substantially less covered than the core student CRUD path. That is a good problem because the test strategy has exposed it.

#### 3. Search functionality is another clear next target

`search_students()` is currently a meaningful uncovered production path. This should eventually become part of the database/query/testing progression rather than being left as a permanent gap.

#### 4. Don't turn every interesting side project into curriculum

The Telegram bot is valuable precisely because it is a sandbox. Keep:

```text
Project ₹50L = structured curriculum
Personal projects = experimental laboratory
```

That boundary protects the main objective.

---

# What Should We Change?

## Major changes: **No.**

The current system is working.

The five-week progression shows the same positive pattern seen in Weeks 1–4: a single evolving project, daily implementation, documentation, GitHub updates, and gradual increase in production realism. The earlier weekly reviews explicitly identified consistency and continuous project evolution as major strengths. fileciteturn0file0L23-L28 fileciteturn0file1L23-L29 fileciteturn0file2L23-L28 fileciteturn0file3L23-L29

I recommend only three small adjustments:

1. **Keep the frozen contract unchanged.**
2. **Bring DSA back as a small recurring side block.**
3. **Use personal projects as supplementary system-design laboratories, not as replacements for the curriculum.**

Everything else should continue exactly as it has:

```text
Learn
  ↓
Implement
  ↓
Experiment
  ↓
Break deliberately
  ↓
Debug
  ↓
Document
  ↓
Commit
  ↓
Review
  ↓
Continue
```

---

# Final Mentor Verdict

| Area                        | Assessment                      |
| --------------------------- | ------------------------------- |
| Roadmap adherence           | 🟢 Strong                       |
| Backend engineering         | 🟢 Strong and accelerating      |
| Architecture understanding  | 🟢 Strong                       |
| Database engineering        | 🟢 Major progress               |
| Testing maturity            | 🟢 Strong foundation            |
| Troubleshooting ability     | 🟢 One of your strongest areas  |
| Documentation discipline    | 🟢 Excellent                    |
| GitHub portfolio value      | 🟢 Increasing significantly     |
| DSA consistency             | 🟡 Needs a small recurring slot |
| Schedule consistency        | 🟡 Imperfect but sustainable    |
| Overall Project ₹50L health | 🟢 **ON TRACK**                 |

The key point is that **the schedule has not been perfect, but the system has been resilient**. You have already navigated interviews, administrative work, festivals, family responsibilities, Docker problems, laptop issues, and separate personal-project work without abandoning the larger roadmap. The roadmap itself is designed around a realistic effective average rather than perfect weeks, and its missed-day policy explicitly favors sustainability over cramming.

That resilience is part of the achievement.

---

# Week 05 Summary

Week 5 transformed the Student Management backend from a production-oriented application into a system where **database behaviour, performance, transaction safety, and software correctness can be measured and verified**.

The database progression went from:

```text
JOINs
  ↓
Execution Plans
  ↓
Indexes
  ↓
Optimization
```

while the engineering-quality progression went from:

```text
Unit Testing
  ↓
Integration Testing
  ↓
Transaction Testing
  ↓
Regression Protection
  ↓
Smoke Testing
  ↓
Coverage / Risk Analysis
```

That is a substantial shift in engineering maturity.

The independent Telegram AI image-generation bot added a second kind of learning: real-world end-to-end AI application development and deployment using the available VM/GPU infrastructure at ₹0 direct cost. Although it remains outside the official Project ₹50L repository and curriculum, it reinforced the same backend, deployment, networking, orchestration, and systems instincts being developed through the main project.

The most important outcome is not any single technology learned this week.

It is the emerging ability to reason about an entire system:

```text
Application
   ↓
Architecture
   ↓
Database
   ↓
Performance
   ↓
Transactions
   ↓
Testing
   ↓
Reliability
   ↓
Deployment
```

**Week 05 Successfully Completed.** ✅

**Mentor recommendation:** keep the current system, add only small DSA and high-risk test-coverage “sprinkles,” and continue into the next frozen-contract phase without trying to compensate for past calendar disruptions through cramming.
