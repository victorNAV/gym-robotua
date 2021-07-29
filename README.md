# ENTORNO DESARROLLADO POR VÍCTOR NAVARRO

En este proyecto nos centraremos en el diseño e implementación de un entorno simulado en el que un robot debe aprender a salir de una habitación sin intervención humana. Este entorno incluye obstáculos que dificultan el alcance del objetivo del robot. También, tiene la característica de ser configurado de forma personalizada. Y además, todo ello acompañado de un estudio comparativo entre los diferentes algoritmos de Aprendizaje por refuerzo empleados para su resolución. 


## Instalación del entorno
Para poder ejecutar el proyecto, deberemos tener instalada la versión 3.5 o superior de Python. 

Una vez la tengamos, necesitamos descargar e instalar la librería PyGame. Para ello, desde el terminal de comandos, ejecutaremos pip install pygame. A continuación, será necesaria la librería Gym. Ejecutando el comando pip install gym descargamos e instalamos esta librería. Luego, en la carpeta del proyecto, debemos ejecutar el comando pip install -e. Esto creará los archivos necesarios para poder ejecutar nuestro entorno Gym personalizado.

Finalmente, para comprobar que todo funciona correctamente podemos ejecutar el comando py demo.py, lo que ejecutará el código de prueba aportado con el proyecto.




## Implementación del entorno
Para la implementación del entorno se ha hecho una división de responsabilidades entre dos clases fundamentales, RobotUAEnv y Circuito2D, implementadas en los ficheros robotUA_env.py y circuito_2d.py respectivamente, dentro del subdirectorio envs.

RobotUAEnv representa el entorno en general, es la clase que se encarga de crear el circuito bajo la configuración deseada y delega el movimiento del robot si se cumplen las condiciones necesarias. Esta clase se apoya en Circuito2D creando una instancia de esta. 

Por otro lado, Circuito2D es la clase que representa físicamente el circuito con todos sus componentes. Utiliza la librería PyGame para pintar gráficamente el circuito y poder visualizarlo en caso de que sea necesario. También, cuando se desea realizar un movimiento se encarga de comprobar que se realice dentro de la matriz y que además no haya obstáculos.

### Clase RobotUAEnv
Como se ha comentado con anterioridad, la clase RobotUAEnv extiende de gym.Env, y por lo tanto, debe implementar una serie de métodos para su funcionamiento.

El constructor puede recibir opcionalmente un parámetro. Este parámetro hace referencia al fichero JSON de configuración que contendrá las características del entorno. Se espera que sea la cadena con la dirección relativa dentro del directorio config con el fichero JSON. Si el parámetro está vacío el entorno se construirá bajo unos valores predeterminados. Además, dentro del constructor también definimos el espacio de acción disponible para el agente, que en nuestro caso es un espacio discreto son cuatro posibles movimientos, y, también,  el espacio de observación como un espacio también discreto según el tamaño de la matriz.

Step es la función que se encarga de realizar el movimiento del agente, recibe un parámetro que es la acción a realizar  y devuelve cuatro variables. El parámetro recibido es un número entero y su codificación es la que sigue:
 - Movimiento hacia la izquierda: 0
 - Movimiento hacia arriba: 1
 - Movimiento hacia la derecha: 2
 - Movimiento hacia abajo: 3

Existen una serie de condiciones para poder realizar un movimiento:
 - El número de movimientos hasta el momento es menor que el número máximo permitido.
 - El movimiento no está bloqueado a causa de haber pisado una trampa.
 - El movimiento a realizar está dentro del circuito.
 - El movimiento a realizar no sea hacia un obstáculo.

Tras haber realizado el movimiento, si el robot ha pisado una trampa el siguiente movimiento será bloqueado.

En cuanto a las variables de salida son las siguientes:
 - Estado. Representa la posición lógica actual del agente tras realizar el movimiento.
 - Reward. Es la recompensa asociada al movimiento realizado. Esta recompensa es 1 si el agente ha llegado al objetivo o -1 si no ha podido llegar, el movimiento está bloqueado o se ha alcanzado el número máximo de movimientos.
 - Done. Hace referencia a si el agente ha resuelto el episodio.
 - Info. Esta variable es un diccionario que puede contener información adicional, aunque en nuestro caso no es necesario.

La función reset no recibe ningún parámetro. Se utiliza para restablecer el entorno al estado inicial. Mueve el robot a la posición (0, 0) y devuelve esa posición como variable de salida.

Como última función a implementar tenemos render. Esta función no recibe ningún parámetro y se utiliza para visualizar el estado del circuito. Delega su implementación a la clase Circuito2D.

Por otro lado, esta clase tiene una serie de contadores que nos ayudarán a evaluar los algoritmos que implemente la clase cliente del entorno. Estos contadores son:
 - “episodios_completados” es el número total de veces que se ha resuelto el circuito.
 - “num_mov” representa el número de movimientos que se han realizado desde el inicio del episodio. 
 - “num_mov_totales” cuenta todos los movimientos realizados en todos los episodios para una instancia del entorno.
 - “trampas_pisadas” es la cantidad de trampas que se ha pisado en un episodio.
 - “trampas_totales” hace referencia a la cantidad total de trampas pisadas para una instancia del entorno.

 
