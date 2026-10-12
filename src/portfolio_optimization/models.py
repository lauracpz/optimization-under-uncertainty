"""Modelos de optimización de cartera formulados con la API de Gurobi."""

import gurobipy as gp
from gurobipy import GRB


def resolver(modelo):
    """Resuelve el modelo sin imprimir la salida del solver."""
    modelo.Params.OutputFlag = 0
    modelo.optimize()
    if modelo.Status != GRB.OPTIMAL:
        raise RuntimeError(
            f"El modelo {modelo.ModelName} no alcanzó el óptimo "
            f"(estado {modelo.Status})."
        )
    return modelo


def resolver_modelo_nominal():
    """Modelo nominal de una etapa."""
    modelo = gp.Model("cartera_nominal")
    x_A = modelo.addVar(lb=-50, name="x_A")
    x_M = modelo.addVar(lb=-80, name="x_M")
    x_T = modelo.addVar(lb=-30, name="x_T")

    modelo.setObjective(1.2*x_A + 2.5*x_M + 260, GRB.MAXIMIZE)
    modelo.addConstr(144*x_A - 66*x_M - 50*x_T >= -420, name="Res_1")
    modelo.addConstr(-36*x_A + 264*x_M - 50*x_T >= -17820, name="Res_2")
    modelo.addConstr(-36*x_A - 66*x_M + 200*x_T >= 1080, name="Res_3")
    modelo.addConstr(180*x_A + 330*x_M + 250*x_T == 0, name="Res_4")
    modelo.addConstr(200*x_A + 350*x_M + 280*x_T >= -1355, name="Res_5")

    resolver(modelo)
    return modelo, {"x_A": x_A, "x_M": x_M, "x_T": x_T}


def resolver_modelo_dividendos():
    """Modelo con incertidumbre en los valores de los dividendos."""
    modelo = gp.Model("incertidumbre_dividendos")
    x_A = modelo.addVar(lb=-50, name="x_A")
    x_M = modelo.addVar(lb=-80, name="x_M")
    x_T = modelo.addVar(lb=-30, name="x_T")
    alpha = modelo.addVar(lb=0, name="alpha")

    modelo.setObjective(3.4*alpha, GRB.MAXIMIZE)
    modelo.addConstr(50 + x_A >= alpha, name="Res_1")
    modelo.addConstr(80 + x_M >= alpha, name="Res_2")
    modelo.addConstr(30 + x_T >= alpha, name="Res_3")
    modelo.addConstr(144*x_A - 66*x_M - 50*x_T >= -420, name="Res_4")
    modelo.addConstr(-36*x_A + 264*x_M - 50*x_T >= -17820, name="Res_5")
    modelo.addConstr(-36*x_A - 66*x_M + 200*x_T >= 1080, name="Res_6")
    modelo.addConstr(180*x_A + 330*x_M + 250*x_T == 0, name="Res_7")
    modelo.addConstr(200*x_A + 350*x_M + 280*x_T >= -1355, name="Res_8")

    resolver(modelo)
    return modelo, {"x_A": x_A, "x_M": x_M, "x_T": x_T, "alpha": alpha}


def resolver_modelo_porcentajes():
    """Modelo con incertidumbre relacionada en los porcentajes r y s."""
    modelo = gp.Model("incertidumbre_porcentajes")
    x_A = modelo.addVar(lb=-50, name="x_A")
    x_M = modelo.addVar(lb=-80, name="x_M")
    x_T = modelo.addVar(lb=-30, name="x_T")
    y = {i: modelo.addVar(lb=0, name=f"y{i}") for i in range(1, 9)}

    modelo.setObjective(1.2*x_A + 2.5*x_M + 260, GRB.MAXIMIZE)
    modelo.addConstr(0.15*y[1] - 0.25*y[2] >= -9000 - 180*x_A, name="Res_1")
    modelo.addConstr(0.15*y[3] - 0.25*y[4] >= -26400 - 330*x_M, name="Res_2")
    modelo.addConstr(0.15*y[5] - 0.25*y[6] >= -7500 - 250*x_T, name="Res_3")
    modelo.addConstr(180*x_A + 330*x_M + 250*x_T == 0, name="Res_4")
    modelo.addConstr(
        -0.1*y[7] + 0.05*y[8] >= -3500 - 200*x_A - 250*x_M - 280*x_T,
        name="Res_5",
    )
    total = 42900 + 180*x_A + 330*x_M + 250*x_T
    modelo.addConstr(y[1] - y[2] <= -total, name="Res_6")
    modelo.addConstr(-y[7] + y[8] <= -42900, name="Res_7")
    modelo.addConstr(y[3] - y[4] <= -total, name="Res_8")
    modelo.addConstr(y[5] - y[6] <= -total, name="Res_9")

    resolver(modelo)
    variables = {"x_A": x_A, "x_M": x_M, "x_T": x_T}
    variables.update({f"y{i}": y[i] for i in y})
    return modelo, variables


