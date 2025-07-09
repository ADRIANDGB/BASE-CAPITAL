import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        columnas_necesarias = [
            'Activo fijo', 'Descripción SG', 'Val.adq.', 'Amo acum.', 'Val.cont.', 'AÑO DE ACTIVACIÓN'
        ]
        faltantes = [col for col in columnas_necesarias if col not in df.columns]
        if faltantes:
            st.error(f"❌ Faltan columnas necesarias: {faltantes}")
        else:
            for col in ['Val.adq.', 'Amo acum.', 'Val.cont.']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df['AÑO DE ACTIVACIÓN'] = pd.to_numeric(df['AÑO DE ACTIVACIÓN'], errors='coerce')
            df = df[df['AÑO DE ACTIVACIÓN'].notna()].copy()
            df['AÑO DE ACTIVACIÓN'] = df['AÑO DE ACTIVACIÓN'].astype(int)

            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            columnas_graficas = ["Cantidad de Activos", "Val.adq.", "Amo acum.", "Val.cont."]

            comparativos = {}

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_filtrado = df[filtro].copy()

                if df_filtrado.empty:
                    st.warning("No hay datos para esta categoría.")
                    continue

                resumen = df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                    "Activo fijo": "count",
                    "Val.adq.": "sum",
                    "Amo acum.": "sum",
                    "Val.cont.": "sum"
                }).reset_index()

                resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

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
                    use_container_width=False, height=250
                )

                # Gráficas
                st.markdown("### 🖌️ Gráfica de evolución")
                valor = st.selectbox(f"Selecciona qué valor mostrar para {nombre}", columnas_graficas, key=nombre)

                resumen_graf = df_filtrado.groupby("AÑO DE ACTIVACIÓN")[valor].sum().reset_index()

                fig = px.line(resumen_graf, x="AÑO DE ACTIVACIÓN", y=valor,
                              title=f"{valor} a lo largo de los años - {nombre}", markers=True)
                st.plotly_chart(fig, use_container_width=True)

                # Pie Chart
                st.markdown("### 🍌 Distribución por Año (Pie Chart)")
                fig_pie = px.pie(resumen_graf, names="AÑO DE ACTIVACIÓN", values=valor, title=f"Distribución de {valor} por Año")
                st.plotly_chart(fig_pie, use_container_width=True)

                comparativos[nombre] = resumen_graf.set_index("AÑO DE ACTIVACIÓN")[valor]

            if comparativos:
                st.markdown("## 🌐 Comparativo entre tipos de luminarias")
                df_comp = pd.DataFrame(comparativos).reset_index()
                fig = px.line(df_comp, x="AÑO DE ACTIVACIÓN", y=df_comp.columns[1:],
                              title="Comparación entre tipos por Año", markers=True)
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
