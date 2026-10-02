#!/usr/bin/env bash
# Render build for Lucy's brain service (Stage 5). Installs Python deps and the Claude Code CLI.
set -euo pipefail

echo "[build] python deps"
pip install --no-cache-dir -r requirements.txt

# Claude Code CLI — the OAuth (`claude -p`) brain path. Production runs HC_BACKEND=api (metered
# key, no CLI needed), but install it so the subscription path also works where OAuth is present.
echo "[build] Claude Code CLI"
npm install -g @anthropic-ai/claude-code || echo "[build] claude CLI install skipped (api backend does not need it)"

echo "[build] done"
