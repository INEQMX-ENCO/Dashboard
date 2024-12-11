import streamlit as st

# Configuración inicial de Streamlit
st.set_page_config(page_title="Dashboard Efecto Doña Florinda", layout="wide")

from PIL import Image
import base64

from utils.helpers.data_loader import load_estado_data, load_municipio_data, load_nacional_data, load_summary_cluster_data
from utils.helpers.helper import load_css
from utils.helpers.visualizations import graficar_deciles, graficar_percepciones, graficar_distribucion_gini, graficar_gini, graficar_ingresos_deciles, graficar_percepciones_economicas, graficar_consumo_ahorro
from utils.helpers.introduccion import mostrar_intro
from utils.helpers.dashboard import mostrar_dashboard_exploracion

import plotly.express as px

# Cargar estilos CSS
load_css("assets/styles.css")

# Cachear la carga de datos globales
@st.cache_data
def cargar_datos():
    return {
        "estados": load_estado_data(),
        "municipios": load_municipio_data(),
        "nacional": load_nacional_data(),
        "cluster": load_summary_cluster_data()
    }

# Clase principal para manejar la aplicación
class DashboardApp:
    def __init__(self):
        self.datos = cargar_datos()
        if "section" not in st.session_state:
            st.session_state["section"] = "Introducción"
        if "user_data" not in st.session_state:
            st.session_state["user_data"] = {}
        self.secciones = {
            "Introducción": self.mostrar_intro,
            "Cuestionario": self.mostrar_cuestionario,
            "Respuestas": self.mostrar_respuestas,
            "Clusters": self.mostrar_cluster,
            "Dashboard": self.mostrar_dashboard,
        }

    def navegacion_botones(self, seccion_actual):
        """Renderiza botones de navegación para moverse entre secciones."""
        secciones = list(self.secciones.keys())
        indice_actual = secciones.index(seccion_actual)
        
        col1, col2 = st.columns(2)

        # Botón de "Anterior"
        with col1:
            if indice_actual > 0:  # Mostrar si no estamos en la primera sección
                st.button(
                    "⬅️ Anterior",
                    on_click=self.set_section,
                    args=(secciones[indice_actual - 1],)
                )

        # Botón de "Siguiente"
        with col2:
            if indice_actual < len(secciones) - 1:  # Mostrar si no estamos en la última sección
                st.button(
                    "➡️ Siguiente",
                    on_click=self.set_section,
                    args=(secciones[indice_actual + 1],)
                )

    def set_section(self, section):
        """Callback para cambiar la sección."""
        st.session_state["section"] = section

    def render_sidebar(self):
        """Renderiza el sidebar con la navegación."""
        # Load the image and convert it to a base64 string
        image_path = "R.png"  # Path to your image
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()

        # HTML to center the title and image
        st.sidebar.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{encoded_image}" style="width:85px; margin-bottom:5px;">
                <h1 style="font-size:24px; margin-bottom:5px;">Efecto Doña Florinda</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.sidebar.markdown("---")
        st.sidebar.header("Navegación")

        for section, func in self.secciones.items():
            disabled = False
            if section == "Dashboard" and not st.session_state.get("user_data"):
                disabled = True
            st.sidebar.button(section, on_click=self.set_section, args=(section,), disabled=disabled)
            
        st.sidebar.markdown(f"### Estás en: **{st.session_state['section']}**")

        # Información adicional
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            """
            <div style="text-align: center;">
                <a href="https://github.com/INEQMX-ENCO/Dashboard" target="_blank">
                    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    def render_seccion(self):
        """Renderiza la sección seleccionada."""
        seccion_actual = self.secciones.get(st.session_state["section"])
        if seccion_actual:
            seccion_actual()
        else:
            st.error("Sección no encontrada.")

    # Secciones
    def mostrar_intro(self):
        mostrar_intro()
        # Botones de navegación
        self.navegacion_botones("Introducción")

    def mostrar_cuestionario(self):
        estados = self.datos["estados"]
        municipios = self.datos["municipios"]

        # Datos Básicos
        st.markdown("### 🧑 Datos Básicos")
        st.text_input("Nombre", key="nombre_input", help="Escribe tu nombre completo.")
        estado = st.selectbox("Selecciona tu estado", estados["estado"].unique(), key="estado_select")
        if estado:
            municipios_filtrados = municipios[municipios["estado"] == estado]["nombre_municipio"].str.upper().unique()
            st.selectbox("Selecciona tu municipio", municipios_filtrados, key="municipio_select")
        else:
            st.warning("Por favor, selecciona un estado para ver los municipios.")

        # Ingresos
        st.slider("Selecciona tus ingresos mensuales aproximados ($0 - $100,000)",
                min_value=0, max_value=100000, step=1000, value=5000, key="ingresos_select")

        # Percepciones Económicas
        st.markdown("### 💰 Percepciones Económicas")
        st.radio("¿Cómo percibes tu situación económica actual?", ["Positiva", "Neutra", "Negativa"], key="percepcion_personal")
        st.radio("¿Crees que tu situación económica mejorará en los próximos años?", ["Sí", "No"], key="mejora_personal")
        st.radio("¿Cómo percibes la economía del país actualmente?", ["Positiva", "Neutra", "Negativa"], key="percepcion_nacional")
        st.radio("¿Crees que la economía del país mejorará en los próximos años?", ["Sí", "No"], key="mejora_nacional")

        # Consumo y Ahorro
        st.markdown("### 💳 Consumo y Ahorro")
        st.radio("¿Consideras que puedes ahorrar parte de tus ingresos?", ["Sí", "No"], key="ahorro_radio")
        st.radio("¿Sientes que tu consumo ha disminuido en los últimos años?", ["Sí", "No"], key="consumo_radio")

        # Incertidumbre Económica
        st.markdown("### 🔮 Incertidumbre Económica")
        st.radio("¿Cómo calificarías la estabilidad de tu economía personal?", 
                ["Muy estable", "Estable", "Inestable", "Muy inestable"], key="incertidumbre_personal")
        st.radio("¿Cómo calificarías la estabilidad de la economía del país?", 
                ["Muy estable", "Estable", "Inestable", "Muy inestable"], key="incertidumbre_nacional")

        st.button("Enviar", on_click=self.enviar_respuestas)

    def enviar_respuestas(self):
        """Valida y procesa las respuestas del formulario con un spinner."""
        with st.spinner("Guardando tus respuestas..."):
            warnings = []
            if not st.session_state.get("nombre_input", "").strip():
                warnings.append("Por favor, ingresa tu nombre.")
            if not st.session_state.get("estado_select"):
                warnings.append("Por favor, selecciona tu estado.")
            if not st.session_state.get("municipio_select"):
                warnings.append("Por favor, selecciona tu municipio.")

            if warnings:
                for warning in warnings:
                    st.warning(warning)
                return

            # Guardar respuestas
            st.session_state["user_data"] = {
                "Nombre": st.session_state["nombre_input"],
                "Estado": st.session_state["estado_select"],
                "Municipio": st.session_state["municipio_select"],
                "Ingresos": st.session_state.get("ingresos_select", 15000),
                "Percepcion_Economica_Personal": st.session_state.get("percepcion_personal"),
                "Mejora_Economica_Personal": st.session_state.get("mejora_personal"),
                "Percepcion_Economica_Nacional": st.session_state.get("percepcion_nacional"),
                "Mejora_Economica_Nacional": st.session_state.get("mejora_nacional"),
                "Ahorro": st.session_state.get("ahorro_radio"),
                "Consumo": st.session_state.get("consumo_radio"),
                "Incertidumbre_Personal": st.session_state.get("incertidumbre_personal"),
                "Incertidumbre_Nacional": st.session_state.get("incertidumbre_nacional"),
            }
            st.success("¡Formulario guardado exitosamente!")
            self.set_section("Respuestas")

    def mostrar_respuestas(self):
        if "user_data" not in st.session_state or not st.session_state["user_data"]:
            st.warning("Por favor, completa primero el cuestionario para ver los resultados.")
            return

        user_data = st.session_state["user_data"]

        # Selección de año para el clúster
        st.markdown("### 📅 Selecciona el Año del Clúster")
        year = st.selectbox("Año del Clúster", options=["2022", "2020", "2018"], index=0)

        # Explicación sobre cambios por año
        st.markdown(
            """
            <p><i>Nota: Los clústeres pueden cambiar año con año debido a cambios en los datos económicos y sociales. 
            Si seleccionas un año diferente, puedes observar variaciones en el clúster de tu municipio.</i></p>
            """,
            unsafe_allow_html=True
        )

        # Buscar el clúster del municipio seleccionado
        municipio_data = self.datos["municipios"]
        municipio = user_data["Municipio"]
        estado = user_data["Estado"]

        municipio_cluster = municipio_data[
            (municipio_data["nombre_municipio"].str.upper() == municipio) &
            (municipio_data["estado"].str.upper() == estado) &
            (municipio_data["year"] == int(year))
        ]

        if municipio_cluster.empty:
            st.error(f"No se encontraron datos del clúster para tu municipio en el año {year}.")
            return

        # Extraer información del clúster y promedios
        cluster = municipio_cluster["Cluster"].values[0]
        cluster_data = municipio_data[(municipio_data["Cluster"] == cluster) & (municipio_data["year"] == int(year))]
        promedio_cluster = cluster_data.mean(numeric_only=True).to_dict()

        # Crear diccionario de deciles
        deciles = {
            f"Decil {i}": promedio_cluster.get(f"decil_{i}", 0) for i in range(1, 11)
        }

        # Analogía del clúster
        analogias = {
            1: "Doña Florinda: Los que tienen, pero quieren más.",
            2: "Quico: Los reyes inquietos.",
            3: "Don Ramón: Los que luchan y avanzan.",
            4: "El Chavo: Los que sobreviven con esperanza."
        }

        analogia = analogias.get(cluster, "Desconocido")
        st.markdown(f"### 📖 Analogía del Clúster: {analogia}")

        st.write(
            f"Tu municipio pertenece al clúster **{cluster}** para el año **{year}**. "
            f"Este clúster está representado por el personaje: **{analogia}**."
        )

        # Comparativa personalizada
        ingresos_usuario = user_data.get("Ingresos")
        ingresos_promedio = deciles.get("Decil 5")
        decil_1_cluster = deciles.get("Decil 1")
        decil_10_cluster = deciles.get("Decil 10")

        st.markdown("### 📊 Comparativa Personalizada")
        st.markdown(
            f"""
            <p>Tu ingreso mensual es de <b>${ingresos_usuario:,}</b>.</p>
            <p>En tu clúster para el año <b>{year}</b>:</p>
            <ul>
                <li>El decil 1 (los ingresos más bajos) reporta un promedio de <b>${decil_1_cluster:,.2f}</b>.</li>
                <li>El decil 10 (los ingresos más altos) alcanza <b>${decil_10_cluster:,.2f}</b>.</li>
                <li>El decil 5 (promedio) reporta ingresos mensuales de <b>${ingresos_promedio:,.2f}</b>.</li>
            </ul>
            <p>Esto significa que estás <b>{'por encima' if ingresos_usuario > ingresos_promedio else 'por debajo'}</b> del promedio del decil 5.</p>
            """,
            unsafe_allow_html=True
        )

        # Generar gráfica de deciles
        st.markdown("### 📈 Visualización de Comparación por Deciles")
        grafica_deciles = graficar_deciles(deciles, ingresos_usuario, titulo=f"Comparación de tu Ingreso con los Deciles del Clúster ({year})")
        st.plotly_chart(grafica_deciles, use_container_width=True)

        # Coeficiente GINI
        gini_municipio = municipio_cluster["gini"].values[0]

        # Texto explicativo sobre el coeficiente GINI
        st.markdown("### 📉 Análisis del Coeficiente GINI")
        html_gini = f"""
        <p>El coeficiente GINI es una medida de la desigualdad en los ingresos dentro de una población. 
        Este valor oscila entre 0 y 1, donde:</p>
        <ul>
            <li><b>0</b>: Indica igualdad perfecta (todos tienen los mismos ingresos).</li>
            <li><b>1</b>: Indica desigualdad máxima (una sola persona concentra todos los ingresos).</li>
        </ul>
        <p>En tu municipio, el coeficiente GINI es de <b>{gini_municipio:.3f}</b>. Esto significa que 
        la distribución de ingresos presenta un nivel {'alto' if gini_municipio > 0.4 else 'moderado' if gini_municipio > 0.3 else 'bajo'} de desigualdad.</p>
        """
        st.markdown(html_gini, unsafe_allow_html=True)

        # Gráfica de distribución del GINI
        st.markdown("### 📊 Distribución del Coeficiente GINI en Todos los Municipios")
        graficar_distribucion_gini(
            data=municipio_data[municipio_data["year"] == int(year)],
            gini_municipio=gini_municipio,
            nivel=f"Año {year}",
            bins=20
        )

        # Percepciones económicas
        percepcion_positiva_cluster = promedio_cluster.get("Percepcion_Economica_Personal_Positiva", 0)
        percepcion_negativa_cluster = promedio_cluster.get("Percepcion_Economica_Personal_Negativa", 0)
        percepcion_nacional_positiva_cluster = promedio_cluster.get("Percepcion_Naciona_Positiva", 0)
        percepcion_nacional_negativa_cluster = promedio_cluster.get("Percepcion_Nacional_Negativa", 0)

        percepcion_usuario = user_data.get("Percepcion_Economica_Personal", "Neutra")

        # Texto combinado para percepciones
        st.markdown("### 💭 Análisis de Percepciones Económicas")
        html_percepcion = f"""
        <p>En cuanto a tus percepciones económicas:</p>
        <ul>
            <li>Indicaste que tu percepción económica personal es <b>{percepcion_usuario.lower()}</b>.</li>
            <li>En tu clúster, un <b>{percepcion_positiva_cluster:.2f}%</b> de los encuestados tiene una percepción positiva personal, mientras que un <b>{percepcion_negativa_cluster:.2f}%</b> la considera negativa.</li>
            <li>Sobre la economía nacional, un <b>{percepcion_nacional_positiva_cluster:.2f}%</b> tiene una percepción positiva, y un <b>{percepcion_nacional_negativa_cluster:.2f}%</b> la percibe negativamente.</li>
        </ul>
        """
        st.markdown(html_percepcion, unsafe_allow_html=True)

        # Gráfico combinado para percepciones personales y nacionales
        categorias_percepcion_combined = {
            "Percepción Personal Positiva": "Percepcion_Economica_Personal_Positiva",
            "Percepción Personal Negativa": "Percepcion_Economica_Personal_Negativa",
            "Percepción Nacional Positiva": "Percepcion_Naciona_Positiva",
            "Percepción Nacional Negativa": "Percepcion_Nacional_Negativa"
        }
        st.markdown("### 📊 Distribución de Percepciones Económicas (Personales y Nacionales)")
        graficar_percepciones(
            categorias_percepcion=categorias_percepcion_combined,
            data=cluster_data,
            nivel=f"Clúster {cluster} ({year})"
        )

        # Consumo y ahorro
        consumo_usuario = "positivo" if user_data.get("Ahorro") == "Sí" else "restringido"
        consumo_ahorro_positivo_cluster = promedio_cluster.get("Consumo_Ahorro_Positivo", 0)
        consumo_ahorro_negativo_cluster = promedio_cluster.get("Consumo_Ahorro_Negativo", 0)

        html_consumo_ahorro = f"""
        <p>En términos de consumo y ahorro:</p>
        <ul>
            <li>Clasificaste tu consumo como <b>{consumo_usuario}</b>.</li>
            <li>En tu clúster, un <b>{consumo_ahorro_positivo_cluster:.2f}%</b> de los encuestados reportó consumo y ahorro positivos, mientras que un <b>{consumo_ahorro_negativo_cluster:.2f}%</b> enfrenta consumo restringido.</li>
        </ul>
        """
        st.markdown(html_consumo_ahorro, unsafe_allow_html=True)

        # Gráfico para consumo y ahorro
        categorias_consumo_ahorro = {
            "Ahorro Positivo": "Consumo_Ahorro_Positivo",
            "Consumo Restringido": "Consumo_Ahorro_Negativo"
        }
        st.markdown("### 📊 Distribución de Consumo y Ahorro")
        graficar_percepciones(
            categorias_percepcion=categorias_consumo_ahorro,
            data=cluster_data,
            nivel=f"Clúster {cluster} ({year})"
        )
        # Botones de navegación
        self.navegacion_botones("Respuestas")

    def mostrar_cluster(self):
        import pandas as pd

        st.title("📊 Dashboard: Análisis de Clústeres")
        st.markdown(
            """
            En esta sección, puedes seleccionar uno o más clústeres para comparar sus características.
            También puedes elegir comparar con el promedio de todos los clústeres.
            """
        )

        # Load cluster data
        cluster_data = self.datos["cluster"]

        # Aggregate cluster data to summarize relevant KPIs
        cluster_summary = cluster_data.groupby('Cluster').agg({
            'gini': 'mean',
            'decil_1': 'mean',
            'decil_10': 'mean',
            'Consumo_Ahorro_Negativo': 'mean',
            'Consumo_Ahorro_Positivo': 'mean',
            'Percepcion_Nacional_Negativa': 'mean',
            'Percepcion_Naciona_Positiva': 'mean',
            'Percepcion_Economica_Personal_Negativa': 'mean',
            'Percepcion_Economica_Personal_Positiva': 'mean'
        }).reset_index()

        # Add "Promedio" cluster
        promedio_row = cluster_summary.mean(numeric_only=True).to_dict()
        promedio_row["Cluster"] = "Promedio"
        cluster_summary = pd.concat([cluster_summary, pd.DataFrame([promedio_row])], ignore_index=True)

        # Map cluster IDs to analogies
        analogias = {
            1: "Doña Florinda",
            2: "Quico",
            3: "Don Ramón",
            4: "El Chavo",
            "Promedio": "Promedio"
        }
        cluster_summary["Cluster_Nombre"] = cluster_summary["Cluster"].map(analogias)

        # Select clusters
        clusters_seleccionados = st.multiselect(
            "Selecciona los clústeres para comparar:",
            cluster_summary["Cluster_Nombre"].unique(),
            default=["Promedio"]
        )

        # Filtrar los datos seleccionados
        cluster_summary_filtered = cluster_summary[
            cluster_summary["Cluster_Nombre"].isin(clusters_seleccionados)
        ]

        # Expander: 
        with st.expander("Recordatorio: ¿Qué representan los clústeres?"):
            st.markdown("""
            - **Doña Florinda**: Los que tienen, pero quieren más. Municipios con economías cómodas, pero con presión de mantener el nivel.
            - **Quico**: Los reyes inquietos. Municipios con altos ingresos, pero atrapados en la sociedad aspiracional.
            - **Don Ramón**: Los que luchan y avanzan. Municipios que representan la fuerza trabajadora y la resiliencia.
            - **El Chavo**: Los que sobreviven con esperanza. Municipios en economías de subsistencia con desafíos diarios.
            - **Promedio de Clústeres**: Valores promedio calculados de todos los clústeres.
            """)

        st.subheader("📊 Comparativa entre los Clústeres Seleccionados")

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(graficar_ingresos_deciles(cluster_summary_filtered, clusters_seleccionados))
            st.plotly_chart(graficar_gini(cluster_summary_filtered, clusters_seleccionados))
        with col2:
            st.plotly_chart(graficar_consumo_ahorro(cluster_summary_filtered, clusters_seleccionados))
            st.plotly_chart(graficar_percepciones_economicas(cluster_summary_filtered, clusters_seleccionados))

        # Conexión a la siguiente sección
        st.subheader("🔗 Explora Datos Personalizados en el Dashboard")
        st.markdown(
            """
            Ahora que hemos analizado los cambios en los clústeres y el Índice de GINI, puedes explorar todos los datos disponibles
            para cada municipio y año. Esto te permitirá realizar análisis personalizados y profundizar en las dinámicas económicas
            y sociales que afectan a cada región.
            """
        )
        # Botones de navegación
        self.navegacion_botones("Clusters")


    def mostrar_dashboard(self):

        mostrar_dashboard_exploracion(self.datos["municipios"], self.datos["estados"])
        # Botón para la sección anterior
        col1, col2 = st.columns(2)

        with col1:
            st.button("⬅️ Anterior", on_click=self.set_section, args=("Clusters",))

        with col2:
            st.button("🏠 Volver al Inicio", on_click=self.set_section, args=("Introducción",))

# Ejecución de la aplicación
app = DashboardApp()
app.render_sidebar()
app.render_seccion()
