"""
Custom OpenAI Gym Enviornment for the Bixler2
performing a perched landing manoeuvre.
"""
import gym
import json
import time
import numpy as np 
from gym import logger, spaces
from gym.utils import seeding
import math
# import scenarios
from flightaxis import FlightAxis

class RealFlightEnv(gym.Env):

    def __init__(self):

        self.flightaxis = FlightAxis()
        
        self.flightaxis.disconnect()
        self.flightaxis.connect()

        # self.action_space = gym.spaces.Box(low = np.array([-1, -1, -1, -1]),
        #                                     high = np.array([1, 1, 1, 1]), dtype = np.float32)

        # self.action_space = gym.spaces.Box(low = np.array([-1, -1]),
        #                                     high = np.array([1, 1]), dtype = np.float32)

        self.action_space = gym.spaces.MultiDiscrete([11, 11])

        self.observation_space = gym.spaces.Box(low=-np.inf, high = np.inf, shape = (1, 9), dtype = np.float32)

        self.time = 0.0
        self.pT = 0.0
        self.cT = 0.0
        self.flag_1, self.flag_2, self.flag_3 = False, False, False


        
    def step(self, action):
        # peform action

        # time.sleep(0.05)

        self.flightaxis.set_action(action)

        # TODO update control array
        # self.flightaxis.controls[0] = self.flightaxis.ail_control
        self.flightaxis.controls[1] = self.flightaxis.elev_control
        # self.flightaxis.controls[1] = 0.45
        self.flightaxis.controls[2] = self.flightaxis.throttle_control
        # self.flightaxis.controls[2] = 1.0
        # self.flightaxis.controls[3] = self.flightaxis.rud_control
        
        # print(self.controls)

        self.flightaxis.set_controls(self.flightaxis.controls)

        self.cT = self.flightaxis.phys_time
        dt =  self.cT - self.pT

        self.time += dt


        # print(self.time, dt )

        # self.update_elev(steptime)

        self.pT = self.cT


        obs = self.flightaxis.get_state()

        reward = self.get_reward()
        # print(reward)

        done = self.is_terminal()
     
        return obs, reward, done, {}
        

    def reset(self):

        self.flightaxis.reset()
        self.pT = self.flightaxis.phys_time
        self.time = 0.0
        self.flag_1, self.flag_2, self.flag_3 = False, False, False
        return self.flightaxis.get_state()

    def render(self, mode):
        pass

    def close(self):
        self.flightaxis.disconnect()

    # def get_reward(self):
    #     # angular_ref = np.array([150, 0 , 0])
    #     angular_ref = np.array([0, 90 , 0])
    #     # angular_ref = 90 
    #     weights = np.array([0.25, 0.50, 0.25])

    #     angular_rates = np.array([self.flightaxis.get_state()[9], self.flightaxis.get_state()[10], self.flightaxis.get_state()[11]])
    #     return -np.dot((angular_rates-angular_ref) ** 2, weights)
    #     # return -(self.flightaxis.get_state()[10] - angular_ref)**2

    def get_reward(self):

        state = self.flightaxis.get_state()

        # print(f"{state[]=} {state[4]=} {state[5]=}")

        # if state[2] < 10:
        #     return - 100000000
        target_x = 0
        radius = 50

        distance = math.sqrt((state[0]- target_x)**2 + (state[1] - (100 + radius))**2)

        return - (distance - radius)**2


    def is_terminal(self):

        state = self.flightaxis.get_state()
        # print(state[4])

        def is_in_range(x,lower,upper):
            return lower < x and x < upper
        # # Check x remains sensible
        # # if not is_in_range(self.position_e[0,0],-110,10):
        # #     return True
        if self.time > 15.0:
            return True
        # # Check y remains sensible
        # if not is_in_range(state[1],-5,5):
        #     return True
        # Check z remains sensible (i.e. not crashed)
        # if not is_in_range(abs(state[2]),75,125):
        #     return True
        # if not is_in_range(state[10],-100,300):
        #     return True
        # # Check u remains sensible, > 0
        # if not is_in_range(state[6],0,25):
        #     return True
        if self.flightaxis.pitch > 80:
            self.flag_1 = True
        if self.flag_1:
            if self.flightaxis.pitch < 10:
                self.flag_2 = True
        if self.flag_2:
            if self.flightaxis.pitch < -80:
                self.flag_3 = True
        if self.flag_3:
            if self.flightaxis.pitch > -5:
                return True
        return False










        
