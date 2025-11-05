# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### It walks randomly in the environment looking for victims. When half of the
### exploration has gone, the explorer goes back to the base.

import sys
import os
import random
import math
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map

import sys

flag = 1

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the explorer's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
    
        self.walk_stack = Stack()  # a stack to store the movements
        self.set_state(VS.ACTIVE)  # explorer is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0
        self.map = Map()           # create a map for representing the environment
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals
        self.config_file = config_file
        
        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())

    # def verific_agent(self, name_file):
    #     string = str(name_file)
    #     partes = string.split("\\")     # precisa ser \\ ou string bruta
    #     nome = partes[-1].replace(".txt", "")

    #     return nome

    def get_next_position(self):
        """Retorna o próximo movimento usando DFS."""
        # Se a pilha estiver vazia, inicializa com a posição atual
        if self.walk_stack.is_empty():
            self.walk_stack.push((self.x, self.y))
        
        nome = os.path.splitext(os.path.basename(self.config_file))[0].upper()

        priority_list_1 = [1, 2, 3, 4, 5, 0, 6, 7]

        priority_list_2 = [2, 3, 4, 1, 5, 0, 6, 7]

        priority_list_3 = [3, 4, 5, 2, 1, 0, 6, 7]

        if nome == "explorer_1":
            prioridade = priority_list_1
        elif nome == "explorer_2":
            prioridade = priority_list_2
        else:
            prioridade = priority_list_3

        while not self.walk_stack.is_empty():
            cx, cy = self.walk_stack.pop()
            self.x, self.y = cx, cy

            obstacles = self.check_walls_and_lim()

            directions = prioridade

            for direction in directions:
                if obstacles[direction] == VS.CLEAR:
                    dx, dy = Explorer.AC_INCR[direction]
                    nx = cx + dx
                    ny = cy + dy

                    # Se ainda não visitou essa célula no mapa
                    if not self.map.is_visited((nx, ny)):
                        # Empilha a posição atual para retornar depois (DFS)
                        self.walk_stack.push((cx, cy))
                        # Empilha o próximo passo para explorar
                        self.walk_stack.push((nx, ny))
                        return dx, dy

        # Se não houver mais posições para visitar, fica parado
        return 0, 0

    def explore(self):
        # get an random increment for x and y       
        dx, dy = self.get_next_position()

        # Moves the explorer agent to another position
        rtime_bef = self.get_rtime()   ## get remaining batt time before the move
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()   ## get remaining batt time after the move

        # Test the result of the walk action
        # It should never bump, since get_next_position always returns a valid position...
        # but for safety, let's test it anyway
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            #print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # puts the visited position in a stack. When the batt is low, 
            # the explorer unstack each visited position to come back to the base
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin of 
            # the coordinate system used by the agents
            self.x += dx
            self.y += dy          

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[seq] = ((self.x, self.y), vs)
                #print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
            # Calculates the difficulty of the visited cell
            difficulty = (rtime_bef - rtime_aft)
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

        return

   
   

    def come_back(self):
        dx, dy = self.walk_stack.pop()
        dx = dx * -1
        dy = dy * -1

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            # print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy
            #print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
        
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        consumed_time = self.TLIM - self.get_rtime()
        if consumed_time < self.get_rtime():
            self.explore()
            return True

        # time to come back to the base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
            #input(f"{self.NAME}: type [ENTER] to proceed")
            self.resc.go_save_victims(self.map, self.victims)
            return False

        self.come_back()
        return True

 # def explore(self):
    #     """Explora o ambiente usando DFS."""
    #     dx, dy = self.get_next_position()

    #     if dx == 0 and dy == 0:
    #         # Não há mais para onde ir
    #         return

    #     # Move o agente
    #     rtime_bef = self.get_rtime()
    #     result = self.walk(dx, dy)
    #     rtime_aft = self.get_rtime()

    #     if result == VS.BUMPED:
    #         self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
    #         return

    #     if result == VS.EXECUTED:
    #         # Atualiza posição
    #         self.x += dx
    #         self.y += dy

    #         # Verifica vítima
    #         seq = self.check_for_victim()
    #         if seq != VS.NO_VICTIM:
    #             vs = self.read_vital_signals()
    #             self.victims[vs[0]] = ((self.x, self.y), vs)
    #             # print(f"{self.NAME} Victim found at ({self.x}, {self.y})")

    #         # Calcula dificuldade
    #         difficulty = (rtime_bef - rtime_aft)
    #         if dx == 0 or dy == 0:
    #             difficulty /= self.COST_LINE
    #         else:
    #             difficulty /= self.COST_DIAG

    #         # Marca célula como visitada
    #         self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
