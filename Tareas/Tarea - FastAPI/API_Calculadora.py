from enum import Enum
from typing import List
import numpy as np

from fastapi import FastAPI
app = FastAPI()

# =================
# Desplegar con el comando 'uvicorn API_Calculadora:app --reload'
# Ingresar a http://127.0.0.1:8000/docs#/ para probar los requests disponibles.
# =================

@app.post("/suma")
def suma(nums: List[int]):
    return {"resultado" : sum(nums)}

@app.post("/resta")
def resta(nums: List[int]):
    return {"resultado" : nums[0] - sum(nums[1:])}

@app.post("/multiplicacion")
def multiplicacion(nums: List[int]):
    return {"resultado" : float(np.prod(nums))}

@app.post("/division")
def division(nums: List[int]):
    return {"resultado" : float(np.true_divide.reduce(np.array(nums, dtype = float)))}

class Operaciones(str, Enum):
    sum = "suma"
    diff = "resta"
    prod = "multiplicacion"
    div = "division"

@app.post("/calculadora")
def calculadora(operacion: Operaciones, nums: List[int]):

    operacion = operacion.lower()

    if operacion == Operaciones.sum:
        return {"operacion": operacion, "operandos": nums, "resultado" : sum(nums)}
    elif operacion == Operaciones.diff:
        return {"operacion": operacion, "operandos": nums, "resultado" : nums[0] - sum(nums[1:])}
    elif operacion == Operaciones.prod:
        return {"operacion": operacion, "operandos": nums, "resultado" : float(np.prod(nums))}
    elif operacion == Operaciones.div:
        return {"operacion": operacion, "operandos": nums, "resultado" : float(np.true_divide.reduce(np.array(nums, dtype = float)))}
    else:
        return {"operacion": operacion, "operandos": nums, "error": "Operación desconocida"}