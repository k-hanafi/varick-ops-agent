"""Run the agent over labeled cases and score it two ways:
- assertions: verdict match + required citations present (deterministic)
- LLM-as-judge: groundedness 1-5 (is each reason supported by policy?)
"""

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agents import Runner  # noqa: E402
from openai import OpenAI  # noqa: E402

from agent.ops_agent import ops_agent  # noqa: E402

MODEL = os.getenv("OPS_MODEL", "gpt-4o-mini")
CASES_PATH = Path(__file__).resolve().parent / "cases.json"
POLICY_DIR = Path(__file__).resolve().parent.parent / "policies"


def all_policies_text() -> str:
    return "\n\n".join(
        f"### {p.name}\n{p.read_text()}" for p in sorted(POLICY_DIR.glob("*.md"))
    )


def judge_groundedness(rec, policies_text: str) -> int:
    prompt = f"""Evaluate whether an accounts-payable agent's decision is grounded.

Company policies:
{policies_text}

Agent decision:
verdict: {rec.verdict}
reasons: {rec.reasons}
citations: {rec.citations}

Score groundedness from 1 to 5: are the reasons and verdict supported by the
policies above and internally consistent? 5 = fully supported, 1 = fabricated.
Respond with ONLY the integer."""
    client = OpenAI()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    match = re.search(r"[1-5]", resp.choices[0].message.content)
    return int(match.group()) if match else 0


def main() -> None:
    cases = json.loads(CASES_PATH.read_text())
    policies_text = all_policies_text()

    rows = []
    for case in cases:
        result = Runner.run_sync(
            ops_agent,
            f"Reconcile invoice {case['invoice_id']} and decide whether to pay it.",
        )
        rec = result.final_output
        verdict_ok = rec.verdict == case["expected_verdict"]
        cite_ok = all(c in rec.citations for c in case["must_cite"])
        grounded = judge_groundedness(rec, policies_text)
        rows.append(
            {
                "id": case["invoice_id"],
                "expected": case["expected_verdict"],
                "got": rec.verdict,
                "verdict_ok": verdict_ok,
                "cite_ok": cite_ok,
                "grounded": grounded,
            }
        )

    print(f"\n{'invoice':<10}{'expected':<10}{'got':<10}{'verdict':<9}{'cites':<7}{'grounded'}")
    print("-" * 56)
    for r in rows:
        print(
            f"{r['id']:<10}{r['expected']:<10}{r['got']:<10}"
            f"{('OK' if r['verdict_ok'] else 'X'):<9}"
            f"{('OK' if r['cite_ok'] else 'X'):<7}"
            f"{r['grounded']}/5"
        )

    n = len(rows)
    accuracy = sum(r["verdict_ok"] for r in rows) / n
    cite_rate = sum(r["cite_ok"] for r in rows) / n
    avg_grounded = sum(r["grounded"] for r in rows) / n
    print("-" * 56)
    print(f"verdict accuracy: {accuracy:.0%}   citation pass: {cite_rate:.0%}   "
          f"avg groundedness: {avg_grounded:.1f}/5")


if __name__ == "__main__":
    main()
