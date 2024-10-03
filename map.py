# import random

# # Constants representing directions
# UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3

# class Cell:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.filled = False
#         self.no = None
#         self.connect = [False, False, False, False]  # connections to UP, RIGHT, DOWN, LEFT
#         self.next = [None, None, None, None]         # adjacent cells UP, RIGHT, DOWN, LEFT
    
#     def __repr__(self):
#         return f"Cell({self.x}, {self.y}, filled={self.filled}, no={self.no})"

# class TetrisGrid:
#     def __init__(self, rows=9, cols=5):
#         self.rows = rows
#         self.cols = cols
#         self.cells = [[Cell(x, y) for y in range(rows)] for x in range(cols)]
#         self.num_filled = 0
#         self.num_groups = 0
#         self.init_neighbors()
#         self.prob_stop_growing_at_size = [0, 0, 0.10, 0.5, 0.75, 1]
    
#     def init_neighbors(self):
#         # Initialize neighbors for each cell
#         for x in range(self.cols):
#             for y in range(self.rows):
#                 if y > 0:
#                     self.cells[x][y].next[UP] = self.cells[x][y - 1]
#                 if y < self.rows - 1:
#                     self.cells[x][y].next[DOWN] = self.cells[x][y + 1]
#                 if x > 0:
#                     self.cells[x][y].next[LEFT] = self.cells[x - 1][y]
#                 if x < self.cols - 1:
#                     self.cells[x][y].next[RIGHT] = self.cells[x + 1][y]
    
#     def fill_cell(self, cell):
#         cell.filled = True
#         cell.no = self.num_filled
#         self.num_filled += 1
    
#     def get_leftmost_empty_cells(self):
#         left_cells = []
#         for x in range(self.cols):
#             for y in range(self.rows):
#                 if not self.cells[x][y].filled:
#                     left_cells.append(self.cells[x][y])
#             if left_cells:
#                 break
#         return left_cells
    
#     def is_open_cell(self, cell, direction, prev_dir, size):
#         if cell.next[direction] and not cell.next[direction].filled:
#             if direction in [UP, DOWN] and size == 2 and (direction == prev_dir or (direction + 2) % 4 == prev_dir):
#                 return False
#             return True
#         return False
    
#     def get_open_cells(self, cell, prev_dir, size):
#         open_cells = []
#         for i in range(4):
#             if self.is_open_cell(cell, i, prev_dir, size):
#                 open_cells.append(i)
#         return open_cells
    
#     def connect_cell(self, cell, direction):
#         cell.connect[direction] = True
#         if cell.next[direction]:
#             cell.next[direction].connect[(direction + 2) % 4] = True
    
#     def generate_grid(self):
#         # Pre-fill a square block at columns 1 and 2, rows 4 and 5
#         self.fill_cell(self.cells[0][3])
#         self.fill_cell(self.cells[0][4])
#         self.fill_cell(self.cells[1][3])
#         self.fill_cell(self.cells[1][4])
        
#         while self.num_filled < self.rows * self.cols:
#             open_cells = self.get_leftmost_empty_cells()
#             if not open_cells:
#                 break
#             first_cell = cell = random.choice(open_cells)
#             self.fill_cell(cell)
#             size = 1
#             prev_dir = None
#             while size < 5:
#                 open_directions = self.get_open_cells(cell, prev_dir, size)
#                 if not open_directions:
#                     break
#                 direction = random.choice(open_directions)
#                 new_cell = cell.next[direction]
#                 self.connect_cell(cell, direction)
#                 self.fill_cell(new_cell)
#                 cell = new_cell
#                 prev_dir = direction
#                 size += 1
#                 if random.random() <= self.prob_stop_growing_at_size[size]:
#                     break
    
#     def print_grid(self):
#         for y in range(self.rows):
#             row = []
#             for x in range(self.cols):
#                 cell = self.cells[x][y]
#                 if cell.filled:
#                     row.append(f'{cell.no:02d}')
#                 else:
#                     row.append('..')
#             print(' '.join(row))

# # Create the grid and generate the pieces
# tetris_grid = TetrisGrid()
# tetris_grid.generate_grid()
# tetris_grid.print_grid()

import sys
import random

# TODO:
# define an Obstacle class to represent a single group of contiguous wall tiles 
# Obstacle class
# Box Obstacle
# Line Obstacle
# map from tile to Obstacle

def all(iter):
    for e in iter:
        if not e: return False
    return True

def any(iter):
    for e in iter:
        if e: return True
    return False


# takes multi-line map string, trims indentation, replaces newlines with given separator
def format_map_str(tiles,sep):
    return sep.join(line.strip() for line in tiles.splitlines())

