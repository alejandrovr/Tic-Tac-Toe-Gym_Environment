import gym
from gym import error, spaces, utils
from gym.utils import seeding
from htmd.ui import *
from htmd.vmdviewer import getCurrentViewer
from moleculekit.smallmol.smallmollib import SmallMolLib
import random
import pickle

class TicTac4(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, VMD_mol_IDX=0):
        self.VMD_mol_IDX = VMD_mol_IDX
        [os.remove(i) for i in glob("/home/alejandro/rl_chemist/snapshots/vmdscene*.tga")]        
        available_codes = pickle.load(open('/home/alejandro/rl_chemist/available_codes.pkl','rb'))
        #code = random.choice(available_codes)
        code = '2gks_1'
        good_code = False

        while not good_code:
            try:
                lig = SmallMolLib('/shared/alejandro/redocked_scPDB/docks/v3_{}/docked/outlig1.sdf'.format(code),sanitize=False,fixHs=False)
                pose = random.choice(lig)
                good_code = True
            except:
                print('This code is not working!')
                pass
            
        recep = Molecule('/shared/alejandro/scPDB/{}/protein.mol2'.format(code))
        recep.filter('protein and noh')
        recep_clean = recep.copy()

        htmdpose = pose.toMolecule()
        site = recep.copy()   
        htmdpose.set('resname','LIG')
        
        self.label = 0
        if np.random.rand() > 0.5:
            htmdpose.moveBy([2., 2., 2.])
            self.label = 1
        
        site.append(htmdpose)
        site.filter('same residue as within 5 of resname LIG')
        site.reps.add(sel='protein and same residue as within 5 of resname LIG',style='QuickSurf',color=3)
        site.reps.add(sel='resname LIG',style='Licorice',color=8)
        site.view(name=str(self.label))

        site._moveVMD(self.VMD_mol_IDX, action='scaleout')
        site._moveVMD(self.VMD_mol_IDX, action='quicksurf')
        self.available_actions = ['rotx', 'roty', 'rotz', 'terminate']
        self.mol = site.copy()
        first_caption = self.mol._moveVMD(self.VMD_mol_IDX, action='rotx')

        self.state = first_caption
        self.counter = 0
        self.done = 0
        self.reward = 0
        self.add = {}
        self.history = []

    def check(self):
        whites = (len(self.state[self.state>0.9]) / (224*224) )
        reward = whites

        print('#whites',whites)
        if 'terminate' in self.history:
            self.reward = reward
            self.done = True

        elif len(self.history) > 10:
            self.reward = reward
            self.done = True
            
        else:
            self.reward = 0.0

        return


    def step(self, target):
        target = self.available_actions[target]
        if target not in self.available_actions:
            raise
        self.history.append(target)
        self.state = self.mol._moveVMD(self.VMD_mol_IDX, action=target)
        self.counter += 1
        self.check() #get reward
        return [self.state, self.reward, self.done, self.add]

    def reset(self):
        #reset view!
        vhandle = getCurrentViewer()
        vhandle.send("mol delete all") 
        self.VMD_mol_IDX += 1
        vhandle.send("color Display Background black")
        #vhandle.send("quit") 
        self.__init__(VMD_mol_IDX=self.VMD_mol_IDX)
        return self.state #first caption
