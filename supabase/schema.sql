-- 在 Supabase SQL Editor 中运行此脚本
-- https://app.supabase.com → 你的项目 → SQL Editor → New Query → 粘贴并 Run

-- 成员表
CREATE TABLE members (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    student_id TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    department TEXT DEFAULT '',
    join_date DATE DEFAULT CURRENT_DATE,
    status TEXT DEFAULT 'active',
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 活动表
CREATE TABLE events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    event_date DATE NOT NULL DEFAULT CURRENT_DATE,
    location TEXT DEFAULT '',
    description TEXT DEFAULT '',
    max_participants INT DEFAULT 0,
    fee NUMERIC(10,2) DEFAULT 0,
    status TEXT DEFAULT 'upcoming',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 活动报名表
CREATE TABLE event_participants (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    member_id BIGINT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(event_id, member_id)
);

-- 财务表
CREATE TABLE finances (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    amount NUMERIC(10,2) NOT NULL,
    category TEXT DEFAULT '',
    description TEXT DEFAULT '',
    date DATE DEFAULT CURRENT_DATE,
    member_id BIGINT REFERENCES members(id) ON DELETE SET NULL,
    event_id BIGINT REFERENCES events(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 设置表（存储管理密码）
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO settings (key, value) VALUES ('password', 'admin123')
ON CONFLICT (key) DO NOTHING;

-- 为每个表开启 Row Level Security
ALTER TABLE members ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE finances ENABLE ROW LEVEL SECURITY;
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- RLS 策略：已认证用户可读写
CREATE POLICY "Enable all for authenticated" ON members FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for authenticated" ON events FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for authenticated" ON event_participants FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Enable all for authenticated" ON finances FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Enable select for anon" ON settings FOR SELECT TO anon USING (true);
