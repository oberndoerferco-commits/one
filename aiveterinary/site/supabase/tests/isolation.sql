-- Cross-tenant isolation tests for site/supabase/schema.sql.
-- Run by run.sh against a throwaway cluster: shim -> schema.sql -> this file.
-- Every check prints "NOTICE: ok - <label>"; the first failure raises
-- "FAIL - <label>" and psql (ON_ERROR_STOP) exits non-zero.
--
-- Threat model: what a client can do through the Supabase API (PostgREST
-- table SELECT/INSERT/UPDATE/DELETE/upsert and RPC) as `anon` or as an
-- `authenticated` user whose JWT `sub` is their own id. Raw-SQL-only powers
-- (SET of the claims GUC, TRUNCATE, …) are not reachable over the API and are
-- not modelled as attacks here; see docs/24-tenant-isolation-tests.md.

\set ON_ERROR_STOP 1
set client_min_messages = notice;

-- ---------------------------------------------------------------- helpers
create schema tests;

create function tests.ok(cond boolean, label text) returns void language plpgsql as $$
begin
  if coalesce(cond, false) then raise notice 'ok - %', label;
  else raise exception 'FAIL - %', label; end if;
end $$;

-- Expect `stmt` to fail with one of `states` (SQLSTATE codes).
create function tests.throws(stmt text, label text, states text[] default array['42501']) returns void
language plpgsql as $$
declare st text; msg text;
begin
  begin
    execute stmt;
  exception when others then st := sqlstate; msg := sqlerrm;
  end;
  if st is null then raise exception 'FAIL - % (statement succeeded: %)', label, stmt; end if;
  if not (st = any(states)) then raise exception 'FAIL - % (expected % got %: %)', label, states, st, msg; end if;
  raise notice 'ok - % [%]', label, st;
end $$;

-- Expect `stmt` to succeed.
create function tests.lives(stmt text, label text) returns void language plpgsql as $$
begin
  begin execute stmt;
  exception when others then raise exception 'FAIL - % (% : %)', label, sqlstate, sqlerrm;
  end;
  raise notice 'ok - %', label;
end $$;

-- Rows affected by a DML statement.
create function tests.affected(stmt text) returns bigint language plpgsql as $$
declare n bigint;
begin execute stmt; get diagnostics n = row_count; return n; end $$;

-- Become a user the way PostgREST does after verifying a JWT.
create function tests.login(uid uuid) returns void language plpgsql as $$
begin
  perform set_config('request.jwt.claims', json_build_object('sub', uid, 'role', 'authenticated')::text, false);
  perform set_config('role', 'authenticated', false);
end $$;

create function tests.as_anon() returns void language plpgsql as $$
begin
  perform set_config('request.jwt.claims', '{"role":"anon"}', false);
  perform set_config('role', 'anon', false);
end $$;

grant usage on schema tests to anon, authenticated;

-- Users. A and B are the two tenants; C exists to exercise account deletion.
\set A '''aaaaaaaa-0000-4000-8000-00000000000a'''
\set B '''bbbbbbbb-0000-4000-8000-00000000000b'''
\set C '''cccccccc-0000-4000-8000-00000000000c'''
insert into auth.users (id, email, role) values
  (:A, 'a@example.test', 'authenticated'),
  (:B, 'b@example.test', 'authenticated'),
  (:C, 'c@example.test', 'authenticated');

-- ------------------------------------------------- 1. structural sweep
-- Tables this suite covers. A new table in public fails the sweep until a
-- test for it is added here.
create table tests.covered (relname text primary key);
insert into tests.covered values ('profiles'), ('passports');

