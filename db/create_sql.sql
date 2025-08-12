create table album
(
    id           INTEGER
        primary key autoincrement,
    folder_id    INTEGER not null,
    filename     TEXT    not null,
    filepath     TEXT    not null,
    filesize     INTEGER not null,
    filetype     TEXT    not null,
    create_time  TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag     TINYINT   default 0,
    longitude    REAL,
    latitude     REAL,
    capture_time TIMESTAMP default NULL,
    metadata     TEXT,
    thumb_path   TEXT,
    check (filetype IN ('image', 'video', 'audio'))
);

create table album_folders
(
    id          INTEGER
        primary key autoincrement,
    folder_name TEXT not null
        unique,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    is_lock     TINYINT   default 0
);

create table comment
(
    id          INTEGER
        primary key autoincrement,
    cid         INTEGER   default NULL,
    author_id   INTEGER   default NULL,
    ip          TEXT      default NULL,
    content     TEXT,
    type        TINYINT   default 0,
    status      TINYINT   default 0,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag    TINYINT   default 0
);

create table contents
(
    id           INTEGER
        primary key autoincrement,
    title        TEXT      default NULL,
    thumb_img    TEXT      default NULL,
    content      TEXT,
    author_id    INTEGER   default NULL,
    type         TINYINT   default 1,
    status       TINYINT   default 0,
    tags_id      TEXT      default '',
    categorie_id INTEGER   default NULL,
    hits         INTEGER   default 0,
    sort         INTEGER   default 0,
    create_time  TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag     TINYINT   default 0
);

create table material
(
    id          INTEGER
        primary key autoincrement,
    thumb_img   TEXT,
    content     TEXT,
    user_id     INTEGER,
    type        TINYINT   default 1,
    status      TINYINT   default 0,
    source      TEXT      default '',
    author      TEXT      default '佚名',
    original    TINYINT   default 0,
    metas_id    INTEGER,
    hits        INTEGER   default 0,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag    TINYINT   default 0
);

create table metas
(
    id          INTEGER
        primary key autoincrement,
    name        TEXT      default '',
    type        INTEGER   default 0,
    sort        INTEGER   default 0,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag    TINYINT   default 0
);

create table tag
(
    id          INTEGER
        primary key autoincrement,
    name        TEXT      default '',
    sort        INTEGER   default 0,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag    TINYINT   default 0
);

create table user
(
    id          INTEGER
        primary key autoincrement,
    username    TEXT      default '',
    password    TEXT      default '',
    mobile      TEXT      default '',
    realname    TEXT      default '',
    mailbox     TEXT      default '',
    head_img    TEXT      default '',
    background  TEXT      default '',
    signature   TEXT      default '',
    status      TINYINT   default 1,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag    TINYINT   default 0
);

create table website_resource
(
    id               INTEGER
        primary key autoincrement,
    website_title_id INTEGER not null,
    name             TEXT      default '',
    website_url      TEXT      default '',
    state            TEXT      default '',
    icon             TEXT      default '',
    sort             INTEGER   default 1,
    create_time      TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag         TINYINT   default 0
);

create table website_title
(
    id          INTEGER
        primary key autoincrement,
    title       TEXT      default '',
    sort        INTEGER   default 1,
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    del_flag    TINYINT   default 0
);

