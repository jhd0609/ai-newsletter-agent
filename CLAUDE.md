# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Newsletter Agent — a Python script that uses Claude's web search to find recent AI news, curates it into a formatted newsletter, and posts it to Slack via webhook.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent
python newsletter_agent.py

# Trigger the GitHub Actions workflow manually
gh workflow run "AI Newsletter" --repo jhd0609/ai-newsletter-agent
```

There is no test suite, linter, or build system configured.

## Required Environment Variables

- `ANTHROPIC_API_KEY` — required, exits if missing
- `SLACK_WEBHOOK_URL` — optional, prints newsletter preview to stdout if missing

Both are configured as GitHub Secrets for CI usage.

## Architecture

Single-file application (`newsletter_agent.py`) with a 2-step pipeline:

1. **Search & Curate** (`search_and_curate_newsletter`) — single Claude Sonnet API call with the `web_search_20250305` tool (capped at 5 searches via `max_uses`) that gathers AI news from the past 7 days and formats it into a newsletter in one pass
2. **Distribute** (`format_for_slack` + `post_to_slack`) — converts to Slack Block Kit JSON and posts via webhook

`run_newsletter_agent()` orchestrates the full pipeline.

### Slack Block Kit constraints

`format_for_slack` splits newsletter content into multiple `section` blocks to stay under Slack's 3000 character per-block limit. It splits on paragraph boundaries (`\n\n`).

## CI/CD

GitHub Actions workflow at `.github/workflows/newsletter.yml`:
- Runs automatically every Monday at 8:00 AM Pacific (cron: `0 15 * * 1`)
- Can be triggered manually via `workflow_dispatch`

## Customization

- News topics/sources: edit the search prompt in `search_and_curate_newsletter()`
- Newsletter format/tone/story count: edit the format instructions in the same function