def resolver_modelo_reglas_decision():
    """Modelo de segunda etapa mediante reglas de decisión."""
    modelo = gp.Model("segunda_etapa_reglas_decision")
    nombres_libres = (
        "x_A", "x_M", "x_T", "m_A", "m_M", "m_T", "k_A", "k_M", "k_T"
    )
    v = {
        nombre: modelo.addVar(lb=-GRB.INFINITY, name=nombre)
        for nombre in nombres_libres
    }
    y = {i: modelo.addVar(lb=0, name=f"y{i}") for i in range(1, 21)}
    x_A, x_M, x_T = v["x_A"], v["x_M"], v["x_T"]
    m_A, m_M, m_T = v["m_A"], v["m_M"], v["m_T"]
    k_A, k_M, k_T = v["k_A"], v["k_M"], v["k_T"]

    modelo.setObjective(
        1.2*x_A + 2.5*x_M + 260 + 0.96*k_A + 2*k_M
        + 150*y[1] - 280*y[2],
        GRB.MAXIMIZE,
    )
    modelo.addConstr(y[1] - y[2] <= 0.96*m_A + 2*m_M, name="Res_1")
    modelo.addConstr(150*y[3] - 280*y[4] >= -50 - x_A - k_A, name="Res_2")
    modelo.addConstr(y[3] - y[4] <= m_A, name="Res_3")
    modelo.addConstr(150*y[5] - 280*y[6] >= -80 - x_M - k_M, name="Res_4")
    modelo.addConstr(y[5] - y[6] <= m_M, name="Res_5")
    modelo.addConstr(150*y[7] - 280*y[8] >= -30 - x_T - k_T, name="Res_6")
    modelo.addConstr(y[7] - y[8] <= m_T, name="Res_7")
    modelo.addConstr(
        150*y[9] - 280*y[10]
        >= -420 - 144*x_A + 66*x_M + 50*x_T
        - 144*k_A + 66*k_M + 50*k_T,
        name="Res_8",
    )
    modelo.addConstr(
        y[9] - y[10] <= 144*m_A - 66*m_M - 50*m_T,
        name="Res_9",
    )
    modelo.addConstr(
        150*y[11] - 280*y[12]
        >= -17820 + 36*x_A - 264*x_M + 50*x_T
        + 36*k_A - 264*k_M + 50*k_T,
        name="Res_10",
    )
    modelo.addConstr(
        y[11] - y[12] <= -36*m_A + 264*m_M - 50*m_T,
        name="Res_11",
    )
    modelo.addConstr(
        150*y[13] - 280*y[14]
        >= 1080 + 36*x_A + 66*x_M - 200*x_T
        + 36*k_A + 66*k_M - 200*k_T,
        name="Res_12",
    )
    modelo.addConstr(
        y[13] - y[14] <= -36*m_A - 66*m_M + 200*m_T,
        name="Res_13",
    )
    modelo.addConstr(180*m_A + 330*m_M + 250*m_T == 0, name="Res_14")
    modelo.addConstr(
        180*x_A + 180*k_A + 330*x_M + 330*k_M
        + 250*x_T + 250*k_T == 0,
        name="Res_15",
    )
    modelo.addConstr(150*y[15] - 280*y[16] >= -k_A, name="Res_16")
    modelo.addConstr(150*y[17] - 280*y[18] >= -k_M, name="Res_17")
    modelo.addConstr(150*y[19] - 280*y[20] >= -k_T, name="Res_18")
    modelo.addConstr(
        150*(50 + x_A + 150*m_A + k_A + 350*m_M + 280*m_T)
        + 350*x_M + 350*k_M + 280*x_T + 280*k_T >= 8645,
        name="Res_19",
    )
    modelo.addConstr(
        280*(50 + x_A + 280*m_A + k_A + 350*m_M + 280*m_T)
        + 350*x_M + 350*k_M + 280*x_T + 280*k_T >= 8645,
        name="Res_20",
    )

    # Res_21 es no lineal; la variable de holgura impone que la expresión sea >= 0.
    termino_1 = -(50 + x_A + k_A + 350*m_M + 280*m_T) / 2
    termino_2 = 50 + x_A + termino_1 + k_A + 350*m_M + 280*m_T
    diferencia = m_A.nl*termino_1*termino_2 - 8645*(m_A.nl**2)
    holgura = modelo.addVar(lb=0, name="holgura_Res_21")
    modelo.addGenConstrNL(holgura, diferencia, name="Res_21")

    modelo.addConstr(y[15] - y[16] <= m_A, name="Res_22")
    modelo.addConstr(y[17] - y[18] <= m_M, name="Res_23")
    modelo.addConstr(y[19] - y[20] <= m_T, name="Res_24")

    resolver(modelo)
    variables = dict(v)
    variables.update({f"y{i}": y[i] for i in y})
    variables["holgura_Res_21"] = holgura
    return modelo, variables


