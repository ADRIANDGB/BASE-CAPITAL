import streamlit as st
import pandas as pd

# --------------------------------------------
# FASE 1: Configuración y carga de datos
# --------------------------------------------
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        # Leer archivo Excel
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas duplicadas si las hay
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Validar columnas mínimas necesarias
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
            # Convertir a numérico donde sea necesario
            for col in ["AÑO DE ACTIVACIÓN", "Val.adq.", "Val.cont.", "Amo acum."]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Agrupaciones por tipo de luminaria
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_filtrado = df[filtro]

                # Agrupación
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

                # Totales
                total = pd.DataFrame({
                    "AÑO DE ACTIVACIÓN": ["TOTAL"],
                    "Cantidad de Activos": [resumen["Cantidad de Activos"].sum()],
                    "Val.adq.": [resumen["Val.adq."].sum()],
                    "Amo acum.": [resumen["Amo acum."].sum()],
                    "Val.cont.": [resumen["Val.cont."].sum()],
                })

                resumen_total = pd.concat([resumen, total], ignore_index=True)

                # Formato bonito
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen_total[col] = resumen_total[col].apply(lambda x: f"{x:,.2f}")

                resumen_total["Cantidad de Activos"] = resumen_total["Cantidad de Activos"].apply(lambda x: f"{int(x):,}" if isinstance(x, (int, float)) else x)

                # Mostrar tabla con estilos
                def estilo_verde(val):
                    return 'background-color: #d4edda; font-weight: bold;' if val == "TOTAL" else ""

                st.dataframe(
                    resumen_total.style.applymap(estilo_verde, subset=["AÑO DE ACTIVACIÓN"]),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
