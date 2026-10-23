-- Minimal Supabase shim for local RLS tests. APPROXIMATION, not Supabase.
--
-- Mirrors the parts of a fresh Supabase project that schema.sql and its RLS
-- policies depend on:
--   * roles anon / authenticated (NOLOGIN, no BYPASSRLS) and service_role (BYPASSRLS)
--   * schema auth with a cut-down auth.users table
--   * auth.uid() / auth.role() / auth.jwt(), defined the way Supabase defines
--     them: they read the JWT claims that PostgREST copies into the
--     request.jwt.claims GUC (and the legacy request.jwt.claim.* GUCs)
--   * Supabase's default grants: USAGE on public and ALL on new tables,
--     sequences and functions in public for anon, authenticated, service_role
--     (this is why RLS, not GRANTs, is the real access control on Supabase)
--
-- NOT mirrored: GoTrue (login, magic links, JWT signing/verification),
-- PostgREST (request parsing, role switching from the JWT `role` claim),
-- Storage buckets and storage.objects policies, Realtime, the full auth.users
-- column set, supabase_admin / the non-superuser `postgres` role, pg_graphql.
-- Here the tests become a user by `SET ROLE` + setting the claims GUC, which
-- is what PostgREST does after it has verified the JWT.

do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'anon') then create role anon nologin noinherit; end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then create role authenticated nologin noinherit; end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role') then create role service_role nologin noinherit bypassrls; end if;
end $$;

create schema if not exists auth;

create table if not exists auth.users (
  id uuid primary key,
  email text unique,
  role text,
  created_at timestamptz not null default now()
);

create or replace function auth.uid() returns uuid language sql stable as $$
  select coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
  )::uuid
$$;

create or replace function auth.role() returns text language sql stable as $$
  select coalesce(
    nullif(current_setting('request.jwt.claim.role', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
  )::text
$$;

create or replace function auth.jwt() returns jsonb language sql stable as $$
  select coalesce(
    nullif(current_setting('request.jwt.claim', true), ''),
    nullif(current_setting('request.jwt.claims', true), '')
  )::jsonb
$$;

-- Supabase: API roles may use the auth schema's functions but cannot read auth.users.
grant usage on schema auth to anon, authenticated, service_role;
grant execute on all functions in schema auth to anon, authenticated, service_role;
grant all on auth.users to service_role;

-- Supabase default privileges in public.
grant usage on schema public to anon, authenticated, service_role;
alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
alter default privileges in schema public grant all on sequences to anon, authenticated, service_role;
alter default privileges in schema public grant all on functions to anon, authenticated, service_role;
