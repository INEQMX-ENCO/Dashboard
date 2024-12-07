import streamlit as st

# Configuración inicial de Streamlit
st.set_page_config(page_title="Dashboard Efecto Doña Florinda", layout="wide")

from utils.helpers.data_loader import load_estado_data, load_municipio_data, load_nacional_data
from utils.helpers.helper import load_css
from utils.helpers.visualizations import graficar_deciles, graficar_percepciones, graficar_distribucion_gini, graficar_consumo_restringido, graficar_gini, graficar_ingresos_promedio, graficar_percepciones_negativas
from utils.helpers.introduccion import mostrar_intro
from utils.helpers.dashboard import mostrar_dashboard_exploracion

# Cargar estilos CSS
load_css("assets/styles.css")

# Cachear la carga de datos globales
@st.cache_data
def cargar_datos():
    return {
        "estados": load_estado_data(),
        "municipios": load_municipio_data(),
        "nacional": load_nacional_data(),
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

    def set_section(self, section):
        """Callback para cambiar la sección."""
        st.session_state["section"] = section

    def render_sidebar(self):
        """Renderiza el sidebar con la navegación."""
        st.sidebar.image("assets\R.png", width=120)
        st.sidebar.title("Navegación")
        for section in self.secciones.keys():
            st.sidebar.button(section, on_click=self.set_section, args=(section,))
        st.sidebar.markdown(f"### Estás en: **{st.session_state['section']}**")


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

        # Percepción Económica
        st.markdown("### 💰 Percepción Económica")
        st.radio("¿Cómo percibes tu situación económica actual?", ["Positiva", "Neutra", "Negativa"], key="percepcion_personal")
        st.radio("¿Crees que ha mejorado en los últimos años?", ["Sí", "No"], key="mejora_personal")
        st.radio("¿Cómo percibes la economía del país?", ["Positiva", "Neutra", "Negativa"], key="percepcion_nacional")
        st.radio("¿Crees que ha mejorado en los últimos años?", ["Sí", "No"], key="mejora_nacional")
        st.radio("¿Consideras que puedes ahorrar parte de tus ingresos?", ["Sí", "No"], key="ahorro_radio")
        st.radio("¿Sientes que tu consumo ha disminuido en los últimos años?", ["Sí", "No"], key="consumo_radio")

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

            st.session_state["user_data"] = {
                "Nombre": st.session_state["nombre_input"],
                "estado": st.session_state["estado_select"],
                "municipio": st.session_state["municipio_select"],
                "Ingresos": st.session_state.get("ingresos_select", 15000),
                "Percepcion_Economica_Personal": st.session_state.get("percepcion_personal"),
                "Mejora_Economica_Personal": st.session_state.get("mejora_personal"),
                "Percepcion_Economica_Nacional": st.session_state.get("percepcion_nacional"),
                "Mejora_Economica_Nacional": st.session_state.get("mejora_nacional"),
                "Ahorro": st.session_state.get("ahorro_radio"),
                "Consumo": st.session_state.get("consumo_radio"),
            }
            st.success("¡Formulario guardado exitosamente!")
            self.set_section("Respuestas")

    def mostrar_respuestas(self):
        if st.session_state["user_data"]:
            self.mostrar_comparaciones(
                st.session_state["user_data"],
                self.datos["estados"],
                self.datos["municipios"],
                self.datos["nacional"],
            )
        else:
            st.warning("Por favor, completa primero el cuestionario para ver los resultados.")

    def mostrar_comparaciones(self, usuario, estado_data, municipio_data, nacional_data):
        with st.spinner("Cargando comparaciones..."):
            st.subheader("📊 Comparación con datos reales")
            st.markdown("""
            Explora cómo se posicionan tus ingresos y percepciones económicas en relación con los datos promedio nacionales, estatales y municipales.
            """)

            col1, col2 = st.columns(2)
            with col1:
                tipo_comparativa = st.radio("Selecciona el nivel de comparación", ["Nacional", "Estatal", "Municipal"])
            with col2:
                years_disponibles = nacional_data["year"].unique()
                year_seleccionado = st.select_slider("Selecciona el año", options=sorted(years_disponibles), value=sorted(years_disponibles)[-1])
            
            if tipo_comparativa == "Nacional":
                self.procesar_comparativa(usuario, nacional_data, year_seleccionado, "nacional", "Deciles Nacionales")
                self.comparar_gini(nacional_data, "Nivel Nacional")
                self.comparar_percepciones(nacional_data, "Nivel Nacional")
            elif tipo_comparativa == "Estatal" and not estado_data.empty:
                self.procesar_comparativa(usuario, estado_data, year_seleccionado, "estatal", "Deciles Estatales")
                self.comparar_gini(estado_data, "Nivel Estatal")
                self.comparar_percepciones(estado_data, "Nivel Estatal")
            elif tipo_comparativa == "Municipal" and not municipio_data.empty:
                self.procesar_comparativa(usuario, municipio_data, year_seleccionado, "municipal", "Deciles Municipales")
                self.comparar_gini(municipio_data, "Nivel Municipal")
                self.comparar_percepciones(municipio_data, "Nivel Municipal")
            else:
                st.warning("No hay datos disponibles para la selección realizada.")
            # Texto de transición hacia la sección de clusters
            st.markdown(
                """
                ---
                ### 🔍 ¿Qué nos dicen los datos agrupados?

                Hasta ahora hemos explorado cómo se distribuyen los ingresos, la desigualdad, y las percepciones económicas. 
                Sin embargo, detrás de estos datos existen patrones comunes que conectan a diferentes municipios según 
                sus características económicas, sociales y culturales.

                En la siguiente sección, descubriremos los **clusters**, o grupos de municipios con similitudes marcadas. 
                Cada cluster cuenta una historia distinta sobre cómo se vive la economía en México. 
                ¿A cuál grupo pertenece tu municipio?
                """
            )
            
            st.button("Clusters:", on_click=self.set_section, args=("Clusters",))

    def comparar_gini(self, data, nivel):
        gini_value = data["gini"].mean()
        gini_max = data["gini"].max()
        gini_min = data["gini"].min()

        st.subheader(f"📈 Coeficiente GINI ({nivel})")
        st.markdown(
            f"""
            En este nivel, el **promedio del coeficiente GINI** es de **{gini_value:.2f}**, una medida que 
            captura la desigualdad en la distribución del ingreso. 

            - El **GINI más alto**, de **{gini_max:.2f}**, refleja zonas de alta desigualdad, donde los ingresos están 
              altamente concentrados en pocos grupos.
            - El **GINI más bajo**, de **{gini_min:.2f}**, representa áreas más equitativas, donde los ingresos se distribuyen 
              de manera más uniforme.

            En este gráfico, puedes ver cómo la desigualdad varía en diferentes regiones, destacando la diversidad económica del {nivel.lower()}.
            """
        )
        graficar_distribucion_gini(data, nivel)

    def comparar_percepciones(self, data, nivel):
        """Compara las percepciones económicas del encuestado con los datos agregados."""
        st.subheader(f"📋 Comparación de Percepciones Económicas ({nivel})")
        st.markdown(
            """
            Más allá de los números, las percepciones económicas cuentan una historia sobre cómo las personas sienten y experimentan la economía. 
            Este gráfico divide las percepciones en categorías clave, mostrando si las personas en {nivel.lower()} ven su situación económica 
            como positiva, negativa, o neutra.
            
            Observa cómo estas percepciones cambian dependiendo del contexto social y económico:
            
            - **Económica Personal:** ¿Cómo evalúan su bienestar personal?
            - **Económica Nacional:** ¿Qué tan optimistas son sobre la economía del país?
            - **Consumo/Ahorro:** ¿Qué tanto han podido ahorrar o gastar libremente?
            """
        )
        
        categorias_percepcion = {
            "Económica Personal (Positiva)": "Percepcion_Economica_Personal_Positiva",
            "Económica Personal (Negativa)": "Percepcion_Economica_Personal_Negativa",
            "Económica Nacional (Positiva)": "Percepcion_Nacional_Positiva",
            "Económica Nacional (Negativa)": "Percepcion_Nacional_Negativa",
            "Consumo/Ahorro (Positivo)": "Consumo_Ahorro_Positivo",
            "Consumo/Ahorro (Negativo)": "Consumo_Ahorro_Negativo",
            "Incertidumbre Económica (Personal)": "Incertidumbre_Economica_Personal",
            "Incertidumbre Económica (Nacional)": "Incertidumbre_Economica_Nacional",
        }

        graficar_percepciones(categorias_percepcion, data, nivel)

    def procesar_comparativa(self, usuario, data, year, tipo, titulo):
        deciles = self.obtener_deciles(data, year)
        decil_usuario = self.calcular_decil_usuario(usuario["Ingresos"], deciles)
        st.markdown(
            f"""
            **Tus ingresos:** Con un ingreso de **${usuario['Ingresos']:,.2f}**, te encuentras en el **Decil {decil_usuario}** 
            en el nivel {tipo.lower()} seleccionado.

            Los deciles dividen a la población en 10 grupos según sus ingresos. 
            El primer decil representa al 10% con los ingresos más bajos, mientras que el décimo decil agrupa al 10% más rico. 

            Este gráfico te muestraS que tan lejos o que tan cerca estas de cada decil, destacando la diversidad de ingresos en {tipo.lower()}.
            """
        )
        fig = graficar_deciles(deciles, usuario["Ingresos"], f"Comparación de {titulo} con el Usuario")
        st.plotly_chart(fig)

    @st.cache_data
    def obtener_deciles(_self, data, year):
        data_filtrada = data[data["year"] == year]
        return {f"decil_{i}": data_filtrada[f"decil_{i}"].mean() for i in range(1, 11)}

    @st.cache_data
    def calcular_decil_usuario(_self, ingreso_usuario, deciles):
        for i in range(1, 11):
            if ingreso_usuario <= float(deciles.get(f"decil_{i}", float("inf"))):
                return i
        return 10

    def mostrar_cluster(self):
        import pandas as pd

        st.title("📊 Dashboard: Análisis de Clusters")
        st.markdown(
            """
            En esta sección, exploraremos los clusters identificados en el análisis. 
            Estos clusters agrupan municipios según sus características económicas, sociales y culturales, 
            ofreciendo una visión más profunda de las dinámicas económicas en México.
            """
        )

        # Explicación de Clusters
        with st.expander("¿Qué son los clusters?"):
            st.markdown(
                """
                Los clusters son grupos de municipios que comparten características similares en términos de ingresos, desigualdad, 
                y percepciones económicas. Este enfoque permite identificar patrones clave y diferencias entre regiones, 
                ayudando a comprender mejor las dinámicas económicas del país.
                """
            )

        # Datos de los Clusters
        cluster_data = {
            "Cluster 1": {"Ingreso Promedio": 27537, "GINI": 0.37, "Percepción Negativa": 16.8, "Consumo Restringido": 49.2},
            "Cluster 2": {"Ingreso Promedio": 81224, "GINI": 0.39, "Percepción Negativa": 24.8, "Consumo Restringido": 46.6},
            "Cluster 3": {"Ingreso Promedio": 19457, "GINI": 0.36, "Percepción Negativa": 15.3, "Consumo Restringido": 37.3},
            "Cluster 4": {"Ingreso Promedio": 13752, "GINI": 0.39, "Percepción Negativa": 23.0, "Consumo Restringido": 63.0},
        }

        df_clusters = pd.DataFrame(cluster_data).T.reset_index().rename(columns={"index": "Cluster"})

        # Selección de Cluster
        cluster_seleccionado = st.selectbox(
            "Selecciona un cluster para destacar en las gráficas:",
            list(cluster_data.keys())
        )

        # Detalle del Cluster Seleccionado
        st.subheader(f"🔍 Detalle del {cluster_seleccionado}")
        st.markdown(f"""
            El cluster **{cluster_seleccionado}** muestra las siguientes características destacadas:
            - Ingreso Promedio: ${cluster_data[cluster_seleccionado]['Ingreso Promedio']:,.0f} trimestrales.
            - Índice GINI: {cluster_data[cluster_seleccionado]['GINI']}.
            - Percepción Económica Negativa: {cluster_data[cluster_seleccionado]['Percepción Negativa']}%.
            - Consumo Restringido: {cluster_data[cluster_seleccionado]['Consumo Restringido']}%.
        """)

        # Graficar Comparativas
        st.subheader("📊 Comparativas Generales entre Clusters")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(graficar_ingresos_promedio(df_clusters, cluster_seleccionado))
            st.plotly_chart(graficar_gini(df_clusters, cluster_seleccionado))
        with col2:
            st.plotly_chart(graficar_percepciones_negativas(df_clusters, cluster_seleccionado))
            st.plotly_chart(graficar_consumo_restringido(df_clusters, cluster_seleccionado))
        # Conexión a la siguiente sección
        st.subheader("🔗 Conexión entre Clusters y Variaciones en el Índice de GINI")
        # Transición a la exploración general
        st.markdown(
            """
            Ahora que hemos analizado los cambios en los clusters y el Índice de GINI, puedes explorar todos los datos disponibles
            para cada municipio y año. Esto te permitirá realizar análisis personalizados y profundizar en las dinámicas económicas
            y sociales que afectan a cada región.
            """
        )
        st.button("Ir al Dashboard", on_click=self.set_section, args=("Dashboard",))

    def mostrar_dashboard(self):

        mostrar_dashboard_exploracion(self.datos["municipios"], self.datos["estados"])

# Ejecución de la aplicación
app = DashboardApp()
app.render_sidebar()
app.render_seccion()
