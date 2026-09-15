# Crypto Pro Suite Documentation Standard

**Project:** Crypto Pro Suite  
**Document:** Documentation Standard  
**Version:** 1.0.0  
**Status:** Stable  
**Owner:** Rogerio Raposo  
**Language:** English  
**Last Updated:** 2026-09-15  
**Documentation Standard:** [DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md)

---

# 1. Purpose

This document defines the official documentation standard for technical repositories within the Crypto Pro Suite ecosystem. Documentation is a core engineering asset and shall evolve together with source code and public interfaces.

# 2. Principles

Technical documentation shall prioritize clarity, consistency, simplicity, accuracy, auditability, maintainability, reproducibility, and traceability. Each document should have one primary responsibility and avoid unnecessary duplication.

# 3. Standard Repository Documentation

A repository adopting this standard should organize institutional documentation as follows whenever applicable:

```text
README.md
CHANGELOG.md
CONTRIBUTING.md
LICENSE
docs/
├── DOCUMENTATION_OVERVIEW.md
├── DOCUMENTATION_STANDARD.md
├── SPEC.md
├── ARCHITECTURE.md
├── DEVELOPMENT.md
└── ROADMAP.md
```

`README.md`, `DOCUMENTATION_OVERVIEW.md`, `SPEC.md`, `ARCHITECTURE.md`, `DEVELOPMENT.md`, `DOCUMENTATION_STANDARD.md`, `ROADMAP.md`, `CHANGELOG.md`, and `CONTRIBUTING.md` are governed documents. The `LICENSE` file should preserve the canonical license text and is not required to use the Markdown metadata header or footer.

# 4. Document Responsibilities

| Document | Responsibility |
|----------|----------------|
| README.md | Project entry point and executive overview. |
| DOCUMENTATION_OVERVIEW.md | Documentation index, navigation, and reading order. |
| SPEC.md | Requirements, constraints, interfaces, and acceptance criteria. |
| ARCHITECTURE.md | Architecture, boundaries, and design decisions. |
| DEVELOPMENT.md | Engineering, validation, Git, and release practices. |
| ROADMAP.md | Planned project evolution. |
| DOCUMENTATION_STANDARD.md | Documentation governance. |
| CHANGELOG.md | Notable project changes. |
| CONTRIBUTING.md | Contribution requirements. |

# 5. Mandatory Metadata Header

Every governed Markdown document shall include:

```markdown
**Project:** ...
**Document:** ...
**Version:** ...
**Status:** Draft | Review | Stable | Deprecated
**Owner:** ...
**Language:** English | Portuguese
**Last Updated:** YYYY-MM-DD
**Documentation Standard:** <relative link to DOCUMENTATION_STANDARD.md>
```

Root-level documents shall use `[docs/DOCUMENTATION_STANDARD.md](docs/DOCUMENTATION_STANDARD.md)`. Documents inside `docs/` shall use `[DOCUMENTATION_STANDARD.md](DOCUMENTATION_STANDARD.md)`.

# 6. Mandatory Footer

Every governed Markdown document shall end with a `Document History` table followed by `**End of Document**`.

# 7. Relative Links

Documentation links shall be relative to the file containing the link. Examples:

```markdown
[ARCHITECTURE.md](ARCHITECTURE.md)
[Documentation Overview](docs/DOCUMENTATION_OVERVIEW.md)
[CHANGELOG.md](../CHANGELOG.md)
```

Links shall be updated whenever files are moved or renamed.

# 8. Versioning and Status

Documents follow Semantic Versioning. Major versions represent breaking structural or conceptual changes, minor versions significant additions, and patch versions editorial or backward-compatible corrections.

Defined statuses are Draft, Review, Stable, and Deprecated. Stable documents must accurately reflect the current implementation and pass technical, editorial, and cross-document consistency review.

# 9. Language Policy

Technical repository documentation is written in English. Governance documents for the wider Crypto Pro Suite may use Portuguese when appropriate to their audience and role.

# 10. Markdown Conventions

Use hierarchical Markdown headings, unordered lists when ordering is unnecessary, GitHub Markdown tables, language-labelled code blocks when possible, and simple ASCII diagrams unless graphical diagrams add substantial value.

# 11. Architecture Decisions

Architecture decisions should use stable identifiers such as `AD-001`, `AD-002`, and `AD-003`. Identifiers must never be reused for different decisions.

# 12. Change Management

Documentation changes shall update `Last Updated`, `Document History` when material, and the project `CHANGELOG.md` when the change represents a notable technical or structural modification. Significant code changes and documentation changes shall remain synchronized.

# 13. Review Process

Before a release is declared complete, documentation shall pass technical review, editorial review, cross-document consistency review, link/path validation, and implementation-to-specification validation.

# Guiding Principle

> Well-structured documentation is an architectural asset, not an administrative artifact.

---

# Document History

| Version | Date | Description |
|---------|------------|-------------|
| 1.0.0 | 2026-07-18 | First stable baseline. |
| 1.0.0 | 2026-09-15 | Aligned governance with the docs hierarchy and relative-link policy. |

---

**End of Document**
