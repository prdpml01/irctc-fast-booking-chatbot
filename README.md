# IRCTC Fast Booking Chatbot

A speed-optimized, **compliance-first** booking assistant for preparing an IRCTC journey. It parses a request, reads cached schedule data, validates passenger input, and returns a ready-to-review booking plan.

> **Important:** This project does not bypass OTP, CAPTCHA, payment authentication, or IRCTC rate limits. Those steps remain under the user's control and must be completed on the official IRCTC booking page or through an authorized IRCTC partner/API.

## Optimized flow

```text
User request
  ├─ Parse and validate in parallel
  ├─ Read schedule cache (short TTL)
  ├─ Load encrypted passenger profile (no payment secrets)
  └─ Build booking plan
       ↓
Official IRCTC page/API → user verifies → OTP/CAPTCHA/payment → ticket confirmation
```

The one-second target applies to local request parsing, cache lookup, and booking-plan preparation—not to railway inventory, OTP, CAPTCHA, payment, or ticket issuance, which depend on external systems and user verification.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API documentation.

## Example

```bash
curl -X POST http://127.0.0.1:8000/booking/plan \\
  -H 'content-type: application/json' \\
  -d '{"request":"26 Oct Mumbai to Delhi, 2AC, 2 passengers"}'
```

## Production requirements

- Use an authorized IRCTC integration; do not scrape or automate around controls.
- Store passenger data encrypted, minimize retention, and never store CVV or OTP values.
- Add authentication, authorization, audit logs, rate limiting, consent, and idempotency keys.
- Treat cached availability as advisory and re-check it immediately before the user submits.
