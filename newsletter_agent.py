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

def search_ai_news() -> str:
    """
    Use Claude with web search to gather recent AI news.
    Returns raw search results as context for summarization.
    """
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        messages=[{
            "role": "user",
            "content": f"""Search for the most significant AI news and developments from the past week 
            ({week_ago.strftime('%B %d')} to {today.strftime('%B %d, %Y')}).
            
            Focus on:
            - Major model releases or announcements (OpenAI, Anthropic, Google, Meta, etc.)
            - Significant research breakthroughs
            - AI policy and regulation news
            - Notable AI product launches
            - Important industry moves (funding, acquisitions, partnerships)
            
            Search multiple times if needed to get comprehensive coverage.
            Return a detailed summary of what you find with sources."""
        }]
    )
    
    # Extract text content from response
    result_text = ""
    for block in response.content:
        if hasattr(block, 'text'):
            result_text += block.text
    
    return result_text


def curate_newsletter(raw_news: str) -> str:
    """
    Take raw news and curate it into a concise newsletter format.
    """
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""You are curating a weekly AI newsletter. Based on the following news gathered 
from the past week, create a concise newsletter with exactly 5-7 of the most important stories.

RAW NEWS:
{raw_news}

FORMAT REQUIREMENTS:
- Start with a one-line "TLDR" of the week's theme
- Each story should have:
  - A bold headline (use *bold* for Slack)
  - 2-3 sentence summary explaining why it matters
  - Source attribution
- End with a "Worth Watching" section with 1-2 developing stories
- Keep total length under 800 words
- Use plain text with Slack-compatible formatting (*bold*, _italic_, • for bullets)
- No emoji overload - keep it professional

Write the newsletter now:"""
        }]
    )
    
    return response.content[0].text


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
    
    # Step 1: Search for news
    print("\n[1/3] Searching for AI news from the past week...")
    raw_news = search_ai_news()
    print(f"     Found {len(raw_news)} characters of news content")
    
    # Step 2: Curate into newsletter
    print("\n[2/3] Curating newsletter...")
    newsletter = curate_newsletter(raw_news)
    print(f"     Newsletter ready ({len(newsletter)} characters)")
    
    # Step 3: Format and post to Slack
    print("\n[3/3] Posting to Slack...")
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
        print("\n[1/2] Searching for AI news...")
        raw_news = search_ai_news()
        print("\n[2/2] Curating newsletter...")
        newsletter = curate_newsletter(raw_news)
        
        print("\n" + "=" * 50)
        print("NEWSLETTER PREVIEW")
        print("=" * 50)
        print(newsletter)
    else:
        run_newsletter_agent()
