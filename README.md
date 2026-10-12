# Optimización de carteras con Gurobi

Este proyecto reúne cinco modelos de optimización de carteras formulados en Python con **gurobipy**. Al ejecutar el programa, se resuelve cada modelo y se muestran su valor objetivo y sus variables de decisión.

## Modelos incluidos

- **Nominal:** modelo de una etapa.
- **Incertidumbre en dividendos:** maximiza el mínimo de acciones finales.
- **Incertidumbre en porcentajes:** formula las restricciones asociadas a los porcentajes inciertos.
- **Reglas de decisión:** modelo de segunda etapa; incluye la restricción no lineal **Res_21**.
- **Estocástico:** modelo con tres escenarios.

Los datos del caso están incluidos en el código. El programa oculta el registro detallado del solver y presenta los resultados al terminar. Si algún modelo no alcanza el estado óptimo, muestra un error indicando su estado.

## Requisitos

- Python 3.10 o posterior.
- Gurobi 12.0 o posterior y una licencia válida, configurada en el equipo donde se ejecuta el proyecto.

El modelo de reglas de decisión utiliza **Model.addGenConstrNL** para representar Res_21; consulta la [referencia oficial de Gurobi](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/model.html) para esa API.

## Instalación y ejecución

Desde la carpeta del repositorio, en Windows:

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m portfolio_optimization
~~~

En macOS o Linux:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m portfolio_optimization
~~~

También se puede ejecutar el comando instalado:

~~~text
portfolio-optimization
~~~

Instalar gurobipy no configura por sí solo la licencia. Sigue la [documentación oficial de configuración de Gurobi](https://docs.gurobi.com/projects/optimizer/en/current/concepts/environments/configuration.html). No incluyas archivos de licencia ni credenciales en el repositorio.

## Estructura

~~~text
src/portfolio_optimization/
├── models.py     # Construcción, resolución y presentación de los modelos
├── cli.py        # Ejecución de los cinco modelos
└── __main__.py   # Permite ejecutar python -m portfolio_optimization
~~~

