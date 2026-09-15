# Crypto Pro Data Feed Development Guide

**Project:** Crypto Pro Data Feed  
**Document:** Development Guide  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-09-15  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md)

---

# 1. Purpose

This document defines engineering practices, development workflow, validation strategy, and maintenance guidelines for the Crypto Pro Data Feed.

# 2. Development Philosophy

Development shall prioritize simplicity, reliability, deterministic behavior, explicit code, ease of maintenance, and long-term sustainability. Every feature must justify its maintenance cost.

# 3. Repository Structure

```text
crypto-pro-datafeed/
├── .github/
│   └── workflows/
│       └── update-datafeed.yml
├── src/
│   └── datafeed.py
├── data/
│   ├── snapshot.json
│   └── status.json
├── docs/
│   ├── DOCUMENTATION_OVERVIEW.md
│   ├── DOCUMENTATION_STANDARD.md
│   ├── SPEC.md
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   └── ROADMAP.md
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

A `tests/` directory shall be introduced only when automated tests are added; empty placeholder directories are intentionally avoided.

# 4. Development Environment

Version 1.0.0 uses Python 3.12 in GitHub Actions and requires only the Python Standard Library, Git, and GitHub Actions. Local execution from the repository root is:

```bash
python src/datafeed.py
```

# 5. Coding Standards

Prefer explicit behavior, focused functions, descriptive names, clear failures, deterministic execution, and backward-compatible interfaces. Avoid unnecessary abstractions and external dependencies.

# 6. Data Integrity and Error Handling

Every execution shall update `data/status.json`. A failure shall never overwrite a valid `data/snapshot.json`. JSON publication shall remain atomic and external responses shall be semantically validated before publication.

# 7. Testing Strategy

Until automated tests are introduced, relevant changes require functional, failure, regression, and manual validation. Validation must cover successful JSON generation, snapshot preservation on failure, status reporting, schema compatibility, documentation consistency, and GitHub Actions behavior.

# 8. Git Workflow

Use a feature or refactor branch, implement one coherent concern, validate functionality, update documentation, review the complete diff, and merge only after the branch is consistent with `main` and release requirements.

# 9. Workflow Validation

`.github/workflows/update-datafeed.yml` must execute `python src/datafeed.py`, validate `data/status.json`, validate `data/snapshot.json` on success, stage the appropriate files, and preserve the valid snapshot on collector failure.

# 10. Release Process

```text
Development
    ↓
Validation
    ↓
Documentation Review
    ↓
Version Review
    ↓
CHANGELOG
    ↓
Git Tag
    ↓
GitHub Release
```

A release shall not be completed while implementation, documentation, or public paths are inconsistent.

# 11. Documentation Requirements

Engineering changes shall keep [SPEC.md](SPEC.md), [ARCHITECTURE.md](ARCHITECTURE.md), this guide, [ROADMAP.md](ROADMAP.md), [DOCUMENTATION_OVERVIEW.md](DOCUMENTATION_OVERVIEW.md), the root [README.md](../README.md), and [CHANGELOG.md](../CHANGELOG.md) synchronized when applicable.

# 12. Future Development Guidelines

Future enhancements should preserve the public JSON contract, deterministic behavior, snapshot preservation, consumer independence, and low operational complexity. New functionality should extend the architecture rather than replace stable foundations whenever possible.

# Guiding Principle

> Sustainable software is built through disciplined engineering, not accumulated features.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable baseline. |
| 1.0.0 | 2026-09-15 | Updated repository paths, workflow guidance, and documentation references. |

---

**End of Document**
