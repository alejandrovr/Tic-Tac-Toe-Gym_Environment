import gym
from gym import error, spaces, utils
from gym.utils import seeding
from htmd.ui import *
from htmd.vmdviewer import getCurrentViewer

class TicTac4(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        [os.remove(i) for i in glob("/home/alejandro/virtual_chemist/snapshots/vmdscene*.tga")]
        self.mol = Molecule('3iej') #this should be a roulette wheel
        self.mol.filter('chain A')
        self.mol.filter('not water')
        self.mol.reps.add('protein',style='Licorice',color='16')
        self.mol.reps.add('not protein',style='Licorice',color='8')
        self.mol.view()
        first_caption = self.mol._moveVMD(action='init')
        self.state = first_caption
        self.counter = 0
        self.done = 0
        self.reward = 0
        self.add = [0, 0]

    def check(self):
        whites = len(np.where(self.state>.7)[0])
        print('whites',whites)
        total = self.state.shape[0] * self.state.shape[1]
        coef = (whites / total) * 100
        self.reward = coef * 0.1 #/ self.counter) * 0.1
        
        if self.done:
            self.reward = coef #/ self.counter

    def step(self, target):
        if target=='submit':
            self.done = True
            self.check()
            return [self.state, self.reward, self.done, self.add]
        

        self.state = self.mol._moveVMD(action=target)
        self.counter += 1
        self.render()
        self.check() #get reward
        return [self.state, self.reward, self.done, self.add]

    def reset(self):
        #reset view!
        vhandle = getCurrentViewer()
        vhandle.send("mol delete all") 
        self.__init__()
        self.counter = 0
        self.done = 0
        self.reward = 0
        return self.state

    def render(self):
        pass
