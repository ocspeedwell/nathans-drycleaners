# Nathans Dry Cleaners: AI Concierge implementation

## Repository audit (21 November 2026)
The current site is a **standalone static HTML page** (`index.html`) with inline CSS, not a WordPress theme or PopularFX export. Do not overwrite a production WordPress installation with this repository without first establishing its deployment relationship.

The homepage already includes seven locations: Lagos, Abuja, Enugu, Port Harcourt, Asaba, Owerri and New Owerri. It currently routes general WhatsApp enquiries to a single number. Branch-specific telephone numbers, opening hours and approved service prices have not been supplied.

## Delivery approach
1. Preserve the existing static homepage and verify its hosting/deployment arrangement.
2. Build a reusable, accessible chat interface with branch selection, service selection and a human handoff. Until branch numbers are approved, use the existing central WhatsApp number and include the selected branch in the prefilled message.
3. Add a **server-side** AI endpoint with authentication/rate limiting, input validation, prompt-injection defenses, logging controls and a strictly controlled knowledge base. Never put API secrets in HTML or browser JavaScript.
4. Maintain structured branch data and approved price lists (service, unit, currency, effective date, availability, branch). The agent must never invent a price or guarantee cleaning outcomes.
5. Add consent-based lead capture, privacy notice, spam protection and customer-request tracking. Do not collect sensitive information unnecessarily.
6. Once WordPress access is confirmed, package the UI and admin controls as a separate WordPress plugin compatible with PopularFX, avoiding edits to the parent theme.

## Branches
- Lagos
- Abuja
- Enugu
- Port Harcourt
- Asaba
- Owerri
- New Owerri

## Data required before live AI quotations
- Confirmed branch WhatsApp and telephone contacts, opening hours, addresses and pickup zones
- Per-branch price lists and minimum order / delivery charges
- Booking confirmation workflow and escalation contacts
- Approved marketing offers and customer privacy policy

## Acceptance criteria
- Responsive, keyboard-accessible chat interface
- Branch-specific context persists throughout a session
- No made-up prices or promises
- Explicit distinction between a pickup **request** and a confirmed booking
- No exposure of AI credentials in client code
- Existing homepage continues working
