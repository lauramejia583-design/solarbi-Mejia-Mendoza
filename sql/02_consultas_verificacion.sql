-- 1. Cantidad de lecturas almacenadas en Silver.
SELECT COUNT(*) AS total_lecturas
FROM silver.lectura_5min;

-- 2. Consultar algunas lecturas de Silver.
SELECT
    ts,
    dispositivo_id,
    p_ac_kw,
    irradiancia_wm2,
    temp_modulo_c
FROM silver.lectura_5min
ORDER BY ts
LIMIT 10;

-- 3. Resumen diario de energía en Gold.
SELECT
    fecha,
    dispositivo,
    energia_kwh,
    pct_datos_validos
FROM dwh.fact_energia_dia
ORDER BY fecha, dispositivo;

-- 4. Cantidad de resúmenes diarios por dispositivo.
SELECT
    dispositivo,
    COUNT(*) AS dias_resumidos,
    SUM(energia_kwh) AS energia_total_kwh,
    AVG(pct_datos_validos) AS promedio_datos_validos
FROM dwh.fact_energia_dia
GROUP BY dispositivo
ORDER BY dispositivo;

-- 5. Verificar que no existan claves duplicadas en Silver.
SELECT
    ts,
    dispositivo_id,
    COUNT(*) AS cantidad
FROM silver.lectura_5min
GROUP BY ts, dispositivo_id
HAVING COUNT(*) > 1;