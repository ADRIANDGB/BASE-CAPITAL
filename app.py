import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        columnas_necesarias = ['Cantidad', 'Descripción SG', 'Val.adq.', 'Amo acum.', 'Val.cont.', 'AÑO DE ACTIVACIÓN']
        faltantes = [col for col in columnas_necesarias if col not in df.columns]
        if faltantes:
            st.error(f"❌ Faltan columnas necesarias: {faltantes}")
        else:
            for col in ['Cantidad', 'Val.adq.', 'Amo acum.', 'Val.cont.']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df['AÑO DE ACTIVACIÓN'] = pd.to_numeric(df['AÑO DE ACTIVACIÓN'], errors='coerce')
            df = df[df['AÑO DE ACTIVACIÓN'].notna()]
            df['AÑO DE ACTIVACIÓN'] = df['AÑO DE ACTIVACIÓN'].astype(int)

            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            all_resumenes = {}
            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_filtrado = df[filtro].copy()

                if df_filtrado.empty:
                    st.warning("No hay datos para esta categoría.")
                    continue

                resumen = df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                    "Cantidad": "sum",
                    "Val.adq.": "sum",
                    "Amo acum.": "sum",
                    "Val.cont.": "sum"
                }).reset_index()

                resumen = resumen.rename(columns={"Cantidad": "Cantidad de Activos"})

                totales = {
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
                    "Val.adq.": resumen["Val.adq."].sum(),
                    "Amo acum.": resumen["Amo acum."].sum(),
                    "Val.cont.": resumen["Val.cont."].sum()
                }
                resumen = pd.concat([resumen, pd.DataFrame([totales])], ignore_index=True)

                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)

                resumen["Cantidad de Activos"] = resumen["Cantidad de Activos"].apply(
                    lambda x: f"{x:,}" if isinstance(x, (int, float)) else x
                )

                def resaltar_total(fila):
                    if fila["AÑO DE ACTIVACIÓN"] == "TOTAL":
                        return ['background-color: #d4edda; font-weight: bold'] * len(fila)
                    else:
                        return [''] * len(fila)

                st.dataframe(
                    resumen.style.apply(resaltar_total, axis=1),
                    use_container_width=True
                )

                # Gráficas interactivas por tipo
                st.markdown("### 📈 Gráfica de evolución")

                df_numerico = df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                    "Cantidad": "sum",
                    "Val.adq.": "sum",
                    "Amo acum.": "sum",
                    "Val.cont.": "sum"
                }).reset_index()

                df_numerico = df_numerico[df_numerico["AÑO DE ACTIVACIÓN"] % 1 == 0]
                df_numerico = df_numerico.sort_values("AÑO DE ACTIVACIÓN")

                # Cálculo de porcentajes
                for col in ["Cantidad", "Val.adq.", "Amo acum.", "Val.cont."]:
                    total = df_numerico[col].sum()
                    df_numerico[col + " (%)"] = df_numerico[col] / total * 100

                variables = st.multiselect(
                    f"Selecciona variables para graficar - {nombre}",
                    ["Cantidad", "Val.adq.", "Amo acum.", "Val.cont."],
                    default=["Cantidad", "Val.adq."]
                )

                if variables:
                    fig = px.line(
                        df_numerico,
                        x="AÑO DE ACTIVACIÓN",
                        y=variables,
                        markers=True,
                        labels={"value": "Valor", "AÑO DE ACTIVACIÓN": "Año"},
                        hover_data={f"{var} (%)": True for var in variables},
                        title=f"📊 Evolución de {' y '.join(variables)} - {nombre}"
                    )
                    fig.update_traces(mode="lines+markers")
                    st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
