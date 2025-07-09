import streamlit as st
import pandas as pd

# FASE 1 - Carga y validación
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        # Eliminar columna '2025' si existe
        df = df.drop(columns=["2025"], errors="ignore")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        columnas_esperadas = [
            'Activo fijo', 'Subnúmero', 'Capitalizado el', 'Denominación del activo fijo',
            'Número de serie', 'Cantidad', 'Amortización normal',
            'Val.adq.', 'Amo acum.', 'Val.cont.',
            'Moneda', 'Unidad de Retiro', 'Descripción SG', 'AÑO DE ACTIVACIÓN'
        ]
        columnas_faltantes = [col for col in columnas_esperadas if col not in df.columns]

        if columnas_faltantes:
            st.error(f"❌ Faltan columnas: {columnas_faltantes}")
        else:
            # Conversión segura
            for col in ["Val.adq.", "Val.cont.", "Amo acum."]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Normalizar año como texto para evitar errores
            df["AÑO DE ACTIVACIÓN"] = df["AÑO DE ACTIVACIÓN"].astype(str).str.extract(r'(\d{4})')
            df["AÑO DE ACTIVACIÓN"] = pd.to_numeric(df["AÑO DE ACTIVACIÓN"], errors='coerce')

            # FASE 2 - Clasificación y resumen
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")

                df_filtrado = df[filtro].copy()

                resumen = (
                    df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                        "Activo fijo": "count",
                        "Val.adq.": "sum",
                        "Amo acum.": "sum",
                        "Val.cont.": "sum"
                    }).reset_index()
                )

                resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

                # Agregar fila de totales
                total = pd.DataFrame([{
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
                    "Val.adq.": resumen["Val.adq."].sum(),
                    "Amo acum.": resumen["Amo acum."].sum(),
                    "Val.cont.": resumen["Val.cont."].sum()
                }])
                resumen = pd.concat([resumen, total], ignore_index=True)

                # Formatear números
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "-")

                # Aplicar estilo
                def estilo_totales(row):
                    return ['background-color: #d4f4dd; font-weight: bold' if row["AÑO DE ACTIVACIÓN"] == "TOTAL" else '' for _ in row]

                st.dataframe(resumen.style.apply(estilo_totales, axis=1), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
