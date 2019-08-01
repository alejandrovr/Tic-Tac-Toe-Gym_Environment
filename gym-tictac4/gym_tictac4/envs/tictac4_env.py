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
        self.get_rot_bonds()
        self.mol.view()

        #TODO: randomize starting point
        self.available_actions = ['rotx','roty','rotz','scalein','scaleout']
        [self.mol._moveVMD(action='scaleout') for i in range(20)]
        first_caption = self.mol._moveVMD(action='init')
        self.state = first_caption
        self.counter = 0
        self.done = 0
        self.reward = 0
        self.add = {}
        self.history = []

        _, self.mol.dihedrals = guessAnglesAndDihedrals(molbonds)

        l, r = molecule.get_LR(rb, bonds=molbonds,check_cycle=True)
        for bond in rotatable_bonds:
            if bond[0] in r and bond[1] in r:
                splits[tuple(rb)] += 1



    def check(self):
        whites = len(np.where(self.state>.7)[0])
        total = self.state.shape[0] * self.state.shape[1]
        coef = (whites / total) * 100
        self.reward = 0.

        #timeout
        if self.counter > 30:
            self.reward = coef * 100.
            self.done = True        
            return


    def step(self, target):
        target = self.available_actions[target]
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
        vhandle.send("mol delete all") 
        self.__init__()
        return self.state #first caption
