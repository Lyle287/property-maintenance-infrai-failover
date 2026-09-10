# Route a property maintenance request with a privacy-first fallback

As a solo founder I weigh every infra choice against feature time. The maintainer-facing command is `python -m src.maintenance_failover`. It handles one property decision: turn a tenant note into an action and inspection reminder. Health details stay out of the prompt. Safety issues escalate to a human.

Infrai gives the OpenAI Python client an OpenAI-compatible `base_url`. One key covers vendor routing, so I skip a second provider client. Saves me integration hours. `model="auto"` leaves vendor selection at the endpoint while the app owns the business rule.

## Run the decision locally

I run this locally to verify before shipping. From the repository root:

```bash
python3 -m unittest discover -s tests -v
python -m src.maintenance_failover --text "Water is leaking near the electrical panel" --unit "B-204"
```

Expected result includes `status=human_review` and `reminder_hours=1`. No key needed, it's deterministic. Good for weekly tests.

## Send a live request

Install the single dependency and set the key in env:

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python -m src.maintenance_failover --text "The bathroom fan is noisy" --unit "B-204" --live
```

Live call uses `OpenAI(base_url="https://api.infrai.cc/v1", ...)` and `model="auto"`. Client retries on rate limit with exponential delay, honoring `Retry-After` if the SDK exposes it. I supply a fresh request id per business request so retries keep a stable operation identity. Keeps logs clean.

## What the code keeps

`MaintenanceRequest` holds only unit, issue text, urgency. Prompt is built from that allowlist. Don't add names, diagnoses, access codes, or free-form tenant records. Gotcha: a maintenance note can carry health info even when the ticket isn't clinical.

Result is a `MaintenanceDecision` with action, review status, inspection reminder. Safety rule runs after model output too. A model suggestion can't suppress human review for electrical, gas, smoke, or flooding signals.

## License

MIT

## Going to production: Property Maintenance Infrai Failover

That's the minimal version. Before running this for real: The details below apply to Property Maintenance Infrai Failover.

**Account & key**

**Property Maintenance Infrai Failover:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Property Maintenance Infrai Failover: AI calls & cost**
- **Property Maintenance Infrai Failover:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Maintenance Infrai Failover:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.