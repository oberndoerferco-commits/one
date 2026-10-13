# AI Veterinary — to-do list

The living backlog. Ordered by what unblocks the most. "Me" = Claude working in
this repo; "You" = the owner of the project, for things that need a human,
an account or a signature. Everything here costs €0 unless marked.

## Done

- [x] Research: competitors, PIMS market, user complaints, costs (docs 01, 07, 08)
- [x] Architecture, MVP spec, UX, security model, brand, roadmap (docs 02–06, 09)
- [x] Website v1: home, animals section, 3 draft articles, vets page, research, about, newsletter, privacy draft
- [x] Digital pet passport, local-first, with backup/restore/print

## Now (me)

- [x] Site basics: sitemap, robots.txt, social preview image, build workflow
- [x] Owner accounts: privacy design (doc 10) + drafts of privacy policy, terms, processing register, breach procedure
- [x] Owner accounts: database schema with per-user isolation, email-link login, sync, export, delete
- [x] 10 more animal articles (drafts, awaiting vet review)
- [x] Vet tool core: clinical record schema, validators (nothing you didn't write), synthetic cases, offline test runner
- [x] Vet tool: extraction prompt + model adapter + demo on synthetic cases
- [x] Vet tool: one-screen browser workspace prototype (preview at /vets/workspace, synthetic cases)

## Next (me)

- [x] Italian and German site versions (home, about, vets; articles still EN)
- [x] Pre-visit brief for owners (/visit-brief, prefills from the passport)
- [ ] Vaccination-expiry reminders (needs accounts + email)
- [ ] Share-with-vet link for the passport (read-only, expiring)
- [ ] Public quality page for the vet tool
- [ ] Clinic letterhead + PDF export in the vet tool

## Needs you (cannot be done from the repo)

- [ ] **GitHub**: confirm the `oberndoerferco-commits` account is yours, or create one; merge branch `claude/modest-dirac-s1uvdm`
- [ ] **Cloudflare Pages**: connect the repo (root `aiveterinary/site`, build `npm run build`, output `dist`), add domain `aiveterinary.org`
- [ ] **GoDaddy**: point DNS at Cloudflare (nameservers) or add the CNAME; check `aiveterinary.com/.de/.it`; turn on 2FA
- [ ] **Newsletter**: free account (Buttondown / MailerLite / Brevo), paste form URL into `PUBLIC_NEWSLETTER_ACTION`
- [ ] **Supabase**: free project in EU (Frankfurt) for owner accounts; paste URL + anon key into site env vars; run `supabase/schema.sql`
- [ ] **Company details**: legal entity name, address, contact email for the privacy policy and terms (data controller)
- [ ] **Lawyer, one hour**: read the privacy policy and terms before real sign-ups (the only likely spend before the vet pilot)
- [ ] **Language**: Italian or German first
- [ ] **Vets**: 1–2 who will put their name on reviewed articles; 5 who will do the typing test
- [ ] **Owner questions**: the 10 questions your vets hear most (for articles)
- [ ] **Anthropic API key** when the vet tool should run on real model calls (free during development with synthetic cases; a few euros/month in testing)

## Later (needs money or partners)

- [ ] Penetration test and DPIA before any clinic puts real records in
- [ ] Provet / ezyVet partner programme applications
- [ ] Trademark registration