def resolver_modelo_estocastico():
    """Modelo estocástico con tres escenarios."""
    modelo = gp.Model("cartera_estocastica")
    escenarios = (1, 2, 3)
    activos = ("A", "M", "T")

    x = {
        a: modelo.addVar(lb=-GRB.INFINITY, name=f"x_{a}")
        for a in activos
    }
    x_d = {
        a: {
            d: modelo.addVar(lb=-GRB.INFINITY, name=f"x_{a}_d{d}")
            for d in escenarios
        }
        for a in activos
    }
    x_limite = {
        a: modelo.addVar(lb=0, name=f"x_{a}_")
        for a in activos
    }
    b = modelo.addVar(lb=-GRB.INFINITY, name="b")

    modelo.setObjective(
        1.2*x["A"] + 2.5*x["M"] + 260 + b
        - 0.1*x_limite["A"] - x_limite["M"] - x_limite["T"],
        GRB.MAXIMIZE,
    )

    limites = {"A": -50, "M": -80, "T": -30}
    for d in escenarios:
        modelo.addConstr(b <= 0.96*x_d["A"][d] + 2*x_d["M"][d], name=f"Res_b_d{d}")
        for a in activos:
            modelo.addConstr(x[a] + x_d[a][d] >= limites[a], name=f"Res_limite_{a}_d{d}")
            modelo.addConstr(x_d[a][d] <= x_limite[a], name=f"Res_sup_{a}_d{d}")
            modelo.addConstr(x_d[a][d] >= -x_limite[a], name=f"Res_inf_{a}_d{d}")

        modelo.addConstr(
            -144*x["A"] - 144*x_d["A"][d]
            + 66*x["M"] + 66*x_d["M"][d]
            + 50*x["T"] + 50*x_d["T"][d] <= 420,
            name=f"Res_cartera_1_d{d}",
        )
        modelo.addConstr(
            36*x["A"] - 36*x_d["A"][d]
            - 264*x["M"] - 264*x_d["M"][d]
            + 50*x["T"] + 50*x_d["T"][d] <= 17820,
            name=f"Res_cartera_2_d{d}",
        )
        modelo.addConstr(
            36*x["A"] - 36*x_d["A"][d]
            + 66*x["M"] + 66*x_d["M"][d]
            - 200*x["T"] - 200*x_d["T"][d] <= -1080,
            name=f"Res_cartera_3_d{d}",
        )
        modelo.addConstr(
            180*(x["A"] + x_d["A"][d])
            + 330*(x["M"] + x_d["M"][d])
            + 250*(x["T"] + x_d["T"][d]) == 0,
            name=f"Res_balance_d{d}",
        )

    precios_A = {1: 150, 2: 200, 3: 280}
    cotas = {1: 1145, 2: -1355, 3: -5355}
    for d in escenarios:
        modelo.addConstr(
            precios_A[d]*(x["A"] + x_d["A"][d])
            + 350*(x["M"] + x_d["M"][d])
            + 280*(x["T"] + x_d["T"][d]) >= cotas[d],
            name=f"Res_valor_d{d}",
        )

    resolver(modelo)
    variables = {
        "x_A": x["A"], "x_M": x["M"], "x_T": x["T"], "b": b,
        "x_A_": x_limite["A"], "x_M_": x_limite["M"], "x_T_": x_limite["T"],
    }
    variables.update({
        f"x_{a}_d{d}": x_d[a][d]
        for a in activos for d in escenarios
    })
    return modelo, variables


def imprimir_resultados(modelos):
    """Muestra el objetivo y los valores de las variables de cada modelo."""
    for nombre_modelo, (modelo, variables) in modelos.items():
        titulo = nombre_modelo.replace("_", " ").title()
        print(f"\n--- {titulo} ---")
        print(f"Valor objetivo: {modelo.ObjVal:.6f}")
        for nombre_variable, variable in variables.items():
            print(f"{nombre_variable}: {variable.X:.6f}")


def ejecutar_modelos():
    """Construye y resuelve los cinco modelos."""
    return {
        "nominal": resolver_modelo_nominal(),
        "incertidumbre_dividendos": resolver_modelo_dividendos(),
        "incertidumbre_porcentajes": resolver_modelo_porcentajes(),
        "reglas_decision": resolver_modelo_reglas_decision(),
        "estocastico": resolver_modelo_estocastico(),
    }
