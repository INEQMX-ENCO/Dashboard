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
            name=f"Decil {i + 1}",  # Nombre de la barra
            x=[key],  # Nombre del decil en eje X
            y=[diferencia],  # Diferencia en eje Y
            text=f"{diferencia:+,.0f} MXN",  # Texto con diferencia formateada
            textposition="outside",  # Posición del texto fuera de las barras
            marker_color=color
        ))

    # Agregar línea base del usuario
    fig.add_trace(go.Scatter(
        name=f"Ingreso del Usuario (${ingreso_usuario:,.0f})",
        x=list(deciles.keys()),  # Línea a lo largo de los deciles
        y=[0] * len(deciles),  # Línea en 0
        mode="lines",
        line=dict(color="brown", width=3, dash="dash"),
        showlegend=False  # Elimina la leyenda para esta traza
    ))

    # Ajustar rango dinámico para asegurar que la anotación sea visible
    max_valor = max(valores)
    min_valor = min(valores)
    margen = (abs(max_valor) + abs(min_valor)) * 0.1  # Margen dinámico (10% del rango total)
    y_max = max_valor + margen
    y_min = min_valor - margen

    # Configurar anotación simplificada
    fig.update_layout(
        annotations=[
            dict(
                xref="paper",  # Referencia al espacio del gráfico
                yref="y",  # Referencia al eje Y
                x=0.05,  # Pegado a la izquierda (1% desde el borde izquierdo)
                y=0,  # Posición en el eje Y = 0
                text=(
                    f"<b style='font-size:16px; color:red;'>Ingreso del Usuario</b><br>"
                    f"<span style='font-size:16px; color:black;'>${ingreso_usuario:,.0f} MXN</span>"
                ),
                showarrow=True,  # Mostrar flecha
                arrowhead=2,  # Tipo de flecha
                arrowcolor="red",  # Color de la flecha
                ax=50,  # Desplazamiento horizontal desde el texto
                ay=-50,  # Flecha apuntando hacia abajo
                align="left",  # Alineado a la izquierda
            ),
        ],
        title=dict(
            text=titulo,
            x=0.5,  # Centrar título
            xanchor="center",
            font=dict(size=18, color="black")
        ),
        xaxis=dict(
            title="Deciles de Ingreso",
            titlefont=dict(size=14),
            showticklabels=False,
            tickangle=0,  # Asegura que los ticks estén horizontalmente alineados
            automargin=True  # Ajusta automáticamente el margen para evitar que los ticks se corten
        ),
        yaxis=dict(
            title="Diferencia de Ingresos ($)",
            titlefont=dict(size=14),
            tickfont=dict(size=12),
            range=[y_min, y_max],  # Asegura que la anotación y las etiquetas sean visibles
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

def graficar_distribucion_gini(data, nivel, bins=20):
    # Calcular el promedio del GINI
    promedio_gini = data["gini"].mean()

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
    
    # Agregar línea vertical para el promedio
    fig.add_shape(
        type="line",
        x0=promedio_gini, x1=promedio_gini,
        y0=0, y1=1,  # De 0 al 100% del rango del eje Y
        xref="x",  # Referencia al eje X
        yref="paper",  # Referencia a todo el rango del papel (gráfico)
        line=dict(color="red", width=2, dash="dash")  # Línea roja discontinua
    )
    
    # Agregar anotación para el promedio
    fig.add_annotation(
        x=promedio_gini,
        y=1.05,  # Justo por encima del rango del gráfico
        text=(
                    f"<b style='font-size:16px; color:red;'>GINI Promedio</b><br>"
                    f"<span style='font-size:16px; color:black;'>{promedio_gini:,.3f}</span>"
                ),
        showarrow=False,
        font=dict(size=12, color="red"),
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
        margin=dict(t=50, b=50, l=50, r=50)  # Margenes uniformes
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


def ajustar_rango_y(fig, max_value, margen=0.15):
    """
    Ajusta el rango del eje Y para evitar que los valores altos se corten.
    """
    fig.update_yaxes(range=[0, max_value * (1 + margen)])
    return fig


def graficar_ingresos_promedio(df_clusters, cluster_seleccionado):
    color_map = {cluster: "lightgray" for cluster in df_clusters["Cluster"]}
    color_map[cluster_seleccionado] = "orange"  # Resalta el cluster seleccionado

    fig = px.bar(
        df_clusters,
        x="Cluster",
        y="Ingreso Promedio",
        title="Ingresos Promedio por Cluster",
        text="Ingreso Promedio",
        labels={"Ingreso Promedio": "Ingreso Promedio ($)", "Cluster": "Clusters"},
        color="Cluster",
        color_discrete_map=color_map,
    )
    fig.update_traces(texttemplate="$%{text:,}", textposition="outside")
    max_value = df_clusters["Ingreso Promedio"].max()
    return ajustar_rango_y(fig, max_value)


def graficar_gini(df_clusters, cluster_seleccionado):
    color_map = {cluster: "lightgray" for cluster in df_clusters["Cluster"]}
    color_map[cluster_seleccionado] = "blue"  # Resalta el cluster seleccionado

    fig = px.bar(
        df_clusters,
        x="Cluster",
        y="GINI",
        title="Índice GINI por Cluster",
        text="GINI",
        labels={"GINI": "Índice GINI", "Cluster": "Clusters"},
        color="Cluster",
        color_discrete_map=color_map,
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    max_value = df_clusters["GINI"].max()
    return ajustar_rango_y(fig, max_value)


def graficar_percepciones_negativas(df_clusters, cluster_seleccionado):
    color_map = {cluster: "lightgray" for cluster in df_clusters["Cluster"]}
    color_map[cluster_seleccionado] = "green"  # Resalta el cluster seleccionado

    fig = px.bar(
        df_clusters,
        x="Cluster",
        y="Percepción Negativa",
        title="Percepción Económica Negativa por Cluster",
        text="Percepción Negativa",
        labels={"Percepción Negativa": "Percepción Económica Negativa (%)", "Cluster": "Clusters"},
        color="Cluster",
        color_discrete_map=color_map,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    max_value = df_clusters["Percepción Negativa"].max()
    return ajustar_rango_y(fig, max_value)


def graficar_consumo_restringido(df_clusters, cluster_seleccionado):
    color_map = {cluster: "lightgray" for cluster in df_clusters["Cluster"]}
    color_map[cluster_seleccionado] = "purple"  # Resalta el cluster seleccionado

    fig = px.bar(
        df_clusters,
        x="Cluster",
        y="Consumo Restringido",
        title="Consumo Restringido por Cluster",
        text="Consumo Restringido",
        labels={"Consumo Restringido": "Consumo Restringido (%)", "Cluster": "Clusters"},
        color="Cluster",
        color_discrete_map=color_map,
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    max_value = df_clusters["Consumo Restringido"].max()
    return ajustar_rango_y(fig, max_value)
