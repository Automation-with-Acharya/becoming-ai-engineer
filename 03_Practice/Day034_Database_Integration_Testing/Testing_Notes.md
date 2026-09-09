# Software Testing Notes

Software testing is categorized across different scopes, stages, and objectives throughout the development lifecycle.

## Functional and Scope-Based Tests

### Unit Testing

- **Meaning:** Validates that individual, isolated components, functions, or methods execute as expected without external dependencies, which are usually mocked or stubbed.
- **Who writes:** Software Engineers / Developers.
- **Who performs:** Automated via CI/CD pipelines upon every commit or pull request, and run locally by Software Engineers.
- **Methods:** Arrange inputs and dependencies, act on one unit, and assert outputs, state changes, exceptions, and edge cases. Test one behavior at a time and keep tests deterministic.
- **Tools:** `pytest`, `unittest`, JUnit, NUnit, Jest, Vitest, Moq, Mockito, Sinon, and coverage.py or JaCoCo.
- **Automation:** Run `pytest`, `mvn test`, `dotnet test`, `npm test`, or the relevant CI job. Add coverage with `pytest --cov` or JaCoCo.
- **Manual testing:** Usually not required. Manually review the test cases and use a debugger or REPL for a failing edge case.

### Integration Testing

- **Meaning:** Verifies that multiple software modules, services, or third-party integrations interact and exchange data correctly, such as an API service calling a database or payment gateway.
- **Who writes:** Software Engineers or Software Development Engineers in Test (SDETs).
- **Who performs:** CI/CD automation on branch builds or staging deployments, occasionally executed manually during feature verification.
- **Methods:** Connect real collaborating components and verify request/response mapping, persistence, serialization, authentication, errors, retries, and external-service boundaries. Use isolated databases or containers and clean up test data.
- **Tools:** `pytest` with Testcontainers, Docker Compose, REST Assured, Spring Boot Test, Supertest, WireMock, MockServer, and Postman/Newman.
- **Automation:** Start dependencies with `docker compose up -d`, then run `pytest tests/integration/`, `mvn verify`, or `newman run collection.json` in CI.
- **Manual testing:** Start the dependent services, use Postman or `curl` to send representative requests, and verify database or service state afterward.

### Component Testing

- **Meaning:** Tests an entire subsystem or module independently of other modules, verifying internal data flow and logic within that module's boundaries.
- **Who writes:** Software Engineers or SDETs.
- **Who performs:** Automated in the CI/CD pipeline or locally by Developers.
- **Methods:** Exercise a complete component through its public interface while replacing unrelated dependencies. Test internal workflows, data transformations, configuration, failure handling, and component-level contracts.
- **Tools:** Playwright component testing, Cypress Component Testing, Storybook, Testing Library, pytest, and framework-specific test harnesses.
- **Automation:** Run `npx playwright test`, `npx cypress run --component`, or the framework's component-test command in CI.
- **Manual testing:** Usually supplementary. Open the component in Storybook or the application, interact with states such as loading and error, and compare behavior with the specification.

### End-to-End (E2E) Testing

- **Meaning:** Simulates real user scenarios across the entire software stack, from the front-end user interface to backend services, databases, and network calls.
- **Who writes:** SDETs, Automation Engineers, or QA Engineers.
- **Who performs:** Automated scheduled pipeline runs, such as nightly builds, or executed manually by QA Engineers before release.
- **Methods:** Model critical user journeys such as sign-in, checkout, and recovery. Assert visible outcomes and business results, test happy paths and high-value failures, and use stable test data with independent scenarios.
- **Tools:** Playwright, Cypress, Selenium, WebdriverIO, Appium, BrowserStack, Sauce Labs, and Allure Report.
- **Automation:** Run `npx playwright test`, `npx cypress run`, or `pytest` with Selenium/Appium drivers; execute the suite in BrowserStack or Sauce Labs for device coverage.
- **Manual testing:** Follow the documented user journey in a production-like environment, verify visible results and notifications, and record evidence for failed steps.

### System Testing

