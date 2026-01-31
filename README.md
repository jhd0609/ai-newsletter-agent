# AI Newsletter Agent

A simple agent that curates weekly AI news and delivers it to Slack.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 3. Run manually (for testing)
```bash
python newsletter_agent.py
```

## Running with Claude Code

You can also run this directly via Claude Code:
```bash
claude code "Run the newsletter agent at ./newsletter_agent.py"
```

## Scheduling with GitHub Actions

See `.github/workflows/newsletter.yml` for automated Monday delivery.

## Customization

Edit the prompts in `newsletter_agent.py` to adjust:
- **News sources/focus areas**: Modify the search prompt in `search_ai_news()`
- **Newsletter format**: Modify the curation prompt in `curate_newsletter()`
- **Number of stories**: Change "5-7" to your preference
- **Tone**: Adjust the formatting requirements

## Cost Estimate

- ~2 Claude API calls per run (search + curate)
- Approximately $0.02-0.05 per newsletter using claude-sonnet
- Free Slack webhook delivery