### Clase Circuito2D
La clase Circuito2D contiene todos los elementos necesarios para representar físicamente el entorno. La clase RobotUAEnv crea una instancia de esta clase en su constructor pasándole como parámetro los diferentes elementos que son configurables.

Los elementos que recibe como parámetro son el tamaño de la matriz, localización del punto objetivo, de las trampas y obstáculos, si se debe visualizar el entorno, el retardo de tiempo entre cada movimiento, el número de episodios que deben pasar para cambiar el tiempo entre cada movimiento, el nuevo tiempo entre movimientos tras completar un cierto número de episodios y el tamaño de las elementos dentro de la matriz. Todos estos elementos vienen derivados de los requisitos recopilados en la fase de análisis.

Si se ha seleccionado una configuración en la que se debe visualizar el entorno, se crea una ventana de escritorio, creando una instancia de PyGame y utilizando las funciones adecuadas. Gracias a esta librería podemos cargar las diferentes imágenes de lo que representa una trampa, el punto objetivo, el robot y los obstáculos.

En el apartado anterior dijimos que la función render se delegaba en esta clase. Esta función sólo tiene sentido si se ha seleccionado la opción de visualización, es por esto que se lo delegamos a esta clase pues es ella la que contiene la configuración del entorno.

## Configuración del entorno
Uno de los requisitos no funcionales era la posibilidad de crear el entorno bajo diferentes configuraciones. Esta característica hace que se pueda tener un número de configuraciones muy elevado y personalizadas, ya que no hay un límite en los tamaños de la matriz ni número de obstáculos.  También, dispone de una configuración por defecto.

Este requisito ha sido implementado gracias a la lectura de ficheros JSON, situados en el directorio config, que contienen la configuración. En estos ficheros se pueden incluir los siguientes parámetros:
 - “MAX_MOVIMIENTOS” es un número entero que representa el número máximo de movimientos que se pueden realizar para la resolución del circuito.
 - “visualizar” es un dato booleano que utilizamos para activar la visualización del circuito y los movimientos del robot. Si esta opción está desactivada el programa tendrá  - unos tiempos de ejecución mucho menores.
 - “tam_matrix” es una dupla de valores enteros (x, y) que representan el tamaño de la matriz en su eje x e y.
 - “delay” nos referimos a este parámetro como el número entero que representa la cantidad de milisegundos entre cada movimiento del robot. Este parámetro sólo tiene sentido cuando la opción de visualización está activada).
 - “tam_casilla” es un número entero que representa el tamaño, en píxeles, de las celdas de la matriz. Este parámetro sólo tiene sentido cuando la visualización está activada.
 - “objetivos” es un array con una o dos duplas (x, y) que contiene las coordenadas de los objetivos. Estas coordenadas serán la posición donde deberá llegar el robot para completar el circuito. El valor de la segunda dupla lo explicaremos en el apartado de extras del presente capítulo.
 - “trampas” es un array que contiene un número variable de duplas (x, y), las cuales son la localización de cada una de las trampas.
 - “obstaculos” también es un array que contiene un número variable de duplas (x, y), con las coordenadas de los obstáculos.
 - “delay” es un número entero que representa el tiempo de espera entre movimientos, se mide en milisegundos. Esta opción sólo tiene sentido con la visualización activada.
 - “incluir_delay” es un número entero. Tras la resolución del circuito en este número de veces el tiempo entre movimiento se verá modificado. Este parámetro sólo tiene sentido cuando la visualización está activada.
 - “delay_incluido” al igual que el anterior, es un número entero. Cuando se resuelva el circuito tantas veces como marque la variable “incluir_delay”, se modificara el tiempo entre movimientos a este valor. Solo tiene sentido cuando la opción de visualización está activada.ç
Si alguno de estos parámetros no se encuentran en el fichero de configuración, se usarán unos valores por defecto.
##  Cliente del entorno
La utilización del entorno es bastante simple. Solo debe tener en cuenta unas pocas funciones y para qué sirven. El fichero demo.py contiene un ejemplo.

Para que un cliente pueda hacer uso de nuestro entorno debe hacer el import de “gym_robotUA” y crear una instancia del entorno con la llamada a la función  “gym.make(‘robotUA-v0’)”. A continuación, dentro de un bucle hasta el número de episodios que el código cliente quiere definir, debe realizar acciones haciendo llamadas a la función “step(action)”, dónde action es el movimiento a realizar. También, puede obtener una acción al azar dentro del espacio de acciones disponible haciendo una llamada a la función action_space.sample(). Luego, tras cada movimiento, debe llamar a la función render() para visualizar los cambios dentro del entorno. Y por último, cuando el episodio ha sido completado, debe llamar a la función “reset()” para restablecer reiniciar los parámetros necesarios.


