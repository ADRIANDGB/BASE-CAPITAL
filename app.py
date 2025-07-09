import streamlit as st
import pandas as pd
import plotly.express as px

#------------------------------------------------------------------------------------------------------
# Fase 1: Configuración inicial
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
            'Moneda', 'Unidad de Retiro', 'Descripción SG', 'AÑO DE ACTIVACIÓN', '2025'
        ]
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]

        if columnas_faltantes:
            st.error(f"❌ Faltan columnas: {columnas_faltantes}")
        else:
            # Normalizar texto en Descripción SG
            df["Descripción SG"] = df["Descripción SG"].astype(str).str.upper().str.strip()
            df["Descripción SG"] = df["Descripción SG"].replace("NAN", None)

            # Convertir a número columnas clave
            for col in ["AÑO DE ACTIVACIÓN", "Val.adq.", "Val.cont.", "Amo acum."]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Fase 2: Resumen por tipo
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"] == "LED ALTA INTENSIDAD",
                "LED BAJA INTENSIDAD": df["Descripción SG"] == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_filtrado = df[filtro]

                resumen = (
                    df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                        "Activo fijo": "count",
                        "Val.adq.": "sum",
                        "Amo acum.": "sum",
                        "Val.cont.": "sum"
                    }).reset_index()
                )

                resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

                # Formato de miles
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}")

                # Mostrar tabla sin totales aún
                st.dataframe(resumen, use_container_width=True)

                # Agregar fila de totales generales
                totales = {
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
                    "Val.adq.": resumen["Val.adq."].replace({',': ''}, regex=True).astype(float).sum(),
                    "Amo acum.": resumen["Amo acum."].replace({',': ''}, regex=True).astype(float).sum(),
                    "Val.cont.": resumen["Val.cont."].replace({',': ''}, regex=True).astype(float).sum(),
                }

                totales_formateados = {
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": int(totales["Cantidad de Activos"]),
                    "Val.adq.": f"{totales['Val.adq.']:,.2f}",
                    "Amo acum.": f"{totales['Amo acum.']:,.2f}",
                    "Val.cont.": f"{totales['Val.cont.']:,.2f}"
                }

                resumen_total = pd.concat([resumen, pd.DataFrame([totales_formateados])], ignore_index=True)

                def resaltar_total(fila):
                    if fila["AÑO DE ACTIVACIÓN"] == "TOTAL":
                        return ['background-color: #c7f5c1; font-weight: bold'] * len(fila)
                    else:
                        return [''] * len(fila)

                st.dataframe(resumen_total.style.apply(resaltar_total, axis=1), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
