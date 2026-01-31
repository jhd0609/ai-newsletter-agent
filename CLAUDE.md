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
```

There is no test suite, linter, or build system configured.

## Required Environment Variables

- `ANTHROPIC_API_KEY` — required, exits if missing
- `SLACK_WEBHOOK_URL` — optional, prints newsletter preview to stdout if missing

## Architecture

Single-file application (`newsletter_agent.py`) with a 3-step pipeline:

1. **Search** (`search_ai_news`) — calls Claude Sonnet with web search tool to gather AI news from the past 7 days
2. **Curate** (`curate_newsletter`) — calls Claude Sonnet to select 5-7 top stories and format as a newsletter (max 800 words, Slack markdown)
3. **Distribute** (`format_for_slack` + `post_to_slack`) — converts to Slack Block Kit JSON and posts via webhook

`run_newsletter_agent()` orchestrates the full pipeline.

## Customization

- News topics/sources: edit the search prompt in `search_ai_news()`
- Newsletter format/tone/story count: edit the curation prompt in `curate_newsletter()`
