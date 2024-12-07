import pandas as pd
import streamlit as st
import geopandas as gpd

@st.cache_data
def load_municipio_data():
    """Cargar datos de clusters de municipios y convertir ingresos a valores mensuales."""
    # Cargar los datos
    data = pd.read_csv('data/processed/resultados_municipales_cluster.csv')
    
    # Generar la lista de columnas de deciles del 1 al 10
    decile_columns = [f"decil_{i}" for i in range(1, 11)]
    
    # Agregar la columna de ingreso promedio total a la lista
    columns_to_convert = decile_columns + ["ingreso_promedio_total"]
    
    # Convertir las columnas seleccionadas a valores mensuales
    data[columns_to_convert] = data[columns_to_convert] / 3
    
    # Renombrar las columnas para reflejar que son mensuales
    #data.rename(columns={col: col for col in columns_to_convert}, inplace=True)
    
    return data

@st.cache_data
def load_estado_data():
    # Cargar los datos
    data = pd.read_csv('data/processed/resultados_estatales_merged.csv')
    
    # Generar la lista de columnas de deciles del 1 al 10
    decile_columns = [f"decil_{i}" for i in range(1, 11)]
    
    # Agregar la columna de ingreso promedio total a la lista
    columns_to_convert = decile_columns + ["ingreso_promedio_total"]
    
    # Convertir las columnas seleccionadas a valores mensuales
    data[columns_to_convert] = data[columns_to_convert] / 3
    return data

@st.cache_data
def load_nacional_data():
    """Cargar datos de ENIGH nacionales y ajustar nombres de columnas."""
    # Cargar datos
    df = pd.read_csv('data/processed/resultados_nacionales_merged.csv')
    
    # Generar la lista de columnas de deciles del 1 al 10
    decile_columns = [f"decil_{i}" for i in range(1, 11)]
    
    # Agregar la columna de ingreso promedio total a la lista
    columns_to_convert = decile_columns + ["ingreso_promedio_total"]
    
    # Convertir las columnas seleccionadas a valores mensuales
    df[columns_to_convert] = df[columns_to_convert] / 3
    
    return df

@st.cache_data
def cargar_geodatos():
    """Cargar geodatos desde archivos locales."""
    ent_gdf = gpd.read_file("./data/shp/shp_ent_tidy_data.shp")
    mpio_gdf = gpd.read_file("./data/shp/shp_mun_tidy_data.shp")
    return ent_gdf, mpio_gdf