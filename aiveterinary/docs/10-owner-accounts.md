# Owner accounts — design and privacy

Status: designed and coded; waiting for a Supabase project (free, EU) and company
details. Not legal advice; have a lawyer read the public texts once before real
sign-ups.

## What accounts add

| Without account (today) | With account |
|---|---|
| Passport in the browser only | Passport saved to the owner's account, available on every device |
| Backup = manual file | Backup still available, plus automatic |
| Nothing for us to protect | Personal data we are responsible for |
| — | Later: expiry reminders, share link for the vet, pre-visit brief |

Local mode stays. Logging in is optional and the page says what changes.

## Data we store

| Data | Why | Optional? |
|---|---|---|
| Email address | login (magic link), account recovery, reminders if enabled | required |
| Passport content (animal identity, microchip, vaccinations, treatments, medications, conditions, visits, notes, photo) | the service itself | all fields optional except animal name |
| Owner contact fields inside the passport | the owner chooses to store them for printing | optional |
| Timestamps (created, updated, last login) | sync and security | automatic |
| Server logs (IP, user agent) for 30 days | security, abuse | automatic, at the provider |

Not stored: payment data, location, browsing behaviour, tracking identifiers.

## Legal basis and roles

- **Controller:** the company named in the privacy policy (to be filled in).
- **Processor:** Supabase (database and login), EU region Frankfurt; its DPA is
  part of its terms. Cloudflare (hosting, email routing). The newsletter
  provider, only for subscribers.
- **Legal basis:** Art. 6(1)(b) GDPR, performance of a contract: the user asks
  us to store their passport. Reminders: 6(1)(b) as well, switched on by the
  user. Newsletter: consent, separate opt-in.
- Animal data is personal data because it is linked to the owner; it is not a
  "special category". No DPIA or DPO required at this scale; we re-check when
  vets get access or the vet tool stores clinic records (then
  `05-security-model.md` applies).
- Minimum age 16.

## Security

- Login by email magic link; no passwords exist.
- TLS everywhere; encryption at rest at the provider.
- **Row-level security** in the database: a user can only read and write rows
  where `user_id = auth.uid()`. Enforced by Postgres, not by our JavaScript.
- The browser talks to Supabase with the public "anon" key, which can do
  nothing without a valid user session and the RLS rules.
- Photos are resized on the device to ≤ 320 px before upload.
- No admin backdoor: we do not read user passports. Support works with the
  user's own export.

## Rights, built in as buttons

| Right | How |
|---|---|
| Access / portability | **Export everything** → JSON file (same format as the local backup) |
| Rectification | the owner edits their passport |
| Erasure | **Delete my account** → all rows deleted immediately; provider backups expire within 30 days |
| Objection / restriction | reminders can be switched off; account can be deleted |
| Information | privacy policy, plain language |

## Retention

Account data: as long as the account exists. Deleted accounts: gone immediately,
provider backups expire ≤ 30 days. Accounts unused for 3 years: email warning,
then deletion after 60 days. Logs: 30 days.

## Breach procedure (internal)

1. Contain: revoke keys, disable affected function.
2. Assess within 24 h: what data, how many users, risk to them.
3. If risk to users: notify the supervisory authority within 72 h (Italy:
   Garante; Germany: the Land authority of the company's seat) and inform the
   affected users by email in plain language.
4. Write it down: what happened, when, what was done.

## Database shape

See `site/supabase/schema.sql`. One table `passports`: `id`, `user_id`,
`animal` (JSON, same shape as the local store), `updated_at`. One row per
animal. RLS: owner only. A `profiles` row per user holds reminder preferences.

## Sync rules

- Logged out: local storage, as today.
- On login: if the account is empty and local has animals, offer to upload them;
  if both have data, show both and let the user merge (keep both by default).
- While logged in: every save writes to the account (debounced) and keeps a
  local copy for offline use; last write wins per animal, by `updated_at`.
- Logout: local copy stays unless the user ticks "remove from this device".
