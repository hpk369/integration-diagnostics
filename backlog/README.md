# Backlog: how work happens in this repo

Every piece of work is a ticket, the way it would be on a production team. A ticket has
context, requirements, acceptance criteria (as tests that already exist), what's out of scope,
and explain-back questions you answer in the PR.

## Cadence

| Day | Time | What |
| --- | --- | --- |
| Mon · Wed · Fri | 30 min | One XS ticket |
| Sat · Sun | ~3 h each | Two to four tickets, sized S or M |
| Sunday end | 15 min | Sprint review: say "check-in" to Claude; next sprint's tickets get written |

Sizes: **XS** ≤ 30 min · **S** ≤ 1.5 h · **M** ≤ 3 h. Anything bigger gets split.

## The loop for one ticket

1. **Pick up** the next ticket in the sprint table below. Read it to the end first.
2. **Branch:** `git checkout -b feat/ACME-2-api-key-auth`
3. **Un-skip** the ticket's tests: delete the `pytestmark = pytest.mark.skip(...)` line.
   Run them; watch them fail. That's your to-do list.
4. **Build** until `make check` is green. Don't edit the tests. If one looks wrong, stop and ask.
5. **Commit and open a PR** using the template: what changed, how you tested, explain-back answers.
   Add a changelog entry (CI requires one per PR).
6. **Review:** tell Claude "review ACME-2". You get *Must fix / Should / Nit* comments and a
   check of your explain-back answers. Fix the Must-fix items, then merge on green.
7. **Log** estimate vs actual in the ticket file, and five lines in LEARNING.md if you like.

## When you're stuck: don't stay stuck

| You say | You get |
| --- | --- |
| "hint ACME-3" | The next rung: H1 direction → H2 pseudo-code → H3 skeleton with blanks |
| "solution ACME-3" | A working solution, explained line by line |

