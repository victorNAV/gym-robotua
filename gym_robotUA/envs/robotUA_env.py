import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_robotUA.envs.circuito_2d import Circuito2D
import numpy as np
import json
import sys

class RobotUAEnv(gym.Env):

  MOVIMIENTOS = ["IZQ", "ARR", "DER", "ABA"]



  def __init__(self, config=""):
        """Constructor de la clase que representa el entorno. Puede recibir un archivo json para la configuración del circuito.
        Los parametros que se pueden configurar a traves de este archivo son:
            - MAX_MOVIMIENTOS. Numero de movimientos maximos para la resolución de una instancia del circuito.
            - visualizar. Opción que permite visualizar o no la ejecución del programa.
            - delay. Cantidad de milisegundos de espera entre cada movimiento (solo tiene sentido si la opción de visualizar es True)
            - tam_matrix. Tupla (x,y) con el numero de columnas (x) y filas (y) de la matriz.
            - tam_casillas. Tamaño de las casillas de la matriz en pixeles (solo tiene sentido si la opcion de visualizar es True)
            - objetivos. Array con una o dos tuplas (x,y). La primera tupla es la posicion (x,y) donde se encuentra el objetivo. 
              La segunda tupla es la posición (x,y) del subobjetivo (se deberá pasar primero por ésta casilla y luego por la meta para completar el circuto)
              Si solo existe una tupla unicamente se deberá llegar a esta casilla para completar el circuito.
            - trampas. Array de tuplas con la posicion (x,y) de cada trampa del circuito.
            - obstaculos. Array de tuplas con la posicion (x,y) de cada obstaculo del circuito.
            - incluir_delay. Numero de veces que se debe completar el circuito para que el delay entre movimientos cambie.
            - delay_incluido. Cantidad en milisegundos de espera entre cada movimiento despues de haber superado el circuito 'incluir_delay' veces.
        
        Los posibles movimientos del entorno son 4, codificados de la siguiente forma:
            - 0: movimiento izquierda
            - 1: movimiento arriba
            - 2: movimiento derecha
            - 3: movimiento abajo
        
        Contadores de la clase:
            - episodios_completados. Indica el numero de veces que se ha completado el circuito.
            - num_mov. Indica el numero de movimientos realizados hasta el momento para la resolución del circuito.
            - num_mov_totales. Indica el numero de movimientos totales que se han realizado en todas las resoluciones del circuito.
            - trampas_pisadas. Indica cuantas trampas se han pisado hasta el momento para la resolución del circuito.
            - trampas_totales. Indica cuantas trampas se han pisado en todas las resoluciones del circuito.
        """

        if config != "":
            try:
                with open("config/" + config) as file:
                    datos = json.load(file)
            except FileNotFoundError:
                print("ERROR!!")
                print("Fichero", config, "no encontrado")
                sys.exit()
            self.circuito = Circuito2D(visualizar=datos['visualizar'], tam_matrix = datos['tam_matrix'], delay = datos.get("delay", 0), tam_casilla = datos.get("tam_casilla", 35), objetivos = datos['objetivos'], trampas = datos.get("trampas", []), obstaculos = datos.get("obstaculos", []), incluir_delay = datos.get("incluir_delay", 7), delay_incluido = datos.get("delay_incluido", 100))
            self.MAX_MOVIMIENTOS = datos['MAX_MOVIMIENTOS']
        else:    
            self.circuito = Circuito2D()
            self.MAX_MOVIMIENTOS = 1000
            
        
        #4 posibles movimientos.
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Tuple( (spaces.Discrete(self.circuito.tam_matrix[0]), spaces.Discrete(self.circuito.tam_matrix[1])))
        self.estado = None
        self.done = False
        self.mov_bloqueado = False
        self.episodios_completados = 0
        self.num_mov = 0
        self.num_mov_totales = 0
        self.trampas_pisadas = 0
        self.trampas_totales = 0
        
        

  def step(self, action):      
        #Si la accion es un numero entre 0 y 3 ambos incluidos...
        if action in range(0,4):
            #Si el numero de movimientos realizados es menor al maximo permitido
            if self.num_mov < self.MAX_MOVIMIENTOS:
                #Si el movimiento no está bloqueado
                if not self.mov_bloqueado:
                    self.circuito.mover_robot(self.MOVIMIENTOS[action])
                    self.num_mov += 1
                    self.num_mov_totales += 1
                    if self.circuito.hayTrampa():
                        #print("Ha pisado una trampa, el siguiente movimiento será bloqueado")
                        self.mov_bloqueado = True
                        self.trampas_pisadas += 1
                        self.trampas_totales += 1

                    #estar en la meta y haber pasado por el subobjetivo (si lo hay)
                    if np.array_equal(self.circuito.getCoordenadasRobot(), self.circuito.getCoordenadasMeta()) and self.circuito.subobjetivoAlcanzado:
                        reward = 1
                        self.done = True
                        self.episodios_completados += 1
                    else:
                        reward = -1
                        self.done = False

                else:
                    #movimiento bloqueado
                    self.num_mov += 1
                    self.num_mov_totales += 1
                    self.mov_bloqueado = False
                    reward = -1
                    self.done = False

            else:
                #numero maximo de movimientos alcanzado
                #self.episodios_completados += 1
                self.done = True
                reward = -1
        else:
            print("ERROR!!")
            print("Accion no válida!!")
            print("Las acciones válidas son números comprendidos entre 0 y 3, ambos includos.")
            sys.exit()

        #devolver una tupla con la posicion del robot (x,y)
        self.estado = self.circuito.getCoordenadasRobot()
        info = {}

        return self.estado, reward, self.done, info


  def reset(self):
        #mover el robot al punto inicial
        self.circuito.reset()
        self.estado = self.circuito.getCoordenadasRobot()
        self.done = False
        self.num_mov = 0
        self.trampas_pisadas = 0
        self.mov_bloqueado = False
        return self.estado
        

  def render(self):

        return self.circuito.actualizar(self.episodios_completados)
