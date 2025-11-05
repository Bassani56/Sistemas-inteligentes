import os

# importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
import sys
import time
import threading

def main(vict_folder, env_folder, config_ag_folder):
    # Instantiate the environment
    env = Env(vict_folder, env_folder)
    

    def run_explorer(exp_file, resc, env):
        Explorer(env, exp_file, resc)  # apenas cria o Explorer, que vai usar resc


    threads = []

    for i in range(1, 4):
        resc_file = os.path.join(config_ag_folder, f"rescuer_{i}.txt")
        exp_file = os.path.join(config_ag_folder, f"explorer_{i}.txt")
        
        # Cria o objeto Rescuer primeiro
        resc = Rescuer(env, resc_file)
        
        run_explorer(exp_file, resc, env)
        # t_exp = threading.Thread(target=run_explorer, args=(exp_file, resc, env))
             
        # t_exp.start()
        
        # threads.append(t_resc)
        # threads.append(t_exp)

    # for t in threads:
    #     t.join()
    
    # Run the environment simulator
    env.run()
    
    print('env ::: ', env.dic)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    ROOT_PATH_REL = os.path.join(os.path.dirname(__file__), "..", "..")

    vict_folder_rel = os.path.join(ROOT_PATH_REL, "datasets", "vict", "408v")
    env_folder_rel  = os.path.join(ROOT_PATH_REL, "datasets", "env", "94x94_408v")
    
    vict_folder = os.path.abspath(vict_folder_rel)
    env_folder  = os.path.abspath(env_folder_rel)

    config_ag_folder = os.path.join(os.path.dirname(__file__), "config_ag_1")

    main(vict_folder, env_folder, config_ag_folder)
