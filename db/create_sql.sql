-- 账户表
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    username TEXT DEFAULT '',              -- 用户名
    password TEXT DEFAULT '',              -- 密码
    mobile TEXT DEFAULT '',                -- 手机号
    realname TEXT DEFAULT '',              -- 昵称
    mailbox TEXT DEFAULT '',               -- 邮箱
    head_img TEXT DEFAULT '',              -- 用户头像
    background TEXT DEFAULT '',            -- 默认背景
    signature TEXT DEFAULT '',             -- 个性签名
    status TINYINT DEFAULT 1,             -- 状态 1:启用 2:禁用
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0           -- 逻辑删除
);


-- 评论表
CREATE TABLE comment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    cid INTEGER DEFAULT NULL,              -- 文章或素材id
    author_id INTEGER DEFAULT NULL,        -- 评论人id
    ip TEXT DEFAULT NULL,                  -- IP地址
    content TEXT,                          -- 评论内容
    type TINYINT DEFAULT 0,                -- 类型 -0：素材 1:文章
    status TINYINT DEFAULT 0,              -- 状态 0：未回复 1 已回复
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);

-- 文章表
CREATE TABLE contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    title TEXT DEFAULT NULL,               -- 文章名称
    thumb_img TEXT DEFAULT NULL,           -- 展示图URL
    content TEXT,                          -- 文章内容
    author_id INTEGER DEFAULT NULL,        -- 作者（用户）id
    type TINYINT DEFAULT 1,                -- 文章格式 1：markdown
    status TINYINT DEFAULT 0,              -- 发布状态 0-草稿 1-发布
    tags_id TEXT DEFAULT '',               -- 标签id
    categorie_id INTEGER DEFAULT NULL,     -- 类别id
    hits INTEGER DEFAULT 0,                -- 浏览量
    sort INTEGER DEFAULT 0,               -- 排序
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0             -- 逻辑删除
);

-- 素材表
CREATE TABLE material (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    thumb_img TEXT,                        -- 图片
    content TEXT,                          -- 素材内容
    user_id INTEGER,                       -- 用户id
    type TINYINT DEFAULT 1,                -- 文章格式 1：markdown
    status TINYINT DEFAULT 0,              -- 发布状态：0-草稿 1-发布
    source TEXT DEFAULT '',                -- 素材出处
    author TEXT DEFAULT '佚名',            -- 作者
    original TINYINT DEFAULT 0,            -- 原创 - 0：否  1：是
    metas_id INTEGER,                      -- 分类id
    hits INTEGER DEFAULT 0,                -- 浏览量
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);


-- 文章素材分类表
CREATE TABLE metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    name TEXT DEFAULT '',                  -- 分类名称
    type INTEGER DEFAULT 0,                -- 类型
    sort INTEGER DEFAULT 0,                -- 排序
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);

-- 文章素材标签表
CREATE TABLE tag (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    name TEXT DEFAULT '',                  -- 标签名称
    sort INTEGER DEFAULT 0,                -- 排序
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);


-- 网站资源表
CREATE TABLE website_resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    website_title_id INTEGER NOT NULL,     -- 网站合集标题id
    name TEXT DEFAULT '',                  -- 名称
    website_url TEXT DEFAULT '',           -- 网站URL
    state TEXT DEFAULT '',                 -- 描述
    icon TEXT DEFAULT '',                  -- icon
    sort INTEGER DEFAULT 1,                -- 排序
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);

-- 网站合集标题表
CREATE TABLE website_title (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 主键，自动递增
    title TEXT DEFAULT '',                 -- 网站合集标题
    sort INTEGER DEFAULT 1,                -- 排序
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
);


CREATE TABLE album (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    filesize INTEGER NOT NULL,
    filetype TEXT NOT NULL CHECK(filetype IN ('image', 'video', 'audio')),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    del_flag TINYINT DEFAULT 0              -- 逻辑删除
)

ALTER TABLE album ADD COLUMN longitude REAL;  -- 经度(允许为空)
ALTER TABLE album ADD COLUMN latitude REAL;   -- 纬度(允许为空)
ALTER TABLE album ADD capture_time TIMESTAMP DEFAULT NULL;
ALTER TABLE album ADD COLUMN metadata TEXT;   -- 元数据

CREATE TABLE IF NOT EXISTS album_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder_name TEXT NOT NULL UNIQUE,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 创建时间
)
ALTER TABLE album_folders ADD COLUMN is_lock TINYINT DEFAULT 0;   -- 是否锁定