- **Meaning:** Evaluates the complete, integrated software product to verify that it meets end-to-end business and technical requirements in an environment closely mirroring production.
- **Who writes:** QA Engineers / SDETs.
- **Who performs:** QA Engineers, SDETs, or Test Leads.
- **Methods:** Trace requirements to business workflows and validate functional behavior, integrations, configuration, permissions, observability, and operational readiness in a production-like environment.
- **Tools:** TestRail, Xray, Zephyr, Jira, Playwright, Selenium, Postman, and CI/CD environment pipelines.
- **Automation:** Trigger the full system suite from CI/CD with commands such as `npx playwright test` or `newman run collection.json`, then publish results to the test-management system.
- **Manual testing:** Execute requirements-based scenarios in the staging environment, including configuration, permissions, integrations, and operational checks, then record sign-off.

## Build and Release Lifecycle Tests

### Smoke Testing (Build Verification Test)

- **Meaning:** A shallow suite of critical-path tests run immediately after a new build is deployed to check whether core functionality works and the build is stable enough for deeper testing.
- **Who writes:** SDETs or QA Automation Engineers.
- **Who performs:** Automated immediately by CI/CD upon deployment to an environment, or run manually by QA Engineers.
- **Methods:** Run a small, fast set of checks for deployment health, application startup, authentication, core APIs, key pages, and one critical business transaction. Stop deeper testing when smoke tests fail.
- **Tools:** Postman/Newman, pytest, Playwright, Cypress, curl, Kubernetes probes, GitHub Actions, and Jenkins.
- **Automation:** Run a tagged subset such as `pytest -m smoke`, `npx playwright test --grep @smoke`, or `newman run smoke.json` immediately after deployment.
- **Manual testing:** Open the deployed application, verify health and login, call a critical API with Postman or `curl`, and complete one key transaction.

### Sanity Testing

- **Meaning:** A targeted subset of tests performed after minor code modifications, bug fixes, or hotfixes to verify that the specific problem is solved without breaking basic surrounding functionality.
- **Who writes:** QA Engineers or Developers, often using existing test cases or ad hoc scripts.
- **Who performs:** QA Engineers or Software Engineers manually in the test environment.
- **Methods:** Reproduce the reported defect, verify the fix, and run focused checks around the changed code and its nearest dependencies. Include a small set of critical-path checks.
- **Tools:** Jira, TestRail, Postman, pytest, Playwright, Cypress, and browser developer tools.
- **Automation:** Run a focused tag or test file, such as `pytest tests/test_bug_123.py`, `npx playwright test --grep @sanity`, or a targeted Newman collection.
- **Manual testing:** Reproduce the defect in the test environment, apply the documented verification steps, and check nearby critical functionality in the browser or Postman.

### Regression Testing

- **Meaning:** Re-executes existing functional and non-functional tests to ensure that recent code modifications, bug fixes, or enhancements have not negatively impacted existing features.
- **Who writes:** QA Engineers, SDETs, and Software Engineers.
- **Who performs:** Automated regression suites via CI/CD, typically nightly or before release, alongside targeted manual execution by QA Engineers.
- **Methods:** Maintain a risk-based suite, run tests across supported configurations, compare results with the baseline, and prioritize changed areas plus historically fragile features.
- **Tools:** Playwright, Selenium Grid, pytest, JUnit, Cypress, TestRail, GitHub Actions, Jenkins, and Allure Report.
- **Automation:** Run the complete suite with `pytest`, `mvn test`, `npx playwright test`, or the CI regression workflow across the supported matrix.
- **Manual testing:** Perform risk-based exploratory checks for changed or historically fragile features and compare results with the previous release baseline.

### User Acceptance Testing (UAT)

- **Meaning:** Validates that the software handles real-world business scenarios and fulfills contract or product requirements before release to general users.
- **Who writes:** Business Analysts, Product Managers, or QA Engineers in collaboration with clients.
- **Who performs:** Business stakeholders, client end users, or Product Managers.
- **Methods:** Convert acceptance criteria into realistic business scenarios, use representative data, record pass/fail evidence, and capture stakeholder sign-off and unresolved risks.
- **Tools:** Jira, Azure DevOps, TestRail, Xray, Microsoft Teams, Confluence, and spreadsheet-based sign-off templates.
- **Automation:** Run automated acceptance scenarios with `npx playwright test`, `pytest`, or API collections, and attach the reports to the release ticket.
- **Manual testing:** Business users execute realistic acceptance scenarios from the criteria, record pass/fail evidence, and provide stakeholder sign-off.

