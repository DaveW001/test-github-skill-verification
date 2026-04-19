# Plan: Install and Validate OpenCode DCP Plugin

**Track ID**: 20260314-dcp-install-validation  
**Spec**: [spec.md](./spec.md)  
**Created**: 2026-03-14  
**Status**: Completed (2026-03-14)

---

## Phase 1: Source Checkout and Local Validation

- [x] Clone upstream DCP repository into a local temp workspace.
- [x] Install dependencies (`npm ci`).
- [x] Run package validation suite (`npm run test`, `npm run build`, `npm run typecheck`).

## Phase 2: OpenCode Installation

- [x] Update OpenCode user config plugin list to include `@tarquinen/opencode-dcp@latest`.
- [x] Preserve existing plugins and ordering conventions.

## Phase 3: Runtime Verification and Evidence

- [x] Confirm resolved runtime config includes DCP via `opencode debug config`.
- [x] Capture validation summary in artifacts.
- [x] Note remaining manual verification action requiring live session restart.
