import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

# Subida de archivo
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Validación de columnas necesarias
        columnas_necesarias = [
            'Activo fijo', 'Val.adq.', 'Amo acum.', 'Val.cont.',
            'Descripción SG', 'AÑO DE ACTIVACIÓN'
        ]
        faltantes = [col for col in columnas_necesarias if col not in df.columns]

        if faltantes:
            st.error(f"❌ Faltan columnas requeridas: {faltantes}")
        else:
            # Limpieza y conversión de datos
            df["AÑO DE ACTIVACIÓN"] = pd.to_numeric(df["AÑO DE ACTIVACIÓN"], errors="coerce")
            df["Val.adq."] = pd.to_numeric(df["Val.adq."], errors="coerce")
            df["Amo acum."] = pd.to_numeric(df["Amo acum."], errors="coerce")
            df["Val.cont."] = pd.to_numeric(df["Val.cont."], errors="coerce")

            df = df[df["AÑO DE ACTIVACIÓN"].notna()]

            # Diccionario de categorías
            categorias = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            for nombre_categoria, filtro in categorias.items():
                df_filtrado = df[filtro]

                if df_filtrado.empty:
                    continue

                resumen = (
                    df_filtrado
                    .groupby("AÑO DE ACTIVACIÓN", dropna=False)
                    .agg({
                        "Activo fijo": "count",
                        "Val.adq.": "sum",
                        "Amo acum.": "sum",
                        "Val.cont.": "sum"
                    })
                    .reset_index()
                    .rename(columns={
                        "Activo fijo": "Cantidad de Activos"
                    })
                )

                # Total general
                total = pd.DataFrame({
                    "AÑO DE ACTIVACIÓN": ["TOTAL"],
                    "Cantidad de Activos": [resumen["Cantidad de Activos"].sum()],
                    "Val.adq.": [resumen["Val.adq."].sum()],
                    "Amo acum.": [resumen["Amo acum."].sum()],
                    "Val.cont.": [resumen["Val.cont."].sum()],
                })

                resumen_final = pd.concat([resumen, total], ignore_index=True)

                # Formato de números
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen_final[col] = resumen_final[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "-")

                resumen_final["Cantidad de Activos"] = resumen_final["Cantidad de Activos"].apply(
                    lambda x: f"{x:,.0f}" if pd.notnull(x) else "-"
                )

                # Mostrar resultado
                st.subheader(f"🔦 Resumen por Año - {nombre_categoria}")
                st.dataframe(
                    resumen_final.style
                    .apply(lambda x: ["background-color: #d4edda; font-weight: bold" if v == "TOTAL" else "" for v in x], 
                           subset=["AÑO DE ACTIVACIÓN"]),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