### Beta and Alpha Testing

- **Meaning:** Alpha testing is conducted internally by staff or employees during a pre-release stage. Beta testing distributes the build to a select group of external end users to gather feedback in diverse real-world conditions.
- **Who writes:** Product Managers and QA teams, who provide structured feedback guidelines and test scenarios.
- **Who performs:** Internal teams for Alpha testing and external real-world users for Beta testing.
- **Methods:** Release to a controlled audience, define feedback tasks and guardrails, monitor crashes and usage, collect qualitative feedback, and compare behavior across real devices and environments.
- **Tools:** TestFlight, Google Play Console, Firebase App Distribution, LaunchDarkly, Sentry, Crashlytics, and Productboard.
- **Automation:** Distribute builds with TestFlight, Google Play Console, or Firebase App Distribution; use LaunchDarkly to control exposure and Sentry or Crashlytics to collect failures.
- **Manual testing:** Alpha or beta users install the build, complete guided scenarios on real devices, report feedback and defects, and note device or environment details.

## Non-Functional Tests

### Performance Testing

- **Meaning:** Measures system responsiveness, speed, throughput, and stability under a defined workload.
- **Who writes:** Performance Engineers, SDETs, or DevOps/SREs.
- **Who performs:** Performance Engineers or automated scheduled staging pipelines.
- **Methods:** Define service-level objectives, workload profiles, user journeys, test duration, and thresholds. Measure latency percentiles, throughput, error rate, resource usage, and capacity under repeatable conditions.
- **Tools:** Grafana k6, Apache JMeter, Gatling, Locust, Apache Bench, Prometheus, Grafana, and Datadog.
- **Automation:** Run `k6 run script.js`, `jmeter -n -t plan.jmx`, `gatling`, or `locust -f load_test.py`; collect metrics in Prometheus/Grafana or Datadog.
- **Manual testing:** Usually not a manual load test. Review the workload model, thresholds, dashboards, and results, then perform a small controlled request check when needed.

### Load Testing

- **Meaning:** A subset of performance testing that evaluates system behavior under anticipated peak normal-use traffic over a sustained duration.
- **Who writes:** Performance Engineers, SDETs, or Backend Engineers.
- **Who performs:** Automated test execution tools triggered by Performance Engineers or SREs.
- **Methods:** Ramp virtual users to expected peak traffic, sustain the load, observe response-time and throughput thresholds, and verify autoscaling, queues, database connections, and recovery.
- **Tools:** Grafana k6, JMeter, Gatling, Locust, Artillery, Prometheus, Grafana, and cloud load-testing services.
- **Automation:** Execute a scripted workload with `k6 run load.js`, `artillery run load.yml`, or the selected cloud load-testing job against staging.
- **Manual testing:** Usually not required. Manually verify the target environment, baseline health, dashboards, and post-test recovery before and after the run.

### Stress Testing

- **Meaning:** Pushes the software beyond normal operational capacity until it breaks, determining system limits and verifying how gracefully the system recovers from failures.
- **Who writes:** Performance Engineers, DevOps, or Site Reliability Engineers (SREs).
- **Who performs:** Performance Engineers or SREs in dedicated performance environments.
- **Methods:** Increase load beyond expected capacity, identify the breaking point, observe graceful degradation and failure modes, and verify alerts, recovery, and data integrity after load decreases.
- **Tools:** Grafana k6, JMeter, Gatling, Locust, LitmusChaos, Prometheus, Grafana, and PagerDuty.
- **Automation:** Increase virtual users with `k6`, JMeter, or Locust until defined limits are reached, while collecting metrics and alerts automatically.
- **Manual testing:** Usually not required for generating load. Engineers manually observe dashboards, validate alerts and runbooks, and approve safe stop or recovery actions.

