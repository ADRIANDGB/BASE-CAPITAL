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

            resumenes_por_tipo = {}

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
                resumenes_por_tipo[nombre] = resumen.copy()

                # Totales
                totales = {
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
                    "Val.adq.": resumen["Val.adq."].sum(),
                    "Amo acum.": resumen["Amo acum."].sum(),
                    "Val.cont.": resumen["Val.cont."].sum()
                }
                resumen = pd.concat([resumen, pd.DataFrame([totales])], ignore_index=True)

                # Formateo
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
                    use_container_width=True,
                    height=300
                )

                # Gráficas interactivas por tipo
                st.markdown("### 📈 Gráfica de evolución")
                df_graf = resumenes_por_tipo[nombre].copy()

                for col in ["Cantidad de Activos", "Val.adq.", "Amo acum.", "Val.cont."]:
                    df_graf[col + " (%)"] = df_graf[col] / df_graf[col].sum() * 100

                variables = st.multiselect(
                    f"Selecciona variables para graficar - {nombre}",
                    ["Cantidad de Activos", "Val.adq.", "Amo acum.", "Val.cont."],
                    default=["Cantidad de Activos", "Val.adq."]
                )

                if variables:
                    fig = px.line(
                        df_graf,
                        x="AÑO DE ACTIVACIÓN",
                        y=variables,
                        markers=True,
                        labels={"value": "Valor", "AÑO DE ACTIVACIÓN": "Año"},
                        hover_data={f"{var} (%)": True for var in variables},
                        title=f"📊 Evolución de {' y '.join(variables)} - {nombre}"
                    )
                    fig.update_traces(mode="lines+markers")
                    st.plotly_chart(fig, use_container_width=True)

            # 🔄 COMPARATIVA FINAL
            st.markdown("---")
            st.header("📊 Comparativa general entre tipos")

            tipo_var = st.selectbox(
                "Selecciona la variable a comparar entre tipos:",
                ["Cantidad de Activos", "Val.adq.", "Amo acum.", "Val.cont."]
            )

            df_comparativo = pd.DataFrame()
            for tipo, df_tipo in resumenes_por_tipo.items():
                temp = df_tipo.copy()
                temp["Tipo"] = tipo
                df_comparativo = pd.concat([df_comparativo, temp], ignore_index=True)

            if not df_comparativo.empty:
                fig_comp = px.line(
                    df_comparativo,
                    x="AÑO DE ACTIVACIÓN",
                    y=tipo_var,
                    color="Tipo",
                    markers=True,
                    labels={"AÑO DE ACTIVACIÓN": "Año", tipo_var: "Valor"},
                    title=f"📈 Comparación entre tipos por '{tipo_var}'"
                )
                fig_comp.update_traces(mode="lines+markers")
                st.plotly_chart(fig_comp, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
