import streamlit as st
import pandas as pd

# Configuración de la página
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

        # Eliminar columnas innecesarias (como la llamada '2025' si aparece)
        df = df.drop(columns=["2025"], errors="ignore")

        # Validación de columnas necesarias
        columnas_necesarias = [
            'Activo fijo', 'Val.adq.', 'Amo acum.', 'Val.cont.',
            'Descripción SG', 'AÑO DE ACTIVACIÓN'
        ]
        faltantes = [col for col in columnas_necesarias if col not in df.columns]

        if faltantes:
            st.error(f"❌ Faltan columnas requeridas: {faltantes}")
        else:
            # Limpieza y conversión
            df["AÑO DE ACTIVACIÓN"] = pd.to_numeric(df["AÑO DE ACTIVACIÓN"], errors="coerce").astype("Int64")
            df["Val.adq."] = pd.to_numeric(df["Val.adq."], errors="coerce")
            df["Amo acum."] = pd.to_numeric(df["Amo acum."], errors="coerce")
            df["Val.cont."] = pd.to_numeric(df["Val.cont."], errors="coerce")

            df = df[df["AÑO DE ACTIVACIÓN"].notna()]

            # Estándar de categorías
            df["Descripción SG"] = df["Descripción SG"].astype(str).str.strip().str.upper()

            categorias = {
                "LED ALTA INTENSIDAD": df["Descripción SG"] == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"] == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isin(["NAN", ""])  # Vacíos reales o textos vacíos
            }

            for nombre, filtro in categorias.items():
                df_cat = df[filtro]

                if df_cat.empty:
                    continue

                resumen = (
                    df_cat.groupby("AÑO DE ACTIVACIÓN", dropna=False)
                    .agg({
                        "Activo fijo": "count",
                        "Val.adq.": "sum",
                        "Amo acum.": "sum",
                        "Val.cont.": "sum"
                    })
                    .reset_index()
                    .rename(columns={"Activo fijo": "Cantidad de Activos"})
                )

                # Agregar fila de totales
                total = pd.DataFrame({
                    "AÑO DE ACTIVACIÓN": ["TOTAL"],
                    "Cantidad de Activos": [resumen["Cantidad de Activos"].sum()],
                    "Val.adq.": [resumen["Val.adq."].sum()],
                    "Amo acum.": [resumen["Amo acum."].sum()],
                    "Val.cont.": [resumen["Val.cont."].sum()]
                })

                resumen = pd.concat([resumen, total], ignore_index=True)

                # Formatear
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "-")

                resumen["Cantidad de Activos"] = resumen["Cantidad de Activos"].apply(
                    lambda x: f"{x:,.0f}" if pd.notnull(x) else "-"
                )

                # Mostrar tabla
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                st.dataframe(
                    resumen.style
                    .apply(lambda x: ['background-color: #d4edda; font-weight: bold' if v == "TOTAL" else "" for v in x],
                           subset=["AÑO DE ACTIVACIÓN"]),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
