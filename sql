create table users (
  discord_id text primary key,
  points integer not null default 0,
  created_at timestamp with time zone default now()
);


create table quests (
  thread_id text primary key,
  channel_id text not null,
  tag text not null check (tag in ('obligatoire', 'journaliere')),
  points integer not null,
  images_required integer not null,
  created_at timestamp with time zone default now()
);


create table quest_claims (
  id bigserial primary key,
  discord_id text not null,
  thread_id text not null,
  claimed_at timestamp with time zone default now()
);

create index on quest_claims (discord_id, thread_id);
create index on quest_claims (claimed_at);

create or replace function increment_points(
  p_discord_id text,
  p_points integer
)
returns void
language plpgsql
as $$
begin
  insert into users (discord_id, points)
  values (p_discord_id, p_points)
  on conflict (discord_id)
  do update set points = users.points + p_points;
end;
$$;

alter table quests
add column reward_message text not null default '🎉 Quest completed! +{points} points';


-- Amazing work! You earned +{points} points for this quest.

-- Bravo {user}, vous avez terminé la quête {quest} et gagné +{points} points !