import streamlit as st

import streamlit as st

def mostrar_intro():
    st.title("📊 El Síndrome de Doña Florinda")
    st.markdown("### Cómo la desigualdad y las expectativas moldean la percepción económica en México")

    st.markdown(
        """
        Bienvenido a este dashboard interactivo, donde exploraremos **cómo la percepción económica no siempre refleja la realidad,**
        sino que está influida por factores como la **desigualdad**, las **expectativas** y las **comparaciones sociales.**

        Este análisis está inspirado en los personajes de la icónica serie mexicana **El Chavo del 8**, creada en 1973 por Roberto Gómez Bolaños (Chespirito). 
        Aunque originalmente pensada como humor, sus personajes reflejan diferentes actitudes y situaciones económicas que son universales. En particular, 
        nos enfocamos en el **síndrome de Doña Florinda**, un concepto acuñado por el escritor argentino **Rafael Ton**, que describe cómo ciertas actitudes y 
        presiones sociales afectan a las clases trabajadoras de América Latina y el mundo.

        El síndrome de Doña Florinda simboliza la búsqueda de aparentar un estatus más elevado del que se posee, muchas veces acompañado de una percepción 
        distorsionada de la realidad económica y social. Esta idea sirve como base para nuestra analogía con los personajes de la serie:

        - **Doña Florinda:** Representa a quienes tienen recursos pero viven bajo presión social y buscan proyectar una imagen de superioridad.
        - **Quico:** Simboliza a quienes aspiran siempre a más, incluso desde una posición privilegiada, enfrentando la insatisfacción constante.
        - **Don Ramón:** Encapsula la lucha diaria por mejorar, enfrentando barreras estructurales y desigualdad.
        - **El Chavo:** Refleja la subsistencia y la esperanza frente a desafíos constantes, a menudo en condiciones de vulnerabilidad.

        Este dashboard está diseñado para ofrecer una perspectiva crítica y analítica sobre cómo las dinámicas económicas y sociales moldean nuestras 
        percepciones y realidades, a través de un enfoque lúdico pero fundamentado.
        """
    )


    # Expander: ¿Por qué el Chavo del 8?
    with st.expander("¿Por qué usar El Chavo del 8 como inspiración?"):
        st.write(
            """
            Usamos **El Chavo del 8** porque es una serie que refleja la diversidad económica y social de México.
            
            Esta analogía ayuda a explicar conceptos complejos de forma simple y conecta los datos con una referencia cultural familiar.
            """
        )

    # Expander: ¿De dónde provienen los datos?
    with st.expander("¿De dónde provienen los datos?"):
        st.write(
            """
            Usamos datos oficiales de encuestas nacionales:
            
            - **ENIGH (Encuesta Nacional de Ingresos y Gastos de los Hogares):** Mide ingresos, gastos y desigualdad económica.
            - **ENCO (Encuesta Nacional de Confianza del Consumidor):** Evalúa las percepciones y expectativas económicas.

            Combinamos estos datos para entender tanto los aspectos objetivos (ingresos, gastos) como los subjetivos (percepciones económicas).
            """
        )

    # Expander: ¿Por qué podemos contar esta historia?
    with st.expander("#### ¿Por qué podemos contar esta historia?"):
        st.write(
            """
            Basamos nuestra historia en datos sólidos y un análisis estructurado que incluye:
            
            - **Indicadores objetivos:** Como ingresos promedio, índice de GINI, y consumo.
            - **Indicadores subjetivos:** Percepciones económicas personales y nacionales.

            #### Lo que debes saber:
            - Los datos explican **correlaciones**, pero no siempre causan los resultados.
            - Las percepciones económicas pueden variar según factores sociales y culturales que no están en las encuestas.
            
            A pesar de estas limitaciones, el análisis permite identificar patrones clave y ayudar a entender mejor la realidad económica.
            """
        )

    # Expander: ¿Qué es un clúster?
    with st.expander("¿Qué es un clúster?"):
        st.write(
            """
            Un clúster es un grupo de municipios con características económicas y sociales parecidas. 
            Por ejemplo, agrupamos municipios con ingresos altos y desigualdad baja en un clúster, 
            mientras que los de ingresos bajos y alta desigualdad están en otro.

            ### ¿Cómo formamos los clústeres?
            Usamos datos como:
            - **Ingresos promedio por decil:** Diferentes niveles de ingresos.
            - **Índice de GINI:** Una medida de desigualdad económica.
            - **Percepciones económicas:** Cómo las personas ven su situación y la economía nacional.

            Esto nos permite identificar tendencias y diferencias importantes entre los municipios.
            """
        )

    st.markdown(
        """
        🚀 **¡Comencemos explorando cómo te ubicas en este panorama económico!**
        """
    )
