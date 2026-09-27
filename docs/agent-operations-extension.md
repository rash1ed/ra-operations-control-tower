# Agent Operations Extension (v0.2 experimental)

This extension adds a **synthetic AI-workforce operations view** to RA Operations Control Tower without changing the validated v0.1 task/project workflow.

## Why it exists
Modern operations teams increasingly coordinate human work, automation, and AI agents. The extension demonstrates how a PMO / Operations control tower can track:
- agent roles and reporting lines;
- monthly budget and spend;
- open and blocked workload;
- heartbeat freshness;
- deterministic RAG health;
- audit-friendly management reporting.

The implementation is dependency-free and does not call any model or external API.

## Relation to Paperclip
This project is **not a fork or copy of Paperclip** and does not include Paperclip code.

It is an original portfolio extension inspired by the broader agent-operations pattern: org structure, budgets, work tracking, governance, and heartbeat health. Paperclip is an external MIT-licensed orchestration platform. A future adapter could ingest exported or webhook-delivered health data from an orchestrator and apply these deterministic reporting rules.

## Public-data boundary
All repository samples are synthetic. No API keys, credentials, production agent IDs, employer data, customer data, or private operational records are included.
