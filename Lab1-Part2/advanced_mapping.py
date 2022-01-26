import picar_4wd as fc
import time
import math
import numpy as np


class Mapping():
    def __init__(self, map_width = 101, clearance = 10):
        self.map_width = map_width
        self.clearance = clearance
        self.scan_map = np.zeros((map_width, map_width))

    def scan(self):
       
        angle_dist_list = self.scan_angle_and_distance_step(5)
        
        for i in range(len(angle_dist_list)):
            angle = angle_dist_list[i][0]
            distance = angle_dist_list[i][1]
            if distance > 0:
                xPos, yPos = self.convert_coordinate(angle, distance)
                if self.is_valid((xPos, yPos)):
                    self.scan_map[xPos, yPos] = 1
                    
                # fille in the spots between two valid points
                if i > 1:
                    pre_angle = angle_dist_list[i - 1][0]
                    pre_dist = angle_dist_list[i - 1][1]
                    if pre_dist > 0:
                        pre_xPos, pre_yPos = self.convert_coordinate(pre_angle, pre_dist)
                        inter_dist = math.sqrt((xPos - pre_xPos) ** 2 + (yPos - pre_yPos) ** 2)
                        if inter_dist < 5:         # 5 cm cutoff distance
                            for x in range(xPos + 1, pre_xPos):
                                y_low = math.floor((yPos - pre_yPos) / (xPos - pre_xPos) * (x - pre_xPos) + pre_yPos)
                                y_high = y_low + 1
                                if self.is_valid((x, y_low)):
                                    self.scan_map[x, y_low] = 1
                                if self.is_valid((x, y_high)):
                                    self.scan_map[x, y_high] = 1
                                    
        self.add_clearance(self.clearance)          
         
        return self.scan_map
    
    
    def scan_angle_and_distance_step(self, scan_step_angle): 
        min_angle = 0
        while min_angle >= -70 + scan_step_angle: # scan angle range [-70, 70]
            min_angle -= scan_step_angle
        
        angle_distance_list = []
        
        cur_angle = min_angle
        while cur_angle <= -min_angle:
            distance = fc.get_distance_at(cur_angle)
            angle_distance_list.append([-cur_angle, distance])
            cur_angle += scan_step_angle
        
        for i in range(1, len(angle_distance_list) - 1):
            pre_dist = angle_distance_list[i - 1][1]
            cur_dist = angle_distance_list[i][1]
            post_dist = angle_distance_list[i + 1][1]
            
            # remove single point measurement error
            if cur_dist > 0 and pre_dist < 0 and post_dist < 0:
                angle_distance_list[i][1] = -2
        
        return angle_distance_list
    

    def convert_coordinate(self, angle, distance):
        xPos = round(distance * math.sin(angle * math.pi / 180)) + self.map_width // 2
        yPos = round(distance * math.cos(angle * math.pi / 180))
        return xPos, yPos
    
    def is_valid(self, location):
        x, y = location
        width = self.map_width
        return 0 <= x < width and 0 <= y < width
        
    def change_circle_neighbors(self, location, r):   # add r cm clearance for one loation whose value is 1
        a, b = location
        res = []
        for x in range(round(a - r), round(a + r) + 1):
            y1_low = math.floor(b + math.sqrt(r ** 2 - (a - x) ** 2))
            y1_high = y1_low + 1
            y2_low = math.floor(b + math.sqrt(r ** 2 - (a - x) ** 2))
            y2_high = y2_low + 1
            if self.is_valid((x, y1_low)):
                self.scan_map[x, y1_low] = 1
            if self.is_valid((x, y1_high)):
                self.scan_map[x, y1_high] = 1
            if self.is_valid((x, y2_low)):
                self.scan_map[x, y2_low] = 1
            if self.is_valid((x, y2_high)):
                self.scan_map[x, y2_high] = 1
    
    def add_clearance(self, r):    # add r cm clearance for all locations whose value is 1
        points = []
        for x in range(self.map_width):
            for y in range(self.map_width):
                if self.scan_map[x, y] == 1:
                    points.append((x, y))
                    
        for point in points:
            self.change_circle_neighbors(point, r)

