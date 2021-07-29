import gym
import gym_robotUA

env = gym.make('robotUA-v0')
#env = gym.make('robotUA-v0' config='sinSubobjetivo/5x5.json')
#env = gym.make('robotUA-v0' config='sinSubobjetivo/10x10.json')
#env = gym.make('robotUA-v0' config='sinSubobjetivo/12x20.json')
#env = gym.make('robotUA-v0' config='sinSubobjetivo/15x15.json')
done = False
observation = env.reset()
intento = 0
print(env)

while intento < 9999:
    print("----------Intento", intento, "----------")
    while not done:
        #env.action_space.sample devuelve un numero entero entre 0 y 3, ambos incluidos.
        #0: movimiento izquierda
        #1: movimiento arriba
        #2: movimiento derecha
        #3: movimiento abajo
        action = env.action_space.sample() 
        observation, reward, done, _ = env.step(action) #(_ es un valor que no lo usaremos)
        env.render()
        if done:
            print("Movimiento realizados:\t" , env.num_mov)
            print("Trampas pisadas:\t", env.trampas_pisadas)
            print("")
            intento += 1
            env.reset()
            env.render()
    
    done = False
        
print("--------------------")
print("Numero de veces completado:\t", env.episodios_completados)
print("Movimientos totales realizados:\t", env.num_mov_totales)
print("Trampas pisadas totales:\t", env.trampas_totales)
print("")
env.close()
