# Contributing Guide

**Project:** Crypto Pro Data Feed  
**Document:** Contributing Guide  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-09-15  
**Documentation Standard:** [docs/DOCUMENTATION_STANDARD.md](docs/DOCUMENTATION_STANDARD.md)

---

# Purpose

This document defines contribution requirements for the Crypto Pro Data Feed.

# Engineering Principles

Contributions shall preserve simplicity, reliability, deterministic behavior, public-contract stability, snapshot preservation, and low operational complexity.

# Before Submitting

Validate the affected behavior, confirm `src/` and `data/` paths remain correct, verify that the public JSON contract is preserved or explicitly versioned, update relevant documentation, and update [CHANGELOG.md](CHANGELOG.md) when the change is notable.

# Pull Requests

Each pull request should address one coherent engineering concern. The description should explain the purpose, affected behavior, validation performed, and any public-contract or documentation impact.

# Code Style

Use the Python Standard Library only for the current baseline, prefer explicit code, keep functions focused, use descriptive names, and fail clearly rather than suppressing errors.

# Documentation

Behavioral or structural changes require synchronized documentation. Start with [docs/DOCUMENTATION_OVERVIEW.md](docs/DOCUMENTATION_OVERVIEW.md) to identify the responsible documents.

# Guiding Principle

> Good software is built through disciplined collaboration.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable baseline. |
| 1.0.0 | 2026-09-15 | Updated contribution requirements for the reorganized repository. |

---

**End of Document**
