import streamlit as st
import pandas as pd
import plotly.express as px

# Función para normalizar las columnas
def normalizar_columnas(data):
    columnas_renombradas = {
        "year": "Año",
        "estado": "Estado",
        "nombre_municipio": "Municipio",
        "municipio": "ID Municipio",
        "gini": "Coeficiente GINI",
        "decil_1": "Decil 1",
        "decil_2": "Decil 2",
        "decil_3": "Decil 3",
        "decil_4": "Decil 4",
        "decil_5": "Decil 5",
        "decil_6": "Decil 6",
        "decil_7": "Decil 7",
        "decil_8": "Decil 8",
        "decil_9": "Decil 9",
        "decil_10": "Decil 10",
        "Percepcion_Naciona_Positiva": "Percepción Económica Nacional (Positiva)",
        "Percepcion_Nacional_Negativa": "Percepción Económica Nacional (Negativa)",
        "Percepcion_Economica_Personal_Positiva": "Percepción Económica Personal (Positiva)",
        "Percepcion_Economica_Personal_Negativa": "Percepción Económica Personal (Negativa)",
        "Consumo_Ahorro_Positivo": "Consumo y Ahorro (Positivo)",
        "Consumo_Ahorro_Negativo": "Consumo y Ahorro (Negativo)",
    }
    return data.rename(columns=columnas_renombradas)

