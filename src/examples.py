"""Example usage of the LLM with market data context. This runs separately from the mcp server"""

import sys
import os

if not os.environ.get("DEEPSEEK_API_KEY"):
    print("⚠️  DEEPSEEK_API_KEY not set. Please set it in your .env file.")
    sys.exit(1)

from using_external_llm import analyze_market, narrate_market_with_instructions


def example_multi_model():
    """Compare responses from different models."""
    print("\n" + "="*60)
    print("Multi-Model Comparison")
    print("="*60)
    
    question = "Compare current S&P 500 (SPX) and Russell 2000 (IWM) performance."
    print(f"Question: {question}\n")
    
    for model in ["deepseek-chat"]:
        print(f"\n[Model: {model}]")
        try:
            response = analyze_market(question, model=model, temperature=0.1)
            print(response[:500] + "..." if len(response) > 500 else response)
        except Exception as e:
            print(f"Error: {e}")


def generate_narrative():
    """Generate market narrative with instructions."""
    try:
        narrative = narrate_market_with_instructions()
        print(narrative)
        print("-" * 60)
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    generate_narrative()
