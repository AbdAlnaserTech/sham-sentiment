-- Sentiment Analysis Platform — SQLite schema
-- Users ──< analysis_batches ──< analysis_items
-- analysis_batches ──< alerts

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'analyst' CHECK (role IN ('admin', 'analyst', 'viewer')),
    full_name_ar TEXT,
    full_name_en TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS analysis_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    source TEXT DEFAULT 'manual',
    model_kind TEXT DEFAULT 'bert',
    total_count INTEGER NOT NULL DEFAULT 0,
    positive_count INTEGER NOT NULL DEFAULT 0,
    negative_count INTEGER NOT NULL DEFAULT 0,
    neutral_count INTEGER NOT NULL DEFAULT 0,
    avg_confidence REAL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS analysis_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    language TEXT,
    sentiment TEXT NOT NULL,
    confidence REAL NOT NULL DEFAULT 0,
    is_reliable INTEGER NOT NULL DEFAULT 1,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (batch_id) REFERENCES analysis_batches(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id INTEGER NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'critical')),
    alert_type TEXT NOT NULL,
    message TEXT NOT NULL,
    metric_value REAL,
    threshold REAL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (batch_id) REFERENCES analysis_batches(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    key_hash TEXT NOT NULL UNIQUE,
    label TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_batches_user ON analysis_batches(user_id);
CREATE INDEX IF NOT EXISTS idx_batches_created ON analysis_batches(created_at);
CREATE INDEX IF NOT EXISTS idx_items_batch ON analysis_items(batch_id);
CREATE INDEX IF NOT EXISTS idx_items_sentiment ON analysis_items(sentiment);
CREATE INDEX IF NOT EXISTS idx_alerts_batch ON alerts(batch_id);
