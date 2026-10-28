-- AI Veterinary — owner accounts schema
-- Run once in the Supabase SQL editor of a project in an EU region.
-- Login: enable "Email" provider with magic links in Authentication settings.

create table if not exists public.profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  reminders_enabled boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.passports (
  id text not null,                        -- same id as the local store (client-generated)
  user_id uuid not null references auth.users (id) on delete cascade,
  animal jsonb not null,                   -- full animal object, same shape as the browser store
  updated_at timestamptz not null default now(),
  -- Keyed per user: ids come from the browser and from backup files, so two
  -- owners can hold the same id. A global key would let one user's row block
  -- another user's sync and reveal that the id exists. The key also serves
  -- as the user_id index.
  primary key (user_id, id)
);

-- Row-level security: a user sees and changes only their own rows.
alter table public.profiles enable row level security;
alter table public.passports enable row level security;

create policy "profiles: own row" on public.profiles
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "passports: own rows" on public.passports
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Keep updated_at honest.
create or replace function public.touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists passports_touch on public.passports;
create trigger passports_touch before update on public.passports
  for each row execute function public.touch_updated_at();

-- Account deletion from the browser: deletes the auth user, which cascades to all rows.
create or replace function public.delete_my_account() returns void
language sql security definer set search_path = public as $$
  delete from auth.users where id = auth.uid();
$$;
-- Supabase's default privileges also grant EXECUTE on new public functions to
-- anon explicitly, so revoking from PUBLIC alone leaves anon able to call it.
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;