do $$
declare r record; n int;
begin
  for r in
    select c.oid, c.relname, c.relrowsecurity, c.relforcerowsecurity
    from pg_class c join pg_namespace s on s.oid = c.relnamespace
    where s.nspname = 'public' and c.relkind in ('r', 'p')
    order by c.relname
  loop
    perform tests.ok(r.relrowsecurity, format('RLS enabled on public.%I', r.relname));
    perform tests.ok(exists (select 1 from tests.covered where relname = r.relname),
                     format('public.%I is covered by this suite', r.relname));
    select count(*) into n from pg_policies where schemaname = 'public' and tablename = r.relname;
    perform tests.ok(n > 0, format('public.%I has at least one policy', r.relname));
    -- FORCE only matters for the table owner; no API role owns tables.
    if not r.relforcerowsecurity then
      raise notice 'info - public.% has RLS but not FORCE RLS (owner bypasses; owner is not an API role)', r.relname;
    end if;
  end loop;

  -- Every policy must be tied to the caller's identity.
  for r in select tablename, policyname, qual, with_check from pg_policies where schemaname = 'public' loop
    perform tests.ok(coalesce(r.qual, '') like '%auth.uid()%' and coalesce(r.with_check, r.qual, '') like '%auth.uid()%',
                     format('policy %s on %s uses auth.uid() in USING and WITH CHECK', r.policyname, r.tablename));
  end loop;

  -- Views run with the owner's rights unless security_invoker is set (PG15+).
  for r in
    select c.relname, c.relkind, c.reloptions from pg_class c join pg_namespace s on s.oid = c.relnamespace
    where s.nspname = 'public' and c.relkind in ('v', 'm')
  loop
    perform tests.ok(r.relkind = 'v' and 'security_invoker=true' = any(coalesce(r.reloptions, '{}')),
                     format('view public.%I is security_invoker', r.relname));
  end loop;

  -- SECURITY DEFINER functions: pinned search_path, not callable by anon.
  for r in
    select p.oid, p.proname, p.proconfig from pg_proc p join pg_namespace s on s.oid = p.pronamespace
    where s.nspname = 'public' and p.prosecdef
  loop
    perform tests.ok(exists (select 1 from unnest(coalesce(r.proconfig, '{}')) x where x like 'search_path=%'),
                     format('security definer public.%I pins search_path', r.proname));
    perform tests.ok(not has_function_privilege('anon', r.oid, 'execute'),
                     format('anon cannot execute security definer public.%I', r.proname));
  end loop;
end $$;

-- API roles must not read the auth schema's user table.
select tests.ok(not has_table_privilege('anon', 'auth.users', 'select'), 'anon has no SELECT on auth.users');
select tests.ok(not has_table_privilege('authenticated', 'auth.users', 'select'), 'authenticated has no SELECT on auth.users');

-- ------------------------------------------------- 2. seed as A, B, C
select tests.login(:A);
select tests.lives($$insert into public.profiles (user_id, reminders_enabled) values (auth.uid(), true)$$, 'A creates own profile');
select tests.lives($$insert into public.passports (id, user_id, animal) values
  ('pet-a1', auth.uid(), '{"name":"Rex","microchip":"380260000000001"}'),
  ('pet-a2', auth.uid(), '{"name":"Mia"}')$$, 'A creates two passports');
reset role;

select tests.login(:B);
select tests.lives($$insert into public.profiles (user_id) values (auth.uid())$$, 'B creates own profile');
select tests.lives($$insert into public.passports (id, user_id, animal) values ('pet-b1', auth.uid(), '{"name":"Bello"}')$$, 'B creates a passport');
reset role;

select tests.login(:C);
select tests.lives($$insert into public.profiles (user_id) values (auth.uid())$$, 'C creates own profile');
select tests.lives($$insert into public.passports (id, user_id, animal) values ('pet-c1', auth.uid(), '{"name":"Tom"}')$$, 'C creates a passport');
reset role;

-- Non-vacuity: the rows really exist (owner/superuser view).
select tests.ok((select count(*) from public.passports) = 4, 'seed: 4 passports exist in total');
select tests.ok((select count(*) from public.profiles) = 3, 'seed: 3 profiles exist in total');

-- ------------------------------------------------- 3. B attacks A
select tests.login(:B);
select tests.ok(auth.uid() = :B::uuid, 'B: auth.uid() is B');

