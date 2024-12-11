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
            if section == "Respuestas" and not st.session_state.get("user_data"):
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
        
        # Al final de mostrar_respuestas
        # Al final de la sección del cuestionario
        st.markdown("---")  # Línea divisoria para separar visualmente
        st.markdown(
            """
            <div style="background-color:#F1F8E9;padding:15px;border-radius:10px;margin-top:20px;">
                <h4 style="text-align:center;color:#2E7D32;">📝 Descubre los Resultados</h4>
                <p style="text-align:center;">
                    En la siguiente sección, exploraremos a qué <b>clúster económico</b> pertenece tu municipio basado en los datos que proporcionaste.
                </p>
                <p style="text-align:center;">
                    También analizaremos cómo se compara tu ingreso con los deciles de ingresos de tu municipio, proporcionándote una <b>visión personalizada</b> de tu situación económica.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")  # Línea divisoria para separar visualmente

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
            <p><i>Nota: La colocacion de clústeres pueden cambiar año con año debido a cambios en los datos económicos y sociales. 
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

        # Comparativa personalizada
        ingresos_usuario = user_data.get("Ingresos")

        # Mostrar datos del municipio
        decil_1_municipio = municipio_cluster["decil_1"].values[0]
        decil_5_municipio = municipio_cluster["decil_5"].values[0]
        decil_10_municipio = municipio_cluster["decil_10"].values[0]
        gini_municipio = municipio_cluster["gini"].values[0]

        # Resumen del municipio y clúster
        st.markdown(
            f"""
            <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #f9f9f9;">
                <h2 style="color: #4CAF50; text-align: center;">📝 Resumen para tu Municipio</h2>
                <p style="font-size: 18px; text-align: center;">
                    En el año <b style="color: #2196F3;">{year}</b>, tu municipio <b style="color: #FF9800;">{municipio}</b> pertenece al clúster de:
                </p>
                <div style="margin-top: 20px; text-align: center;">
                    <h1 style="font-size: 24px; color: #FF5722;">{analogias.get(cluster, "Desconocido")}</h1>
                </div>
                <div style="margin-top: 20px; text-align: center;">
                    <p style="font-size: 14px; color: #757575;">
                        Este clúster refleja las características económicas, sociales y culturales de municipios similares al tuyo. 
                        A continuación, exploraremos los datos específicos de tu municipio.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # Resumen económico del municipio
        st.markdown(
            f"""
            <div style="background-color:#F1F8E9;padding:15px;border-radius:10px;margin-bottom:20px;">
                <h3 style="text-align:center;color:#2E7D32;">📊 Resumen Económico del Municipio</h3>
                <p style="text-align:center;">Datos específicos para tu municipio en el año seleccionado:</p>
                <ul style="list-style:none;padding:0;margin:0;text-align:center;">
                    <li style="margin-bottom:15px;">
                        <b style="font-size:18px;color:#4CAF50;">Decil 1:</b> 
                        <span style="font-size:16px;color:#616161;">${decil_1_municipio:,.2f}</span>
                    </li>
                    <li style="margin-bottom:15px;">
                        <b style="font-size:18px;color:#FFC107;">Decil 5 (Promedio):</b> 
                        <span style="font-size:16px;color:#616161;">${decil_5_municipio:,.2f}</span>
                    </li>
                    <li style="margin-bottom:15px;">
                        <b style="font-size:18px;color:#FF5722;">Decil 10:</b> 
                        <span style="font-size:16px;color:#616161;">${decil_10_municipio:,.2f}</span>
                    </li>
                    <li style="margin-bottom:15px;">
                        <b style="font-size:18px;color:#1976D2;">Índice GINI:</b> 
                        <span style="font-size:16px;color:#616161;">{gini_municipio:.3f}</span>
                    </li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 📊 Comparativa Personalizada")

        st.markdown(
            f"""
            <p>Tu ingreso mensual reportado es de <b>${ingresos_usuario:,}</b>.</p>
            <p>Comparado con el promedio del decil 5 en <b style="color: #FF9800;">{municipio}</b>, estás <b>{'por encima de la media' if ingresos_usuario > decil_5_municipio else 'por debajo de la media'}</b>.</p>
            <p>La siguiente gráfica muestra cómo se ubica tu ingreso en comparación con los diez deciles de ingresos registrados en <b style="color: #FF9800;">{municipio}</b>.</p>
            """,
            unsafe_allow_html=True
        )

        # Generar gráfica de deciles
        st.markdown("### 📈 Visualización de Comparación por Deciles")

        # Gráfica de deciles del municipio
        deciles_municipio = {
            f"Decil {i}": municipio_cluster[f"decil_{i}"].values[0] for i in range(1, 11)
        }
        grafica_deciles = graficar_deciles(
            deciles_municipio,
            ingresos_usuario,
            titulo=f"Comparación de tu Ingreso con los Deciles del Municipio ({year})"
        )
        st.plotly_chart(grafica_deciles, use_container_width=True)

        with st.expander("¿Qué representan los deciles y la línea roja?"):
            st.markdown(
                """
                <p>Los deciles dividen la población en diez grupos iguales según ingreso:</p>
                <ul>
                    <li><b>Decil 1:</b> El 10% con los ingresos más bajos.</li>
                    <li><b>Decil 10:</b> El 10% con los ingresos más altos.</li>
                </ul>
                <p>La línea punteada roja (eje 0) muestra tu ingreso. Las barras indican:</p>
                <ul>
                    <li><b>Encima:</b> Ingresos promedio del decil mayores que los tuyos.</li>
                    <li><b>Debajo:</b> Ingresos promedio del decil menores que los tuyos.</li>
                </ul>
                """,
                unsafe_allow_html=True
            )


        # Coeficiente GINI
        gini_municipio = municipio_cluster["gini"].values[0]

        # Texto explicativo sobre el coeficiente GINI
        st.markdown("### 📉 Análisis del Coeficiente GINI")

        html_gini = f"""
        <p>El coeficiente GINI en tu municipio es de <b>{gini_municipio:.3f}</b>, indicando un nivel de desigualdad en los ingresos clasificado como 
        <b>{'alto' if gini_municipio > 0.4 else 'moderado' if gini_municipio > 0.3 else 'bajo'}</b>.</p>
        <p>Este valor refleja cómo se distribuyen los ingresos entre los habitantes de tu municipio: 
        un valor más cercano a 0 indica mayor igualdad, mientras que un valor cercano a 1 refleja una mayor concentración de riqueza en pocas manos.</p>
        """
        st.markdown(html_gini, unsafe_allow_html=True)

        # Expander:
        with st.expander("¿Qué es y como se calucula el coeficiente GINI?"):
            st.markdown(
                """
                <p>El coeficiente GINI es una medida ampliamente utilizada para evaluar la desigualdad en la distribución de ingresos dentro de una población. 
                Este valor se sitúa entre <b>0</b> y <b>1</b>, donde:</p>
                <ul>
                    <li><b>0</b>: Representa igualdad perfecta, es decir, todos los individuos tienen los mismos ingresos.</li>
                    <li><b>1</b>: Representa desigualdad máxima, donde una sola persona concentra todos los ingresos.</li>
                </ul>
                <p>El cálculo del coeficiente GINI se basa en la <b>curva de Lorenz</b>, que compara la distribución acumulativa de los ingresos 
                frente a una línea de igualdad perfecta:</p>
                <ul>
                    <li>Se ordenan a los individuos por nivel de ingreso de menor a mayor.</li>
                    <li>Se calcula el porcentaje acumulativo de ingresos para cada grupo (por ejemplo, deciles).</li>
                    <li>La desviación entre la curva de Lorenz y la línea de igualdad se utiliza para calcular el GINI.</li>
                </ul>
                <p>Los <b>deciles</b> son herramientas clave en este cálculo. Dividen la población en 10 grupos iguales según nivel de ingreso, 
                ayudando a identificar cómo se distribuyen los recursos:</p>
                <ul>
                    <li><b>Decil 1:</b> Representa al 10% más pobre de la población.</li>
                    <li><b>Decil 10:</b> Representa al 10% más rico de la población.</li>
                </ul>
                <p>Una mayor desigualdad en los deciles (por ejemplo, si el decil 10 concentra una proporción desproporcionada del ingreso total) 
                resulta en un coeficiente GINI más alto.</p>
                <p>En resumen, el GINI es un indicador crucial para entender no solo cuánto gana una población en promedio, sino cómo 
                se distribuye esa riqueza entre sus habitantes.</p>
                """,
                unsafe_allow_html=True
            )

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

        # Expander: Explicación sobre la categorización de percepciones
        with st.expander("¿Cómo se categorizaron las percepciones?"):
            st.markdown(
                """
                <p>Las percepciones se clasificaron en categorías tomando como base las respuestas a la encuesta ENCO:</p>
                <ul>
                    <li><b>Percepción Económica Personal Positiva:</b> Respuestas optimistas sobre su situación económica personal.</li>
                    <li><b>Percepción Económica Personal Negativa:</b> Respuestas que reflejan preocupación o insatisfacción económica personal.</li>
                    <li><b>Percepción Nacional Positiva:</b> Opiniones optimistas sobre la economía del país.</li>
                    <li><b>Percepción Nacional Negativa:</b> Respuestas que indican incertidumbre o descontento con la economía nacional.</li>
                </ul>
                <p>Estas categorías se construyeron al agrupar las respuestas individuales en función de su tono y enfoque.</p>
                """,
                unsafe_allow_html=True
            )

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

        # Al final de mostrar_respuestas
        st.markdown("---")  # Línea divisoria para separar visualmente
        st.markdown(
            """
            <div style="background-color:#E3F2FD;padding:15px;border-radius:10px;margin-top:20px;">
                <h4 style="text-align:center;color:#0D47A1;">🔍 Explora Comparaciones entre Clústeres</h4>
                <p style="text-align:center;">
                    En la siguiente sección, podrás visualizar cómo se comparan los <b>promedios de los clústeres</b> en términos de ingresos, desigualdad y percepciones económicas.
                </p>
                <p style="text-align:center;">
                    Esta comparación te permitirá entender las <b>dinámicas generales</b> y cómo diferentes clusters se posicionan frente a otros clusters.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")  # Línea divisoria para separar visualmente
        # Botones de navegación
        self.navegacion_botones("Respuestas")

    def mostrar_cluster(self):
        import pandas as pd

        st.title("📊 Análisis de Clústeres")
        st.markdown(
            """
            <div style="background-color:#E3F2FD;padding:15px;border-radius:10px;margin-bottom:20px;">
                <h4 style="text-align:center;color:#0D47A1;">🔍 ¿Qué son los clústeres?</h4>
                <p style="text-align:justify;font-size:16px;">
                    Los clústeres son agrupaciones de municipios con características socioeconómicas similares. 
                    Estas agrupaciones ayudan a identificar patrones compartidos y diferencias entre localidades que 
                    enfrentan retos y oportunidades parecidos. A diferencia de la sección anterior, aquí analizamos 
                    <b>grupos de municipios</b> en lugar de datos individuales de un solo municipio.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("🧐 ¿Por qué comparar clústeres?"):
            st.markdown(
                """
                Comparar clústeres nos permite:
                - Identificar similitudes y diferencias entre grupos de municipios.
                - Analizar cómo factores como ingresos, consumo y percepción económica varían entre clústeres.
                - Comprender cómo se comportan los municipios similares en un contexto más amplio.
                """
            )

        st.markdown(
            """
            <div style="background-color:#F1F8E9;padding:15px;border-radius:10px;margin-bottom:20px;">
                <h4 style="text-align:center;color:#2E7D32;">🛠️ ¿Qué encontrarás aquí?</h4>
                <p style="text-align:justify;font-size:16px;">
                    En esta sección, puedes explorar las diferencias entre clústeres en términos de:
                </p>
                <ul>
                    <li>Distribución de ingresos por deciles.</li>
                    <li>Índice GINI (desigualdad).</li>
                    <li>Percepciones económicas.</li>
                </ul>
                <p style="text-align:justify;font-size:16px;">
                    También puedes comparar los datos de los clústeres seleccionados con el <b>promedio general de todos los clústeres</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True
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

        with st.expander("📖 ¿Qué significan los clústeres?"):
            st.markdown(
                """
                Para entender mejor los clústeres, usamos **analogías inspiradas en personajes** del Chavo del 8, 
                que simbolizan diferentes situaciones económicas:
                - **Clúster 1: “Los que tienen, pero quieren más” (Doña Florinda):** Municipios con economías cómodas, pero bajo presión social.
                - **Clúster 2: “Los reyes inquietos” (Quico):** Municipios privilegiados que enfrentan tensiones por altas expectativas.
                - **Clúster 3: “Los que luchan y avanzan” (Don Ramón):** Municipios resilientes que trabajan para superar barreras.
                - **Clúster 4: “Los que sobreviven con esperanza” (El Chavo):** Municipios con economías de subsistencia y baja desigualdad.
                """
            )

        st.subheader("📊 Comparativa entre los Clústeres Seleccionados")

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(graficar_ingresos_deciles(cluster_summary_filtered, clusters_seleccionados))
            st.plotly_chart(graficar_gini(cluster_summary_filtered, clusters_seleccionados))
        with col2:
            st.plotly_chart(graficar_consumo_ahorro(cluster_summary_filtered, clusters_seleccionados))
            st.plotly_chart(graficar_percepciones_economicas(cluster_summary_filtered, clusters_seleccionados))

        st.markdown("## 🔍 Observaciones Resumidas por Clúster")

        # Crear dos columnas para los expanders
        col1, col2 = st.columns(2)

        # Clúster 1 y 2 en la primera columna
        with col1:
            with st.expander("Clúster 1: Los que tienen, pero quieren más (Doña Florinda)"):
                st.markdown(
                    f"""
                    <p><b>Ingresos promedio mensuales:</b></p>
                    <ul>
                        <li><b>Decil 1:</b> ${6_876:,.0f}</li>
                        <li><b>Decil 5:</b> ${19_547:,.0f}</li>
                        <li><b>Decil 10:</b> ${80_421:,.0f}</li>
                    </ul>
                    <p><b>Desigualdad:</b> Moderada (GINI: 0.3705)</p>
                    <p><b>Lo que se vive aquí:</b></p>
                    <ul>
                        <li>El 49.2% enfrenta consumo restringido, mientras que un 20.5% ahorra y gasta en cosas no esenciales.</li>
                        <li>Percepciones mixtas: 16.9% tiene percepciones negativas personales; 24.1% perciben la economía nacional en mal estado.</li>
                    </ul>
                    <p><b>Conclusión:</b> La presión de mantener un nivel económico y la comparación social generan tensiones.</p>
                    """,
                    unsafe_allow_html=True
                )

            with st.expander("Clúster 2: Los reyes inquietos (Quico)"):
                st.markdown(
                    f"""
                    <p><b>Ingresos promedio mensuales:</b></p>
                    <ul>
                        <li><b>Decil 1:</b> ${8_820:,.0f}</li>
                        <li><b>Decil 5:</b> ${29_865:,.0f}</li>
                        <li><b>Decil 10:</b> ${465_308:,.0f}</li>
                    </ul>
                    <p><b>Desigualdad:</b> Alta (GINI: 0.5565)</p>
                    <p><b>Lo que se vive aquí:</b></p>
                    <ul>
                        <li>43.1% enfrenta consumo restringido, aunque el 25.1% logra consumo positivo.</li>
                        <li>Optimismo personal (solo 13.9% percepciones negativas), pero 24.8% ven la economía nacional preocupante.</li>
                    </ul>
                    <p><b>Conclusión:</b> Las altas expectativas en estos municipios generan insatisfacción, incluso con altos ingresos.</p>
                    """,
                    unsafe_allow_html=True
                )

        # Clúster 3 y 4 en la segunda columna
        with col2:
            with st.expander("Clúster 3: Los que luchan y avanzan (Don Ramón)"):
                st.markdown(
                    f"""
                    <p><b>Ingresos promedio mensuales:</b></p>
                    <ul>
                        <li><b>Decil 1:</b> ${4_955:,.0f}</li>
                        <li><b>Decil 5:</b> ${14_072:,.0f}</li>
                        <li><b>Decil 10:</b> ${56_016:,.0f}</li>
                    </ul>
                    <p><b>Desigualdad:</b> Moderada (GINI: 0.3631)</p>
                    <p><b>Lo que se vive aquí:</b></p>
                    <ul>
                        <li>El 49.6% enfrenta consumo restringido, pero un 21.9% mejora su situación con ahorro.</li>
                        <li>Percepciones: 15.3% negativas personales; 22.9% negativas nacionales.</li>
                    </ul>
                    <p><b>Conclusión:</b> Estos municipios representan la fuerza trabajadora, donde las pequeñas mejoras son grandes logros.</p>
                    """,
                    unsafe_allow_html=True
                )

            with st.expander("Clúster 4: Los que sobreviven con esperanza (El Chavo)"):
                st.markdown(
                    f"""
                    <p><b>Ingresos promedio mensuales:</b></p>
                    <ul>
                        <li><b>Decil 1:</b> ${3_704:,.0f}</li>
                        <li><b>Decil 5:</b> ${10_377:,.0f}</li>
                        <li><b>Decil 10:</b> ${36_104:,.0f}</li>
                    </ul>
                    <p><b>Desigualdad:</b> Baja (GINI: 0.3384)</p>
                    <p><b>Lo que se vive aquí:</b></p>
                    <ul>
                        <li>El 63.0% enfrenta consumo restringido, mientras que el 21.7% logra ahorro positivo.</li>
                        <li>Las percepciones son las más negativas: 23.0% personales; 28.7% nacionales.</li>
                    </ul>
                    <p><b>Conclusión:</b> Aunque enfrentan grandes desafíos diarios, las bajas expectativas ayudan a manejar las dificultades con resiliencia.</p>
                    """,
                    unsafe_allow_html=True
                )

        # Conclusiones generales
        st.markdown("## 📝 Conclusiones Finales")
        st.markdown(
            """
            - **Los municipios ricos también lloran:** En el clúster 2 (*Quico*), las expectativas elevadas generan insatisfacción, incluso en contextos privilegiados.
            - **Expectativas ajustadas en los más pobres:** En el clúster 4 (*El Chavo*), las personas manejan mejor las dificultades gracias a expectativas más bajas.
            - **La clase trabajadora valora cada mejora:** En el clúster 3 (*Don Ramón*), las intervenciones económicas en los deciles bajos y medios generan impactos positivos desproporcionados.
            - **La desigualdad amplifica tensiones:** En todos los clústers, las brechas extremas entre deciles aumentan las percepciones negativas y las tensiones sociales.
            """
        )

        # Conexión a la siguiente sección
        st.markdown("---")  # Línea divisoria para separar visualmente
        st.markdown(
            """
            <div style="background-color:#E8F5E9;padding:15px;border-radius:10px;margin-top:20px;">
                <h4 style="text-align:center;color:#1B5E20;">🔍 Explora y Experimenta en el Dashboard</h4>
                <p style="text-align:center;">
                    Hasta ahora, hemos analizado <b>tus datos personales en comparación con tu municipio</b> y también explorado 
                    <b>cómo se comportan los clústeres en promedio</b>, destacando patrones generales y tendencias importantes.
                </p>
                <p style="text-align:center;">
                    En la próxima sección, tendrás acceso a un <b>dashboard interactivo</b>, diseñado para que experimentes con diferentes 
                    configuraciones. Podrás explorar datos personalizados seleccionando otros municipios, estados, años, y comparando métricas clave.
                </p>
                <p style="text-align:center;font-weight:bold;">
                    ¡Descubre cómo otros municipios se comportan y cómo se posicionan en el panorama socioeconómico!
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")
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
