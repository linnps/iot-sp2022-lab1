import picar_4wd as fc
import time
import math
import numpy as np
import matplotlib.pylab as plt
import scipy.sparse as sparse

MAP_DIMENSION = 101

def main():
   
    angle_dist_list = scan_angle_and_distance_step(5)
    
    scan_map = np.zeros((MAP_DIMENSION, MAP_DIMENSION))
    
    for i in range(len(angle_dist_list)):
        angle = angle_dist_list[i][0]
        distance = angle_dist_list[i][1]
        if distance > 0:
            xPos, yPos = convert_coordinate(angle, distance)
            if (0 <= xPos < MAP_DIMENSION) and (0 <= yPos < MAP_DIMENSION):
                scan_map[xPos, yPos] = 1
                
            # fille in the spots between two valid points
            if i > 1:
                pre_angle = angle_dist_list[i - 1][0]
                pre_dist = angle_dist_list[i - 1][1]
                if pre_dist > 0:
                    pre_xPos, pre_yPos = convert_coordinate(pre_angle, pre_dist)
                    inter_dist = math.sqrt((xPos - pre_xPos) ** 2 + (yPos - pre_yPos) ** 2)
                    if inter_dist < 15:         # 15 cm cutoff distance
                        for x in range(xPos + 1, pre_xPos):
                            y = (yPos - pre_yPos) / (xPos - pre_xPos) * (x - pre_xPos) + pre_yPos
                            y = int(y + 0.5)
                            scan_map[x, y] = 1
                
    
    plt.spy(scan_map, markersize = 2)
    plt.plot(0, MAP_DIMENSION // 2, marker='>', markersize=20)   # car location
    plt.ylabel("Car", fontsize = 12)
    plt.show()

def convert_coordinate(angle, distance):
    xPos = int(distance * math.sin(angle * math.pi / 180) + 0.5) + MAP_DIMENSION // 2
    yPos = int(distance * math.cos(angle * math.pi / 180) + 0.5)
    return xPos, yPos
    
def scan_angle_and_distance_step(scan_step_angle): 
    min_angle = 0
    while min_angle >= -70 + scan_step_angle: # scan angle range [-70, 70]
        min_angle -= scan_step_angle
    
    angle_distance_list = []
    
    cur_angle = min_angle
    while cur_angle <= -min_angle:
        distance = fc.get_distance_at(cur_angle)
        angle_distance_list.append([-cur_angle, distance])
        cur_angle += scan_step_angle
    
    # remove single point measurement error
    for i in range(1, len(angle_distance_list) - 1):
        pre_dist = angle_distance_list[i - 1][1]
        cur_dist = angle_distance_list[i][1]
        post_dist = angle_distance_list[i + 1][1]
        
        if cur_dist > 0 and pre_dist < 0 and post_dist < 0:
            angle_distance_list[i][1] = -2
    
    return angle_distance_list



if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()