# Función para mostrar el dashboard de exploración
def mostrar_dashboard_exploracion(municipios_data, estados_data):
    # Normalizar columnas
    municipios_data = normalizar_columnas(municipios_data)
    estados_data = normalizar_columnas(estados_data)

    # Eliminar columnas irrelevantes
    columnas_eliminar = ["ingreso_promedio_total", "Unnamed: 0"]
    municipios_data = municipios_data.drop(columns=[col for col in columnas_eliminar if col in municipios_data.columns], errors="ignore")
    estados_data = estados_data.drop(columns=[col for col in columnas_eliminar if col in estados_data.columns], errors="ignore")

    st.title("📊 Dashboard Exploración de Datos")
    st.markdown("""
        Este dashboard permite explorar los datos económicos y sociales de los municipios y estados de México.
        Selecciona el nivel de análisis, el año, y utiliza los filtros para visualizar los datos relevantes.
    """)

    # Botón para limpiar filtros
    if st.button("🔄 Limpiar Filtros"):
        st.session_state["estados_seleccionados"] = []
        st.session_state["municipios_seleccionados"] = []
        st.session_state["year_seleccionado"] = 2018

    # Configuración inicial de Session State
    if "estados_seleccionados" not in st.session_state:
        st.session_state["estados_seleccionados"] = []
    if "municipios_seleccionados" not in st.session_state:
        st.session_state["municipios_seleccionados"] = []
    if "year_seleccionado" not in st.session_state:
        st.session_state["year_seleccionado"] = 2018

    # Selección del nivel de análisis
    nivel_analisis = st.radio("Nivel de Análisis", ["Estatal", "Municipal"], horizontal=True)

    # Selección del año
    year_seleccionado = st.selectbox(
        "Selecciona el Año",
        [2018, 2020, 2022],
        key="year_seleccionado"
    )

    if nivel_analisis == "Estatal":
        # Selección múltiple de estados
        estados_seleccionados = st.multiselect(
            "Selecciona Estados",
            estados_data["Estado"].unique(),
            key="estados_seleccionados"
        )

        # Filtrar datos para los estados seleccionados
        data_filtrada = estados_data[
            (estados_data["Estado"].isin(estados_seleccionados)) &
            (estados_data["Año"] == year_seleccionado)
        ]
        agrupador = "Estado"

    elif nivel_analisis == "Municipal":
        # Selección múltiple de estados
        estados_seleccionados = st.multiselect(
            "Selecciona Estados",
            municipios_data["Estado"].unique(),
            key="estados_seleccionados"
        )

        # Filtrar municipios disponibles
        municipios_disponibles = municipios_data[municipios_data["Estado"].isin(estados_seleccionados)]
        municipios_seleccionados = st.multiselect(
            "Selecciona Municipios",
            municipios_disponibles["Municipio"].unique(),
            key="municipios_seleccionados"
        )

        # Filtrar datos para los municipios seleccionados
        data_filtrada = municipios_disponibles[
            (municipios_disponibles["Municipio"].isin(municipios_seleccionados)) &
            (municipios_disponibles["Año"] == year_seleccionado)
        ]
        agrupador = "Municipio"

    # Filtro de columnas relevantes automáticamente
    columnas_relevantes = [
        col for col in data_filtrada.columns
        if not any(p in col.lower() for p in ["respuesta", "id municipio", "region", "cluster"])
    ]
    data_filtrada = data_filtrada[columnas_relevantes]

    # Filtro de columnas para la tabla
    st.subheader("📋 Información Seleccionada")
    columnas_disponibles = list(data_filtrada.columns)
    columnas_seleccionadas = st.multiselect("Selecciona las columnas a mostrar:", columnas_disponibles, default=columnas_disponibles)

    # Mostrar tabla filtrada
    if not data_filtrada.empty:
        st.write(f"**Datos filtrados para el nivel seleccionado ({year_seleccionado}):**")
        st.dataframe(data_filtrada[columnas_seleccionadas])
    else:
        st.warning("No hay datos disponibles para mostrar en la tabla.")

    # Gráfico 1: Coeficiente GINI
    st.subheader("📈 Coeficiente GINI")
    st.markdown("""
        El coeficiente GINI mide la desigualdad en los ingresos. 
        Un valor de GINI más alto indica mayor desigualdad. 
        Este gráfico compara el coeficiente GINI de los municipios o estados seleccionados.
    """)

    if not data_filtrada.empty:
        data_gini = data_filtrada.groupby(agrupador, as_index=False).agg({"Coeficiente GINI": "mean"})
        promedio_seleccionados = data_gini["Coeficiente GINI"].mean()
        promedio_global = estados_data["Coeficiente GINI"].mean() if nivel_analisis == "Estatal" else municipios_data["Coeficiente GINI"].mean()

        # Ordenar con los seleccionados al final y los promedios al inicio
        data_gini["Grupo"] = data_gini[agrupador].apply(lambda x: "Seleccionado" if x in (estados_seleccionados if nivel_analisis == "Estatal" else municipios_seleccionados) else "Otros")
        data_gini = data_gini.sort_values(by=["Grupo", "Coeficiente GINI"], ascending=[False, True]).reset_index(drop=True)

        fig_gini = px.bar(
            data_gini,
            x=agrupador,
            y="Coeficiente GINI",
            color="Grupo",
            color_discrete_map={"Seleccionado": "#636EFA", "Otros": "lightgray"},
            title=f"Coeficiente GINI por {agrupador} ({year_seleccionado})",
            labels={agrupador: nivel_analisis, "Coeficiente GINI": "GINI"}
        )
        fig_gini.add_hline(y=promedio_global, line_dash="dot", annotation_text=f"Promedio Global: {promedio_global:.2f}", line_color="red")
        fig_gini.add_hline(y=promedio_seleccionados, line_dash="dot", annotation_text=f"Promedio Seleccionados: {promedio_seleccionados:.2f}", line_color="green")
        fig_gini.update_layout(showlegend=False, xaxis_title=None)
        st.plotly_chart(fig_gini, use_container_width=True)

    # Gráfico 2: Distribución de Deciles
    st.subheader("📊 Distribución de Deciles")
    st.markdown("""
        Este gráfico muestra la distribución de los ingresos promedio divididos en deciles.
        - **Municipios o Estados Seleccionados**: Representados con líneas azules.
        - **Promedio Global**: Representado en rojo.
        - **Promedio Seleccionado**: Representado en verde.
    """)

    deciles = [f"Decil {i}" for i in range(1, 11)]
    if all(col in data_filtrada.columns for col in deciles):
        # Datos de los seleccionados
        seleccionados_data = data_filtrada.melt(
            id_vars=[agrupador],
            value_vars=deciles,
            var_name="Decil",
            value_name="Ingreso Promedio"
        )
        seleccionados_data["Grupo"] = seleccionados_data[agrupador]

        # Calcular los promedios seleccionados
        promedio_seleccionados = data_filtrada[deciles].mean().reset_index()
        promedio_seleccionados.columns = ["Decil", "Promedio Seleccionado"]

        # Calcular los promedios globales
        if nivel_analisis == "Municipal":
            promedio_global = municipios_data[municipios_data["Año"] == year_seleccionado][deciles].mean().reset_index()
        else:
            promedio_global = estados_data[estados_data["Año"] == year_seleccionado][deciles].mean().reset_index()
        promedio_global.columns = ["Decil", "Promedio Global"]

        # Graficar las líneas de los seleccionados
        fig_deciles = px.line(
            seleccionados_data,
            x="Decil",
            y="Ingreso Promedio",
            color="Grupo",
            title=f"Distribución de Deciles por {agrupador} ({year_seleccionado})",
            labels={"Ingreso Promedio": "Ingreso Promedio", "Grupo": "Seleccionado"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        # Añadir línea para el promedio seleccionado
        fig_deciles.add_scatter(
            x=promedio_seleccionados["Decil"],
            y=promedio_seleccionados["Promedio Seleccionado"],
            mode="lines+markers",
            line=dict(color="green", dash="solid"),
            name="Promedio Seleccionado"
        )

        # Añadir línea para el promedio global
        fig_deciles.add_scatter(
            x=promedio_global["Decil"],
            y=promedio_global["Promedio Global"],
            mode="lines+markers",
            line=dict(color="red", dash="solid"),
            name="Promedio Global"
        )

        # Ajustar diseño
        fig_deciles.update_layout(
            showlegend=True,
            xaxis_title="Decil",
            yaxis_title="Ingreso Promedio",
            hovermode="x unified"
        )

        # Mostrar el gráfico
        st.plotly_chart(fig_deciles, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para la distribución de deciles.")

    # Gráfico 3: Categorías Económicas
    st.subheader("📋 Categorías Económicas")
    st.markdown("""
        Este gráfico compara las percepciones económicas y los patrones de consumo y ahorro.
        Se muestran las barras de los valores seleccionados y dos líneas promedio:
        - **Promedio Global**: Línea roja.
        - **Promedio Seleccionado**: Línea verde.
    """)
    categorias = [
        "Percepción Económica Personal (Positiva)",
        "Percepción Económica Personal (Negativa)",
        "Percepción Económica Nacional (Positiva)",
        "Percepción Económica Nacional (Negativa)",
        "Consumo y Ahorro (Positivo)",
        "Consumo y Ahorro (Negativo)",
    ]
    categorias_disponibles = [cat for cat in categorias if cat in data_filtrada.columns]

    if categorias_disponibles:
        # Preparar los datos para las barras
        data_categorias = data_filtrada.melt(
            id_vars=[agrupador],
            value_vars=categorias_disponibles,
            var_name="Categoría",
            value_name="Porcentaje"
        )

        # Calcular los promedios seleccionados (solo los datos seleccionados)
        promedio_seleccionados = data_categorias.groupby("Categoría")["Porcentaje"].mean().reset_index(name="Promedio Seleccionados")

        # Calcular los promedios globales (todos los datos del DataFrame original)
        if nivel_analisis == "Municipal":
            promedio_global = municipios_data.melt(
                id_vars=["Municipio"],
                value_vars=categorias_disponibles,
                var_name="Categoría",
                value_name="Porcentaje"
            ).groupby("Categoría")["Porcentaje"].mean().reset_index(name="Promedio Global")
        else:
            promedio_global = estados_data.melt(
                id_vars=["Estado"],
                value_vars=categorias_disponibles,
                var_name="Categoría",
                value_name="Porcentaje"
            ).groupby("Categoría")["Porcentaje"].mean().reset_index(name="Promedio Global")

        # Unir los promedios para graficar las líneas
        lineas_promedio = promedio_seleccionados.merge(promedio_global, on="Categoría")

        # Graficar las barras de los valores individuales
        fig_categorias = px.bar(
            data_categorias,
            x="Categoría",
            y="Porcentaje",
            color=agrupador,
            barmode="group",
            title=f"Categorías Económicas por {agrupador} ({year_seleccionado})",
            color_discrete_map={"Seleccionado": "#636EFA", "Otros": "lightgray"}
        )

        # Añadir línea para el promedio seleccionado
        fig_categorias.add_scatter(
            x=lineas_promedio["Categoría"],
            y=lineas_promedio["Promedio Seleccionados"],
            mode="lines+markers",
            line=dict(color="green", dash="solid"),
            name="Promedio Seleccionado"
        )

        # Añadir línea para el promedio global
        fig_categorias.add_scatter(
            x=lineas_promedio["Categoría"],
            y=lineas_promedio["Promedio Global"],
            mode="lines+markers",
            line=dict(color="red", dash="solid"),
            name="Promedio Global"
        )

        # Ajustar diseño
        fig_categorias.update_layout(
            showlegend=True,
            xaxis_title=None,
            yaxis_title="Porcentaje (%)"
        )

        # Mostrar gráfico
        st.plotly_chart(fig_categorias, use_container_width=True)
    else:
        st.warning("No hay datos disponibles para las categorías económicas.")