-- SELECT
select tests.ok((select count(*) from public.passports) = 1, 'B: SELECT passports returns only own row');
select tests.ok(not exists (select 1 from public.passports where user_id <> auth.uid()), 'B: no foreign user_id visible in passports');
select tests.ok(not exists (select 1 from public.passports where id = 'pet-a1'), 'B: cannot SELECT A''s passport by id');
select tests.ok((select count(*) from public.profiles) = 1, 'B: SELECT profiles returns only own row');
select tests.ok(not exists (select 1 from public.profiles where user_id = :A), 'B: cannot SELECT A''s profile');

-- UPDATE
select tests.ok(tests.affected($$update public.passports set animal = '{"name":"pwned"}' where id = 'pet-a1'$$) = 0, 'B: UPDATE A''s passport by id affects 0 rows');
select tests.ok(tests.affected(format($$update public.passports set animal = '{"name":"pwned"}' where user_id = %L$$, :A)) = 0, 'B: UPDATE A''s passports by user_id affects 0 rows');
select tests.ok(tests.affected($$update public.passports set animal = animal || '{"touched":true}'$$) = 1, 'B: unfiltered UPDATE passports touches only own row');
select tests.ok(tests.affected(format($$update public.profiles set reminders_enabled = false where user_id = %L$$, :A)) = 0, 'B: UPDATE A''s profile affects 0 rows');
select tests.ok(tests.affected($$update public.profiles set reminders_enabled = true$$) = 1, 'B: unfiltered UPDATE profiles touches only own row');

-- DELETE
select tests.ok(tests.affected($$delete from public.passports where id = 'pet-a1'$$) = 0, 'B: DELETE A''s passport affects 0 rows');
select tests.ok(tests.affected(format($$delete from public.passports where user_id = %L$$, :A)) = 0, 'B: DELETE A''s passports by user_id affects 0 rows');
select tests.ok(tests.affected(format($$delete from public.profiles where user_id = %L$$, :A)) = 0, 'B: DELETE A''s profile affects 0 rows');

-- INSERT rows owned by someone else
select tests.throws(format($$insert into public.passports (id, user_id, animal) values ('planted', %L, '{}')$$, :A), 'B: cannot INSERT a passport owned by A');
select tests.throws(format($$insert into public.profiles (user_id) values (%L)$$, :A), 'B: cannot INSERT a profile for A');
select tests.throws($$insert into public.passports (id, user_id, animal) values ('ghost', 'dddddddd-0000-4000-8000-00000000000d', '{}')$$, 'B: cannot INSERT a passport for a non-existent user');

-- Re-parenting own rows (escalation via user_id / the auth.users foreign key)
select tests.throws(format($$update public.passports set user_id = %L where id = 'pet-b1'$$, :A), 'B: cannot move own passport to A');
select tests.throws(format($$update public.profiles set user_id = %L$$, :A), 'B: cannot re-key own profile to A');

-- Upsert (what supabase-js .upsert() sends) aimed at A's row
select tests.throws(format($$insert into public.passports (id, user_id, animal) values ('pet-a1', %L, '{"name":"pwned"}')
  on conflict on constraint passports_pkey do update set animal = excluded.animal$$, :A), 'B: upsert onto A''s passport with A''s user_id is refused');

-- Passport ids come from the browser (and from shared backup files), so two
-- users can hold the same id. B using an id that A already has must neither
-- touch A's row nor fail (a failure would let B block A's sync and would
-- reveal that the id exists).
select tests.lives($$insert into public.passports (id, user_id, animal) values ('pet-a1', auth.uid(), '{"name":"B copy"}')
  on conflict on constraint passports_pkey do update set animal = excluded.animal$$, 'B: upsert of an id A also uses creates B''s own row');
select tests.ok((select count(*) from public.passports where id = 'pet-a1') = 1, 'B: sees exactly one pet-a1 (its own)');
select tests.ok((select animal->>'name' from public.passports where id = 'pet-a1') = 'B copy', 'B: its pet-a1 is B''s copy');

-- auth schema
select tests.throws($$select * from auth.users$$, 'B: cannot read auth.users');
select tests.throws($$delete from auth.users where id <> auth.uid()$$, 'B: cannot delete from auth.users directly');

-- RPC that is not meant for clients
select tests.throws($$select public.touch_updated_at()$$, 'B: trigger function cannot be called as RPC', array['0A000','42501']);
reset role;

