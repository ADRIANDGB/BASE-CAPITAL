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
            # Limpieza de datos
            for col in ['Val.adq.', 'Amo acum.', 'Val.cont.']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df['AÑO DE ACTIVACIÓN'] = pd.to_numeric(df['AÑO DE ACTIVACIÓN'], errors='coerce')
            df = df[df['AÑO DE ACTIVACIÓN'].notna()].copy()
            df['AÑO DE ACTIVACIÓN'] = df['AÑO DE ACTIVACIÓN'].astype(int)

            # Clasificación
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper() == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper() == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            comparativo = []

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
                }).reset_index().rename(columns={"Activo fijo": "Cantidad de Activos"})

                # Guardar para comparativo
                temp = resumen.copy()
                temp["Tipo"] = nombre
                comparativo.append(temp)

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

                def estilo_total(fila):
                    if fila["AÑO DE ACTIVACIÓN"] == "TOTAL":
                        return ['background-color: #d4edda; font-weight: bold'] * len(fila)
                    return [''] * len(fila)

                st.dataframe(resumen.style.apply(estilo_total, axis=1), use_container_width=True)

                # Gráfico de evolución
                graf_data = df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                    "Cantidad de Activos": ("Activo fijo", "count"),
                    "Val.adq.": "sum",
                    "Val.cont.": "sum"
                }).reset_index()

                fig, ax1 = plt.subplots()
                ax1.plot(graf_data["AÑO DE ACTIVACIÓN"], graf_data["Val.adq."], label="Valor Adq.")
                ax1.plot(graf_data["AÑO DE ACTIVACIÓN"], graf_data["Val.cont."], label="Valor Contable")
                ax1.set_title(f"Evolución de Valores - {nombre}")
                ax1.set_xlabel("Año")
                ax1.set_ylabel("Valores")
                ax1.legend()
                st.pyplot(fig)

                fig2, ax2 = plt.subplots()
                ax2.bar(graf_data["AÑO DE ACTIVACIÓN"], graf_data["Cantidad de Activos"], color="skyblue")
                ax2.set_title(f"Cantidad de Activos - {nombre}")
                ax2.set_xlabel("Año")
                ax2.set_ylabel("Activos")
                st.pyplot(fig2)

            # Gráfico comparativo final
            if comparativo:
                st.subheader("📊 Comparación Final entre Tipos")

                df_comp = pd.concat(comparativo)
                fig, ax = plt.subplots()
                for tipo in df_comp["Tipo"].unique():
                    datos = df_comp[df_comp["Tipo"] == tipo]
                    ax.plot(datos["AÑO DE ACTIVACIÓN"], datos["Val.cont."], label=tipo)

                ax.set_title("Comparación de Valor Contable entre Tipos")
                ax.set_xlabel("Año")
                ax.set_ylabel("Valor Contable")
                ax.legend()
                st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
