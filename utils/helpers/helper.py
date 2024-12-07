import streamlit as st

# Callback para cambiar la sección
def set_section(section):
    st.session_state["section"] = section
    st.query_params.from_dict({"section": section})

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Generar HTML para la tabla
def render_html_table(df):
    table_html = df.to_html(index=False, classes="styled-table")
    return table_html