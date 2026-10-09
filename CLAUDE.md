# CLAUDE.md — Optomechanics Project Driver

This is the top-level agent context file. All sub-agent files and skill files are registered here and deferred to for their respective domains.

---

## Project Overview

**Project:** Optomechanics  
**Owner:** ajmstein  
**Created:** 2026-10-08  

_[Fill in: goals, physical system, key questions being investigated]_

---

## Current State

_[Running summary of where the project is — updated as work progresses]_

- [ ] Project initialized
- [ ] Physical model defined
- [ ] Simulation scripts written
- [ ] Analysis pipeline set up

---

## Repository Structure

```
optomechanics/
├── CLAUDE.md               ← this file (top-level driver)
├── agents/                 ← sub-agent context files (one per domain)
├── skills/                 ← reusable skill/tool definitions
├── data/                   ← simulation outputs (gitignored)
├── scripts/                ← simulation and analysis scripts
└── notebooks/              ← exploratory notebooks
```

---

## Sub-Agents

Sub-agent files live in `agents/`. Each handles a specific domain. Register them here as they are created.

| File | Domain | Status |
|------|--------|--------|
| _(none yet)_ | | |

---

## Skills

Skill files live in `skills/`. Each encodes a reusable procedure or workflow.

| File | Purpose | Status |
|------|---------|--------|
| _(none yet)_ | | |

---

## Key Parameters and Constants

_[Fill in as the physical model is defined — e.g., mechanical frequency, optical wavelength, coupling rates]_

---

## Notes and Decisions

_[Log non-obvious choices, constraints, and context that won't be obvious from the code]_
