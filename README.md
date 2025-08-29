Plataforma de Simulación y Optimización de Procesos de Secado (PS-OPS)
PS-OPS es una aplicación web de nivel industrial, construida con Python y Streamlit, para la simulación avanzada de secadores de pulpa moldeada. Esta herramienta permite a ingenieros, jefes de planta y operadores modelar, analizar y optimizar las complejas interacciones entre múltiples variables del proceso para mejorar la calidad del producto, reducir costos energéticos y maximizar la eficiencia operativa.

La plataforma va más allá de una simple simulación al incorporar un modelo físico-empírico que considera variables termodinámicas y de proceso, ofreciendo resultados detallados y accionables.

🌟 Arquitectura y Funcionalidades Clave
Modelo de Simulación Multifactorial: El núcleo de la simulación considera:

Parámetros del Producto: Peso húmedo inicial y espesor del material.

Parámetros del Proceso: Temperatura del secador, velocidad del flujo de aire, tiempo de residencia y humedad relativa del aire de entrada.

Dashboard de KPIs (Key Performance Indicators): Un panel de control central que presenta métricas críticas en tiempo real:

Humedad Residual Promedio (%).

Costo Energético Estimado ($/hora).

Tasa de Evaporación (kg/hora).

Índice de Riesgo de Calidad (Bajo, Medio, Alto).

Análisis de Uniformidad (Heatmap): Un mapa de calor visualiza el perfil de humedad a lo ancho del secador, permitiendo identificar rápidamente problemas de uniformidad.

Análisis de Sensibilidad: Una herramienta poderosa que permite aislar una variable y visualizar gráficamente su impacto directo en la humedad residual, facilitando la identificación de los parámetros más influyentes.

Interfaz Intuitiva por Pestañas: La información está organizada en secciones lógicas (Dashboard, Análisis por Línea, Análisis de Sensibilidad) para una navegación clara y eficiente.

🛠️ Instalación y Despliegue
El despliegue de esta herramienta sigue un proceso estándar para aplicaciones Python.

Clonar el Repositorio:

git clone <URL-de-tu-repositorio-en-GitHub>
cd <nombre-del-repositorio>

Configurar Entorno Virtual:

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

Instalar Dependencias:
Crea un archivo requirements.txt con el siguiente contenido:

streamlit
pandas
numpy
plotly

Y ejecuta la instalación:

pip install -r requirements.txt

Ejecutar la Aplicación:

streamlit run app_industrial.py

La aplicación estará disponible en http://localhost:8501.

🧠 Sobre el Modelo de Simulación
El modelo matemático subyacente se basa en principios de transferencia de calor y masa, ajustado con coeficientes empíricos para reflejar las condiciones de un secador industrial típico.

La tasa de secado se modela como una función de la temperatura y la velocidad del aire.

El costo energético se calcula sumando el consumo del sistema de calentamiento (termodinámica del aire) y el sistema de ventilación (potencia de los ventiladores).

El riesgo de calidad se infiere a partir de condiciones extremas (ej. temperaturas muy altas pueden causar deformaciones, mientras que tiempos de residencia cortos pueden dejar el producto demasiado húmedo).

Esta herramienta está diseñada para ser un gemelo digital del proceso de secado, permitiendo la experimentación virtual sin afectar la producción real.
