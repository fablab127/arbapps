from .tetrisforevolve import *
import numpy as np 

class Optimizer():
    def __init__(self, wl, we, wdeltar, wdeltac, wL, wW):
        self.parameters = [self.wl, self.we, self.wdeltar, self.wdeltac, self.wL, self.wW] \
        			    = [wl, we, wdeltar, wdeltac, wL, wW]

    def evaluate(self, world, c, last_tetro):
        self.world = (np.array(world) >= 1).astype('int')
        self.last_tetro = last_tetro
        self.nb_ligne = c
        return self.wl * self.l + self.we * self.e + self.wdeltar * self.deltar + \
               self.wdeltac * self.deltac + self.wL * self.L + self.wW * self.W
    
    def __str__(self):
        return str([round(parma, 2) for parma in self.parameters])

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
                z = min(index_ones)
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

        # Delacherrie 
        if optimizer is None : self.optimizer = Optimizer(*(-1, 2.5, -1, -1, -4, -1))
        else : self.optimizer = optimizer
        
    def build_best_world(self):
        if self.grid == [] : 
            self.grid = numpy.zeros([self.height, self.width], dtype=int)
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
                    self.grid = deepcopy(keep_grid)
                    if all(self.grid[y][0:2] != 1):
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

    def new_tetromino(self, gui = True):
        self.touchdown = False
        self.tetromino = Tetromino(0, self.width/2, self.height, self.width)
        t = time.time()
        self.build_best_world()
        self.timebuild += (time.time()-t)
        self.grid = self.world[0]
        if self.world[0] == []: 
            print('Game Over, score : %s, optimizer : %s' % (self.score, self.optimizer))
            return False
        self.score += self.world[1]**2
        if gui : self.update_view()
        return True

    def run(self, gui = True):
        self.timebuild = 0
        while self.playing:
            if not self.new_tetromino(gui = gui):
                break
        return self.score

import random as rd

def evolve():
    taille_pop = 20
    n_epoch = 10
    muta_rate = 1/20
    keep_perc = 0.2
    keep_idx = int(taille_pop*keep_perc)
    pop = [Optimizer(*[0.2-np.random.random() for _ in range(6)]) for _ in range(taille_pop)]
    games = [TetrisIa(optimizer = optimizer) for optimizer in pop]
    for epoch in range(n_epoch):
        print('Epoch %s' % epoch)
        for i, game in enumerate(games) :
            t = time.time()
            print(i, end=' : ') ; game.run(gui = False)
            print('Time elapsed : %s' % (round(time.time() - t)), end = ' ; ')
            print('Time spent building worlds : %s' % (round(game.timebuild)))
        games_sorted = sorted(games, reverse = True, key = lambda x : x.score)
        print('Best : %s' % games_sorted[0].optimizer)
        keep = games_sorted[:keep_idx]
        games = deepcopy(keep)
        for _ in range(len(games_sorted) - len(keep)):
            parents = [rd.choice(keep).optimizer for _ in range(2)]
            child = Optimizer(*[rd.choice([parents[0].parameters[i], parents[1].parameters[i]]) for i in range(6)])
            child.parameters[rd.randint(0,5)] += muta_rate*(2*np.random.random() - 1)
            games.append(TetrisIa(optimizer = child))
    for game in games : game.run(gui = False)
    return sorted(games, reverse = True, key = lambda x : x.score)[0]

            



