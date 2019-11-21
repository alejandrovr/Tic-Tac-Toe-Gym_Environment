import gym
from gym import error, spaces, utils
from gym.utils import seeding
from htmd.ui import *
from htmd.vmdviewer import getCurrentViewer
from moleculekit.smallmol.smallmollib import SmallMolLib
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
        
        code = '2gks_1'
        recep = Molecule('/shared/alejandro/scPDB/{}/protein.mol2'.format(code))
        recep.filter('protein and noh')
        recep_clean = recep.copy()
        poses_ints = []
        lig = SmallMolLib('/shared/alejandro/redocked_scPDB/docks/v3_{}/docked/outlig1.sdf'.format(code))
        pose = random.choice(lig)
        pose_idx = 0
    
        htmdpose = pose.toMolecule()
        site = recep.copy()   
        htmdpose.set('resname','LIG')
        
        self.label = 0
        if np.random.rand() > 0.5:
            htmdpose.moveBy([2., 2., 2.])
            self.label = 1
        
        site.append(htmdpose)
        site.filter('same residue as within 5 of resname LIG')
        site.reps.add(sel=' protein and same residue as within 5 of resname LIG',style='Lines')
        site.reps.add(sel='resname LIG',style='Licorice')
        site.view(name=str(self.label))
        [site._moveVMD(action='scaleout') for i in range(1)]
        #site._moveVMD(action='quicksurf')
        #self.available_actions = ['rotx', 'roty', 'rotz', 'pred_non_clash', 'pred_clash']
        self.available_actions = ['rotx', 'pred_non_clash', 'pred_clash']
        self.mol = site.copy()

        if self.label == 0:
            first_caption = self.mol._moveVMD(action='background')
        else:
            first_caption = self.mol._moveVMD(action='other')

        self.state = first_caption
        self.counter = 0
        self.done = 0
        self.reward = 0
        self.add = {}
        self.history = []

    def check(self):
        if 'pred_non_clash' in self.history or 'pred_clash' in self.history:
            if 'pred_non_clash' in self.history and self.label==0:
                self.reward = 1.0

            elif 'pred_non_clash' in self.history and self.label==1:
                self.reward = -1.0

            elif 'pred_clash' in self.history and self.label==0:
                self.reward = -1.0
            
            elif 'pred_clash' in self.history and self.label==1:
                self.reward = 1.0

            
            print('Final reward:', self.reward)
            self.done = True

        elif len(self.history) > 10:
            self.reward = -1.0
            self.done = True
            
        else:
            self.reward = 0.0

        return


    def step(self, target):
        target = self.available_actions[target]
        #print('nextaction:',target)
        if target not in self.available_actions:
            raise
        self.history.append(target)
        self.state = self.mol._moveVMD(action=target)
        self.counter += 1
        self.check() #get reward
        return [self.state, self.reward, self.done, self.add]

    def reset(self):
        #reset view!
        vhandle = getCurrentViewer()
        vhandle.send("mol delete all") 
        vhandle.send("color Display Background black")
        #vhandle.send("quit") 
        self.__init__()
        return self.state #first caption
