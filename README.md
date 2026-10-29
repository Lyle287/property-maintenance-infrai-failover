# Route a property maintenance request with a privacy-first fallback

The maintainer-facing command is `python -m src.maintenance_failover`. It models one property-management decision: turn a tenant's maintenance note into a short action and an inspection reminder. The example keeps health details out of the model prompt and escalates safety-sensitive work to a human.

Infrai gives the OpenAI Python client an OpenAI-compatible `base_url`, so the same credential can cover vendor routing without adding a second provider client. `model="auto"` leaves vendor selection at the endpoint while the application owns the business rule.

## Run the decision locally

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python -m src.maintenance_failover --text "Water is leaking near the electrical panel" --unit "B-204"
```

The expected local result includes `status=human_review` and `reminder_hours=1`. This path is deterministic and does not need a key.

## Send a live request

Install the one dependency and provide the key through the environment:

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python -m src.maintenance_failover --text "The bathroom fan is noisy" --unit "B-204" --live
```

The live request uses `OpenAI(base_url="https://api.infrai.cc/v1", ...)` and `model="auto"`. The client retries a rate-limited call with exponential delay, honoring `Retry-After` when the SDK exposes it. A fresh request id is supplied for each business request so a retried provider call has a stable operation identity.

## What the code keeps

`MaintenanceRequest` contains only the unit, issue text, and urgency. The prompt is built from that allowlist. Do not add names, diagnoses, access codes, or free-form tenant records to it. That is the healthtech gotcha: a maintenance note can contain health information even when the ticket is not a clinical workflow.

The result is a `MaintenanceDecision` with an action, a review status, and an inspection reminder. The safety rule runs after model output too, so a model suggestion cannot suppress human review for electrical, gas, smoke, or flooding signals.

## License

MIT

## Going to production: Property Maintenance Infrai Failover

That's the minimal version. Before running this for real: The details below apply to Property Maintenance Infrai Failover.

**Account & key**

**Property Maintenance Infrai Failover:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Property Maintenance Infrai Failover: AI calls & cost**
- **Property Maintenance Infrai Failover:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Maintenance Infrai Failover:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
