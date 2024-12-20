# visualizations.py

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.cm
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.colors as mcolors


@st.cache_resource
def graficar_deciles(deciles, ingreso_usuario, titulo):
    fig = go.Figure()

    # Calcular diferencias con respecto al ingreso del usuario
    diferencias = {key: value - ingreso_usuario for key, value in deciles.items()}
    valores = list(diferencias.values())

    # Generar colores cálidos (rojo invertido y verde cálido)
    rojo_invertido = [mcolors.rgb2hex(matplotlib.cm.YlOrRd(1 - i / (len(valores) + 1))) for i in range(len(valores))]
    verde_calmado = [mcolors.rgb2hex(matplotlib.cm.YlGn(i / (len(valores) + 1))) for i in range(len(valores))]

    # Crear las barras con colores personalizados
    for i, (key, diferencia) in enumerate(diferencias.items()):
        color = verde_calmado[i] if diferencia > 0 else rojo_invertido[i]
        fig.add_trace(go.Bar(
            name=f"Decil {i + 1}",
            x=[key],
            y=[diferencia],
            text=f"{diferencia:+,.0f} MXN",
            textposition="outside",
            marker_color=color
        ))

    # Agregar línea base del usuario
    fig.add_trace(go.Scatter(
        name=f"Ingreso del Usuario (${ingreso_usuario:,.0f})",
        x=list(deciles.keys()),
        y=[0] * len(deciles),
        mode="lines",
        line=dict(color="brown", width=3, dash="dash"),
        showlegend=False
    ))

    # Ajustar rango dinámico para asegurar que la anotación sea visible
    max_valor = max(valores)
    min_valor = min(valores)
    margen = (abs(max_valor) + abs(min_valor)) * 0.1
    y_max = max_valor + margen
    y_min = min_valor - margen

    # Configurar anotación simplificada, movida a la derecha
    fig.update_layout(
        annotations=[
            dict(
                xref="paper",
                yref="y",
                x=1.05,  # Mover a la derecha, fuera de la gráfica
                y=0,  # Centrado en el eje Y
                text=(
                    f"<b style='font-size:16px; color:red;'>Ingreso del Usuario</b><br>"
                    f"<span style='font-size:16px; color:black;'>${ingreso_usuario:,.0f} MXN</span>"
                ),
                showarrow=False,  # Eliminar la flecha
                align="left",  # Alinear texto a la izquierda
                bordercolor="black",
                borderwidth=1,
                borderpad=5,
                bgcolor="rgba(255, 255, 255, 0.8)",
                font=dict(size=12)
            ),
        ],
        title=dict(
            text=titulo,
            x=0.5,
            xanchor="center",
            font=dict(size=18, color="black")
        ),
        xaxis=dict(
            title="Deciles de Ingreso",
            titlefont=dict(size=14),
            showticklabels=True,
            tickangle=0,
            automargin=True
        ),
        yaxis=dict(
            title="Diferencia de Ingresos ($)",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            range=[y_min, y_max],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="brown"
        ),
        barmode="relative"
    )

    return fig


@st.cache_resource
def graficar_percepciones(categorias_percepcion, data, nivel):
    """
    Genera un gráfico de barras que muestra la distribución de percepciones económicas.

    Parameters:
    - categorias_percepcion (dict): Diccionario que asocia categorías de percepciones con las columnas en el DataFrame.
    - data (pd.DataFrame): DataFrame que contiene los datos de percepciones.
    - nivel (str): Nivel de agregación (e.g., Nacional, Estatal, Municipal).

    Returns:
    - None: Renderiza el gráfico directamente en Streamlit.
    """
    # Crear un gráfico de barras con las percepciones
    fig = go.Figure()
    for categoria, columna in categorias_percepcion.items():
        if columna in data.columns:
            fig.add_trace(go.Bar(
                name=categoria,
                x=[nivel],
                y=[data[columna].mean()],
                text=[f"{data[columna].mean():.2f}%"],
                textposition="auto"
            ))
    
    fig.update_layout(
        title=f"Distribución de Percepciones Económicas - {nivel}",
        xaxis_title="Nivel",
        yaxis_title="Porcentaje (%)",
        barmode="group",
    )
    st.plotly_chart(fig)

