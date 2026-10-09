
-- Crear esquemas.
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS dwh;

-- Tabla Silver: lecturas de telemetría cada 5 minutos.
CREATE TABLE IF NOT EXISTS silver.lectura_5min (
    ts TIMESTAMP NOT NULL,
    dispositivo_id INTEGER NOT NULL,
    p_ac_kw NUMERIC(10,3) NOT NULL,
    irradiancia_wm2 NUMERIC(10,2) NOT NULL,
    temp_modulo_c NUMERIC(6,2) NOT NULL,
    CONSTRAINT pk_lectura_5min
        PRIMARY KEY (ts, dispositivo_id)
);

-- Tabla Gold: resumen diario de energía.
CREATE TABLE IF NOT EXISTS dwh.fact_energia_dia (
    fecha DATE NOT NULL,
    dispositivo INTEGER NOT NULL,
    energia_kwh NUMERIC(12,3) NOT NULL,
    pct_datos_validos NUMERIC(5,2) NOT NULL,
    CONSTRAINT pk_fact_energia_dia
        PRIMARY KEY (fecha, dispositivo)
);