### Security Testing (Including Penetration Testing, DAST, and SAST)

- **Meaning:** Identifies vulnerabilities, authorization flaws, data leakage, and security risks across the application and infrastructure.
- **Who writes:** Application Security Engineers, DevSecOps, or external penetration testing vendors.
- **Who performs:** Automated security scanners for SAST, DAST, and dependency scanning in CI/CD, plus specialized Security Engineers or certified ethical hackers manually.
- **Methods:** Review threat models, scan source and dependencies, test authentication and authorization, probe input validation and secrets exposure, and manually verify exploitable findings without harming production data.
- **Tools:** Semgrep, SonarQube, Checkmarx, Snyk, OWASP ZAP, Burp Suite, Trivy, Dependabot, and GitHub Advanced Security.
- **Automation:** Run SAST and dependency scans in CI, for example `semgrep ci`, `trivy fs .`, or `npm audit`; run DAST with `zap-baseline.py -t https://staging.example.com`.
- **Manual testing:** Use Burp Suite or OWASP ZAP to explore authentication, authorization, input validation, session handling, and data exposure in an authorized test environment.

### Accessibility Testing (a11y)

- **Meaning:** Ensures that the application is usable by people with disabilities, verifying compliance with standards such as WCAG and Section 508 through screen readers, keyboard navigation, and contrast checks.
- **Who writes:** Accessibility Specialists, Front-End Engineers, or QA Engineers.
- **Who performs:** Automated auditing tools, such as axe and Lighthouse, in CI/CD, plus manual verification by QA or Accessibility Specialists.
- **Methods:** Test keyboard-only navigation, focus order, labels, semantics, screen-reader announcements, zoom/reflow, contrast, motion, and error messages against WCAG criteria. Combine automation with manual checks.
- **Tools:** axe-core, axe DevTools, Lighthouse, WAVE, Pa11y, NVDA, JAWS, VoiceOver, and Accessibility Insights.
- **Automation:** Run `npx pa11y https://staging.example.com`, Lighthouse CI, or axe in Playwright/Cypress tests; fail CI for agreed WCAG violations.
- **Manual testing:** Navigate with only the keyboard, test at high zoom, and use NVDA, JAWS, or VoiceOver to verify focus order, labels, announcements, and error messages.

### Usability Testing

- **Meaning:** Measures how intuitive, user-friendly, and easy the interface is to navigate for end users.
- **Who writes:** UX Researchers and Product Designers.
- **Who performs:** Monitored real users or representative target audiences observed by UX Researchers.
- **Methods:** Define user goals, observe representative users completing tasks, measure completion rate, time, errors, and satisfaction, then synthesize friction points and iterate on the design.
- **Tools:** UserTesting, Lookback, Maze, Hotjar, Microsoft Clarity, Figma prototypes, and surveys such as Qualtrics.
- **Automation:** Use scheduled surveys, session analytics, heatmaps, and funnel reports in Hotjar, Clarity, Amplitude, or Qualtrics; automated tools support measurement, not full usability judgment.
- **Manual testing:** Give representative users realistic tasks through UserTesting, Lookback, or Maze, observe without leading them, and record completion, errors, time, and feedback.

### Compatibility and Cross-Browser Testing

- **Meaning:** Checks application functionality, layout, and visual fidelity across multiple browsers, operating systems, mobile devices, and screen sizes.
- **Who writes:** QA Automation Engineers or Front-End Developers.
- **Who performs:** Automated cloud grid tools, such as BrowserStack, Sauce Labs, and Playwright, plus manual QA testers on physical test devices.
- **Methods:** Define a supported browser/device matrix, run functional and visual checks at target viewport sizes, test responsive behavior and input methods, and investigate rendering differences.
- **Tools:** BrowserStack, Sauce Labs, LambdaTest, Playwright, Selenium Grid, Percy, and Applitools.
- **Automation:** Run `npx playwright test` across a browser matrix in BrowserStack/Sauce Labs, and use Percy or Applitools for visual regression snapshots.
- **Manual testing:** Open the application on selected physical devices and browsers, resize or rotate the viewport, test touch and keyboard input, and document visual differences.

