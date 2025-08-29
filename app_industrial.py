# app_industrial.py
# Importación de librerías
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Simulador Industrial de Secado",
    page_icon="🏭",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .stMetric {
        border-left: 5px solid #4A90E2;
        padding-left: 15px;
        border-radius: 5px;
        background-color: #f0f2f6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F0F0;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)


# --- MODELO DE SIMULACIÓN AVANZADO ---
def run_industrial_simulation(params):
    """
    Ejecuta una simulación de secado industrial con un modelo multifactorial.
    
    Args:
        params (dict): Diccionario con todos los parámetros de entrada.

    Returns:
        pd.DataFrame: DataFrame con resultados detallados por línea.
    """
    # Constantes del modelo (ajustables para calibración)
    DRY_WEIGHT_G = 50.0  # Peso seco constante del producto en gramos
    BASE_TEMP_C = 90.0
    BASE_AIR_SPEED_MS = 1.5
    
    # Calcular masa de agua inicial
    initial_water_mass = params['peso_humedo'] - DRY_WEIGHT_G
    
    # Calcular factor de tasa de secado base (influencia de T y V)
    temp_factor = (params['temperatura'] / BASE_TEMP_C)**1.5
    airspeed_factor = (params['velocidad_aire'] / BASE_AIR_SPEED_MS)**0.8
    drying_rate_base = temp_factor * airspeed_factor
    
    # Ajustar por humedad relativa del aire de entrada
    rh_factor = 1 - (params['humedad_aire'] / 100)
    
    # Calcular la masa de agua evaporada base
    water_evaporated_base = initial_water_mass * (1 - np.exp(-0.05 * params['tiempo_residencia'] * drying_rate_base * rh_factor))
    
    # Simulación por línea
    nombres_lineas = [f'Línea {i+1}' for i in range(params['num_lineas'])]
    humedad_final_list = []
    
    for i in range(params['num_lineas']):
        # Factor de no uniformidad (líneas externas secan menos)
        if i == 0 or i == params['num_lineas'] - 1:
            uniformity_factor = 0.85
        elif i == 1 or i == params['num_lineas'] - 2:
            uniformity_factor = 0.95
        else:
            uniformity_factor = 1.0
        
        # Agua evaporada en la línea específica
        water_evaporated_line = water_evaporated_base * uniformity_factor
        final_water_mass = initial_water_mass - water_evaporated_line
        
        # Calcular humedad residual en base húmeda
        final_total_mass = final_water_mass + DRY_WEIGHT_G
        final_humidity = (final_water_mass / final_total_mass) * 100
        
        humedad_final_list.append(max(0, final_humidity))

    df = pd.DataFrame({
        'Línea': nombres_lineas,
        'Humedad Residual (%)': humedad_final_list
    })
    return df

def calculate_kpis(params, df_results):
    """Calcula los KPIs (Key Performance Indicators) del proceso."""
    # CONSTANTES FÍSICAS Y DE COSTO
    AIR_DENSITY_KGM3 = 1.0  # Densidad del aire a T de operación
    AIR_SPECIFIC_HEAT_J_KGK = 1005
    PRICE_KWH = 0.15  # Precio de la energía en $/kWh
    
    # Tasa de Evaporación
    initial_water_kg = (params['peso_humedo'] - 50) / 1000
    final_water_kg_avg = ((df_results['Humedad Residual (%)'].mean() / 100) * (params['peso_humedo'])) / 1000
    evaporated_water_kg_per_piece = initial_water_kg - final_water_kg_avg
    pieces_per_hour = (60 / params['tiempo_residencia']) * params['num_lineas']
    evaporation_rate_kgh = evaporated_water_kg_per_piece * pieces_per_hour
    
    # Costo Energético
    dryer_cross_section_m2 = params['num_lineas'] * 0.5 # Asumiendo 0.5m de ancho por línea
    air_flow_m3s = params['velocidad_aire'] * dryer_cross_section_m2
    air_mass_kgs = air_flow_m3s * AIR_DENSITY_KGM3
    
    # Energía para calentar aire (asumiendo T_ambiente = 25°C)
    power_heating_kw = (air_mass_kgs * AIR_SPECIFIC_HEAT_J_KGK * (params['temperatura'] - 25)) / 1000
    # Energía para ventiladores (modelo cúbico simple)
    power_fan_kw = 2.5 * (params['velocidad_aire']**3) * params['num_lineas']
    
    total_power_kw = power_heating_kw + power_fan_kw
    energy_cost_per_hour = total_power_kw * PRICE_KWH
    
    # Riesgo de Calidad
    risk = "Bajo"
    if params['temperatura'] > 160 or df_results['Humedad Residual (%)'].max() > 12:
        risk = "Alto"
    elif params['temperatura'] > 140 or df_results['Humedad Residual (%)'].max() > 9:
        risk = "Medio"

    return {
        "humedad_promedio": df_results['Humedad Residual (%)'].mean(),
        "costo_energetico": energy_cost_per_hour,
        "tasa_evaporacion": evaporation_rate_kgh,
        "riesgo_calidad": risk
    }

# --- INTERFAZ DE USUARIO (UI) ---
st.title("🏭 Plataforma de Simulación y Optimización de Procesos de Secado")
st.caption("Una herramienta de gemelo digital para la optimización de la eficiencia y calidad en la producción de pulpa moldeada.")

# --- BARRA LATERAL DE PARÁMETROS ---
with st.sidebar:
    st.header("⚙️ Parámetros de Simulación")
    
    st.subheader("📦 Propiedades del Producto")
    p_peso_humedo = st.slider('Peso Húmedo Inicial (g)', 200, 300, 240, 5)
    p_espesor = st.slider('Espesor del Material (mm)', 2.0, 5.0, 3.0, 0.1)

    st.subheader("🔥 Parámetros del Proceso")
    p_temperatura = st.slider('Temperatura del Secador (°C)', 80, 180, 135, 5)
    p_velocidad_aire = st.slider('Velocidad del Aire (m/s)', 0.5, 3.0, 1.5, 0.1)
    p_tiempo_residencia = st.slider('Tiempo de Residencia (min)', 5, 20, 10, 1)
    p_humedad_aire = st.slider('Humedad Relativa Aire Entrada (%)', 10, 80, 50, 5)
    
    st.subheader("🔧 Configuración del Equipo")
    p_num_lineas = st.number_input('Número de Líneas en Secador', 2, 12, 6, 1)

params = {
    'peso_humedo': p_peso_humedo,
    'espesor': p_espesor,
    'temperatura': p_temperatura,
    'velocidad_aire': p_velocidad_aire,
    'tiempo_residencia': p_tiempo_residencia,
    'humedad_aire': p_humedad_aire,
    'num_lineas': p_num_lineas
}

# --- EJECUCIÓN Y VISUALIZACIÓN ---
df_results = run_industrial_simulation(params)
kpis = calculate_kpis(params, df_results)

# --- PESTAÑAS DE NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(["📈 Dashboard de KPIs", " heatmap Análisis por Línea", "🔬 Análisis de Sensibilidad"])

with tab1:
    st.header("Panel de Control de Rendimiento del Proceso")
    cols = st.columns(4)
    with cols[0]:
        st.metric(label="Humedad Residual Promedio", value=f"{kpis['humedad_promedio']:.2f} %")
    with cols[1]:
        st.metric(label="Costo Energético Estimado", value=f"$ {kpis['costo_energetico']:.2f} / hora")
    with cols[2]:
        st.metric(label="Tasa de Evaporación", value=f"{kpis['tasa_evaporacion']:.2f} kg/h")
    with cols[3]:
        st.metric(label="Índice de Riesgo de Calidad", value=kpis['riesgo_calidad'])
    
    st.info("Este dashboard resume los indicadores clave de rendimiento (KPIs) para la configuración de parámetros actual. Utilícelo para una evaluación rápida de la eficiencia y la calidad.", icon="ℹ️")

with tab2:
    st.header("Análisis de Uniformidad del Secado")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Perfil de Humedad a lo Ancho del Secador")
        # Heatmap
        fig_heatmap = go.Figure(data=go.Heatmap(
                   z=[df_results['Humedad Residual (%)'].values],
                   x=df_results['Línea'],
                   y=['Humedad (%)'],
                   colorscale='Viridis_r',
                   zmin=0, zmax=15))
        fig_heatmap.update_layout(title='Mapa de Calor de Humedad Residual', autosize=True)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with col2:
        st.subheader("Datos Detallados por Línea")
        st.dataframe(df_results, hide_index=True, use_container_width=True)

with tab3:
    st.header("Análisis de Sensibilidad de Variables")
    st.markdown("Seleccione una variable para analizar su impacto en la humedad residual promedio, manteniendo los demás parámetros constantes.")
    
    variable_options = {
        'Temperatura (°C)': 'temperatura',
        'Velocidad del Aire (m/s)': 'velocidad_aire',
        'Tiempo de Residencia (min)': 'tiempo_residencia',
        'Peso Húmedo (g)': 'peso_humedo'
    }
    selected_var_label = st.selectbox("Seleccione la variable a analizar:", options=list(variable_options.keys()))
    selected_var_key = variable_options[selected_var_label]

    # Generar datos para el gráfico de sensibilidad
    sens_values = np.linspace(
        st.session_state[f'sidebar_{selected_var_key}_min'], 
        st.session_state[f'sidebar_{selected_var_key}_max'], 
        20
    )
    
    sens_results = []
    for val in sens_values:
        temp_params = params.copy()
        temp_params[selected_var_key] = val
        df_sens = run_industrial_simulation(temp_params)
        sens_results.append(df_sens['Humedad Residual (%)'].mean())

    # Crear el gráfico
    fig_sens = px.line(
        x=sens_values, 
        y=sens_results, 
        title=f'Impacto de {selected_var_label} en la Humedad Promedio',
        labels={'x': selected_var_label, 'y': 'Humedad Residual Promedio (%)'}
    )
    fig_sens.add_vline(x=params[selected_var_key], line_dash="dash", line_color="red", annotation_text="Valor Actual")
    st.plotly_chart(fig_sens, use_container_width=True)

# Hack para que el análisis de sensibilidad funcione con los rangos del slider
# Se necesita almacenar los min/max de los sliders en el estado de la sesión
for key, component in st.sidebar._components.items():
    if isinstance(component, st.delta_generator.DeltaGenerator) and hasattr(component, 'label'):
        if 'Peso Húmedo' in component.label:
            st.session_state['sidebar_peso_humedo_min'] = 200
            st.session_state['sidebar_peso_humedo_max'] = 300
        if 'Temperatura' in component.label:
            st.session_state['sidebar_temperatura_min'] = 80
            st.session_state['sidebar_temperatura_max'] = 180
        if 'Velocidad del Aire' in component.label:
            st.session_state['sidebar_velocidad_aire_min'] = 0.5
            st.session_state['sidebar_velocidad_aire_max'] = 3.0
        if 'Tiempo de Residencia' in component.label:
            st.session_state['sidebar_tiempo_residencia_min'] = 5
            st.session_state['sidebar_tiempo_residencia_max'] = 20
