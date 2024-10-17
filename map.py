
import sys
import random
import numpy as np

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
    def __init__(self,max_blocks,w,h,tile_str=None):

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
        self.max_blocks = max_blocks

    # create a map from a tile string
    def setMap(self,w,h,tile_str):
        self.w = w
        self.h = h        
        # self.tiles = list(format_map_str(tile_str,""))
        self.tiles = np.array([list(line) for line in tile_str.splitlines()])

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

    # validates x,y
    def xy_valid(self,x,y):
        return x >= 0 and x < self.w and y>=0 and y<self.h

    # gets tile at x,y or returns None if invalid
    def get_tile(self,x,y):
        if not self.xy_valid(x,y):
            return None
        return self.tiles[y][x]

    # adds a single wall tile at x,y
    def add_wall_tile(self,x,y):
        if self.xy_valid(x,y):
            self.tiles[y][x] = '0'

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

    def update_connections(self):
        self.connections = {}
        for y in range(self.h):
            for x in range(self.w):
                if (x,y) in self.pos_list:
                    if any(self.get_tile(x-1,y+y0)=='0' for y0 in range(4)): self.add_connection(x,y,1,0)
                    if any(self.get_tile(x+4,y+y0)=='0' for y0 in range(4)): self.add_connection(x,y,-1,0)
                    if any(self.get_tile(x+x0,y-1)=='0' for x0 in range(4)): self.add_connection(x,y,0,1)
                    if any(self.get_tile(x+x0,y+4)=='0' for x0 in range(4)): self.add_connection(x,y,0,-1)

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
        # first_lines = str(self).splitlines()
        # grow_lines = [""]*(self.h+2)
        # extend_lines = [""]*(self.h+2)

        # mandatory grow phase
        count = self.expand_wall(x,y)
        # if count > 0:
        #     grow_lines = str(self).splitlines()

        # extend phase
        if extend:

            # desired maximum block size
            # self.max_blocks = 4

            # 35% chance of forcing the block to turn
            # turn means the turn has been taken
            # turn_blocks is the number of blocks traveled before turning
            turn = False
            # self.max_blocks = 1
            turn_blocks = self.max_blocks
            if random.random() <= 0.35:
                turn_blocks = 4
                self.max_blocks += turn_blocks

            # choose a random direction
            dx,dy = random.choice(((0,-1),(0,1),(1,0),(-1,0)))
            orig_dir = (dx,dy)

            i = 0
            while count < self.max_blocks:
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
            # extend_lines = str(self).splitlines()

        # print the map states after each phase for debugging
        # if self.verbose:
        #     print ("added block at ",x,y)
        #     for a,b,c in zip(first_lines, grow_lines, extend_lines):
        #         print( a,b,c)

        return True
    # New method to fill nodes with 'x'
    def fill_nodes(self):
        for y in range(self.h):
            for x in range(self.w):
                if self.get_tile(x, y) == '.' and self.is_node(x, y):
                    self.tiles[y][x] = '+'

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
                self.tiles[y][x] = 'X'
        self.tiles[12][13] = 'X'
        self.tiles[11][13] = '+'
                    

def gen_map(max_blocks):
    
    tile_map_str = (
        "0000000000000000\n" +
        "0...............\n" * 11 +  
        "0.........000000\n" +
        "0.........0.....\n" * 3 +  
        "0.........000000\n" +
        "0...............\n" * 13 +  
        "0000000000000000"
     )
    tileMap = Map(max_blocks,16,31,tile_map_str)
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        tileMap.verbose = True

    # generate map by adding walls until there's no more room
    while tileMap.add_wall_obstacle(extend=True):
        pass
    
    tileMap.fill_nodes()
    tileMap.set_ghost()
    
    map_lines = []
    for line in tileMap.tiles:
        if line.size > 0:  
            mirrored_line = np.concatenate((line[:14], np.flip(line[:14])))  # Mirror the first half
            map_lines.append(mirrored_line)

    map_lines = np.array(map_lines)

    x_row = np.full(map_lines.shape[1], 'X')  
    map_lines = np.vstack((x_row, x_row, x_row, map_lines,x_row,x_row))  # Stack the 'X' rows on top and b
    
    for row in map_lines:
        print(''.join(row)) 
    return map_lines