class Map:
    def __init__(self,w,h,tile_str=None):

        if tile_str is None:
            # just create a clear map
            self.tiles = []
            self.w = w
            self.h = h
            for i in range(w*h):
                self.tiles.append('.')
        else:
            self.setMap(w,h,tile_str)

        # sets logging verbosity (onXoff)
        self.verbose = False

    # create a map from a tile string
    def setMap(self,w,h,tile_str):
        self.w = w
        self.h = h
        self.tiles = list(format_map_str(tile_str,""))

    # creates a string of the current map
    def __str__(self):
        s = "\n"
        i = 0
        for y in range(self.h):
            for x in range(self.w):
                s += self.tiles[i]
                i += 1
            s += "\n"
        return s

    # converts x,y to index
    def xy_to_i(self,x,y):
        return x+y*self.w

    # converts index to x,y
    def i_to_xy(self,i):
        return i%self.w, i/self.w

    # validates x,y
    def xy_valid(self,x,y):
        return x >= 0 and x < self.w and y>=0 and y<self.h

    # gets tile at x,y or returns None if invalid
    def get_tile(self,x,y):
        if not self.xy_valid(x,y):
            return None
        return self.tiles[x+y*self.w]

    # adds a single wall tile at x,y
    def add_wall_tile(self,x,y):
        if self.xy_valid(x,y):
            self.tiles[x+y*self.w] = '0'

    def is_wall_block_filled(self,x,y):
        return all(self.get_tile(x+dx,y+dy) == '0' for dy in range(1,3) for dx in range(1,3))

    # adds a 2x2 block inside the 4x4 block at the given x,y coordinate 
    def add_wall_block(self,x,y):
        self.add_wall_tile(x+1,y+1)
        self.add_wall_tile(x+2,y+1)
        self.add_wall_tile(x+1,y+2)
        self.add_wall_tile(x+2,y+2)

    # determines if a 2x2 block can fit inside the 4x4 block at the given x,y coordinate
    # (the whole 4x4 block must be empty)
    def can_new_block_fit(self,x,y):
        if not (self.xy_valid(x,y) and self.xy_valid(x+3,y+3)):
            return False
        for y0 in range(y,y+4):
            for x0 in range(x,x+4):
                if self.get_tile(x0,y0) != '.':
                    return False
        return True

    # create a list of valid starting positions
    def update_pos_list(self):
        self.pos_list = []
        for y in range(self.h):
            for x in range(self.w):
                if self.can_new_block_fit(x,y):
                    self.pos_list.append((x,y))

    # A connection is a sort of dependency of one tile block on another.
    # If a valid starting position is against another wall, then add this tile
    # to other valid start positions' that intersect this one so that they fill
    # it when they are chosen.  This filling is a heuristic to eliminate gaps.
    def update_connections(self):
        self.connections = {}
        for y in range(self.h):
            for x in range(self.w):
                if (x,y) in self.pos_list:
                    if any(self.get_tile(x-1,y+y0)=='0' for y0 in range(4)): self.add_connection(x,y,1,0)
                    if any(self.get_tile(x+4,y+y0)=='0' for y0 in range(4)): self.add_connection(x,y,-1,0)
                    if any(self.get_tile(x+x0,y-1)=='0' for x0 in range(4)): self.add_connection(x,y,0,1)
                    if any(self.get_tile(x+x0,y+4)=='0' for x0 in range(4)): self.add_connection(x,y,0,-1)

    # the block at x,y is against a wall, so make intersecting blocks in the direction of 
    # dx,dy fill the block at x,y if they are filled first.
    def add_connection(self,x,y,dx,dy):
        def connect(x0,y0):
            src = (x,y)
            dest = (x0,y0)
            if not dest in self.pos_list:
                return
            if dest in self.connections:
                self.connections[dest].append(src)
            else:
                self.connections[dest] = [src]
        if (x,y) in self.pos_list:
            connect(x+dx,y+dy)
            connect(x+2*dx,y+2*dy)
            if not (x-dy,y-dx) in self.pos_list: connect(x+dx-dy,y+dy-dx)
            if not (x+dy,y+dx) in self.pos_list: connect(x+dx+dy,y+dy+dx)
            if not (x+dx-dy,y+dy-dx) in self.pos_list: connect(x+2*dx-dy, y+2*dy-dx)
            if not (x+dx+dy,y+dy+dx) in self.pos_list: connect(x+2*dx+dy, y+2*dy+dx)

    # update the starting positions and dependencies
    def update(self):
        self.update_pos_list()
        self.update_connections()

    # expand a wall block at the given x,y
    # return number of tiles added
    def expand_wall(self,x,y):
        visited = []
        def expand(x,y):
            count = 0
            src = (x,y)
            if src in visited:
                return 0
            visited.append(src)
            if src in self.connections:
                for x0,y0 in self.connections[src]:
                    if not self.is_wall_block_filled(x0,y0):
                        count += 1
                        self.add_wall_block(x0,y0)
                    count += expand(x0,y0)
            return count
        return expand(x,y)

    def get_most_open_dir(self,x,y):
        dirs = ((0,-1),(0,1),(1,0),(-1,0))
        max_dir = random.choice(dirs)
        max_len = 0
        for dx,dy in dirs:
            len = 0
            while (x+dx*len,y+dy*len) in self.pos_list:
                len += 1
            if len > max_len:
                max_dir = (dx,dy)
                max_len = len
        return max_dir

    # start a wall at block x,y
    def add_wall_obstacle(self,x=None,y=None,extend=False):
        self.update()
        if not self.pos_list:
            return False

        # choose random valid starting position if none provided
        if (x is None or y is None):
            x,y = random.choice(self.pos_list)

        # add first block
        self.add_wall_block(x,y)

        # initialize verbose print lines
        first_lines = str(self).splitlines()
        grow_lines = [""]*(self.h+2)
        extend_lines = [""]*(self.h+2)

        # mandatory grow phase
        count = self.expand_wall(x,y)
        if count > 0:
            grow_lines = str(self).splitlines()

        # extend phase
        if extend:

            # desired maximum block size
            max_blocks = 4

            # 35% chance of forcing the block to turn
            # turn means the turn has been taken
            # turn_blocks is the number of blocks traveled before turning
            turn = False
            turn_blocks = max_blocks
            if random.random() <= 0.35:
                turn_blocks = 4
                max_blocks += turn_blocks

            # choose a random direction
            dx,dy = random.choice(((0,-1),(0,1),(1,0),(-1,0)))
            orig_dir = (dx,dy)

            i = 0
            while count < max_blocks:
                x0 = x+dx*i
                y0 = y+dy*i
                # turn if we're past turning point or at a dead end
                if (not turn and count >= turn_blocks) or not (x0,y0) in self.pos_list:
                    turn = True
                    dx,dy = -dy,dx # rotate
                    i = 1
                    # stop if we've come full circle
                    if orig_dir == (dx,dy): break
                    else: continue

                # add wall block and grow to fill gaps
                if not self.is_wall_block_filled(x0,y0):
                    self.add_wall_block(x0,y0)
                    count += 1 + self.expand_wall(x0,y0)
                i += 1
            extend_lines = str(self).splitlines()

        # print the map states after each phase for debugging
        if self.verbose:
            print ("added block at ",x,y)
            for a,b,c in zip(first_lines, grow_lines, extend_lines):
                print( a,b,c)

        return True
    # New method to fill nodes with 'x'
    def fill_nodes(self):
        for y in range(self.h):
            for x in range(self.w):
                if self.get_tile(x, y) == '.' and self.is_node(x, y):
                    self.tiles[x + y * self.w] = '+'

    def is_node(self, x, y):
        # Check for valid turn nodes: path on both x and y directions
        # Ensure valid tile access
        if self.get_tile(x-1, y) in ['.', '+'] and self.get_tile(x, y+1) in ['.', '+']:
            return True  # Horizontal turn
        if self.get_tile(x-1, y) in ['.', '+'] and self.get_tile(x, y-1) in ['.', '+']:
            return True  # Vertical turn
        if self.get_tile(x+1, y) in ['.', '+'] and self.get_tile(x, y+1) in ['.', '+']:
            return True  # Horizontal turn
        if self.get_tile(x+1, y) in ['.', '+'] and self.get_tile(x, y-1) in ['.', '+']:
            return True  # Vertical turn
        
        return False
    def set_ghost(self):
        for x in [11,12,13]:
            for y in [13,14,15]:
                self.tiles[x+y * self.w] = 'X'
        self.tiles[13 + 12 * self.w] = '.'
        self.tiles[13 + 11 * self.w] = '+'
                    

def gen_map():

    # initial empty map with standard ghost house
    tileMap = Map(16,31,"""
        0000000000000000
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0.........000000
        0.........0.....
        0.........0.....
        0.........0.....
        0.........000000
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0...............
        0000000000000000
        """)

    # verbosity option (-v)
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        tileMap.verbose = True

    # generate map by adding walls until there's no more room
    while tileMap.add_wall_obstacle(extend=True):
        pass
    
    tileMap.fill_nodes()
    tileMap.set_ghost()
    f = open("maze2.txt", "w")
    f.write(f"{" ".join("X"*28)}\n")
    f.write(f"{" ".join("X"*28)}\n")
    f.write(f"{" ".join("X"*28)}")
    # f.write("x")
    # reflect the first 14 columns to print the map
    # print(str(tileMap))
    for i, line in enumerate(str(tileMap).splitlines()):
        s = line[:14]
        # print(s+s[::-1])        
        f.write(f"{" ".join(s+s[::-1])}\n")
        if i == 10: c = s
    f.write(f"{" ".join("X"*28)}\n")
    f.write(f"{" ".join("X"*28)}\n")
    f.close()
    # print(c)