Rules of thumb:
- 15 minutes with no progress → ask for a hint. Don't burn a whole session.
- Session ends and the ticket isn't done → ask for the solution, then **type it in yourself**
  (don't paste) and still answer the explain-back. That's where the learning sticks.
- H1 is already in each ticket, folded under "Hint 1".

## Owners

- **Owner: you.** Core logic. Claude (here or in VS Code) gives hints, not code, unless you
  ask for the solution. CLAUDE.md's learning-mode section tells Claude Code the same.
- **Owner: Claude.** Scaffolding and plumbing (fixtures, recorders, CI, Docker, UI). It
  arrives as a PR. Skim it; you don't have to review it.

## Sprints

### Sprint 1 · Nov 11–15 · Acme Shield API (evidence source)

| Ticket | Title | Owner | Size | Session |
| --- | --- | --- | --- | --- |
| ACME-1 | Project scaffold | Claude | — | Done in the first PR |
| [ACME-2](sprint-1/ACME-02-api-key-auth.md) | API-key authentication | you | XS | Wed Nov 11 |
| [ACME-3](sprint-1/ACME-03-rate-limiter.md) | Per-key rate limiter | you | XS | Fri Nov 13 |
| [ACME-4](sprint-1/ACME-04-billing-suspension.md) | Suspended accounts get 403 | you | XS | Sat Nov 14 |
| [ACME-5](sprint-1/ACME-05-scim-users.md) | SCIM user provisioning with 409 conflicts | you | S | Sat Nov 14 |
| [ACME-6](sprint-1/ACME-06-alerts-planted-defect.md) | Alerts endpoint with a planted defect | you | XS | Sat Nov 14 |
| [ACME-7](sprint-1/ACME-07-failure-catalog-api.md) | Failure catalog: the API entries | you | S | Sat Nov 14 |
| [ACME-8](sprint-1/ACME-08-evidence-models.md) | Evidence models (diagx/models.py) | you | S | Sun Nov 15 |
| ACME-9 | HAR recorder and scenario runner | Claude | — | PR by Sat Nov 14 |
| [ACME-10](sprint-1/ACME-10-api-scenarios.md) | First 9 eval cases from Acme Shield | you | M | Sun Nov 15 |

**Sprint goal:** Acme Shield answers like a real API, and 9 labeled cases exist.

### Later sprints (tickets written at each sprint review)

| Sprint | Ticket | Title | Owner | Size | Session |
| --- | --- | --- | --- | --- | --- |
| 2 · Nov 16–22 · SSO evidence and parsers | ACME-11 | SAML template and signing helper (test certs generated at runtime, never committed) | Claude | — | before Mon |
| | ACME-12 | `SamlScenario` knobs | you | XS | Mon Nov 16 |
| | ACME-13 | SAML parser, part 1: decode, defusedxml, Issuer, Status, Conditions, Audience | you | XS | Wed Nov 18 |
| | ACME-14 | SAML parser, part 2: NameID, SubjectConfirmation, signature placement, cert | you | XS | Fri Nov 20 |
| | ACME-15 | `TenantConfig` model and SSO fields | you | XS | Sat Nov 21 |
| | ACME-16 | HAR builder for the SSO browser chain | Claude | — | Sat Nov 21 |
| | ACME-17 | HAR parser: failing requests, noise filter, SAMLResponse extraction | you | M | Sat Nov 21 |
| | ACME-18 | 12 SAML cases (4 types × 3 variants) | you | S | Sat Nov 21 |
| | ACME-19 | JWT fixtures | Claude | — | Sun Nov 22 |
| | ACME-20 | JWT parser | you | S | Sun Nov 22 |
| | ACME-21 | 6 cases: OIDC redirect URI ×3, JWT ×3 | you | S | Sun Nov 22 |
| | ACME-22 | KB note "How to read a SAML response" + catalog entries 1–6 | you | S | Sun Nov 22 |
| 3 · Nov 23–29 · Facts to findings | ACME-23 | Webhook `sign()` / `verify()` | you | XS | Mon Nov 23 |
| | ACME-24 | Webhook receiver bug variants and delivery log | Claude | — | before Wed |
| | ACME-25 | Webhook delivery-log parser | you | XS | Wed Nov 25 |
| | ACME-26 | Server log parser (JSON lines and plain text) | you | XS | Fri Nov 27 |
| | ACME-27 | SAML checks | you | S | Sat Nov 28 |
| | ACME-28 | HTTP and JWT checks | you | S | Sat Nov 28 |
| | ACME-29 | Webhook, SCIM, defect and billing checks | you | S | Sat Nov 28 |
| | ACME-30 | Last 13 cases + dev/holdout split | you | S | Sun Nov 29 |
| | ACME-31 | Eval runner | Claude | — | before Sun |
| | ACME-32 | Rules baseline | you | S | Sun Nov 29 |
| | ACME-33 | `scoring.py` | you | S | Sun Nov 29 |
| 4 · Nov 30–Dec 6 · The LLM step | ACME-34 | `redact.py` | you | XS | Mon Nov 30 |
| | ACME-35 | Leak scanner | Claude | — | Mon Nov 30 |
| | ACME-36 | `Diagnosis` model and prompt v1 | you | XS | Wed Dec 2 |
| | ACME-37 | LLM client (timeouts, retries) and tracing helpers | Claude | — | before Wed |
| | ACME-38 | `validate.py`: routing to human review | you | XS | Fri Dec 4 |
| | ACME-39 | `pipeline.py`: wire the stages, spans per stage | you | S | Sat Dec 5 |
| | ACME-40 | Dev run on Haiku + `ERRORS.md` (5 worst misses) | you | S | Sat Dec 5 |
| | ACME-41 | Prompt revisions, judged on dev only | you | S | Sat Dec 5 |
| | ACME-42 | Sonnet comparison + one holdout run per approach | you | S | Sun Dec 6 |
| | ACME-43 | Customer reply and escalation templates | you | S | Sun Dec 6 |
| | ACME-44 | `POST /diagnose` | you | S | Sun Dec 6 |
| 5 · Dec 7–13 · Ship | ACME-45 | Explain-back session (live, with Claude) | you | XS | Mon Dec 7 |
| | ACME-46 | Dockerfile, compose, CI eval job | Claude | — | before Wed |
| | ACME-47 | README: results, limitations, decisions | you | XS | Wed Dec 9 |
| | ACME-48 | Gradio demo (replay + capped live mode) | Claude | — | before Fri |
| | ACME-49 | `docs/runbook.md` | you | XS | Fri Dec 11 |
| | ACME-50 | Deploy to the HF PRO Space (your account steps + secrets) | you + Claude | M | Sat Dec 12 |
| | ACME-51 | Ship: tag v1.0.0, final numbers, 3-min walkthrough, resume bullet | you | M | Sun Dec 13 |

**Slip gate: Sun Nov 29.** If the rules baseline doesn't score all 40 cases that night,
P1 ships Dec 20 instead of Dec 13. The production bar doesn't move.
