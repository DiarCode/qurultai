### SQL Schema: Granular Agent Traceability

```sql
-- 1. Справочник инструментов
CREATE TABLE tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL, -- напр. "web_search"
    description TEXT,
    schema JSONB,                      -- JSON Schema входных параметров
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Реестр агентов
CREATE TABLE agents (
    id VARCHAR(50) PRIMARY KEY,        -- напр. "legal_analyst_01"
    name VARCHAR(255) NOT NULL,
    role_description TEXT,
    system_prompt TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Связь Агент-Инструмент (какие тулзы разрешены агенту)
CREATE TABLE agent_tools (
    agent_id VARCHAR(50) REFERENCES agents(id),
    tool_id UUID REFERENCES tools(id),
    PRIMARY KEY (agent_id, tool_id)
);

-- 4. Комнаты (Сессии)
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(50) DEFAULT 'OPEN', -- OPEN, PROCESSING, COMPLETED, FAILED
    initial_query TEXT NOT NULL,
    context_text TEXT,                 -- Результат парсинга PDF/OCR
    mission_goals JSONB,               -- Список целей от Оркестратора
    final_report_md TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Запуски агентов (Agent Run) - участие конкретного агента в комнате
CREATE TABLE agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    agent_id VARCHAR(50) REFERENCES agents(id),
    status VARCHAR(50) DEFAULT 'IDLE', -- BIDDING, THINKING, DONE
    bid_reason TEXT,                   -- Почему агент решил участвовать
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP WITH TIME ZONE
);

-- 6. Гранулярные шаги (Самая важная таблица для "Истории размышлений")
CREATE TABLE agent_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES agent_runs(id) ON DELETE CASCADE,
    step_type VARCHAR(50) NOT NULL,    -- THOUGHT, TOOL_CALL, TOOL_OUTPUT, MD_FRAGMENT
    content JSONB NOT NULL,            -- Текст мысли или JSON вызова тулзы
    tokens_used INT DEFAULT 0,
    latency_ms FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Источники (Grounding)
CREATE TABLE agent_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID REFERENCES agent_steps(id) ON DELETE CASCADE,
    source_type VARCHAR(50),           -- KNOWLEDGE_BASE, WEB, TOOL_RESULT
    ref_id TEXT,                       -- ID документа или URL
    snippet TEXT,                      -- Цитата из источника
    score FLOAT                        -- Релевантность (0-1)
);

-- Индексы для быстрого поиска в чате
CREATE INDEX idx_steps_run_id ON agent_steps(run_id);
CREATE INDEX idx_runs_room_id ON agent_runs(room_id);
```
