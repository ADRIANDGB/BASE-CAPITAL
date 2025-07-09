import streamlit as st
import pandas as pd

## Fase 1: Configuración inicial
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

# Subir archivo
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        # Leer Excel
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Validar columnas
        columnas_esperadas = [
            'Activo fijo', 'Subnúmero', 'Capitalizado el', 'Denominación del activo fijo',
            'Número de serie', 'Denominación del activo fijo', 'Cantidad',
            'Amortización normal', 'Val.adq.', 'Amo acum.', 'Val.cont.',
            'Moneda', 'Unidad de Retiro', 'Descripción SG', 'AÑO DE ACTIVACIÓN'
        ]
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]

        if columnas_faltantes:
            st.error(f"❌ Faltan columnas: {columnas_faltantes}")
        else:
            # Convertir numéricos
            for col in ["AÑO DE ACTIVACIÓN", "Val.adq.", "Val.cont.", "Amo acum."]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            ## Fase 2: Generar resumen por tipo
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"] == "LED ALTA INTENSIDAD",
                "LED BAJA INTENSIDAD": df["Descripción SG"] == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_filtrado = df[filtro]

           # LIMPIEZA PREVIA DE AÑO DE ACTIVACIÓN
df["AÑO DE ACTIVACIÓN"] = df["AÑO DE ACTIVACIÓN"].astype(str).str.strip()
df["AÑO DE ACTIVACIÓN"] = pd.to_numeric(df["AÑO DE ACTIVACIÓN"], errors="coerce")

# ELIMINAMOS FILAS SIN AÑO DE ACTIVACIÓN
df = df[df["AÑO DE ACTIVACIÓN"].notna()]
df["AÑO DE ACTIVACIÓN"] = df["AÑO DE ACTIVACIÓN"].astype(int)

# AGRUPACIÓN NORMAL
resumen = (
    df_filtrado.groupby("AÑO DE ACTIVACIÓN", dropna=False)
    .agg({
        "Activo fijo": "count",
        "Val.adq.": "sum",
        "Amo acum.": "sum",
        "Val.cont.": "sum"
    })
    .reset_index()
    .sort_values(by="AÑO DE ACTIVACIÓN")
)


                resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

                # Formato bonito
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}")

                st.dataframe(resumen, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
