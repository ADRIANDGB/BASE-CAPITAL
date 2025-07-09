import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuración inicial
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

# Subir archivo
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo, engine="openpyxl")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Validar columnas necesarias
        columnas_necesarias = [
            'Activo fijo', 'Descripción SG', 'Val.adq.', 'Amo acum.', 'Val.cont.', 'AÑO DE ACTIVACIÓN'
        ]
        faltantes = [col for col in columnas_necesarias if col not in df.columns]
        if faltantes:
            st.error(f"❌ Faltan columnas necesarias: {faltantes}")
        else:
            # Convertir columnas numéricas
            for col in ['Val.adq.', 'Amo acum.', 'Val.cont.']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df['AÑO DE ACTIVACIÓN'] = pd.to_numeric(df['AÑO DE ACTIVACIÓN'], errors='coerce')
            df = df[df['AÑO DE ACTIVACIÓN'].notna()].copy()
            df['AÑO DE ACTIVACIÓN'] = df['AÑO DE ACTIVACIÓN'].astype(int)

            # Clasificación por tipo
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

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

                # Agregar fila de totales
                totales = {
                    "AÑO DE ACTIVACIÓN": "TOTAL",
                    "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
                    "Val.adq.": resumen["Val.adq."].sum(),
                    "Amo acum.": resumen["Amo acum."].sum(),
                    "Val.cont.": resumen["Val.cont."].sum()
                }
                resumen = pd.concat([resumen, pd.DataFrame([totales])], ignore_index=True)

                # Formatear números
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)

                resumen["Cantidad de Activos"] = resumen["Cantidad de Activos"].apply(
                    lambda x: f"{x:,}" if isinstance(x, (int, float)) else x
                )

                # Estilo para la fila TOTAL
                def resaltar_total(fila):
                    if fila["AÑO DE ACTIVACIÓN"] == "TOTAL":
                        return ['background-color: #d4edda; font-weight: bold'] * len(fila)
                    else:
                        return [''] * len(fila)

                st.dataframe(
                    resumen.style.apply(resaltar_total, axis=1),
                    use_container_width=True
                )

                # -----------------------------
                # Gráficos por categoría
                # -----------------------------
                graf_data = df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg(
                    Cantidad_de_Activos=("Activo fijo", "count"),
                    Val_adq=("Val.adq.", "sum"),
                    Val_cont=("Val.cont.", "sum")
                ).reset_index()

                # Gráfico de evolución de valores
                fig, ax1 = plt.subplots()
                ax1.plot(graf_data["AÑO DE ACTIVACIÓN"], graf_data["Val_adq"], label="Valor Adq.", marker='o')
                ax1.plot(graf_data["AÑO DE ACTIVACIÓN"], graf_data["Val_cont"], label="Valor Contable", marker='s')
                ax1.set_title(f"📈 Evolución de Valores - {nombre}")
                ax1.set_xlabel("Año")
                ax1.set_ylabel("Valores")
                ax1.legend()
                st.pyplot(fig)

                # Gráfico de cantidad de activos
                fig2, ax2 = plt.subplots()
                ax2.bar(graf_data["AÑO DE ACTIVACIÓN"], graf_data["Cantidad_de_Activos"], color="skyblue")
                ax2.set_title(f"📊 Cantidad de Activos - {nombre}")
                ax2.set_xlabel("Año")
                ax2.set_ylabel("Activos")
                st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
