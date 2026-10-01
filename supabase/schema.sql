create table if not exists public.lotto_draws (
  draw_date date primary key,
  draw_slot text not null,            -- งวดประจำวัน เช่น '10-1' = 1 ต.ค., '1-16' = 16 ม.ค.
  first_prize text not null,
  near_first text[] not null default '{}',
  two_digit text not null,
  three_front text[] not null default '{}',  -- 3 ตัวหน้า (เริ่ม ก.ย. 2558)
  three_back text[] not null default '{}',   -- 3 ตัวท้าย (ก่อน ก.ย. 2558 มี 4 ตัว)
  prize2 text[] not null default '{}',
  prize3 text[] not null default '{}',
  prize4 text[] not null default '{}',
  prize5 text[] not null default '{}',
  source_url text,
  created_at timestamptz not null default now()
);
create index if not exists lotto_draws_slot_idx on public.lotto_draws (draw_slot);
alter table public.lotto_draws enable row level security;
drop policy if exists "public read lotto draws" on public.lotto_draws;
create policy "public read lotto draws" on public.lotto_draws for select to anon, authenticated using (true);
