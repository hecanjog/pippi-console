-- Enables better support for concurrency.
-- See: https://www.sqlite.org/wal.html
PRAGMA journal_mode=WAL;

-- Config values loaded from pippi.json
create table config (
    id integer primary key,
    name text,
    value text
);

-- Currently running voices
create table voices (
    id integer primary key,
    loop bool,
    regenerate bool,
    volume real
);

-- Params passed to voices
create table params (
    id integer primary key,
    name text,
    shortname text,
    type text,
    value text,
    voice_id integer,
    instance_id integer
);

-- Valid param types for this session
-- Synced from types.json on init
create table types (
    id integer primary key,
    name text,
    shortname text,
    type text,
    accepts text
);