### Chaos Engineering and Resilience Testing

- **Meaning:** Intentionally injects infrastructure failures, such as terminating instances or simulating network latency and dropped database connections, to verify fault tolerance.
- **Who writes:** Site Reliability Engineers (SREs) and Platform Engineers.
- **Who performs:** Automated fault-injection tools, such as Chaos Mesh and Gremlin, managed by SREs.
- **Methods:** Define a steady-state hypothesis, inject one controlled failure at a time, observe user impact and recovery, verify alerts and runbooks, and limit experiments with scope, rollback, and safety controls.
- **Tools:** LitmusChaos, Chaos Mesh, Gremlin, AWS Fault Injection Service, Azure Chaos Studio, Kubernetes, Prometheus, and Grafana.
- **Automation:** Run a controlled experiment with `kubectl apply -f chaos-experiment.yaml`, LitmusChaos, Gremlin, or a cloud fault-injection job, then verify automated alerts and recovery.
- **Manual testing:** Required for experiment approval and observation. Confirm the steady-state hypothesis, monitor impact, follow the rollback plan, and verify runbooks after the fault is removed.

## Exploratory and Specialized Quality Checks

### Exploratory Testing

- **Meaning:** Combines learning, test design, and test execution while relying on intuition, domain knowledge, and edge-case probing rather than predefined scripts.
- **Who writes:** Unscripted; testers may use loose charters or mind maps created by QA.
- **Who performs:** Manual QA Engineers, Product Managers, and Developers during bug bashes.
- **Methods:** Start with a time-boxed charter, explore risks and boundaries, vary data and workflows, follow suspicious behavior, record evidence, and debrief findings with the team.
- **Tools:** Browser developer tools, Charles Proxy, Postman, Jira, Miro, mind-mapping tools, and session-based test-management templates.
- **Automation:** Automation is optional and supports exploration with tools such as Postman collections, browser scripts, or exploratory test charters executed by Playwright.
- **Manual testing:** Use a time-boxed charter, explore varied data and workflows in the UI or Postman, follow suspicious behavior, and record reproducible evidence in Jira.

### Contract Testing

- **Meaning:** Verifies that separate microservices agree on shared API specifications, or consumer/provider contracts, without requiring end-to-end integration environments.
- **Who writes:** Backend Engineers and SDETs.
- **Who performs:** Automated via CI/CD before services are deployed.
- **Methods:** Consumers define expectations for requests and responses; providers verify those contracts against their implementation. Test schema, status codes, headers, compatibility, and backward/forward changes.
- **Tools:** Pact, Pact Broker, Spring Cloud Contract, Schemathesis, OpenAPI, Dredd, and Postman contract tests.
- **Automation:** Run `mvn test`, `npm test`, Pact verification, or `schemathesis run openapi.yaml` in provider and consumer CI pipelines; publish contracts to Pact Broker.
- **Manual testing:** Usually not required. Manually inspect the OpenAPI contract and investigate a failed interaction using Postman or `curl` against a test service.

### A/B Testing

- **Meaning:** Serves two or more variants of a page or feature to live users to compare business metrics, conversion rates, or user engagement.
- **Who writes:** Front-End Engineers, Growth Engineers, or Data Analysts.
- **Who performs:** Deployed dynamically to live traffic and monitored by Product Managers and Data Analysts.
- **Methods:** Define one hypothesis and primary metric, randomize eligible users, calculate sample size and test duration, control exposure and segmentation, monitor guardrail metrics, and analyze statistical significance before rollout.
- **Tools:** Optimizely, LaunchDarkly, Statsig, GrowthBook, Amplitude, Google Analytics, Mixpanel, and experimentation platforms built on feature flags.
- **Automation:** Configure allocation and feature flags in the experimentation platform, validate events with automated tests, and run analysis jobs or dashboards after reaching the planned sample size.
- **Manual testing:** Before launch, preview each variant, verify targeting and analytics events in the browser, and monitor guardrail metrics and user feedback during the experiment.
