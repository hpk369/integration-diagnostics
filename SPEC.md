# SPEC: Project 1 — Integration Diagnostics Extractor

> Anything not written here is out of scope.

## Problem
Support engineers spend the first 20 minutes of most SSO and API tickets on mechanical work:
decoding the SAMLResponse in a HAR, checking the signing cert, comparing the Audience with the
tenant config, counting 429s, lining up request IDs. This tool does that work
deterministically, then uses an LLM only to weigh the findings, explain the root cause and
draft the reply. When it isn't sure, it says "needs human review".

Demoed against the fictional SaaS "Acme Shield" and its synthetic tenants (Fernhollow
Financial, Cedarline Health Network, Relaypoint).

## Users and scenario
A Tier 2 support engineer gets "SSO broke this morning for everyone, HAR attached." They
upload the HAR and the tenant's SSO config. The tool finds the ACS POST, decodes the SAML
response, sees that the signing-cert fingerprint doesn't match the tenant config, and returns:
issue type, classification (configuration / expected behavior / product defect /
specialist-owned), owner, cited evidence, a customer reply draft and an escalation report.

## MVP scope
- In:
  - Evidence: HAR 1.2, SAML Response (HTTP-POST binding), JWT, server logs (JSON lines and
    plain text), webhook delivery logs, tenant config.
  - 12 issue types plus `insufficient_evidence` (catalog: docs/failure-catalog.md).
  - Deterministic parsers and checks; rules-only baseline; LLM diagnosis with structured
    output; validation that routes doubtful cases to human review.
  - Redaction of secrets and PII before any LLM call; JSON trace spans with tokens and cost.
  - 40 labeled cases (27 dev / 13 holdout); eval with numbers in the README.
  - `POST /diagnose`, a Gradio demo on a Hugging Face Docker Space.
- Out (explicitly):
  - A live identity provider (Keycloak, Okta). SSO evidence comes from generated fixtures.
  - SAML Redirect binding, encrypted assertions, cryptographic signature verification, JWKS.
  - Full OIDC flows beyond redirect-URI errors; DNS, TLS and proxy problems.
  - Real customer data of any kind.

## Architecture constraints
- Python 3.12+, FastAPI, pydantic, uv. Claude API (Haiku 5.5 default, Sonnet 5.5 compared).
- One repo: `acme_shield/` (evidence source) and `diagx/` (pipeline).
- The LLM never sees raw evidence: only redacted facts and findings, and it cites finding IDs.
- XML is parsed with defusedxml.
- Tests never call paid APIs; live eval runs are scripts or CI jobs with a secret.
- Demo: Hugging Face PRO Docker Space (port 7860, runs as UID 1000), replay mode by default.

## Done when
- [ ] 40 labeled cases generated from Acme Shield and fixtures
- [ ] Every parser and check has passing tests, including must-not-fire cases
- [ ] Rules baseline and LLM results reported on the holdout, per class
- [ ] 0 redaction leaks across all cases
- [ ] CI runs lint, types, tests, leak scan and the dev-set eval on every push
- [ ] Live demo usable in under a minute
- [ ] README, ADRs, runbook, 3-minute walkthrough

## Deliverables
1. Live demo link:
2. README with architecture diagram: README.md (generated diagrams: docs/diagrams/architecture.md)
3. ADRs: docs/adr/
4. Integration guide: docs/integration-guide.md
5. Runbook: docs/runbook.md
6. CI passing: .github/workflows/ci.yml
7. Demo video link:

## Open questions
- Space sleep and cold-start behavior on HF PRO cpu-basic: test before sharing the link.
