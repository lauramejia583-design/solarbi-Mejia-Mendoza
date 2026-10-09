from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_ENTRADA = BASE_DIR / "Data" / "Bronze" / "telemetria.csv"
ARCHIVO_SALIDA = BASE_DIR / "Data" / "Silver" / "telemetria_limpia.csv"
ARCHIVO_REPORTE = BASE_DIR / "Reports" / "calidad_datos.txt"


ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
ARCHIVO_REPORTE.parent.mkdir(parents=True, exist_ok=True)


df = pd.read_csv(ARCHIVO_ENTRADA)
total_original = len(df)

print("Columnas encontradas:", df.columns.tolist())
print("Registros originales:", total_original)


df.columns = df.columns.str.strip().str.lower()


columnas_requeridas = [
    "ts",
    "dispositivo_id",
    "p_ac_kw",
    "irradiancia_wm2",
    "temp_modulo_c"
]

faltantes = [c for c in columnas_requeridas if c not in df.columns]

if faltantes:
    raise ValueError(
        f"Faltan columnas requeridas: {faltantes}. "
        f"Columnas disponibles: {df.columns.tolist()}"
    )

# Convertir campos a sus tipos correspondientes
df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
for columna in ["dispositivo_id", "p_ac_kw",
                "irradiancia_wm2", "temp_modulo_c"]:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

# Detectar registros con campos vacíos o inválidos
campos = columnas_requeridas
mascara_nulos = df[campos].isna().any(axis=1)
registros_nulos = int(mascara_nulos.sum())

# Excluir registros con campos requeridos vacíos o inválidos
df = df.loc[~mascara_nulos].copy()

# Validar rangos físicos razonables
mascara_rango = (
    df["p_ac_kw"].between(0, 5)
    & df["irradiancia_wm2"].between(0, 1200)
    & df["temp_modulo_c"].between(-20, 100)
    & (df["dispositivo_id"] > 0)
)

registros_fuera_rango = int((~mascara_rango).sum())
df = df.loc[mascara_rango].copy()

# Eliminar duplicados por dispositivo y marca de tiempo
duplicados = int(
    df.duplicated(subset=["ts", "dispositivo_id"], keep="first").sum()
)
df = df.drop_duplicates(
    subset=["ts", "dispositivo_id"], keep="first"
)

# Guardar datos limpios sin alterar Bronze
df.to_csv(ARCHIVO_SALIDA, index=False)

# Crear reporte de calidad
total_limpio = len(df)
total_rechazado = total_original - total_limpio
porcentaje_valido = (
    total_limpio / total_original * 100 if total_original else 0
)

reporte = f"""REPORTE DE CALIDAD DE DATOS - FASE SILVER

Archivo de entrada: {ARCHIVO_ENTRADA}
Archivo de salida: {ARCHIVO_SALIDA}

Registros originales: {total_original}
Registros con campos vacíos o inválidos: {registros_nulos}
Registros fuera de rango: {registros_fuera_rango}
Duplicados eliminados: {duplicados}
Registros válidos finales: {total_limpio}
Registros rechazados totales: {total_rechazado}
Porcentaje de registros válidos: {porcentaje_valido:.2f}%
"""

ARCHIVO_REPORTE.write_text(reporte, encoding="utf-8")

print("\nProceso de limpieza terminado.")
print(reporte)
print("CSV limpio:", ARCHIVO_SALIDA)
print("Reporte:", ARCHIVO_REPORTE)