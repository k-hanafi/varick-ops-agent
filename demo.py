"""CLI: reconcile one invoice and show the agent's step-by-step reasoning.

Usage: python demo.py INV-1042
"""

import sys

from dotenv import load_dotenv

load_dotenv()

from agents import Runner  # noqa: E402  (import after env is loaded)

from agent.ops_agent import ops_agent  # noqa: E402


def print_trace(result) -> None:
    print("\n--- agent trace ---")
    for item in result.new_items:
        kind = getattr(item, "type", "")
        if kind == "tool_call_item":
            raw = item.raw_item
            name = getattr(raw, "name", "?")
            args = getattr(raw, "arguments", "")
            print(f"  call  {name}{args}")
        elif kind == "tool_call_output_item":
            out = str(getattr(item, "output", ""))
            print(f"  ret   {out[:280]}{'...' if len(out) > 280 else ''}")


def main() -> None:
    invoice_id = sys.argv[1] if len(sys.argv) > 1 else "INV-1042"
    print(f"Reconciling {invoice_id}...")
    result = Runner.run_sync(
        ops_agent, f"Reconcile invoice {invoice_id} and decide whether to pay it."
    )
    print_trace(result)

    rec = result.final_output
    print("\n--- recommendation ---")
    print(f"  verdict:   {rec.verdict}")
    print("  reasons:")
    for reason in rec.reasons:
        print(f"    - {reason}")
    print(f"  citations: {', '.join(rec.citations)}")


if __name__ == "__main__":
    main()
