-- BotV2 Database Initialization Script
-- Creates necessary tables for production deployment

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    symbol VARCHAR(50) NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('BUY', 'SELL', 'CLOSE')),
    entry_price DECIMAL(18,8) NOT NULL,
    size DECIMAL(18,8) NOT NULL,
    pnl DECIMAL(18,8) DEFAULT 0,
    commission DECIMAL(18,8) DEFAULT 0,
    strategy VARCHAR(100),
    confidence DECIMAL(5,4),
    metadata JSONB,
    CONSTRAINT valid_size CHECK (size > 0),
    CONSTRAINT valid_price CHECK (entry_price > 0)
);

CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy);

-- Portfolio checkpoints table
CREATE TABLE IF NOT EXISTS portfolio_checkpoints (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cash DECIMAL(18,8) NOT NULL,
    equity DECIMAL(18,8) NOT NULL,
    positions JSONB,
    CONSTRAINT valid_cash CHECK (cash >= 0),
    CONSTRAINT valid_equity CHECK (equity >= 0)
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_timestamp ON portfolio_checkpoints(timestamp DESC);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    total_return DECIMAL(10,4),
    win_rate DECIMAL(5,4),
    profit_factor DECIMAL(10,4),
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp DESC);

-- Circuit breaker events table
CREATE TABLE IF NOT EXISTS circuit_breaker_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    level INTEGER NOT NULL CHECK (level IN (1, 2, 3)),
    drawdown DECIMAL(10,4) NOT NULL,
    action VARCHAR(50) NOT NULL,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_breaker_timestamp ON circuit_breaker_events(timestamp DESC);

-- Strategy performance table
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    strategy_name VARCHAR(100) NOT NULL,
    sharpe_ratio DECIMAL(10,4),
    total_return DECIMAL(10,4),
    win_rate DECIMAL(5,4),
    total_trades INTEGER DEFAULT 0,
    weight DECIMAL(5,4),
    enabled BOOLEAN DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_strategy_perf_name ON strategy_performance(strategy_name);
CREATE INDEX IF NOT EXISTS idx_strategy_perf_timestamp ON strategy_performance(timestamp DESC);

-- System logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level);

-- Create views for common queries

-- Recent trades view
CREATE OR REPLACE VIEW recent_trades AS
SELECT 
    timestamp,
    symbol,
    action,
    entry_price,
    size,
    pnl,
    strategy
FROM trades
ORDER BY timestamp DESC
LIMIT 100;

-- Daily performance view
CREATE OR REPLACE VIEW daily_performance AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(pnl) as daily_pnl,
    AVG(pnl) as avg_pnl,
    MAX(pnl) as max_win,
    MIN(pnl) as max_loss
FROM trades
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Strategy summary view
CREATE OR REPLACE VIEW strategy_summary AS
SELECT 
    strategy,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
    ROUND(SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::numeric / COUNT(*)::numeric, 4) as win_rate,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl
FROM trades
WHERE strategy IS NOT NULL
GROUP BY strategy
ORDER BY total_pnl DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO botv2_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO botv2_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO botv2_user;

-- Insert initial data
INSERT INTO performance_metrics (sharpe_ratio, max_drawdown, total_return, win_rate, total_trades)
VALUES (0, 0, 0, 0, 0)
ON CONFLICT DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'BotV2 database initialized successfully!';
END $$;
