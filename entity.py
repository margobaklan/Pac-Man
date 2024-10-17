import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from random import randint
import heapq
from collections import deque

class Entity(object):
    def __init__(self, node):
        self.name = None
        self.directions = {UP:Vector2(0, -1),DOWN:Vector2(0, 1), 
                          LEFT:Vector2(-1, 0), RIGHT:Vector2(1, 0), STOP:Vector2()}
        self.direction = STOP
        self.setSpeed(100)
        self.radius = 10
        self.collideRadius = 5
        self.color = WHITE
        # self.node = node
        # self.setPosition()
        # self.target = node
        self.visible = True
        self.goal = None
        self.directionMethod = self.goalDirection
        self.setStartNode(node)
        self.image = None

    def setStartNode(self, node):
        self.node = node
        self.startNode = node
        self.target = node
        self.setPosition()

    def reset(self):
        self.setStartNode(self.startNode)
        self.direction = STOP
        self.speed = 100
        self.visible = True

    def setBetweenNodes(self, direction):
        if self.node.neighbors[direction] is not None:
            self.target = self.node.neighbors[direction]
            self.position = (self.node.position + self.target.position) / 2.0

    def setPosition(self):
        self.position = self.node.position.copy()

    def update(self, dt):
        self.position += self.directions[self.direction]*self.speed*dt
        if self.overshotTarget():
            self.node = self.target
            directions = self.validDirections()
            # direction = self.randomDirection(directions) 
            direction = self.directionMethod(directions)  
            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction
            else:
                self.target = self.getNewTarget(self.direction)

            self.setPosition()
          
    def validDirection(self, direction):
        if direction is not STOP:
            if self.name in self.node.access[direction]:
                if self.node.neighbors[direction] is not None:
                    return True
        return False
    
    def validDirections(self):
        directions = []
        for key in [UP, DOWN, LEFT, RIGHT]:
            if self.validDirection(key):
                if key != self.direction * -1:
                    directions.append(key)
        if len(directions) == 0:
            directions.append(self.direction * -1)
        return directions

    def randomDirection(self, directions):
        return directions[randint(0, len(directions)-1)]

    def getNewTarget(self, direction):
        if self.validDirection(direction):
            return self.node.neighbors[direction]
        return self.node

    def overshotTarget(self):
        if self.target is not None:
            vec1 = self.target.position - self.node.position
            vec2 = self.position - self.node.position
            node2Target = vec1.magnitudeSquared()
            node2Self = vec2.magnitudeSquared()
            return node2Self >= node2Target
        return False

    def reverseDirection(self):
        self.direction *= -1
        temp = self.node
        self.node = self.target
        self.target = temp
        
    def oppositeDirection(self, direction):
        if direction is not STOP:
            if direction == self.direction * -1:
                return True
        return False

    def setSpeed(self, speed):
        self.speed = speed * TILEWIDTH / 16

    def a_star(self, start, goal):
        open_list = []
        heapq.heappush(open_list, (0, start, []))

        g_cost = {start: 0}
        visited = set()

        while open_list:
            _, current_node, path = heapq.heappop(open_list)

            if current_node == goal:
                if path:
                    return path[0]  
                else:
                    return STOP  

            if current_node not in visited:
                visited.add(current_node)

                for direction in [UP, DOWN, LEFT, RIGHT]:
                    neighbor = current_node.neighbors[direction]

                    if neighbor and neighbor not in visited:
                        new_g_cost = g_cost[current_node] + TILEWIDTH  

                        if neighbor not in g_cost or new_g_cost < g_cost[neighbor]:
                            g_cost[neighbor] = new_g_cost
                            h_cost = (neighbor.position - goal.position).magnitude()
                            f_cost = new_g_cost + h_cost
                            heapq.heappush(open_list, (f_cost, neighbor, path + [direction]))

        return STOP

    def dfs(self, start, goal):
        stack = [(start, [])]  
        visited = set()

        while stack:
            current_node, path = stack.pop()
            if current_node == goal:
                if path:
                    return path[0]  
                else:
                    return STOP  

            if current_node not in visited:
                visited.add(current_node)
                for direction in [UP, DOWN, LEFT, RIGHT]:
                    neighbor = current_node.neighbors[direction]
                    if neighbor and neighbor not in visited:
                        if direction != self.direction * -1:
                            stack.append((neighbor, path + [direction]))
        return STOP  


    def bfs(self, start, goal):
        queue = deque([(start, None)])  
        visited = set()
        visited.add(start)

        while queue:
            current_node, direction_to_current = queue.popleft()

            if current_node == goal:
                return direction_to_current 
            for direction in [UP, DOWN, LEFT, RIGHT]:
                neighbor = current_node.neighbors.get(direction)
                if neighbor and neighbor not in visited:
                    visited.add(neighbor)
                    if direction_to_current is None:
                        queue.append((neighbor, direction))
                    else:
                        queue.append((neighbor, direction_to_current))
        return STOP
    
    
    def goalDirection(self, directions):
        distances = []
        for direction in directions:
            vec = self.node.position  + self.directions[direction]*TILEWIDTH - self.goal
            distances.append(vec.magnitudeSquared())
        index = distances.index(min(distances))
        if self.goal == self.pacman.position:
            if self.name == BLINKY:
                direction = self.bfs(self.node, self.pacman.node)
            if self.name == PINKY:
                direction = self.dfs(self.node, self.pacman.node)
            if self.name == INKY:
                direction = self.a_star(self.node, self.pacman.node)
            if direction is None:
                    direction = self.pacman.direction                      
            return direction
        return directions[index]

    def render(self, screen):
        if self.visible:
            if self.image is not None:
                adjust = Vector2(TILEWIDTH, TILEHEIGHT) / 2
                p = self.position - adjust
                screen.blit(self.image, p.asTuple())
            else:
                p = self.position.asInt()
                pygame.draw.circle(screen, self.color, p, self.radius)