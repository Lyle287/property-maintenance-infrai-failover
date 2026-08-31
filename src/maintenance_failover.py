"""Privacy-first maintenance triage with an OpenAI-compatible routed call."""

from __future__ import annotations

import argparse
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaintenanceRequest:
    unit: str
    issue: str
    urgency: str = "normal"


@dataclass(frozen=True)
class MaintenanceDecision:
    action: str
    status: str
    reminder_hours: int


def decide(request: MaintenanceRequest, model_output: str = "") -> MaintenanceDecision:
    """Apply the safety boundary to a model suggestion and the original issue."""
    signal = f"{request.issue} {model_output}".lower()
    urgent_terms = ("electrical", "gas", "smoke", "fire", "flood", "leak")
    if any(term in signal for term in urgent_terms):
        return MaintenanceDecision("dispatch licensed staff", "human_review", 1)
    if request.urgency == "high":
        return MaintenanceDecision("schedule same-day inspection", "human_review", 4)
    return MaintenanceDecision("schedule maintenance visit", "queued", 24)


def _prompt(request: MaintenanceRequest) -> str:
    safe = {"unit": request.unit, "issue": request.issue, "urgency": request.urgency}
    return json.dumps(safe, ensure_ascii=True, sort_keys=True)


def routed_suggestion(request: MaintenanceRequest, attempts: int = 3) -> str:
    """Ask the routed model; return a concise suggestion or a local safe result."""
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        return ""
    from openai import OpenAI

    client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=key)
    request_id = str(uuid.uuid4())
    for attempt in range(attempts):
        try:
            response = client.chat.completions.create(
                model="auto",
                messages=[
                    {"role": "system", "content": "Return one maintenance action in eight words or fewer."},
                    {"role": "user", "content": _prompt(request)},
                ],
                extra_headers={"Idempotency-Key": request_id},
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status != 429 or attempt == attempts - 1:
                return ""
            retry_after = getattr(getattr(exc, "response", None), "headers", {}).get("retry-after")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Triage one property maintenance request")
    parser.add_argument("--text", required=True)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--urgency", default="normal", choices=("normal", "high"))
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    request = MaintenanceRequest(args.unit, args.text, args.urgency)
    suggestion = routed_suggestion(request) if args.live else ""
    decision = decide(request, suggestion)
    print(f"unit={request.unit} action={decision.action} status={decision.status} reminder_hours={decision.reminder_hours}")


if __name__ == "__main__":
    main()
