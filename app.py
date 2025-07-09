import streamlit as st
import pandas as pd

# Fase 1: Configuración inicial
st.set_page_config(page_title="Análisis de Luminarias", layout="wide")
st.title("📊 Análisis de Base Capital - Luminarias LED")

# Subir archivo
archivo = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if archivo is not None:
    try:
        # Leer Excel
        df = pd.read_excel(archivo, engine="openpyxl")

        # Eliminar columna innecesaria llamada '2025' si existe
        df = df.drop(columns=["2025"], errors="ignore")

        # Renombrar columnas duplicadas
        df.columns = [f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                      for i, col in enumerate(df.columns)]

        # Validar columnas
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
            # Convertir columnas numéricas
            for col in ["AÑO DE ACTIVACIÓN", "Val.adq.", "Val.cont.", "Amo acum."]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Definir tipos de luminarias
            tipos = {
                "LED ALTA INTENSIDAD": df["Descripción SG"] == "LED ALTA INTENSIDAD",
                "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"] == "LUMINARIA BAJA INTENSIDAD",
                "Sin categoría (vacío)": df["Descripción SG"].isna()
            }

            for nombre, filtro in tipos.items():
                st.subheader(f"🔦 Resumen por Año - {nombre}")
                df_filtrado = df[filtro]

                # Agrupar y resumir
                resumen = (
                    df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
                        "Activo fijo": "count",
                        "Val.adq.": "sum",
                        "Amo acum.": "sum",
                        "Val.cont.": "sum"
                    }).reset_index()
                )
                resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

                # Agregar fila TOTAL
                fila_total = pd.DataFrame({
                    "AÑO DE ACTIVACIÓN": ["TOTAL"],
                    "Cantidad de Activos": [resumen["Cantidad de Activos"].sum()],
                    "Val.adq.": [resumen["Val.adq."].sum()],
                    "Amo acum.": [resumen["Amo acum."].sum()],
                    "Val.cont.": [resumen["Val.cont."].sum()],
                })

                resumen_total = pd.concat([resumen, fila_total], ignore_index=True)

                # Formatear columnas numéricas con comas
                for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
                    resumen_total[col] = resumen_total[col].apply(
                        lambda x: f"{x:,.2f}" if pd.notnull(x) else "-"
                    )
                resumen_total["Cantidad de Activos"] = resumen_total["Cantidad de Activos"].apply(
                    lambda x: f"{x:,}" if pd.notnull(x) else "-"
                )

                # Estilo con color para la fila TOTAL
                def resaltar_total(fila):
                    color = 'background-color: #d4edda; font-weight: bold;'
                    return [color if fila["AÑO DE ACTIVACIÓN"] == "TOTAL" else "" for _ in fila]

                st.dataframe(
                    resumen_total.style.apply(resaltar_total, axis=1),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")

else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")
