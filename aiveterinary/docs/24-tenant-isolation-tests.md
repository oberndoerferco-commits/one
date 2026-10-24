# Tenant isolation tests

Status: owner-accounts database covered by an automated suite (green,
23 Oct 2026). Clinic tenants have no database yet; their tests are a plan
(below). This suite does not replace the external pen test or the DPIA
(`05-security-model.md` §9); it is the "cross-tenant isolation test suite"
item of that gate, as far as code exists.

## What is tested

`site/supabase/schema.sql` (owner accounts, `10-owner-accounts.md`) is loaded
**unchanged** into a throwaway PostgreSQL cluster with a small Supabase shim,
then `site/supabase/tests/isolation.sql` runs 76 checks. Each prints
`ok - …`; the first failure stops the run with `FAIL - …` and a non-zero exit.

| Area | Checks |
|---|---|
| Structural sweep (every table in `public`) | RLS enabled; table is on the suite's coverage list, so a new table fails the run until tests are added for it; has at least one policy; every policy uses `auth.uid()` in USING and WITH CHECK; views must be `security_invoker`; every SECURITY DEFINER function pins `search_path` and is not executable by `anon`; `anon`/`authenticated` cannot read `auth.users`. FORCE RLS is reported as info only: it affects only the table owner, and no API role owns tables. |
| User B against user A, `passports` and `profiles` | SELECT (all rows, by id, by user_id) sees only own rows; UPDATE and DELETE of A's rows affect 0 rows; unfiltered UPDATE touches only own rows; INSERT with A's `user_id` refused; INSERT for a non-existent user refused; moving own row to A (`user_id` change) refused; upsert onto A's row refused; B reusing a passport id that A also has creates B's own row and leaves A's alone; no read or delete on `auth.users`; trigger function not callable as RPC. |
| `anon` | Sees no rows; UPDATE/DELETE affect 0 rows; cannot INSERT (for A or ownerless); cannot call `delete_my_account()`; cannot read `auth.users`. |
| User A afterwards | Sees exactly own rows, unchanged by B (name, microchip, profile flag), no planted rows; can still update own rows (policies are not simply deny-all). |
| `delete_my_account()` (SECURITY DEFINER) | Deletes only the caller (C) and cascades C's passports and profile; A and B untouched; a token without `sub` deletes nothing. |

The suite was checked against deliberately broken copies of the schema
(`SCHEMA_FILE=…`): `using (true)`, RLS off on one table, `auth.uid() is not null`
instead of an owner match, a definer function that deletes everyone when
`uid` is null, and the old global passport key. Each one fails the run.

Share links, reminders and storage buckets do not exist in the schema yet, so
there is nothing to test; see "When the schema grows".

## Bugs found and fixed in schema.sql

1. **`anon` could call `delete_my_account()`.** The schema revoked EXECUTE from
   `PUBLIC` only, but Supabase's default privileges grant EXECUTE on new
   functions in `public` to `anon` explicitly, so the revoke did not remove
   it. Harmless today (with no user, `auth.uid()` is null and nothing is
   deleted), but it was not the intended rule and would matter for a future
   definer function. Fix: `revoke all … from public, anon`.
2. **Passport ids were a global primary key.** Ids are generated in the browser
   (`Math.random` + time, not secret) and travel inside backup files. Two
   accounts holding the same id (a backup imported by a second family member,
   a pet handed to a new owner) meant the second user's upsert failed with an
   RLS error forever, and anyone who knew an id could pre-claim it to block
   the owner's sync and could tell whether an id existed. No data leaked
   across accounts, but one account could affect another. Fix: primary key
   `(user_id, id)`; the separate `user_id` index is dropped because the key
   covers it. The site's `upsert(rows)` sends `user_id` in every row and relies
   on the primary key as conflict target, so no client change is needed.
   No Supabase project exists yet; if one had already run the old schema, the
   key would need an explicit `alter table` migration.

## Hardening ideas (not done, not bugs under the API threat model)

- Add `to authenticated` to both policies, so a token with role `anon` never
  matches even if it somehow carried a `sub`.
- `revoke truncate, references, trigger on all tables in schema public from anon, authenticated;`
  TRUNCATE ignores RLS. PostgREST never issues it, so it is not reachable today.
- Put definer functions in a schema PostgREST does not expose when more appear.

## The Supabase shim, and what it does not cover

`site/supabase/tests/supabase_shim.sql` is an approximation of a fresh
Supabase project, enough for RLS:

- roles `anon`, `authenticated` (no BYPASSRLS) and `service_role` (BYPASSRLS);
- `auth.users` (id, email, role, created_at only);
- `auth.uid()`, `auth.role()`, `auth.jwt()` defined as in Supabase: they read
  the `request.jwt.claims` setting (and the legacy `request.jwt.claim.*`);
- Supabase's default grants: ALL on new tables, sequences and functions in
  `public` for the three API roles. Policies, not GRANTs, are the real control.

Tests become a user the way PostgREST does after verifying a JWT: `SET ROLE`
plus the claims setting.

Not covered (needs the real stack or the pen test):

- **GoTrue / JWT**: magic-link login, token signing and verification, expiry,
  refresh, and that `sub` cannot be forged. The suite trusts the claims.
- **PostgREST**: request parsing, which operations are exposed, role
  switching from the JWT `role` claim, `Prefer` headers, embedded resources.
  The suite runs plain SQL that corresponds to what PostgREST would issue.
