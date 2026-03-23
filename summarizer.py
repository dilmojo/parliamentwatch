"""Summarize committee report text using a configurable LLM provider."""

import os
from dotenv import load_dotenv
from config import SUMMARIES_DIR, LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL

load_dotenv()


def ensure_dirs(committee_key):
    """Create summaries directory for a committee."""
    os.makedirs(os.path.join(SUMMARIES_DIR, committee_key), exist_ok=True)


def get_cached_summary(committee_key, report_number):
    """Return cached summary if it exists."""
    ensure_dirs(committee_key)
    safe_name = report_number.replace("/", "-").replace(" ", "_")
    summary_path = os.path.join(SUMMARIES_DIR, committee_key, f"{safe_name}.md")

    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            return f.read()
    return None


def _call_llm(prompt):
    """
    Call the configured LLM provider and return the response text.

    Supports two backends:
      - "anthropic": uses the Anthropic SDK (default)
      - "openai": uses the OpenAI SDK, works with OpenAI, Gemini, Ollama, etc.

    Returns response text, or None on failure.
    """
    api_key = LLM_API_KEY
    if not api_key or api_key == "your-api-key-here":
        return None

    provider = LLM_PROVIDER.lower()

    if provider == "anthropic":
        from anthropic import Anthropic
        model = LLM_MODEL or "claude-sonnet-4-20250514"
        print(f"  Using Anthropic ({model})...")
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    elif provider == "openai":
        from openai import OpenAI
        model = LLM_MODEL or "gpt-4o"
        print(f"  Using OpenAI-compatible ({model})...")
        client_kwargs = {"api_key": api_key}
        if LLM_BASE_URL:
            client_kwargs["base_url"] = LLM_BASE_URL
        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    else:
        print(f"  Unknown LLM_PROVIDER: {provider}. Use 'anthropic' or 'openai'.")
        return None


def summarize_report(text, committee_name, report_number, committee_key):
    """
    Summarize a report using the configured LLM.

    Args:
        text: Full text of the report
        committee_name: Full committee name (for context)
        report_number: Report number/identifier
        committee_key: Short key for caching

    Returns:
        Summary string, or None on failure.
    """
    # Check cache first
    cached = get_cached_summary(committee_key, report_number)
    if cached:
        print(f"  Summary already cached for {committee_key}/{report_number}")
        return cached

    api_key = LLM_API_KEY
    if not api_key or api_key == "your-api-key-here":
        print("  No LLM API key set. Showing text preview instead.")
        print("  (Set LLM_API_KEY in .env, or ANTHROPIC_API_KEY for Claude)\n")
        # Return a preview of the text as fallback
        preview_len = 2000
        preview = text[:preview_len]
        if len(text) > preview_len:
            preview += f"\n\n[... showing {preview_len} of {len(text)} characters. Set API key for full summary ...]"
        return preview

    # Truncate very long reports to fit context window
    max_chars = 400000
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[... text truncated due to length ...]"

    prompt = f"""You are analyzing an Indian Parliamentary Committee report.

Committee: {committee_name}
Report Number: {report_number}

Below is the full text of the report. Please provide a structured summary with:

1. **Subject/Topic**: What is this report about?
2. **Key Findings**: The main observations and findings (bullet points)
3. **Recommendations**: Key recommendations made by the committee (bullet points)
4. **Ministries/Departments Involved**: Which government bodies are addressed
5. **Notable Observations**: Any particularly interesting or surprising findings

Keep the summary concise but comprehensive — aim for 500-800 words.

Report text:
{text}"""

    print(f"  Summarizing report {report_number}...")
    try:
        summary = _call_llm(prompt)

        if not summary:
            print("  LLM returned no response.")
            return None

        # Cache the summary
        ensure_dirs(committee_key)
        safe_name = report_number.replace("/", "-").replace(" ", "_")
        summary_path = os.path.join(SUMMARIES_DIR, committee_key, f"{safe_name}.md")
        with open(summary_path, "w") as f:
            f.write(summary)

        print(f"  Summary saved to {summary_path}")
        return summary
    except Exception as e:
        print(f"  Error summarizing report: {e}")
        return None
