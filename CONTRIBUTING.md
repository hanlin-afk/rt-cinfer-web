# Contributing Guide

Thanks for your interest in contributing! This repository is **docs-first** and sets a high bar for **reproducibility** and **research ethics**.

## Development workflow
1. Open an issue describing the change (bug, feature, or doc).
2. Fork and create a feature branch: `git checkout -b feat/my-idea`.
3. Follow the **API contracts** in `docs/api.md`. If you change an interface, submit a separate proposal PR.
4. Add or update experiment descriptions in `docs/experiments.md`. Ensure all metrics are explicitly defined.
5. Run linters and unit tests (once code is added) via `make test`.
6. Submit a PR and fill out the PR checklist.

## Style
- Python code: PEP8/PEP484 (typing). Prefer pure functions for simulators.
- Reproducibility: Fix random seeds; document versions.
- Documentation: Prefer concise text, equations (LaTeX in Markdown), and clear tables.

## Ethics & reproducibility
- Declare data sources, licenses, and synthetic-data generation methods.
- Never fabricate results. Include negative/neutral outcomes.
- Provide exact commands to reproduce each figure or table.
