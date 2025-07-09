import streamlit as st
import pandas as pd

## Fase 1: Configuración inicial
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

# Subir archivo
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        # Leer Excel (primera hoja)
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas si hay duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Mostrar tabla preliminar
        st.success(f"✅ Archivo cargado correctamente. Total de filas: {df.shape[0]}")
        st.dataframe(df.head(20), use_container_width=True)

        # Validar columnas requeridas
        columnas_esperadas = [
            'Activo fijo', 'Subnúmero', 'Capitalizado el', 'Denominación del activo fijo',
            'Número de serie', 'Denominación del activo fijo', 'Cantidad',
            'Amortización normal', 'Val.adq.', 'Amo acum.', 'Val.cont.',
            'Moneda', 'Unidad de Retiro', 'Descripción SG', 'AÑO DE ACTIVACIÓN', '2025'
        ]
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]

        if columnas_faltantes:
            st.error(f"❌ Faltan las siguientes columnas: {columnas_faltantes}")
        else:
            st.success("✅ Todas las columnas necesarias están presentes.")

            ## Fase 2: Limpieza de tipos de datos
            df["AÑO DE ACTIVACIÓN"] = pd.to_numeric(df["AÑO DE ACTIVACIÓN"], errors='coerce')
            df["Val.adq."] = pd.to_numeric(df["Val.adq."], errors='coerce')
            df["Val.cont."] = pd.to_numeric(df["Val.cont."], errors='coerce')
            df["Amo acum."] = pd.to_numeric(df["Amo acum."], errors='coerce')

            ## Fase 3: Filtro por tipo de luminaria
            tipos_disponibles = df["Descripción SG"].dropna().unique().tolist()
            tipo_filtrado = st.selectbox("🎛️ Filtrar por tipo de luminaria", sorted(tipos_disponibles))
            df_filtrado = df[df["Descripción SG"] == tipo_filtrado]

            ## Fase 4: Resumen por año
            st.subheader(f"📅 Resumen por Año de Activación - {tipo_filtrado}")
            resumen = (
                df_filtrado.groupby("AÑO DE ACTIVACIÓN")[["Val.adq.", "Amo acum.", "Val.cont."]]
                .sum()
                .reset_index()
            )

            # Formato de miles
            resumen_formateado = resumen.copy()
            for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                resumen_formateado[col] = resumen_formateado[col].apply(lambda x: f"{x:,.2f}")

            st.dataframe(resumen_formateado, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Ocurrió un error al leer el archivo: {str(e)}")

else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar el análisis.")
