import tkinter as tk
from tkinter import ttk
from tkinter import *
import matplotlib.pyplot as plt
from pulp import *
import pulp
import numpy as np
def solucion_MG():
    problema = pulp.LpProblem("Optimizacion", pulp.LpMaximize if tipo.get() == "Maximizacion" else pulp.LpMinimize)
    vars= [pulp.LpVariable("x{}".format(i + 1), lowBound=0) for i in range(2)]  #Esta linea define el nombre de las variables y define la cota inferior que sera utilizada en la grafica
    functob_text = funcion_ob.get()
    expr=pulp.LpAffineExpression([(vars[i], float(coef)) for i, coef in enumerate(functob_text.split())]) # esta linea se encarga de tomar los coeficientes de la cadena de texto de la funcion objetivo, la divide en una liste y asocia las variables con los coeficientes
    problema+=expr
    array_res = []
    array_sol= []
    for restriccion in constraints: #Bucle que recorre las restricciones del problema
        restric_text = restriccion.get()
        if restric_text:
            if "<=" in restric_text:
                i_d = restric_text.index("<=") # Separacion de indices de igualdad o desigualdad
                expr_res = restric_text[:i_d].strip()
                v_res = float(restric_text[i_d + 2:].strip()) #transformacion de los coeficientes en float para poder trabajarlos en la libreria
                lista_c = [float(coef) for coef in expr_res.split()] #Separacion y asignacion de los coeficientes
                adicion_lp = pulp.LpConstraint(
                    e=pulp.LpAffineExpression([(vars[i], lista_c[i]) for i in range(len(lista_c))]),
                    sense=pulp.LpConstraintLE,
                    rhs=v_res,
                )#adiocion_lp es una cadena de texto que guarda la metrica para el envio de las restricciones para su posterior resolucion
                array_res.append(lista_c)
                array_sol.append(v_res)
                #Cada condicional funcion igual que el anterior, lo que varia es la expresion de desigualdad para ser interpretada
            elif ">=" in restric_text:
                i_d = restric_text.index(">=")
                expr_res = restric_text[:i_d].strip()
                v_res = float(restric_text[i_d + 2:].strip())
                lista_c = [float(coef) for coef in expr_res.split()]
                adicion_lp = pulp.LpConstraint(
                    e=pulp.LpAffineExpression([(vars[i], lista_c[i]) for i in range(len(lista_c))]),
                    sense=pulp.LpConstraintGE,
                    rhs=v_res,
                )
                array_res.append(lista_c)
                array_sol.append(v_res)


            elif "=" in restric_text:
                iq_i = restric_text.index(">=")
                expr_res = restric_text[:iq_i].strip()
                v_res = float(restric_text[iq_i + 1:])
                lista_c = [float(coef) for coef in expr_res.split()]
                adicion_lp = pulp.LpConstraint(
                    e=pulp.LpAffineExpression([(vars[i], lista_c[i]) for i in range(len(lista_c))]),
                    sense=pulp.LpConstraintEQ,
                    rhs=v_res,
                )
                array_res.append(lista_c)
                array_sol.append(v_res)
            else:
                continue


        problema += adicion_lp #Concatenacion de las restricciones a la variable que enviara los datos para la resolucion del problema

    problema.solve()#Solucion del problema


    sol=[]

    resultado_p="Solucion: Optima\n"
    for v in vars:
        resultado_p += "{} = {}\n".format(v.name,v.varValue)
        sol.append(v.varValue)
        resultado_p +="Solucion optima: {}\n".format(pulp.value(problema.objective)) #cadena String que guarda los valores de los resultados optimos para mostrar

    mostrar_solucion(resultado_p)

    v_grafica(sol,array_res,array_sol)

def v_grafica(sol, array_res,array_sol):#funcion para graficar restricciones

  x_values, y_values =np.meshgrid(np.linspace(0,100000,100), np.linspace(0,100000,100))
  
  array_rectas = []
  for i in range(len(array_res)):#bucle que recorreo los arrays de las restricciones y despeja los puntos para convertirlos en rectas
      linea = []
      punto_x = array_sol[i] / array_res[i][0]
      linea.append([punto_x, 0])

      if (len(array_res[i]) > 1):
          label_restric="{}X1 + {}X2 <= {}".format(array_res[i][0], array_res[i][1], array_sol[i])
          punto_y = array_sol[i] / array_res[i][1]
          linea.append([0, punto_y])
          plt.plot([punto_x, 0], [0, punto_y],label=label_restric)
      else:
         # linea.append(punto_x,6000)
          plt.axvline(x = punto_x)
          array_rectas.append(linea)
     # Ajusta el rango según tus necesidades
      in_region = np.all(
          [(array_res[i][0] * x_values + array_res[i][1] * y_values <= array_sol[i]) for i in range(len(array_res))],
          axis=0)

 # plt.fill_between(x_values, 0, y_values, where=in_region, color='gray', alpha=0.5, label='Zona Factible') linea que pinta la sona factible


  plt.scatter(sol[0],sol[1], color="red", label="Solucion Optima") #grafica del punto solucion
  plt.xlabel("X1")
  plt.ylabel("X2")
  plt.title("Solucion Grafica")
  plt.legend()
  plt.show()


def graficar_restriccion(coef_res, coef_sol):
    plt.plot(coef_res,coef_sol, linestyle='--')
def add_constraint(): #Funcion de adicion de restricciones
    constraint_entry = ttk.Entry(constraints_frame)
    constraint_entry.grid(column=0, row=len(constraints), padx=5, pady=5, sticky="ew")
    constraints.append(constraint_entry)

def mostrar_solucion(result): # Ventana que muestra los valores optimos para X1 y X2 con su solucion optima
    solucion_text=result.upper()
    ventana=tk.Toplevel(root)
    result_label = ttk.Label(ventana,text=solucion_text)
    result_label.pack()


root = tk.Tk()
root.title("Programación LIneal - Método Gráfico")
root.geometry("400x300")


message_tex="Ingrese coeficientes"
tipo = tk.StringVar(value="Maximizacion")
ttk.Label(root, text="Función objetivo, ingrese coeficientes :").grid(column=0, row=0, padx=5, pady=5, sticky="w")

funcion_ob = ttk.Entry(root)

funcion_ob.insert(0,message_tex)
funcion_ob.grid(column=1, row=0, padx=5, pady=5, sticky="ew")

ttk.Label(root, text="Elija el tipo de solución").grid(column=0, row=1, padx=5, pady=5, sticky="w")
ttk.OptionMenu(root, tipo, tipo.get(), "Maximizacion", "Minimizacion").grid(column=1, row=1, padx=5, pady=5, sticky="ew")

constraints_frame = ttk.LabelFrame(root, text="Restricciones")
constraints_frame.grid(column=0, row=2, columnspan=2, padx=5, pady=5, sticky="nsew")

constraints = [] #Arreglo donde se guardaran las restricciones del problema
add_constraint()

ttk.Button(root, text="Agregar Restricción", command=add_constraint).grid(column=0, row=3, padx=5, pady=5, sticky="ew")

ttk.Button(root, text="Resolver", command=solucion_MG).grid(column=1, row=3, padx=5, pady=5, sticky="ew")
root.mainloop()