-- ------------------------------------------------- 4. anon
select tests.as_anon();
select tests.ok(auth.uid() is null, 'anon: auth.uid() is null');
select tests.ok((select count(*) from public.passports) = 0, 'anon: SELECT passports returns nothing');
select tests.ok((select count(*) from public.profiles) = 0, 'anon: SELECT profiles returns nothing');
select tests.ok(tests.affected($$update public.passports set animal = '{}'$$) = 0, 'anon: UPDATE passports affects 0 rows');
select tests.ok(tests.affected($$delete from public.passports$$) = 0, 'anon: DELETE passports affects 0 rows');
select tests.ok(tests.affected($$delete from public.profiles$$) = 0, 'anon: DELETE profiles affects 0 rows');
select tests.throws(format($$insert into public.passports (id, user_id, animal) values ('anon-plant', %L, '{}')$$, :A), 'anon: cannot INSERT a passport for A');
select tests.throws($$insert into public.passports (id, user_id, animal) values ('anon-null', null, '{}')$$, 'anon: cannot INSERT an ownerless passport', array['42501','23502']);
select tests.throws(format($$insert into public.profiles (user_id) values (%L)$$, :A), 'anon: cannot INSERT a profile for A');
select tests.throws($$select public.delete_my_account()$$, 'anon: cannot call delete_my_account()');
select tests.throws($$select * from auth.users$$, 'anon: cannot read auth.users');
reset role;

-- ------------------------------------------------- 5. A sees only own, unharmed rows
select tests.login(:A);
select tests.ok((select count(*) from public.passports) = 2, 'A: sees exactly own 2 passports');
select tests.ok(not exists (select 1 from public.passports where user_id <> auth.uid()), 'A: no foreign rows visible');
select tests.ok((select animal->>'name' from public.passports where id = 'pet-a1') = 'Rex', 'A: pet-a1 unchanged by B''s attempts');
select tests.ok((select animal->>'microchip' from public.passports where id = 'pet-a1') = '380260000000001', 'A: pet-a1 microchip intact');
select tests.ok(not exists (select 1 from public.passports where id = 'planted'), 'A: no rows planted by B');
select tests.ok((select reminders_enabled from public.profiles) is true, 'A: profile unchanged by B');
select tests.ok((select count(*) from public.profiles) = 1, 'A: sees exactly own profile');
-- Own-row operations still work (the policies are not simply deny-all).
select tests.ok(tests.affected($$update public.passports set animal = animal || '{"weight":31}' where id = 'pet-a1'$$) = 1, 'A: can update own passport');
reset role;

-- ------------------------------------------------- 6. SECURITY DEFINER delete_my_account()
select tests.login(:C);
select tests.lives($$select public.delete_my_account()$$, 'C: delete_my_account() runs');
select tests.ok((select count(*) from public.passports) = 0, 'C: own passports gone after deletion');
reset role;
select tests.ok(not exists (select 1 from auth.users where id = :C), 'C deleted from auth.users');
select tests.ok(not exists (select 1 from public.passports where user_id = :C), 'C passports cascaded away');
select tests.ok(not exists (select 1 from public.profiles where user_id = :C), 'C profile cascaded away');
select tests.ok((select count(*) from auth.users where id in (:A, :B)) = 2, 'delete_my_account(): A and B still exist');
select tests.ok((select count(*) from public.passports where user_id = :A) = 2, 'delete_my_account(): A''s passports intact');
select tests.ok((select count(*) from public.passports where user_id = :B) = 2, 'delete_my_account(): B''s passports intact');
select tests.ok((select count(*) from public.profiles) = 2, 'delete_my_account(): A''s and B''s profiles intact');

-- With no identity, the definer function must delete nothing even if called.
set request.jwt.claims = '{"role":"authenticated"}';
set role authenticated;
select tests.lives($$select public.delete_my_account()$$, 'no-sub token: delete_my_account() is a no-op call');
reset role;
select tests.ok((select count(*) from auth.users) = 2, 'no-sub token: no user deleted');

\echo 'isolation suite finished'