- **Storage** buckets and `storage.objects` policies (photos are inline JSON
  today), **Realtime**, **Edge Functions**, the dashboard.
- Supabase's exact role setup (`postgres` is not a superuser there; owner is
  `supabase_admin` for system schemas) and the full `auth.users` columns.
- Raw-SQL-only powers (changing one's own claims, TRUNCATE): not API
  reachable, so not modelled as attacks.

After the Supabase project exists, repeat the B-against-A cases once through
the real API with two magic-link accounts (supabase-js in a browser console
is enough) and keep the result with the pen-test notes.

## How to run

Needs PostgreSQL 15+ server binaries (`initdb`, `pg_ctl`) and `psql`. Nothing
is installed or left behind; the cluster listens on a Unix socket only.

```sh
cd aiveterinary/site
npm run test:db          # = bash supabase/tests/run.sh
```

Options (environment): `PG_BIN` (directory with initdb/pg_ctl; default
`pg_config --bindir`, else the newest `/usr/lib/postgresql/*/bin`),
`PGTEST_DIR` (work directory; default a fresh temp dir), `PGTEST_PORT`
(socket port number, default 54329), `PGTEST_KEEP=1` (keep the cluster
directory), `SCHEMA_FILE` (test another schema copy), `PGTEST_OS_USER` (when
run as root, the unprivileged user that runs postgres; default `nobody`, and
`PGTEST_DIR` must be reachable by that user).

It is not part of `npm run build` and not in CI, because CI runners may lack
PostgreSQL server binaries. Run it by hand whenever `schema.sql` changes.

## Results

23 Oct 2026, PostgreSQL 16.13: schema.sql loaded without errors before and
after the fixes. Before the fixes the suite failed on "anon cannot execute
security definer delete_my_account" and "B: upsert of an id A also uses
creates B's own row". After the fixes: **76 checks passed, 0 failed** (two
info notes: FORCE RLS not set on `passports` and `profiles`, by design).

## When the schema grows

Add the table to `tests.covered` in `isolation.sql` (the sweep fails until
you do) and repeat the B-against-A block for it. For the planned features:

- **Share link for the vet**: no `using (true)` policy and no public table.
  Use an unguessable token (≥128 bits), stored hashed, with expiry and
  revocation, read through one SECURITY DEFINER function that returns only
  the shared passport. Tests: wrong/expired/revoked token returns nothing; a
  valid token for A's pet never returns A's other pets or B's data; the
  function cannot list tokens; `anon` can call it but cannot read the token
  table; B cannot create a token for A's passport.
- **Reminders**: a scheduled job with `service_role` sends them; tests that
  `anon`/`authenticated` cannot read other users' email or reminder rows.
- **Photos in Storage**: bucket private, object path prefixed with
  `auth.uid()`, `storage.objects` policies tested in a real project.

## Clinic tenants (vet side): plan, no code yet

There is no SQL for clinics. The vet tool (`app/`) keeps data on the device;
the server design is in `02-architecture.md` §3 and §5: tenant boundary
`organization`, `membership(user, org, role)`, RLS on `organization_id`
"enforced twice" (service layer and Postgres), and `05-security-model.md`
names "automated cross-tenant tests" as a control. When that schema is
written, the same harness (shim, `run.sh`, sweep) applies, with these tests:

1. **Sweep**: every table carrying clinical or client data has RLS and an
   `organization_id` (directly or through a parent with a checked foreign key);
   the sweep fails on any table without one. The service connects as a role
   without BYPASSRLS; FORCE RLS on all tenant tables so the owner role cannot
   skip it by mistake.
2. **Tenant context**: the org comes from a membership lookup on
   `auth.uid()`, not from a client-supplied header or claim. Test: a user of
   clinic X who sets `organization_id` = Y in a request sees and changes
   nothing in Y.
3. **Two clinics, X and Y**, each with a vet, a nurse, reception and an admin.
   Every role of X: SELECT/UPDATE/DELETE on Y's clients, patients,
   consultations, note inputs, clinical records, documents, document
   versions, templates, audit events, AI generations and approvals returns
   0 rows; INSERT with Y's `organization_id` is refused.
4. **Foreign-key smuggling**: X cannot create a consultation on Y's patient, a
   document on Y's consultation, an approval on Y's record version, or a
   template reference into Y, even with a correct id. Composite foreign keys
   `(organization_id, id)` make this structural; test it anyway.
5. **Roles within a clinic** (the matrix in `02-architecture.md` §5):
   reception cannot write notes or approve; nurse cannot approve the clinical
   record; only a verified vet membership can; audit log readable per the
   matrix; `note_input`, approved `document_version` and `audit_event`
   reject UPDATE and DELETE for every role (append-only).
6. **Membership changes**: a removed member loses access at once; a user in
   both X and Y sees each clinic's data only under that clinic's context and
   never a union in one query.
7. **Owner access** (`access_grant`, later): an owner sees only the
   documents granted to them, only once approved, and nothing of other
   owners in the same clinic.
8. **Indirect paths**: search (FTS) and any vector search, views,
   SECURITY DEFINER functions, the job queue (pg-boss jobs carry
   `organization_id` and workers re-check it), signed file URLs scoped to the
   org prefix, exports, analytics (aggregates only, no cross-clinic rows),
   and logs free of clinical text.
9. **Service layer**: the same cases through the API with tokens for users of
   X and Y, so a missing `WHERE` in code and a missing policy are each caught
   by the other layer.
