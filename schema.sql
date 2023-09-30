-- Converted from PostgreSQL to SQLite

CREATE TABLE event (
    id TEXT,
    content TEXT,
    created_at BIGINT,
    kind BIGINT,
    pubkey TEXT,
    sig TEXT,
    tags TEXT   -- Note: Originally jsonb in PostgreSQL, stored as TEXT in SQLite
);

CREATE TABLE mention (
    id TEXT,
    ref_id TEXT,
    created_at BIGINT,
    kind BIGINT,
    relay_url TEXT,
    petname TEXT
);

CREATE TABLE pablo (
    id TEXT,
    content TEXT,
    created_at BIGINT,
    kind BIGINT,
    pubkey TEXT,
    sig TEXT,
    tags TEXT   -- Note: Originally jsonb in PostgreSQL, stored as TEXT in SQLite
);

CREATE TABLE reply (
    id TEXT,
    ref_id TEXT,
    created_at TEXT,
    kind BIGINT,
    relay_url TEXT,
    marker TEXT
);

CREATE INDEX ix_event_id ON event(id);
CREATE INDEX ix_mention_id ON mention(id);
CREATE INDEX ix_pablo_id ON pablo(id);
CREATE INDEX ix_reply_id ON reply(id);
