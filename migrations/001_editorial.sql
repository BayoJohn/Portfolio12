begin;

create table public.editorial_categories (
  id uuid primary key default gen_random_uuid(),
  name text not null unique check (char_length(name) between 1 and 80),
  section text not null check (section in ('news', 'cybersecurity', 'ai', 'gadgets', 'software', 'academy'))
);

insert into public.editorial_categories (name, section) values
  ('Tech News', 'news'), ('Cybersecurity', 'cybersecurity'), ('Artificial Intelligence', 'ai'),
  ('Gadgets & Reviews', 'gadgets'), ('Software', 'software'), ('Tech Academy', 'academy');

create table public.editorial_articles (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$' and char_length(slug) <= 100),
  collection text not null check (collection in ('blog', 'academy', 'reviews')),
  title text not null check (char_length(title) between 1 and 180),
  summary text not null check (char_length(summary) between 1 and 500),
  body text not null check (char_length(body) between 1 and 150000),
  author text not null check (char_length(author) between 1 and 120),
  seo_description text not null default '' check (char_length(seo_description) <= 320),
  tags text[] not null default '{}',
  category_id uuid not null references public.editorial_categories(id) on delete restrict,
  article_type text not null default '' check (article_type in
    ('', 'reporting', 'news-summary', 'commentary', 'security-update', 'review', 'tutorial')),
  source_url text not null default '',
  image_key uuid unique,
  image_alt text not null default '',
  image_caption text not null default '',
  image_credit text not null default '',
  status text not null default 'draft' check (status in ('draft', 'review', 'published')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  published_at timestamptz,
  constraint published_has_date check (status <> 'published' or published_at is not null),
  constraint cover_has_alt check (image_key is null or length(trim(image_alt)) > 0)
);

create index editorial_publication_index on public.editorial_articles (published_at desc) where status = 'published';
create index editorial_category_index on public.editorial_articles (category_id);

create function public.editorial_article_lifecycle() returns trigger
language plpgsql set search_path = ''
as $$
begin
  if tg_op = 'INSERT' then
    if new.status <> 'draft' then raise exception 'New articles must start in draft'; end if;
    new.published_at := null;
  else
    if old.published_at is not null and (new.slug, new.collection) <> (old.slug, old.collection) then
      raise exception 'Published article URLs are permanent';
    end if;
    if new.status <> old.status and (old.status, new.status) not in
       (('draft', 'review'), ('review', 'draft'), ('review', 'published'), ('published', 'draft')) then
      raise exception 'Invalid publishing transition';
    end if;
    new.published_at := old.published_at;
    if new.status = 'published' and new.published_at is null then new.published_at := now(); end if;
    new.updated_at := clock_timestamp();
  end if;
  return new;
end;
$$;

create trigger editorial_article_lifecycle before insert or update on public.editorial_articles
for each row execute function public.editorial_article_lifecycle();

create table public.editorial_sessions (
  digest text primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  access_token text not null,
  expires_at timestamptz not null
);
create index editorial_session_expiry on public.editorial_sessions (expires_at);

alter table public.editorial_categories enable row level security;
alter table public.editorial_articles enable row level security;
alter table public.editorial_sessions enable row level security;
revoke all on public.editorial_categories, public.editorial_articles, public.editorial_sessions
  from public, anon, authenticated;
grant select, insert, update, delete on public.editorial_categories, public.editorial_articles,
  public.editorial_sessions to service_role;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('editorial-images', 'editorial-images', false, 2800000, array['image/webp']);

commit;
