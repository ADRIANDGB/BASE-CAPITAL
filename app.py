import streamlit as st
import pandas as pd




## Fase 1
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

# 1. Subir archivo
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        # 2. Leer Excel (solo la primera hoja)
        df = pd.read_excel(archivo, engine="openpyxl")
        
        # 3. Renombrar columnas si hay duplicados (evita errores como 2 columnas con el mismo nombre)
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # 4. Mostrar forma y tabla básica
        st.success(f"Archivo cargado correctamente. Total de filas: {df.shape[0]}")
        st.dataframe(df.head(20), use_container_width=True)

        # 5. Validar columnas mínimas esperadas (puedes ajustar los nombres según tu archivo real)
        columnas_esperadas = [
            'Activo fijo', 'Subnúmero', 'Capitalizado el', 'Denominación del activo fijo',
            'Número de serie', 'Denominación del activo fijo', 'Cantidad', 'Amortización normal',
            'Val.adq.', 'Amo acum.', 'Val.cont.', 'Moneda', 'Unidad de Retiro',
            'Descripción SG', 'AÑO DE ACTIVACIÓN', '2025'
        ]

        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]

        if columnas_faltantes:
            st.error(f"❌ Faltan las siguientes columnas: {columnas_faltantes}")
        else:
            st.success("✅ Todas las columnas necesarias están presentes.")

            # 6. Conversión de tipos (por si vienen mal desde Excel)
            df["AÑO DE ACTIVACIÓN"] = pd.to_numeric(df["AÑO DE ACTIVACIÓN"], errors='coerce')
            df["Val.adq."] = pd.to_numeric(df["Val.adq."], errors='coerce')
            df["Val.cont."] = pd.to_numeric(df["Val.cont."], errors='coerce')
            df["Amo acum."] = pd.to_numeric(df["Amo acum."], errors='coerce')

            # Mostrar estadística básica por año
            st.subheader("Resumen por Año de Activación")
            resumen = df.groupby("AÑO DE ACTIVACIÓN")[["Val.adq.", "Amo acum.", "Val.cont."]].sum()
            st.dataframe(resumen, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Ocurrió un error al leer el archivo: {str(e)}")

else:
    st.info("📎 Sube un archivo Excel con tus luminarias para comenzar el análisis.")
