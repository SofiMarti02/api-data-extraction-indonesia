import requests
import pandas as pd
import os
import time

#POSICIONES ARANCELARIAS APARTIR DEL 2022
ruta = r"data"
archivo = "posiciones con descripcion.xlsx"
ruta_completa = os.path.join(ruta, archivo)

data_posicion = pd.read_excel(ruta_completa, dtype={"HS Code": str})
kodehs_list = data_posicion["HS Code"].astype(str).str.zfill(8).tolist()

# LISTA PRUEBAS
#kodehs_list = kodehs_list[:10]

resultados = []
codigos_sin_datos = []

# Tamaño
bloque_size = 10
SUMBER = 1  # 1 = EXPORTACIÓN

for i in range(0, len(kodehs_list), bloque_size):
    bloque = kodehs_list[i:i+bloque_size]
    kodehs_param = ";".join(bloque)

    url = (
        f"https://webapi.bps.go.id/v1/api/dataexim/"
        f"sumber/{SUMBER}/"
        f"kodehs/{kodehs_param}/"
        f"jenishs/2/"
        f"tahun/2026/"
        f"periode/1/"
        f"API"
        )   

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        json_data = response.json()
        if "data" in json_data and json_data["data"]:
            df = pd.json_normalize(json_data["data"])
            resultados.append(df)
        else:
            codigos_sin_datos.extend(bloque)
    except requests.exceptions.RequestException as e:
        print(f"Error en bloque {i}-{i+len(bloque)}: {e}")
        codigos_sin_datos.extend(bloque)

    print(f"Procesados {i+len(bloque)}/{len(kodehs_list)} códigos...")
    time.sleep(1)  # DESCANSO  API

# REINTENTAR LOS CODIGOS QUE NO PASARON
if codigos_sin_datos:
    print("\nIniciando segundo intento para los códigos sin datos...")

    codigos_sin_datos_segundo_intento = []

    for i in range(0, len(codigos_sin_datos), bloque_size):
        bloque = codigos_sin_datos[i:i+bloque_size]
        kodehs_param = ";".join(bloque)

        url = (
            f"https://webapi.bps.go.id/v1/api/dataexim/"
            f"sumber/{SUMBER}/"
            f"kodehs/{kodehs_param}/"
            f"jenishs/2/"
            f"tahun/2026/"
            f"periode/1/"
            f"API"
            )

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            json_data = response.json()
            if "data" in json_data and json_data["data"]:
                df = pd.json_normalize(json_data["data"])
                resultados.append(df)
            else:
                codigos_sin_datos_segundo_intento.extend(bloque)
        except requests.exceptions.RequestException as e:
            print(f"Error en segundo intento bloque {i}-{i+len(bloque)}: {e}")
            codigos_sin_datos_segundo_intento.extend(bloque)

        print(f"Segundo intento: procesados {i+len(bloque)}/{len(codigos_sin_datos)} códigos...")
        time.sleep(1)

    codigos_sin_datos = codigos_sin_datos_segundo_intento

#BASE FINAL
if resultados:
    df_final = pd.concat(resultados, ignore_index=True)   

#LIMPIEZA BASE

df_final.rename(columns={
    "tahun": "YEAR",
    "bulan": "MES",
    "kodehs": "POSICION Y DESCRIPCION",
    #"jenishs": "Tipo Hs",
    "pod": "PORT",
    "ctr": "COUNTRY OF DESTINATION",
    "value": "FOB VALUE (USD)",
    "netweight": "NET WEIGHT (KG)",
}, inplace=True)


df_final['MONTH'] = df_final['MES'].str.extract(r'\[(\d+)\]').astype(int)

meses_dict = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}


df_final["HS CODE"] = df_final["POSICION Y DESCRIPCION"].str.extract(r"\[(\d+)\]")
df_final["DESCRIPTION"] = df_final["POSICION Y DESCRIPCION"].str.replace(
    r"\[\d+\]\s*", "", regex=True
).str.upper()

columnas = df_final.columns.tolist()

columnas_prioritarias = [
    "YEAR",
    "MONTH",
    "HS CODE",
    "DESCRIPTION",
    "COUNTRY OF DESTINATION",
    "NET WEIGHT (KG)",
    "FOB VALUE (USD)",
    "PORT"
]


df_final = df_final[columnas_prioritarias]

# Carpeta donde se guardarán los archivos

ruta_2 = r"output"

os.makedirs(ruta_2, exist_ok=True)


# Generar un Excel ULTIMO mes

# obtener el último año y mes disponible
ultimo_periodo = (
    df_final[['YEAR', 'MONTH']]
    .drop_duplicates()
    .sort_values(['YEAR', 'MONTH'])
    .iloc[-1]
)

año = ultimo_periodo['YEAR']
mes = ultimo_periodo['MONTH']

df_ultimo_mes = df_final[
    (df_final['YEAR'] == año) &
    (df_final['MONTH'] == mes)
]

nombre_mes = meses_dict.get(mes, str(mes))
nombre_archivo = f"Exportacion.xlsx" 
ruta_completa_2 = os.path.join(ruta_2, nombre_archivo)

df_ultimo_mes.to_excel(ruta_completa_2, index=False, sheet_name='EXPORTACION')

print(f"Archivo generado: {ruta_completa_2}")



#GENERAR UN MES EN ESPECIFICO

ruta_3 = r"output/historico"

os.makedirs(ruta_3, exist_ok=True)

año_especifico = 2025   # Define el año
mes_especifico = 11     # Define el mes

df_mes_especifico = df_final[
    (df_final['YEAR'] == año_especifico) &
    (df_final['MONTH'] == mes_especifico)
]

nombre_mes_especifico = meses_dict.get(mes_especifico, str(mes_especifico))
nombre_archivo_especifico = f"Exportacion_{nombre_mes_especifico}_{año_especifico}.xlsx"

ruta_completa_3 = os.path.join(ruta_3, nombre_archivo_especifico)

df_mes_especifico.to_excel(
    ruta_completa_3,
    index=False,
    sheet_name='EXPORTACION'
)

print(f"Archivo generado (mes específico - histórico): {ruta_completa_3}")