@st.cache_resource
def graficar_distribucion_gini(data, gini_municipio, nivel, bins=20):
    """
    Genera un gráfico que muestra la distribución del coeficiente GINI
    para todos los municipios y resalta el GINI del municipio seleccionado.

    Parameters:
    - data (pd.DataFrame): Datos con la columna "gini".
    - gini_municipio (float): GINI del municipio seleccionado.
    - nivel (str): Nivel o descripción del gráfico.
    - bins (int): Número de bins para el histograma.

    Returns:
    - None: Renderiza el gráfico directamente en Streamlit.
    """
    # Crear el histograma con Plotly
    fig = px.histogram(
        data,
        x="gini",
        nbins=bins,
        title=f"Distribución del GINI ({nivel})",
        color_discrete_sequence=["#4CAF50"]  # Verde suave
    )
    
    # Ajustar etiquetas dinámicamente
    fig.update_traces(
        texttemplate="%{y}",  # Mostrar las frecuencias en las barras
        textposition="outside"
    )
    
    # Agregar línea vertical para el GINI del municipio
    fig.add_shape(
        type="line",
        x0=gini_municipio, x1=gini_municipio,
        y0=0, y1=1,  # De 0 al 100% del rango del eje Y
        xref="x",  # Referencia al eje X
        yref="paper",  # Referencia a todo el rango del papel (gráfico)
        line=dict(color="blue", width=3, dash="dash")  # Línea azul discontinua
    )
    
    # Agregar anotación para el GINI del municipio
    fig.add_annotation(
        x=gini_municipio,
        y=1.05,  # Justo por encima del rango del gráfico
        text=(
            f"<b style='font-size:16px; color:blue;'>GINI Municipio</b><br>"
            f"<span style='font-size:16px; color:black;'>{gini_municipio:,.3f}</span>"
        ),
        showarrow=False,
        font=dict(size=12, color="blue"),
        bgcolor="rgba(255, 255, 255, 0.8)",
        borderwidth=1,
        borderpad=4,
    )
    
    # Configuración de ejes y diseño
    fig.update_layout(
        xaxis=dict(
            title="GINI",
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Frecuencia",
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        title=dict(
            x=0.5,
            xanchor="center",
            font=dict(size=18, color="black")
        ),
        bargap=0.2,  # Espacio entre las barras
        plot_bgcolor="rgba(245, 245, 245, 1)",  # Fondo claro
        margin=dict(t=50, b=50, l=50, r=50)  # Márgenes uniformes
    )
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


'''------------------DASHBOARD-------------------------'''
@st.cache_resource
def ajustar_rango_y(fig, max_value, margen=0.15):
    """
    Ajusta el rango del eje Y para evitar que los valores altos se corten.
    """
    # Asegurar que el rango sea ajustado de manera consistente
    if max_value > 0:
        fig.update_yaxes(range=[0, max_value * (1 + margen)])
    else:
        fig.update_yaxes(range=[0, 1])  # Configuración predeterminada para valores bajos o nulos
    return fig

@st.cache_resource
def graficar_ingresos_deciles(data, clusters_seleccionados):
    import plotly.express as px

    melted_data = data.melt(id_vars=["Cluster_Nombre"], value_vars=["decil_1", "decil_10"])
    max_value = melted_data["value"].max()

    fig = px.bar(
        data_frame=melted_data,
        x="variable",
        y="value",
        color="Cluster_Nombre",
        color_discrete_sequence=px.colors.qualitative.Set2,
        barmode="group",
        labels={"value": "Ingreso Mensual (MXN)", "variable": "Decil"},
        title="Comparativa de Ingresos Decil 1 y Decil 10",
    )

    fig.update_layout(
        xaxis_title="Decil",
        yaxis_title="Ingreso Mensual (MXN)",
        legend_title="Clúster",
        font=dict(size=14),
        plot_bgcolor="rgba(245, 245, 245, 1)",
        margin=dict(t=50),
    )
    fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside", cliponaxis=False)
    return ajustar_rango_y(fig, max_value)

@st.cache_resource
def graficar_gini(df_clusters, clusters_seleccionados):
    import plotly.graph_objects as go

    # Filter only the selected clusters
    filtered_clusters = df_clusters[df_clusters["Cluster_Nombre"].isin(clusters_seleccionados)]

    # Maximum GINI value for scaling
    max_value = filtered_clusters["gini"].max()

    # Create a bar chart
    fig = go.Figure()

    # Add bars for each cluster
    for _, row in filtered_clusters.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Cluster_Nombre"]],
            y=[row["gini"]],
            text=f"{row['gini']:.2f}",
            textposition="outside",
            marker_color=px.colors.qualitative.Set2[filtered_clusters.index.get_loc(_)],
            name=row["Cluster_Nombre"]
        ))

    # Update layout
    fig.update_layout(
        title="Índice GINI por Clúster",
        xaxis=dict(
            title="Clúster",
            tickangle=45,
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title="Índice GINI",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            range=[0, max_value * 1.15]  # Add 15% margin for text outside the bars
        ),
        barmode="group",
        legend_title="Clúster",
        plot_bgcolor="rgba(245, 245, 245, 1)",
        margin=dict(t=50, b=50, l=50, r=50),
    )

    return fig


