import gym
from gym import error, spaces, utils
from gym.utils import seeding
from htmd.ui import *
from htmd.vmdviewer import getCurrentViewer

class TicTac4(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        [os.remove(i) for i in glob("/home/alejandro/rl_chemist/snapshots/vmdscene*.tga")]
        self.mol = Molecule('/home/alejandro/rl_chemist/3iej.pdb') #this should be a roulette wheel
        self.mol.filter('chain A and resname 599')
        self.mol.reps.add('all',style='Licorice',color='8')
        #self.mol.reps.add('protein',style='Licorice',color='16')
        self.mol.view()
        [self.mol._moveVMD(action='scaleout') for i in range(10)]
        first_caption = self.mol._moveVMD(action='init')
        self.state = first_caption
        self.counter = 0
        self.done = 0
        self.reward = 0
        self.add = {}
        self.available_actions = ['rotx','roty','rotz','scalein','scaleout','submit']
        self.white_history_x = [0.0]
        self.history = []
    def check(self):
        whites = len(np.where(self.state>.7)[0])
        total = self.state.shape[0] * self.state.shape[1]
        coef = (whites / total) * 100
        last_coef = self.white_history_x[-1]
        hist_reward =  coef - last_coef
        self.reward =  0.0 #hist_reward
        
        if self.done:
            self.reward = len(self.history) * -1.0

    def step(self, target):
        target = self.available_actions[target]
        if target not in self.available_actions:
            raise
        self.history.append(target)
        if target=='submit':
            self.done = True
            self.check()
            return [self.state, self.reward, self.done, self.add]
        
        #if not submit, update state and compute reward
        self.state = self.mol._moveVMD(action=target)
        self.counter += 1
        self.check() #get reward
        return [self.state, self.reward, self.done, self.add]

    def reset(self):
        #reset view!
        vhandle = getCurrentViewer()
        vhandle.send("mol delete all") 
        self.__init__()
        return self.state #first caption
