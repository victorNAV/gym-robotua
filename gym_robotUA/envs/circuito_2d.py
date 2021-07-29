import pygame
import sys
import os
import numpy as np
import json

class Circuito2D:
    #colores
    color_fondo = (243, 240, 193)
    black       = (  0,   0,   0)
    white       = (255, 255, 255)
    red         = (255,   0,   0)
    green       = (  0, 255,   0)
    blue        = (  0,   0, 255)


    CONVERSION = {
        'IZQ' : [-1, 0],
        'ARR' : [0, -1],
        'DER' : [1, 0],
        'ABA' : [0, 1]
    }


    def __init__(self, NOMBRE_PROG="Robot UA", tam_matrix=(10,10), delay = 0, tam_casilla = 50, objetivos = [(9,0)], trampas = [ (2,0), (2,3), (5,2), (2,5), (2,7), (6,3)], obstaculos = [ (5, 5), (2, 1), (2, 4), (9, 8) ], visualizar = True, incluir_delay = 190, delay_incluido = 150):
        
        pygame.init()
        self.tam_screen= (tam_matrix[0] * tam_casilla, tam_matrix[1] * tam_casilla)
        if visualizar:
            self.screen = pygame.display.set_mode(self.tam_screen)
            pygame.display.set_caption(NOMBRE_PROG)
            ruta_icono = os.path.join(u'imagenes', u'icono-ua.png')
            icono = pygame.image.load(ruta_icono)
            pygame.display.set_icon(icono)

        self.tam_casilla = tam_casilla

        #creamos las trampas a partir de su imagen, y obtenemos el rectangulo que lo representa y lo movemos a su posicion.
        self.trampas = []
        self.trampasrect = []
        if len(trampas) > 0:
            for tram in trampas:
                tr = pygame.image.load("imagenes/trampa.png")
                tr = pygame.transform.scale(tr, (self.tam_casilla, self.tam_casilla))
                self.trampas.append(tr)
                trrect = tr.get_rect()
                trrect = trrect.move(tram[0] * self.tam_casilla, tram[1] * self.tam_casilla)
                self.trampasrect.append(trrect)

        #creamos el subobjetivo a partir de su imagen, y obtenemos el rectangulo que lo representa, y lo movemos a su posicion
        if len(objetivos) > 1:
            self.subobjetivo = pygame.image.load("imagenes/punto-de-control.png")
            self.subobjetivo = pygame.transform.scale(self.subobjetivo, (self.tam_casilla, self.tam_casilla))
            self.subobjetivorect = self.subobjetivo.get_rect()
            self.subobjetivorect = self.subobjetivorect.move([objetivos[-1][0] * self.tam_casilla, objetivos[-1][1] * self.tam_casilla ])
            self.subobjetivoAlcanzado = False
        else:
            self.subobjetivorect = None
            self.subobjetivoAlcanzado = True
            

        #creamos la meta a partir de su imagen, y obtenemos el rectangulo que lo representa, y lo movemos a la casilla de meta
        self.meta = pygame.image.load("imagenes/linea-de-meta.png")
        self.meta = pygame.transform.scale(self.meta, (self.tam_casilla, self.tam_casilla))
        self.metarect = self.meta.get_rect()
        self.metarect = self.metarect.move([objetivos[0][0] * self.tam_casilla , objetivos[0][1] * self.tam_casilla ])

        #creamos el robot a partir de su imagen, y obtenemos el rectangulo que lo representa
        self.robot = pygame.image.load("imagenes/robot.png")
        self.robot = pygame.transform.scale(self.robot, (self.tam_casilla, self.tam_casilla))
        self.robotrect = self.robot.get_rect()
        
        #creamos los obstaculos a partir de la imagen, y obtenemos el rectangulo que lo representa
        self.obstaculos = []
        self.obsrects = []
        for obs in obstaculos:
            ob = pygame.image.load("imagenes/obstaculo.png")
            ob = pygame.transform.scale(ob, (self.tam_casilla, self.tam_casilla))
            self.obstaculos.append(ob)
            obrect = ob.get_rect()
            obrect = obrect.move(obs[0] * self.tam_casilla, obs[1] * self.tam_casilla)
            self.obsrects.append(obrect)

        self.delay = delay
        self.incluir_delay = incluir_delay
        self.visualizar = visualizar
        self.delay_incluido = delay_incluido

        #matriz
        self.tam_matrix = tam_matrix
        self.grid = [ [1]*tam_matrix[0] for n in range(tam_matrix[1])]
        

    def mover_robot(self, action):
        """Función que realiza el movimiento del robot. El movimiento se realizará si:
        1º al realizar el movimiento el robot queda dentro de la matriz.
        2º al realizar el movimiento no hay obstaculos."""
        
        movimiento = self.CONVERSION.get(action)[0] * self.tam_casilla, self.CONVERSION.get(action)[1] * self.tam_casilla

        if self.dentroMatriz(movimiento):
            #si no hay obstaculos, permitir movimiento
            if not self.hayObstaculos(movimiento):
                self.robotrect = self.robotrect.move(movimiento)
                #si hay subobjetivo y el robot está en él
                if isinstance(self.subobjetivorect,pygame.Rect) and self.estarEnsubobjetivoAlcanzado():
                    self.subobjetivoAlcanzado = True

            #else:
                #print("Obstaculo en la posicion seleccionada.")

        #else:
            #print("Movimiento no permitido fuera del borde de la matriz.")



    def actualizar(self, episodios_completados):  
        """Función para actualizar la ventana del juego.
        Si la visualización esta activa se actualizarán todos los elementos despues de haber realizado el movimiento.""" 
        #Si se ha pulsado el boton de salir se cierra el programa.
        self.comprobarEventos()

        #Si se quiere visualizar
        if self.visualizar:
            self.screen.fill(self.color_fondo)            
            self.pintarMatriz() #pintar matriz            
            self.pintarObstaculos() #pintamos obstaculos
            self.pintarTrampas() #pintamos trampas        
            self.pintarRobotObjetivos() #pintamos robot, subobjetivo y meta
            pygame.display.update() #actualizamos imagen
            
            #si los episodios completados es igual al indicado, cambiamos el delay 
            if episodios_completados == self.incluir_delay:
                self.delay = self.delay_incluido

            pygame.time.delay(self.delay)

    def reset(self):
        """Función para restablecer la configuración inicial del circuito."""
        self.robotrect.x = 0
        self.robotrect.y = 0
        if isinstance(self.subobjetivorect, pygame.Rect):
            self.subobjetivoAlcanzado = False
        else:
            self.subobjetivoAlcanzado = True



    def estarEnsubobjetivoAlcanzado(self):
        """Funcion que comprueba si el robot está en el subobjetivo (si es que lo hay)
        Devuelve True si el robot está en la celda del subobjetivo.
        Devuelve False si el robot no está en la celda del subobjetivo."""
        return self.robotrect.x == self.subobjetivorect.x and self.robotrect.y == self.subobjetivorect.y



    def dentroMatriz(self, movimiento):
        """Función que comprueba si al hacer el movimiento pasado como parametro el robot quedaría dentro de la matriz.
        Devuelve True si el robot queda dentro de la matriz.
        Devuelve False si el robot sale de la matriz."""
        #----------------no sale por la izquierda-----&&---------no sale por arriba-------------&&-----------------------------no sale por derecha-----------------------------------------------&& -----------------------------------no sale por abajo-----------------------------------------
        return movimiento[0] + self.robotrect.x >= 0 and movimiento[1] + self.robotrect.y >= 0 and movimiento[0] + self.robotrect.x <= self.tam_matrix[0] * self.tam_casilla - self.tam_casilla and movimiento[1] + self.robotrect.y <= self.tam_matrix[1] * self.tam_casilla - self.tam_casilla

    def hayTrampa(self):
        haytrampa = False
        for tram in self.trampasrect:
            if self.robotrect.x == tram.x and self.robotrect.y == tram.y:
                haytrampa = True
                break
                
        return haytrampa

    def hayObstaculos(self, movimiento):
        """Función que comprueba si al hacer el movimiento pasado como parametro el robot estaría en una posicion donde hay un obstaculo.
        Devuelve True si el robot se mueve a un obstaculo.
        Devuelve False si el robot no se mueve a un obstaculo."""
        #recorrer la lista de obstaculos y si alguno está en la posicion de movimiento, denegar el movimiento
        hayobstaculo = False
        for obs in self.obsrects:
            if movimiento[0] + self.robotrect.x == obs.x and movimiento[1] + self.robotrect.y == obs.y:
                hayobstaculo = True
                break
        return hayobstaculo



    def getCoordenadasRobot(self):
        """Función que devuelve la posición logica del robot dentro de la matriz."""
        return ( int(self.robotrect.x / self.tam_casilla), int(self.robotrect.y / self.tam_casilla) )



    def getCoordenadasMeta(self):
        """Función que devuelve la posición logica de la meta dentro de la matriz."""
        return ( int(self.metarect.x / self.tam_casilla), int(self.metarect.y / self.tam_casilla) )



    def escribirJSON(self, tam_matrix, delay, tam_casilla, objetivos, obstaculos):
        """Función auxiliar para escribir la configuración del entorno en un fichero JSON."""
        datos = {}
        datos['tam_matrix'] = tam_matrix
        datos['delay'] = delay
        datos['tam_casilla'] = tam_casilla
        datos['objetivos'] = objetivos
        datos['obstaculos'] = obstaculos

        with open('config/config1.json', 'w') as file:
            json.dump(datos, file, indent = 4)


    def pintarMatriz(self):
        """Función que pinta la matriz (siempre y cuando la visualización esté activa)."""
        x, y = 0, 0
        for row in self.grid:
            for column in row:
                pygame.draw.rect(self.screen, self.black, (x, y, self.tam_casilla, self.tam_casilla), 1)
                x += self.tam_casilla
            x = 0
            y += self.tam_casilla



    def pintarObstaculos(self):
        """Función que pinta los obstaculos del circuito (siempre y cuando la visualización esté activa)."""
        for img, rect in zip(self.obstaculos, self.obsrects):
            self.screen.blit(img, rect)
    


    def pintarRobotObjetivos(self):
        """Función que pinta el robot, el subobjetivo y la meta del circuito (siempre y cuando la visualización esté activa)."""
        self.screen.blit(self.robot, self.robotrect)
        if isinstance(self.subobjetivorect, pygame.Rect):
            self.screen.blit(self.subobjetivo, self.subobjetivorect)
        self.screen.blit(self.meta, self.metarect)

    def pintarTrampas(self):
        """Función que pinta las trampas del circuito (siempre y cuando la visualización esté activa)."""
        for img, rect in zip(self.trampas, self.trampasrect):
            self.screen.blit(img,rect)


    def comprobarEventos(self):
        """Función que comprueba los eventos que ocurren en pygame.
        Si uno de ellos es que se ha pulsado el boton de salir el programa terminará."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Saliendo del programa.")
                sys.exit()
                return
        

