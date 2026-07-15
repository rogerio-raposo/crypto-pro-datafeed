DEVELOPMENT.md

Crypto Pro Suite — Development Standard

Version: Draft 0.1

---

Purpose

This document defines the software development standards adopted by the Crypto Pro Suite.

Its objective is to ensure consistency, maintainability, reproducibility and code quality throughout the project.

---

General Principles

The project follows these principles:

- Simplicity
- Reliability
- Reproducibility
- Modularity
- Readability
- Maintainability
- Auditability

Whenever there is a trade-off between simplicity and unnecessary complexity, simplicity shall prevail.

---

Programming Language

Current primary language:

- Python 3

Future components may use other languages if technically justified.

---

Naming Convention

All source code shall be written in English.

Examples:

- variables
- functions
- classes
- constants
- filenames
- directories

User-facing reports and documentation may be written in Portuguese.

---

Coding Style

The project adopts:

- PEP 8
- Type hints whenever practical
- Meaningful variable names
- Small functions
- Single Responsibility Principle

Avoid unnecessary abbreviations.

Prefer:

market_snapshot

instead of

ms

---

Constants

Avoid hardcoded values.

Configuration values shall be defined as constants.

Example:

PRIMARY_EXCHANGE = "Binance"
DEFAULT_SYMBOL = "BTCUSDT"
REQUEST_TIMEOUT_SECONDS = 20

---

Error Handling

Errors shall never be silently ignored.

Every failure should contain enough information to reproduce the problem.

Whenever possible, log:

- Exchange
- Endpoint
- Date
- Time
- Error message
- HTTP status (if applicable)

---

Data Acquisition

Current policy:

Primary source:

- Binance Spot

Contingency:

- Bybit

A substitute exchange shall only be used if Binance is unavailable.

Whenever contingency is activated, the generated report must explicitly state:

- reason
- substitute exchange
- timestamp

---

Snapshot Policy

No analytical module shall execute without a valid market snapshot.

The snapshot is considered the single source of truth for every analysis.

---

Project Structure

Each module should have a single responsibility.

Avoid unnecessary dependencies between modules.

Future architecture:

- Data Feed
- BTC PRO
- ETH PRO
- Ranking Institucional
- Capital Rotation
- Radar de Narrativas

---

Documentation

Every relevant component shall contain:

- purpose
- inputs
- outputs
- assumptions
- limitations

README files should explain how to use the component.

---

Versioning

Development versions:

Draft 0.x

Stable versions:

v1.x.x

Breaking changes shall be documented before implementation.

---

Commit Convention

Use Conventional Commits.

Examples:

docs: update README

feat: add Binance data collector

fix: handle Binance timeout

refactor: simplify snapshot generation

test: add snapshot validation

chore: configure GitHub Actions

---

Code Quality

Recommended tools:

- Black
- Ruff
- pytest

Future:

- mypy

Tool adoption should remain proportional to the project complexity.

---

Security

Never commit:

- passwords
- API keys
- tokens
- secrets

Use GitHub Secrets whenever authentication becomes necessary.

---

Development Philosophy

The project is intended to evolve incrementally.

A working and simple solution is preferred over a complex architecture introduced prematurely.

Every new component should be designed to be reusable by future modules of the Crypto Pro Suite.

---

Golden Rule

Write code that can be understood, maintained and audited without requiring knowledge from previous ChatGPT conversations.
