#!/usr/bin/env python3
"""
Perplexity Search via LitLLM and OpenRouter

This script performs AI-powered web searches using Perplexity models through
LiteLLM and OpenRouter. It provides real-time, grounded answers with source citations.

Usage:
    python perplexity_search.py "search query" [options]

Requirements:
    - OpenRouter API key set in OPENROUTER_API_KEY environment variable
    - LiteLLM installed: uv pip install litellm

Author: Scientific Skills
License: MIT
"""

import os
import sys
import json
import argparse
from typing import Optional, Dict, Any, List

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import litellm
        return True
    except ImportError:
        print("Error: LiteLLM is not installed.", file=sys.stderr)
        print("Install it with: uv pip install litellm", file=sys.stderr)
        return False


def check_api_key() -> tuple[Optional[str], str]:
    """
    Check if API key is configured (Perplexity or OpenRouter).

    Returns:
        Tuple of (api_key, provider) where provider is 'perplexity' or 'openrouter'
    """
    api_key = os.environ.get("PERPLEXITYAI_API_KEY")
    if api_key:
        return api_key, "perplexity"

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key, "openrouter"

    print("Error: No API key configured.", file=sys.stderr)
    print("\nTo set up your API key:", file=sys.stderr)
    print("For Perplexity Pro:", file=sys.stderr)
    print("1. Get key from https://www.perplexity.ai/settings/api", file=sys.stderr)
    print("2. Set PERPLEXITYAI_API_KEY environment variable", file=sys.stderr)
    print("\nFor OpenRouter:", file=sys.stderr)
    print("1. Get key from https://openrouter.ai/keys", file=sys.stderr)
    print("2. Set OPENROUTER_API_KEY environment variable", file=sys.stderr)
    print("\nOr create a .env file with:", file=sys.stderr)
    print("   PERPLEXITYAI_API_KEY=your-perplexity-key-here", file=sys.stderr)
    print("   OR", file=sys.stderr)
    print("   OPENROUTER_API_KEY=your-openrouter-key-here", file=sys.stderr)
    return None, ""


def search_with_perplexity(
    query: str,
    model: str = "perplexity/sonar-pro",
    max_tokens: int = 4000,
    temperature: float = 0.2,
    verbose: bool = False,
    provider: str = "perplexity"
) -> Dict[str, Any]:
    """
    Perform a search using Perplexity models via LiteLLM.

    Args:
        query: The search query
        model: Model to use (default: sonar-pro)
        max_tokens: Maximum tokens in response
        temperature: Response temperature (0.0-1.0)
        verbose: Print detailed information
        provider: API provider to use ('perplexity' or 'openrouter')

    Returns:
        Dictionary containing the search results and metadata
    """
    try:
        from litellm import completion
    except ImportError:
        return {
            "success": False,
            "error": "LiteLLM not installed. Run: uv pip install litellm"
        }

    # Check API key
    api_key, detected_provider = check_api_key()
    if not api_key:
        return {
            "success": False,
            "error": "API key not configured"
        }

    # Use detected provider if not explicitly set
    provider = provider or detected_provider

    if verbose:
        print(f"Model: {model}", file=sys.stderr)
        print(f"Query: {query}", file=sys.stderr)
        print(f"Max tokens: {max_tokens}", file=sys.stderr)
        print(f"Temperature: {temperature}", file=sys.stderr)
        print("", file=sys.stderr)

    try:
        # Perform the search using LiteLLM
        response = completion(
            model=model,
            messages=[{
                "role": "user",
                "content": query
            }],
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Extract the response
        result = {
            "success": True,
            "query": query,
            "model": model,
            "answer": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

        # Check if citations are available in the response
        if hasattr(response.choices[0].message, 'citations'):
            result["citations"] = response.choices[0].message.citations

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "model": model
        }


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Perform AI-powered web searches using Perplexity models via LiteLLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic search with Perplexity Pro
  python perplexity_search.py "What are the latest developments in CRISPR?"

  # Use Sonar Pro Search for deeper analysis
  python perplexity_search.py "Compare mRNA and viral vector vaccines" --model sonar-pro-search

  # Use Sonar Reasoning for complex queries
  python perplexity_search.py "Explain quantum entanglement" --model sonar-reasoning-pro

  # Use OpenRouter as provider
  python perplexity_search.py "Recent AI developments" --provider openrouter

  # Save output to file
  python perplexity_search.py "COVID-19 vaccine efficacy studies" --output results.json

  # Verbose mode
  python perplexity_search.py "Machine learning trends 2024" --verbose

Available Models:
  - sonar-pro (default): General-purpose search with good balance
  - sonar-pro-search: Most advanced agentic search with multi-step reasoning
  - sonar: Standard model for basic searches
  - sonar-reasoning-pro: Advanced reasoning capabilities
  - sonar-reasoning: Basic reasoning model

Providers:
  - perplexity (default): Direct Perplexity API (requires PERPLEXITYAI_API_KEY)
  - openrouter: Via OpenRouter (requires OPENROUTER_API_KEY)
        """
    )

    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="The search query"
    )

    parser.add_argument(
        "--model",
        default="sonar-pro",
        choices=[
            "sonar-pro",
            "sonar-pro-search",
            "sonar",
            "sonar-reasoning-pro",
            "sonar-reasoning"
        ],
        help="Perplexity model to use (default: sonar-pro)"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4000,
        help="Maximum tokens in response (default: 4000)"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Response temperature 0.0-1.0 (default: 0.2)"
    )

    parser.add_argument(
        "--output",
        help="Save results to JSON file"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information"
    )

    parser.add_argument(
        "--check-setup",
        action="store_true",
        help="Check if dependencies and API key are configured"
    )

    parser.add_argument(
        "--provider",
        choices=["perplexity", "openrouter"],
        default=None,
        help="API provider (default: auto-detect from available keys)"
    )

    args = parser.parse_args()

    # Check setup if requested
    if args.check_setup:
        print("Checking setup...")
        deps_ok = check_dependencies()
        api_key, provider = check_api_key()
        api_key_ok = bool(api_key)

        if deps_ok and api_key_ok:
            print("\n[OK] Setup complete! Ready to search.")
            print(f"Provider detected: {provider}")
            return 0
        else:
            print("\n[X] Setup incomplete. Please fix the issues above.")
            return 1

    if not args.query:
        parser.error("query is required unless --check-setup is used")

    # Check dependencies
    if not check_dependencies():
        return 1

    # Determine provider and construct model name
    _, detected_provider = check_api_key()
    provider = args.provider or detected_provider or "perplexity"

    # Prepend appropriate provider prefix to model name
    model = args.model
    if not model.startswith("perplexity/") and not model.startswith("openrouter/"):
        if provider == "openrouter":
            model = f"openrouter/perplexity/{model}"
        else:
            model = f"perplexity/{model}"

    # Perform the search
    result = search_with_perplexity(
        query=args.query,
        model=model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        verbose=args.verbose,
        provider=provider
    )

    # Handle results
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    # Print answer
    print("\n" + "="*80)
    print("ANSWER")
    print("="*80)
    print(result["answer"])
    print("="*80)

    # Print usage stats if verbose
    if args.verbose:
        print(f"\nUsage:", file=sys.stderr)
        print(f"  Prompt tokens: {result['usage']['prompt_tokens']}", file=sys.stderr)
        print(f"  Completion tokens: {result['usage']['completion_tokens']}", file=sys.stderr)
        print(f"  Total tokens: {result['usage']['total_tokens']}", file=sys.stderr)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✓ Results saved to {args.output}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
