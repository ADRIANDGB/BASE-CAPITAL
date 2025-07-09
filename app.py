import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Validar columnas necesarias
        necesarias = ['Activo fijo', 'Descripción SG', 'Val.adq.', 'Amo acum.', 'Val.cont.', 'AÑO DE ACTIVACIÓN']
        faltan = [col for col in necesarias if col not in df.columns]
        if faltan:
            st.error(f"❌ Faltan columnas: {faltan}")
        else:
            # Preparar datos
            for col in ['Val.adq.', 'Amo acum.', 'Val.cont.']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df['AÑO DE ACTIVACIÓN'] = pd.to_numeric(df['AÑO DE ACTIVACIÓN'], errors='coerce')
            df = df[df['AÑO DE ACTIVACIÓN'].notna()]
            df = df[df['AÑO DE ACTIVACIÓN'] % 1 == 0]  # solo enteros
            df['AÑO DE ACTIVACIÓN'] = df['AÑO DE ACTIVACIÓN'].astype(int)

            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            resumen_global = []

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_tipo = df[filtro].copy()

                if df_tipo.empty:
                    st.warning("No hay datos para esta categoría.")
                    continue

                resumen = df_tipo.groupby("AÑO DE ACTIVACIÓN").agg({
                    "Activo fijo": "count",
                    "Val.adq.": "sum",
                    "Amo acum.": "sum",
                    "Val.cont.": "sum"
                }).reset_index()

                resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

                total = {
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
                    "Val.adq.": resumen["Val.adq."].sum(),
                    "Amo acum.": resumen["Amo acum."].sum(),
                    "Val.cont.": resumen["Val.cont."].sum()
                }
                resumen = pd.concat([resumen, pd.DataFrame([total])], ignore_index=True)

                def resaltar(fila):
                    return ['background-color: #d4edda; font-weight: bold'] * len(fila) if fila["AÑO DE ACTIVACIÓN"] == "TOTAL" else [''] * len(fila)

                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)
                resumen["Cantidad de Activos"] = resumen["Cantidad de Activos"].apply(lambda x: f"{x:,}" if isinstance(x, (int, float)) else x)

                st.dataframe(resumen.style.apply(resaltar, axis=1), use_container_width=True, height=250)

                # ---- GRÁFICA ----
                resumen_graf = resumen[resumen["AÑO DE ACTIVACIÓN"] != "TOTAL"].copy()
                resumen_graf["Categoría"] = nombre
                resumen_graf["AÑO DE ACTIVACIÓN"] = resumen_graf["AÑO DE ACTIVACIÓN"].astype(int)
                resumen_graf["Cantidad de Activos"] = resumen_graf["Cantidad de Activos"].apply(lambda x: int(str(x).replace(',', '')))
                resumen_graf["Val.adq."] = resumen_graf["Val.adq."].apply(lambda x: float(str(x).replace(',', '')))

                resumen_global.append(resumen_graf)

                # 🎛 Selectores personalizados
                st.markdown("### 📈 Gráfica de evolución")
                valor = st.selectbox(f"Selecciona qué valor mostrar para {nombre}", ["Cantidad de Activos", "Val.adq."], key=nombre)
                años = st.multiselect(f"Años a incluir ({nombre})", sorted(resumen_graf["AÑO DE ACTIVACIÓN"].unique()), default=sorted(resumen_graf["AÑO DE ACTIVACIÓN"].unique()), key=nombre+"años")
                data_filtrada = resumen_graf[resumen_graf["AÑO DE ACTIVACIÓN"].isin(años)]

                fig = px.line(
                    data_filtrada,
                    x="AÑO DE ACTIVACIÓN",
                    y=valor,
                    markers=True,
                    title=f"{valor} a lo largo de los años - {nombre}",
                    hover_name="Categoría"
                )
                fig.update_traces(mode='lines+markers')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            # GRÁFICO FINAL COMPARATIVO
            if resumen_global:
                df_final = pd.concat(resumen_global)
                fig_comp = px.line(
                    df_final,
                    x="AÑO DE ACTIVACIÓN",
                    y="Cantidad de Activos",
                    color="Categoría",
                    markers=True,
                    title="📊 Comparativo de Cantidad de Activos por Categoría",
                    hover_name="Categoría"
                )
                fig_comp.update_layout(height=400)
                st.plotly_chart(fig_comp, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