@st.cache_resource
def graficar_percepciones_economicas(data, clusters_seleccionados):
    import plotly.express as px

    percepciones = [
        "Percepcion_Economica_Personal_Positiva",
        "Percepcion_Economica_Personal_Negativa",
        "Percepcion_Naciona_Positiva",
        "Percepcion_Nacional_Negativa",
    ]

    melted_data = data.melt(id_vars=["Cluster_Nombre"], value_vars=percepciones)
    max_value = melted_data["value"].max()

    fig = px.bar(
        data_frame=melted_data,
        x="variable",
        y="value",
        color="Cluster_Nombre",
        color_discrete_sequence=px.colors.qualitative.Set2,
        barmode="group",
        labels={"value": "Porcentaje (%)", "variable": "Percepción"},
        title="Comparativa de Percepciones Económicas",
    )

    fig.update_layout(
        xaxis_title="Percepción Económica",
        yaxis_title="Porcentaje (%)",
        legend_title="Clúster",
        font=dict(size=14),
        plot_bgcolor="rgba(245, 245, 245, 1)",
        margin=dict(t=50),
    )
    fig.update_traces(
        texttemplate="%{y:.2f}%",
        textposition="outside",
        cliponaxis=False,
    )
    return ajustar_rango_y(fig, max_value)

@st.cache_resource
def graficar_consumo_ahorro(data, clusters_seleccionados):
    import plotly.express as px

    consumo_ahorro = [
        "Consumo_Ahorro_Negativo",
        "Consumo_Ahorro_Positivo",
    ]

    melted_data = data.melt(id_vars=["Cluster_Nombre"], value_vars=consumo_ahorro)
    max_value = melted_data["value"].max()

    fig = px.bar(
        data_frame=melted_data,
        x="variable",
        y="value",
        color="Cluster_Nombre",
        color_discrete_sequence=px.colors.qualitative.Set2,
        barmode="group",
        labels={"value": "Porcentaje (%)", "variable": "Consumo/Ahorro"},
        title="Comparativa de Consumo y Ahorro",
    )

    fig.update_layout(
        xaxis_title="Consumo y Ahorro",
        yaxis_title="Porcentaje (%)",
        legend_title="Clúster",
        font=dict(size=14),
        plot_bgcolor="rgba(245, 245, 245, 1)",
        margin=dict(t=50),
    )
    fig.update_traces(
        texttemplate="%{y:.2f}%",
        textposition="outside",
        cliponaxis=False,
    )
    return ajustar_rango_y(fig, max_value)
