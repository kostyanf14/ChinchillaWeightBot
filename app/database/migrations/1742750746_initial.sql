CREATE TABLE IF NOT EXISTS "sessions" (
    "session_id"  TEXT      NOT NULL  UNIQUE,
    "username"    TEXT      NOT NULL  UNIQUE,
    "agent"       TEXT      NOT NULL,
    "time"        NUMERIC   NOT NULL
);

CREATE TABLE IF NOT EXISTS "chinchillas" (
    "id"          INTEGER   PRIMARY KEY AUTOINCREMENT UNIQUE,
    "name"        TEXT      NOT NULL  UNIQUE
);

CREATE TABLE IF NOT EXISTS "weights" (
    "id"              INTEGER   PRIMARY KEY AUTOINCREMENT UNIQUE,
    "chinchilla_id"   INTEGER   NOT NULL,
    "time"            NUMERIC   NOT NULL,
    "weight"          INTEGER   NOT NULL
);
