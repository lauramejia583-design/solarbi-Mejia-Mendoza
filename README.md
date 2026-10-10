**Solar BI — Inteligencia de Negocios**

1\. Información del equipo

Integrante 1: Laura Mejia Delgado

Integrante 2: Yuritza Mendoza

Asignatura: Inteligencia de Negocios

Grupo: 50



**Descripción del proyecto**



Solar BI es un proyecto de análisis de datos orientado al procesamiento de información de un inversor solar de 5 kWp. Su objetivo es generar datos simulados de telemetría, limpiarlos, validar su calidad y calcular indicadores diarios de energía para facilitar el análisis mediante herramientas de inteligencia de negocios.



El proyecto implementa un flujo ETL organizado en tres etapas:



* **Bronze:** almacenamiento de los datos originales simulados.
* **Silver:** limpieza y validación de los registros.
* **Gold:** consolidación de indicadores diarios en PostgreSQL.



Los datos procesados se utilizarán para construir dashboards en Power BI y Grafana.





**Tecnologías utilizadas**



Python y pandas para la simulación y transformación de datos.

PostgreSQL para el almacenamiento de la información.

Power BI para la visualización de indicadores.

Grafana para el monitoreo de potencia e irradiancia.

Git y GitHub para el control de versiones y la colaboración.





**Estructura del proyecto**



Data/Bronze/: datos crudos simulados.

Data/Silver/: datos limpios y validados.

ETL/simulador.py: genera los datos de telemetría.

ETL/limpiar\_datos.py: aplica las reglas de calidad.

ETL/run\_etl.py: ejecuta el proceso ETL y carga los datos en PostgreSQL.

Reports/calidad\_datos.txt: reporte de calidad de los datos.

sql/: scripts de creación y consulta de tablas.

powerbi/: archivos del dashboard de Power BI.

grafana/: configuración exportada del dashboard de Grafana.

docs/: evidencias e informe final.



Las carpetas y archivos de visualización, SQL y documentación se completarán durante el desarrollo.





**Requisitos para ejecutar el proyecto**



Python 3.

PostgreSQL.

Bibliotecas de Python: pandas y psycopg.

Git para clonar y actualizar el repositorio.





**Pasos de reproducción**



Clonar el repositorio de GitHub.

Instalar las dependencias de Python.

Configurar PostgreSQL y crear la base de datos y los esquemas requeridos.

Ejecutar python ETL/simulador.py para generar los datos originales.

Ejecutar python ETL/limpiar\_datos.py para limpiar y validar los registros.

Ejecutar python ETL/run\_etl.py para cargar los datos procesados en PostgreSQL.

Configurar la conexión de Power BI a PostgreSQL e incorporar el dashboard.

Configurar Grafana, conectar PostgreSQL e importar el dashboard cuando esté disponible.



Las credenciales de conexión deben configurarse localmente y no deben publicarse en el repositorio.





Distribución del trabajo



Integrante	Actividades realizadas

Laura Mejia Delgado: Desarrollo del simulador de telemetría, Construcción del proceso ETL, Limpieza y validación de datos, Integración con PostgreSQL,  Visualización en Grafana 

Yuritza Mendoza Mosquera: Crear el dashboard de Power BI, Mostrar indicadores de generación y rendimiento energético, Incluir el ahorro económico en pesos colombianos (COP), Agregar un parámetro de tarifa eléctrica, para ajustar el cálculo del ahorro, Incorporar filtros para consultar y analizar los datos.

Repositorio

https://github.com/lauramejia583-design/solarbi-Mejia-Mendoza

