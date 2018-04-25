from ..tetris import *
import numpy as np 

class Optimizer():
    def __init__(self, a,b,c,d,f,g):
        self.parameters = [self.a, self.b, self.c, self.d, self.f, self.g]  = [a, b, c, d, f, g]

    def evaluate(self, world, c, last_tetro):
        self.world = (np.array(world) >= 1).astype('int')
        self.last_tetro = last_tetro
        self.nb_ligne = c
        return self.a * self.l + self.b * self.e + self.c*self.deltar + \
               self.d * self.deltac + self.f * self.L + self.g * self.W
        
    @property
    def l(self):
        return - self.last_tetro.position[0]

    @property
    def e(self):
        return self.nb_ligne

    @property
    def deltar(self):
        somme = 0
        for line in self.world:
            current = line[0]
            for val in line[1:]:
                if val != current:
                    somme += 1
                current = val
        return somme

    @property
    def deltac(self):
        somme = 0
        for col in self.world.T:
            current = col[0]
            for val in col[1:]:
                if val != current:
                    somme += 1
                current = val
        return somme

    @property
    def L(self):
        nb_holes = 0
        for column in self.world.T:
            index_ones = np.where(column==1)[0]
            if index_ones != []:
                z = min(np.where(column==1)[0])
                for idx_line in range(z+1, len(column)):
                    if column[idx_line] == 0:
                        nb_holes += 1
        return nb_holes

    @property
    def W(self):
        puit = 0
        value = 0
        value_side_one = 0
        value_side_two = 0
        for (a, b) in zip(self.world[1:], self.world[:-1]):
            for (c, d, index) in zip(a, b, range(0, len(a))):
                if index == 0 and c == 0 and d == 0:
                    value_side_one+=1
                elif index == 1 and value_side_one == 1 and c == 1 and d == 1:
                    puit+=1
                    value_side_one = 0
                else:
                    value_side_one = 0
                if value == 0 and c == 1 and d == 1:
                    value+=1
                elif value == 1 and c == 0 and d == 0:
                    value+=1
                elif value == 2 and c == 1 and d == 1:
                    puit+=1
                    value = 0
                else:
                    value = 0
                if index == len(a)-2 and c == 1 and d == 1:
                    value_side_two+=1
                elif index == len(a)-1 and value_side_two == 1 and c == 0 and d == 0:
                    puit+=1
                    value_side_two = 0
        return puit

class TetrisIa(Tetris):
    def __init__(self, optimizer = None):
        Tetris.__init__(self)
        self.dico_actions = {'left' : 0, 'right' : 0, 'rotate' : 0}

        # Delacherrie 
        if optimizer is None : self.optimizer = Optimizer(*(-1, 2.5, -1, -1, -4, -1))
        else : self.optimizer = optimizer
        self.speed = 30   # Execute game in fast mode (all waiting times are faster)

    def build_best_world(self):
        tetro_type = self.tetromino.type
        keep_grid = deepcopy(self.grid)
        keep_tetro = deepcopy(self.tetromino)
        self.world = ([], 0, 0, 0, 0, 0)
        best_grade = -100000000
        
        for x in (0, 3):
            for rot in range(4):
                self.tetromino = deepcopy(keep_tetro)
                for _ in range(rot) : self.rotate_current_tetro()
                for y in range(self.width-len(self.tetromino.get_value()[0])+1):
                    if True:
                        self.grid = deepcopy(keep_grid)
                        self.tetromino = Tetromino(x, y, self.height, self.width, type_ = tetro_type)
                        for _ in range(rot) : self.rotate_current_tetro()
                        self.touchdown = False
                        steps = 0
                        while not self.touchdown:
                            self.old_grid_empty = deepcopy(self.grid)
                            self.draw_tetromino()
                            if self.touchdown:
                                self.grid = self.old_grid_filled
                                c = self.check_and_delete_full_lines()
                            else:
                                self.old_grid_filled = deepcopy(self.grid)
                                self.grid = self.old_grid_empty
                                self.tetromino.falldown()
                            steps += 1

                        if steps > 1 and self.tetromino.position[0] > 0:
                            new_grade = self.optimizer.evaluate(self.grid, c, self.tetromino)
                            if new_grade > best_grade : 
                                self.world = (deepcopy(self.grid), c, steps, x, y, rot)
                                keep_tetro = deepcopy(self.tetromino)
                                best_grade = new_grade
        self.grid = keep_grid
        self.tetromino = keep_tetro
        self.touchdown = False

    def make_dico_action(self):
        self.dico_actions = {'left' : 0, 'right' : 0, 'rotate' : self.world[-1]}

        nb_of_step = int(self.world[4] - self.width/2)
        if nb_of_step < 0 : self.dico_actions['left'] = abs(nb_of_step)
        elif nb_of_step > 0 : self.dico_actions['right'] = abs(nb_of_step) 
        print(self.dico_actions)

    def process_events(self):
        if self.steps == 0 and self.first_wait:
            print("################################################################################## Computation WORLD")
            keep_grid = deepcopy(self.grid)
            keep_old_grid = deepcopy(self.old_grid)
            keep_old_grid_empty = deepcopy(self.old_grid_empty)
            keep_old_grid_filled = deepcopy(self.old_grid_filled)
            keep_tetro = deepcopy(self.tetromino)
            self.build_best_world()
            self.make_dico_action()

            self.tetromino = keep_tetro
            self.grid = keep_grid
            self.old_grid_filled = keep_old_grid_filled
            self.old_grid_empty = keep_old_grid_empty
            self.old_grid = keep_old_grid
            self.first_wait = False

        self.command = {'left': False, 'right': False, 'down': False, 'rotate': False}  # User commands (joy/keyboard)
        if self.dico_actions['left'] > 0:
            self.command['left'] = True
            self.dico_actions['left'] = self.dico_actions['left'] - 1
        elif self.dico_actions['right'] > 0:
            self.command['right'] = True
            self.dico_actions['right'] = self.dico_actions['right'] -1
        elif self.dico_actions['rotate'] > 0:
            self.command['rotate'] = True
            self.dico_actions['rotate'] = self.dico_actions['rotate'] - 1
        #print(self.dico_actions)
        return self.traiter_events()



import random as rd

def evolve(self):
    taille_pop = 50
    n_epoch = 10
    muta_rate = 1/5
    pop = [Optimizer(*[4*np.random.random()-2.5 for _ in range(6)]) for _ in range(taille_pop)]
    games = [TetrisIa(optimizer = optimizer) for optimizer in pop]
    for epoch in range(n_epoch):
        for game in games : game.run(gui = False)
        games_sorted = sorted(games, reverse = True, key = lambda x : x.score)
        keep = [games_sorted][:taille_pop//2]
        games = deepcopy(keep)
        for _ in range(taille_pop//2):
            parents = [rd.choice(keep) for _ in range(2)]
            child = Optimizer(*[(parents[1].x + parents[2].x) / 2 for x in parents[1].parameters])
            self.parameters[rd.randint(0,5)] += 1/5*(2*np.random.random() - 1)
            games.append(child)
    for game in games : game.run(gui = False)
    return sorted(games, reverse = True, key = lambda x : x.score)[0]

            



