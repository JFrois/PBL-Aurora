-- =====================================================================
-- SIFSM - Sistema Integrado de Futuro Sustentável em Marte (Fase 7)
-- script_banco.sql  |  SQLite 3 (biblioteca padrão do Python: sqlite3)
--
-- Cria a estrutura do banco da Aurora Siger. Pode ser executado várias
-- vezes (IF NOT EXISTS). Integrante 1 pode ajustar colunas, mas mantenha
-- os nomes das tabelas: os demais módulos dependem deles.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- Módulos da colônia (habitação, agricultura, laboratório, energia...)
CREATE TABLE IF NOT EXISTS modulos (
    id         TEXT    PRIMARY KEY,                      -- ex.: MOD-01
    nome       TEXT    NOT NULL,
    tipo       TEXT    NOT NULL,
    essencial  INTEGER NOT NULL DEFAULT 0 CHECK (essencial IN (0, 1)),   -- 1 = módulo crítico
    limite_consumo_w REAL NOT NULL DEFAULT 6500 CHECK (limite_consumo_w > 0),
    status     TEXT    NOT NULL DEFAULT 'ativo'
               CHECK (status IN ('ativo', 'alerta', 'falha', 'manutencao'))
);

-- Sensores simulados e seus códigos (hexadecimal, como na Fase 6)
CREATE TABLE IF NOT EXISTS sensores (
    codigo_hex TEXT PRIMARY KEY,                         -- ex.: 0x1A
    modulo_id  TEXT NOT NULL REFERENCES modulos(id) ON DELETE CASCADE,
    tipo       TEXT NOT NULL                             -- consumo, temperatura, umidade...
);

-- Leituras de consumo e ambiente: tabela principal do CRUD
CREATE TABLE IF NOT EXISTS leituras (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id          TEXT NOT NULL REFERENCES modulos(id),
    codigo_sensor      TEXT REFERENCES sensores(codigo_hex),
    data_registro      TEXT NOT NULL,                    -- AAAA-MM-DD HH:MM
    consumo_w          REAL NOT NULL CHECK (consumo_w >= 0),
    temperatura_c      REAL,
    umidade_pct        REAL CHECK (umidade_pct IS NULL OR umidade_pct BETWEEN 0 AND 100),
    carga_bateria_pct  REAL CHECK (carga_bateria_pct IS NULL OR carga_bateria_pct BETWEEN 0 AND 100),
    status_operacional TEXT NOT NULL DEFAULT 'ativo'
               CHECK (status_operacional IN ('ativo', 'alerta', 'falha', 'manutencao'))
);

-- Alertas gerados pela regra booleana (logica.py)
CREATE TABLE IF NOT EXISTS alertas (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id  TEXT NOT NULL REFERENCES modulos(id),
    leitura_id INTEGER REFERENCES leituras(id) ON DELETE SET NULL,
    tipo       TEXT NOT NULL,
    prioridade TEXT NOT NULL CHECK (prioridade IN ('baixa', 'media', 'alta', 'critica')),
    mensagem   TEXT NOT NULL,
    criado_em  TEXT NOT NULL,
    resolvido  INTEGER NOT NULL DEFAULT 0 CHECK (resolvido IN (0, 1))
);

-- Chamados da tripulação (alimentam a fila em estruturas.py)
CREATE TABLE IF NOT EXISTS chamados (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id  TEXT REFERENCES modulos(id),
    descricao  TEXT NOT NULL,
    prioridade INTEGER NOT NULL DEFAULT 3 CHECK (prioridade BETWEEN 1 AND 5),
    status     TEXT NOT NULL DEFAULT 'aberto'
               CHECK (status IN ('aberto', 'em_atendimento', 'concluido')),
    criado_em  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leituras_modulo_data ON leituras (modulo_id, data_registro);
CREATE INDEX IF NOT EXISTS idx_alertas_modulo       ON alertas  (modulo_id, resolvido);
