#!/usr/bin/env python3
"""
AI Newsletter Agent
Searches for top AI news, summarizes it, and posts to Slack.
Designed to run with Claude Code or as a standalone script.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from anthropic import Anthropic

# Configuration
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Initialize the Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def search_and_curate_newsletter() -> str:
    """
    Search for AI news and curate into newsletter in a single API call.
    Reduces token usage by avoiding a second call with the raw search content.
    """
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }],
        messages=[{
            "role": "user",
            "content": f"""Search for the most significant AI news from {week_ago.strftime('%B %d')} to {today.strftime('%B %d, %Y')}, then write a newsletter.

Search for: major AI model releases, research breakthroughs, policy/regulation news, product launches, and industry moves (funding, acquisitions).

Then format the results as a newsletter:
- One-line TLDR of the week's theme
- 5-7 most important stories, each with:
  - *Bold* headline
  - 2-3 sentence summary
  - Source attribution
- "Worth Watching" section with 1-2 developing stories
- Under 800 words, Slack-compatible formatting (*bold*, _italic_, • for bullets)
- Professional tone"""
        }]
    )

    # Extract text content from response
    result_text = ""
    for block in response.content:
        if hasattr(block, 'text'):
            result_text += block.text

    return result_text


def format_for_slack(newsletter_content: str) -> dict:
    """
    Format the newsletter for Slack's Block Kit.
    """
    today = datetime.now()
    
    return {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 AI Weekly — {today.strftime('%B %d, %Y')}",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": newsletter_content
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Curated by your AI Newsletter Agent • Powered by Claude"
                    }
                ]
            }
        ]
    }


def post_to_slack(payload: dict) -> bool:
    """
    Post the formatted newsletter to Slack via webhook.
    """
    if not SLACK_WEBHOOK_URL:
        print("ERROR: SLACK_WEBHOOK_URL environment variable not set")
        return False
    
    response = requests.post(
        SLACK_WEBHOOK_URL,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print("✓ Newsletter posted to Slack successfully")
        return True
    else:
        print(f"✗ Failed to post to Slack: {response.status_code} - {response.text}")
        return False


def run_newsletter_agent():
    """
    Main function to run the full newsletter pipeline.
    """
    print("=" * 50)
    print("AI Newsletter Agent")
    print("=" * 50)
    
    # Step 1: Search and curate newsletter
    print("\n[1/2] Searching for AI news and curating newsletter...")
    newsletter = search_and_curate_newsletter()
    print(f"     Newsletter ready ({len(newsletter)} characters)")

    # Step 2: Format and post to Slack
    print("\n[2/2] Posting to Slack...")
    slack_payload = format_for_slack(newsletter)
    success = post_to_slack(slack_payload)
    
    if success:
        print("\n" + "=" * 50)
        print("Newsletter delivered! ✓")
        print("=" * 50)
    
    return newsletter


if __name__ == "__main__":
    # Check for required environment variables
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)
    
    if not SLACK_WEBHOOK_URL:
        print("WARNING: SLACK_WEBHOOK_URL not set - will print newsletter instead of posting")
        
        # Run without Slack posting for testing
        print("\n[1/1] Searching for AI news and curating newsletter...")
        newsletter = search_and_curate_newsletter()
        
        print("\n" + "=" * 50)
        print("NEWSLETTER PREVIEW")
        print("=" * 50)
        print(newsletter)
    else:
        run_newsletter_agent()
