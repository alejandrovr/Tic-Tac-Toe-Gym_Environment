import gym
from gym import error, spaces, utils
from gym.utils import seeding
from htmd.ui import *
from htmd.vmdviewer import getCurrentViewer
import random

def LJ_potential(prot,lig):
    from scipy.spatial.distance import cdist
    pcoords = prot.coords.squeeze()
    ligcoords = lig.coords.squeeze()
    pl_dists = cdist(pcoords,ligcoords)
    return np.min(pl_dists)

class TicTac4(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        [os.remove(i) for i in glob("/home/alejandro/rl_chemist/snapshots/vmdscene*.tga")]
        
        levels = {'3iej.pdb':('A','599'),}
        levels_keys = list(levels.keys())
        selected_level = random.choice(levels_keys)
        
        crystal = Molecule(selected_level)
        prot = crystal.copy()
        prot.filter('protein and chain {} and noh and (same residue as within 5 of resname {})'.format(levels[selected_level][0],levels[selected_level][1]))
        self.prot = prot.copy()
        self.prot.view(style='Licorice',color=8)

        self.mol = crystal.copy()
        self.mol.filter('chain {} and resname {}'.format(levels[selected_level][0],levels[selected_level][1]))
        self.mol.get_rot_bonds()
        self.mol.view()        
        [self.mol._moveVMD(action='scaleout') for i in range(6)]
        #TODO: randomize starting point
        self.available_actions = ['rotx','roty','rotz','switch_dir','movedih','nextdih']
        #self.available_actions = ['switch_dir','movedih','nextdih']
        #first_caption = [self.mol._moveVMD(action='nextdih') for i in range(random.randint(1,1))][-1]
        first_caption = self.mol._moveVMD(action='nextdih')
        self.state = first_caption
        self.counter = 0
        self.done = 0
        self.reward = 0
        self.add = {}
        self.history = []

    def check_old(self):
        ljpot = LJ_potential(self.prot,self.mol)
        if ljpot < 1.0: #reward clashes
            self.reward = 10.0
            self.done = True 
            
        elif self.counter > 10:
            self.reward = -10.0
            self.done = True
            
        else:
            self.reward = 0.0
            
        return

    def check(self):
        if 'movedih' in self.history:
            self.reward = 10.0
            self.done = True 
            
        elif len(self.history) > 1:
            self.reward = -10.0
            self.done = True
            
        else:
            self.reward = 0.0
        return


    def step(self, target):
        target = self.available_actions[target]
        print('nextaction:',target)
        if target not in self.available_actions:
            raise
        self.history.append(target)
        #if not submit, update state and compute reward
        self.state = self.mol._moveVMD(action=target)
        self.counter += 1
        self.check() #get reward
        return [self.state, self.reward, self.done, self.add]

    def reset(self):
        #reset view!
        vhandle = getCurrentViewer()
        #vhandle.send("mol delete all") 
        vhandle.send("quit") 
        self.__init__()
        return self.state #first caption
