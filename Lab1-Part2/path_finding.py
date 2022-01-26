from queue import PriorityQueue
import numpy as np
import math
from advanced_mapping import Mapping
import matplotlib.pylab as plt
import scipy.sparse as sparse


class Path_finding_A_star():
    def __init__(self, map_grid, starting, destination, wall_clearance = 10):
        self.map_grid = map_grid
        self.starting = starting
        self.dest= destination
        self.wall_clearance = 10
    
    def is_valid(self, location):
        x, y = location
        width = self.map_grid.shape[0]
        return self.wall_clearance <= x < width - self.wall_clearance and\
               self.wall_clearance <= y < width - self.wall_clearance and\
               not self.map_grid[x, y]
    
    def get_neighbors(self, location):
        x, y = location
        neighbors = [(x, y + 1), (x, y - 1), (x - 1, y), (x + 1, y)]  # up, down, left, right
        res = []
        for neighbor in neighbors:
            if self.is_valid(neighbor):
                res.append(neighbor)
        
        return res
    
    def inter_distance(self, a, b):
        a_x, a_y = a
        b_x, b_y = b
        return math.sqrt((a_x - b_x) ** 2 + (a_y - b_y) ** 2)
    
    def heuristic(self, location):
        x, y = location
        return self.inter_distance(location, self.dest)
    
    def search(self):   # output the path in [(x, y), (x, y) ...] to destination destination from starting
        frontier = PriorityQueue()
        start = self.starting
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while not frontier.empty():
            current = frontier.get()
            
            if current == self.dest:
                break
            
            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        path = []
        
        while current != start:
            path.append(current)
            current = came_from[current]
        
        if not path:
            print("No path found.")
        
        return path


def main():
    clearance = 10
    starting = (51, clearance + 1)
    destination = (80, 80)
    map_width = 101
    mapping = Mapping(map_width, clearance)
    map_grid = mapping.scan()

    path_finding = Path_finding_A_star(map_grid, starting, destination, clearance)
    path = path_finding.search()


    fig = plt.figure()
    plt.spy(map_grid, markersize = 2)
    plt.plot(starting[1], starting[0], marker='>', markersize=20)   # car location
    plt.text(starting[1] - 5, starting[0] + 10, "Car", fontsize = 14)
    plt.text(destination[1] - 10, destination[0] + 10, "Destination", fontsize = 14)

    for x, y in path:
        plt.plot(y, x, marker="x", markersize = 4)
        
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    fig.savefig('test1.jpg', dpi = 400)

    plt.show()
    

if __name__ == "__main__":
    main()


main()