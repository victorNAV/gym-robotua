from gym.envs.registration import register

register(
    id='robotUA-v0', #este es el nombre del entorno que se le pasa a make()
    entry_point='gym_robotUA.envs:RobotUAEnv', #nombre de la clase del entorno
)
