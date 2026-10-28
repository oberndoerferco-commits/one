# Record of processing activities (Art. 30 GDPR) — draft

Controller: [Company name], [address]. Contact: privacy@aiveterinary.org.
No DPO appointed (not required at this size and nature of processing).

| # | Activity | Data subjects | Data | Purpose | Legal basis | Recipients / processors | Transfers outside EEA | Retention | Security |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Website visits | visitors | none stored by us; provider access logs (IP, UA) | serve the site, security | legitimate interest | Cloudflare (hosting) | Cloudflare under SCCs/DPF as applicable | logs ≤ 30 days at provider | static site, TLS |
| 2 | Newsletter | subscribers | email, audience type (owner/vet), subscription date | send newsletter | consent | [newsletter provider] | depends on provider (choose EU) | until unsubscribe | provider security, unsubscribe link |
| 3 | Pet-passport accounts | account holders | email, login timestamps, passport content (animal identity, microchip, health records, notes, photo), optional owner/vet contacts | provide the passport service, sync between devices | contract (Art. 6(1)(b)) | Supabase (EU Frankfurt) | none | account lifetime; deleted on request immediately, backups ≤ 30 days; inactive 3 years → deletion after warning | magic-link login, TLS, encryption at rest, row-level security, no staff access |
| 4 | Vaccination reminders | account holders who opt in | email, vaccine dates | remind before expiry | contract; user-enabled | Supabase, email sending service (EU) | none | while enabled | as 3 |
| 5 | Support emails | people who write to us | email, message content | answer the request | legitimate interest | email provider | depends on provider | 12 months | mailbox access limited |

Not yet active (will be added before launch): veterinary documentation tool
(clinic records; separate register entries, DPA with each clinic, DPIA).

Breach procedure: `10-owner-accounts.md`. Review this register every 6 months
or when a new activity starts.
