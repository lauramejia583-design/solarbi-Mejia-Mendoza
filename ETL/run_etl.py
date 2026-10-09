
from pathlib import Path
from getpass import getpass

import pandas as pd
import psycopg

BASE_DIR = Path(__file__).resolve().parent.parent

ARCHIVO_BRONZE = BASE_DIR / "Data" / "Bronze" / "telemetria.csv"
ARCHIVO_SILVER = BASE_DIR / "Data" / "Silver" / "telemetria_limpia.csv"

COLUMNAS = [
    "ts",
    "dispositivo_id",
    "p_ac_kw",
    "irradiancia_wm2",
    "temp_modulo_c",
]

def leer_datos():
    if not ARCHIVO_BRONZE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo Bronze: {ARCHIVO_BRONZE}"
        )

    if not ARCHIVO_SILVER.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo Silver: {ARCHIVO_SILVER}"
        )

    bronze = pd.read_csv(ARCHIVO_BRONZE)
    silver = pd.read_csv(ARCHIVO_SILVER)

    for nombre, df in [("Bronze", bronze), ("Silver", silver)]:
        faltantes = set(COLUMNAS) - set(df.columns)

        if faltantes:
            raise ValueError(
                f"Faltan columnas en {nombre}: {sorted(faltantes)}"
            )

    for df in [bronze, silver]:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df["dispositivo_id"] = pd.to_numeric(
            df["dispositivo_id"], errors="coerce"
        )

    silver = silver.dropna(subset=COLUMNAS).copy()

    for columna in [
        "p_ac_kw",
        "irradiancia_wm2",
        "temp_modulo_c",
    ]:
        silver[columna] = pd.to_numeric(
            silver[columna], errors="coerce"
        )

    silver = silver.dropna(subset=COLUMNAS).copy()

    if silver.empty:
        raise ValueError("El archivo Silver no contiene datos válidos.")

    silver["dispositivo_id"] = silver["dispositivo_id"].astype(int)

    return bronze, silver



#PREPARAR EL RESUMEN DIARIO (GOLD)

def preparar_gold(bronze, silver):
    bronze = bronze.dropna(
        subset=["ts", "dispositivo_id"]
    ).copy()

    bronze["dispositivo_id"] = bronze["dispositivo_id"].astype(int)
    bronze["fecha"] = bronze["ts"].dt.date

    silver["fecha"] = silver["ts"].dt.date

    # Cantidad de registros originales por día y dispositivo.
    originales = (
        bronze.groupby(["fecha", "dispositivo_id"])
        .size()
        .rename("registros_originales")
    )

    # Energía: potencia en kW × 5/60 horas.
    silver["energia_kwh"] = silver["p_ac_kw"] * (5 / 60)

    resumen = (
        silver.groupby(["fecha", "dispositivo_id"])
        .agg(
            energia_kwh=("energia_kwh", "sum"),
            registros_validos=("ts", "count"),
        )
    )

    resumen = resumen.join(originales, how="left")
    resumen["registros_originales"] = (
        resumen["registros_originales"].fillna(0)
    )

    resumen["pct_datos_validos"] = (
        resumen["registros_validos"]
        / resumen["registros_originales"]
        * 100
    ).fillna(0)

    resumen = resumen.reset_index()

    return resumen

# CARGAR SILVER Y GOLD EN POSTGRESQL
def cargar_postgresql(silver, gold):
    usuario = input("Usuario PostgreSQL [postgres]: ").strip()
    if not usuario:
        usuario = "postgres"

    contrasena = getpass("Contraseña de PostgreSQL: ")

    conexion = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="practica_bi",
        user=usuario,
        password=contrasena,
    )

    try:
        with conexion.cursor() as cursor:

            # Cargar lecturas limpias.
            sql_silver = """
                INSERT INTO silver.lectura_5min
                    (ts, dispositivo_id, p_ac_kw,
                     irradiancia_wm2, temp_modulo_c)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (ts, dispositivo_id)
                DO UPDATE SET
                    p_ac_kw = EXCLUDED.p_ac_kw,
                    irradiancia_wm2 = EXCLUDED.irradiancia_wm2,
                    temp_modulo_c = EXCLUDED.temp_modulo_c;
            """

            datos_silver = [
                (
                    fila.ts.to_pydatetime(),
                    int(fila.dispositivo_id),
                    float(fila.p_ac_kw),
                    float(fila.irradiancia_wm2),
                    float(fila.temp_modulo_c),
                )
                for fila in silver.itertuples(index=False)
            ]

            cursor.executemany(sql_silver, datos_silver)

            # Cargar resumen diario.
            sql_gold = """
                INSERT INTO dwh.fact_energia_dia
                    (fecha, dispositivo, energia_kwh,
                     pct_datos_validos)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (fecha, dispositivo)
                DO UPDATE SET
                    energia_kwh = EXCLUDED.energia_kwh,
                    pct_datos_validos = EXCLUDED.pct_datos_validos;
            """

            datos_gold = [
                (
                    fila.fecha,
                    int(fila.dispositivo_id),
                    round(float(fila.energia_kwh), 3),
                    round(float(fila.pct_datos_validos), 2),
                )
                for fila in gold.itertuples(index=False)
            ]

            cursor.executemany(sql_gold, datos_gold)

            # Consultar los totales almacenados.
            cursor.execute(
                "SELECT COUNT(*) FROM silver.lectura_5min;"
            )
            total_silver = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM dwh.fact_energia_dia;"
            )
            total_gold = cursor.fetchone()[0]

        conexion.commit()

        print("\nETL finalizado correctamente.")
        print(f"Lecturas válidas procesadas: {len(silver)}")
        print(f"Resúmenes diarios procesados: {len(gold)}")
        print(f"Filas almacenadas en Silver: {total_silver}")
        print(f"Filas almacenadas en Gold: {total_gold}")

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

def main():
    print("Iniciando proceso ETL...")

    bronze, silver = leer_datos()

    print(f"Registros originales: {len(bronze)}")
    print(f"Registros limpios: {len(silver)}")

    gold = preparar_gold(bronze, silver)

    print(f"Grupos diarios calculados: {len(gold)}")

    cargar_postgresql(silver, gold)


if __name__ == "__main__":
    main()