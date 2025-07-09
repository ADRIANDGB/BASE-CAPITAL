import streamlit as st
import pandas as pd

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

                # Mostrar tabla con estilo
                st.dataframe(
                    resumen.style.apply(resaltar_total, axis=1),
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
else:
    st.info("📂 Sube un archivo Excel con tus luminarias para comenzar.")










#-------------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt

# Fase 5: Sidebar para selección
st.sidebar.header("🎚️ Opciones de visualización")

# Lista de categorías disponibles dinámicamente
categorias_disponibles = {
    "LED ALTA INTENSIDAD": df["Descripción SG"].str.upper().eq("LED ALTA INTENSIDAD"),
    "LUMINARIA BAJA INTENSIDAD": df["Descripción SG"].str.upper().eq("LUMINARIA BAJA INTENSIDAD"),
    "Sin categoría (vacío)": df["Descripción SG"].isna()
}

# Selección desde sidebar
categoria_seleccionada = st.sidebar.selectbox("📂 Escoge una categoría de luminaria", list(categorias_disponibles.keys()))
tipo_grafico = st.sidebar.radio("📊 Tipo de gráfico", ["Resumen tabular", "Evolución de valores", "Cantidad de activos"])

# Aplicar filtro
df_filtrado = df[categorias_disponibles[categoria_seleccionada]].copy()

if df_filtrado.empty:
    st.warning("No hay datos disponibles para esta categoría.")
else:
    resumen = df_filtrado.groupby("AÑO DE ACTIVACIÓN").agg({
        "Activo fijo": "count",
        "Val.adq.": "sum",
        "Amo acum.": "sum",
        "Val.cont.": "sum"
    }).reset_index()

    resumen = resumen.rename(columns={"Activo fijo": "Cantidad de Activos"})

    # Agregar totales
    total = {
        "AÑO DE ACTIVACIÓN": "TOTAL",
        "Cantidad de Activos": resumen["Cantidad de Activos"].sum(),
        "Val.adq.": resumen["Val.adq."].sum(),
        "Amo acum.": resumen["Amo acum."].sum(),
        "Val.cont.": resumen["Val.cont."].sum()
    }
    resumen = pd.concat([resumen, pd.DataFrame([total])], ignore_index=True)

    # Formato
    for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
        resumen[col] = resumen[col].apply(lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else x)
    resumen["Cantidad de Activos"] = resumen["Cantidad de Activos"].apply(
        lambda x: f"{x:,}" if isinstance(x, (int, float)) else x
    )

    # Mostrar tabla
    if tipo_grafico == "Resumen tabular":
        def resaltar_total(fila):
            if fila["AÑO DE ACTIVACIÓN"] == "TOTAL":
                return ['background-color: #d4edda; font-weight: bold'] * len(fila)
            return [''] * len(fila)

        st.subheader(f"📄 Resumen de: {categoria_seleccionada}")
        st.dataframe(
            resumen.style.apply(resaltar_total, axis=1),
            use_container_width=True
        )

    # Mostrar gráfico de evolución de valores
    elif tipo_grafico == "Evolución de valores":
        resumen_graf = resumen[resumen["AÑO DE ACTIVACIÓN"] != "TOTAL"].copy()
        resumen_graf["AÑO DE ACTIVACIÓN"] = resumen_graf["AÑO DE ACTIVACIÓN"].astype(int)
        for col in ["Val.adq.", "Amo acum.", "Val.cont."]:
            resumen_graf[col] = resumen_graf[col].replace({",": ""}, regex=True).astype(float)

        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.plot(resumen_graf["AÑO DE ACTIVACIÓN"], resumen_graf["Val.adq."], marker='o', label="Val. Adq.")
        ax1.plot(resumen_graf["AÑO DE ACTIVACIÓN"], resumen_graf["Amo acum."], marker='o', label="Amortización")
        ax1.plot(resumen_graf["AÑO DE ACTIVACIÓN"], resumen_graf["Val.cont."], marker='o', label="Val. Cont.")
        ax1.set_title(f"Evolución de Valores - {categoria_seleccionada}")
        ax1.set_xlabel("Año")
        ax1.set_ylabel("Monto (USD)")
        ax1.grid(True)
        ax1.legend()
        st.pyplot(fig1)

    # Mostrar gráfico de cantidad de activos
    elif tipo_grafico == "Cantidad de activos":
        resumen_graf = resumen[resumen["AÑO DE ACTIVACIÓN"] != "TOTAL"].copy()
        resumen_graf["AÑO DE ACTIVACIÓN"] = resumen_graf["AÑO DE ACTIVACIÓN"].astype(int)
        resumen_graf["Cantidad de Activos"] = resumen_graf["Cantidad de Activos"].replace({",": ""}, regex=True).astype(int)

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(resumen_graf["AÑO DE ACTIVACIÓN"], resumen_graf["Cantidad de Activos"], color="#4CAF50")
        ax2.set_title(f"Cantidad de Activos por Año - {categoria_seleccionada}")
        ax2.set_xlabel("Año")
        ax2.set_ylabel("Cantidad")
        ax2.grid(axis='y')
        st.pyplot(fig2)

