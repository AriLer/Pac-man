from Point import Point
import math

# general
title = "Pac-man"
fps = 60  # how many times a second game is refreshed
initial_lives = 2
device_size = 1.2

# --- MAP SETTINGS ---

# dimensions
cell_size = int(15 * device_size)
map_height = 36
map_width = 28
wall_width = int(5 * device_size)
corner_width = int(5 * device_size)
gate_width = int(2 * device_size)

total_height = map_height * cell_size
total_width = map_width * cell_size

character_size = int(25 * device_size)  # asset size on map in pixels
pellet_size = int(3 * device_size)

# pause / victory / GO screens
screen_from_x = total_width // 6
screen_from_y = total_height // 4

screen_width = total_width // 2
screen_height = total_height // 4

screen_till_x = screen_from_x + screen_width
screen_till_y = screen_from_y + screen_height

# colors
wall_color = (0, 0, 139)
gate_color = (245, 71, 195)
pellet_color = (255, 211, 0)
guideline_color = (0, 150, 0)
pause_screen_color = (8, 8, 8)
contour_color = (125, 125, 125)
pause_text_color = (255, 255, 255)
black = (0, 0, 0)
white = (255, 255, 255)
ghost_score_color = (126, 249, 255)

# --- CHARACTER SETTINGS ---

# Pacman starting position and velocity
pacman_start = (14, 26)
pacman_vel = int(5 * device_size)

mode_times = [0, 7, 27, 34, 54, 59, 79, 84]  # time spent in each state (LVL 1 in original game)

# velocity settings
chase_vel = int(3 * device_size)
scatter_vel = int(2 * device_size)
frightened_vel = 1 * int(device_size)
eaten_vel = int(3 * device_size)

# individual ghost starting positions
blinky_start = (14, 14)
pinky_start = (14, 17)
clyde_start = (16, 17)
inky_start = (12, 17)

# Individual ghost targets in scatter mode
blinky_target = Point(25, 0)
pinky_target = Point(2, 0)
clyde_target = Point(0, 35)
inky_target = Point(27, 35)

# ghost target in eaten mode (in front of ghost house gate)
eaten_target = Point(14, 16)
caged_target = Point(14, 14)

# maze array for initial render of map (not used in each game, only in order to draw the first maze: "pac-man maze.png")
# 00 - path (free), 11 - horizontal wall, 12 - vertical wall, 21 - top_right corner,
# 22 bottom_right corner, 23 - bottom_left corner, top_right corner, 3 - ghost house gate  ..
maze_col1 = [00,00,00,23,12,12,12,12,12,12,12,12,24,00,00,00,11,00,11,00,00,00,23,12,12,12,12,24,23,12,12,12,12,24,00,00]
maze_col2 = [00,00,00,11,00,00,00,00,00,00,00,00,11,00,00,00,11,00,11,00,00,00,11,00,00,00,00,11,11,00,00,00,00,11,00,00]
maze_col3 = [00,00,00,11,00,23,12,24,00,23,24,00,11,00,00,00,11,00,11,00,00,00,11,00,23,24,00,22,21,00,23,24,00,11,00,00]
maze_col4 = [00,00,00,11,00,11,00,11,00,11,11,00,11,00,00,00,11,00,11,00,00,00,11,00,11,11,00,00,00,00,11,11,00,11,00,00]
maze_col5 = [00,00,00,11,00,11,00,11,00,11,11,00,11,00,00,00,11,00,11,00,00,00,11,00,11,22,12,12,24,00,11,11,00,11,00,00]
maze_col6 = [00,00,00,11,00,22,12,21,00,22,21,00,22,12,12,12,21,00,22,12,12,12,21,00,22,12,12,12,21,00,11,11,00,11,00,00]
maze_col7 = [00,00,00,11,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,11,11,00,11,00,00]
maze_col8 = [00,00,00,11,00,23,12,24,00,23,12,12,12,12,12,12,24,00,23,12,12,12,24,00,23,24,00,23,12,12,21,11,00,11,00,00]
maze_col9 = [00,00,00,11,00,11,00,11,00,22,12,12,24,23,12,12,21,00,22,12,12,12,21,00,11,11,00,22,12,12,24,11,00,11,00,00]
maze_col10 = [00,00,00,11,00,11,00,11,00,00,00,00,11,11,00,00,00,00,00,00,00,00,00,00,11,11,00,00,00,00,11,11,00,11,00,00]
maze_col11 = [00,00,00,11,00,11,00,11,00,23,24,00,11,11,00,23,12,12,12,24,00,23,24,00,11,11,00,23,24,00,11,11,00,11,00,00]
maze_col12 = [00,00,00,11,00,22,12,21,00,11,11,00,22,21,00,11,00,00,00,11,00,11,11,00,22,21,00,11,11,00,22,21,00,11,00,00]
maze_col13 = [00,00,00,11,00,00,00,00,00,11,11,00,00,00,00,11,00,00,00,11,00,11,11,00,00,00,00,11,11,00,00,00,00,11,00,00]
maze_col14 = [00,00,00,22,12,12,12,24,00,11,22,12,12,24,00,30,00,00,00,11,00,11,22,12,12,24,00,11,22,12,12,24,00,11,00,00]
maze_col15 = [00,00,00,23,12,12,12,21,00,11,23,12,12,21,00,30,00,00,00,11,00,11,23,12,12,21,00,11,23,12,12,21,00,11,00,00]
maze_col16 = [00,00,00,11,00,00,00,00,00,11,11,00,00,00,00,11,00,00,00,11,00,11,11,00,00,00,00,11,11,00,00,00,00,11,00,00]
maze_col17 = [00,00,00,11,00,23,12,24,00,11,11,00,23,24,00,11,00,00,00,11,00,11,11,00,23,24,00,11,11,00,23,24,00,11,00,00]
maze_col18 = [00,00,00,11,00,11,00,11,00,22,21,00,11,11,00,22,12,12,12,21,00,22,21,00,11,11,00,22,21,00,11,11,00,11,00,00]
maze_col19 = [00,00,00,11,00,11,00,11,00,00,00,00,11,11,00,00,00,00,00,00,00,00,00,00,11,11,00,00,00,00,11,11,00,11,00,00]
maze_col20 = [00,00,00,11,00,11,00,11,00,23,12,12,21,22,12,12,24,00,23,12,12,12,24,00,11,11,00,23,12,12,21,11,00,11,00,00]
maze_col21 = [00,00,00,11,00,22,12,21,00,22,12,12,12,12,12,12,21,00,22,12,12,12,21,00,22,21,00,22,12,12,24,11,00,11,00,00]
maze_col22 = [00,00,00,11,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,11,11,00,11,00,00]
maze_col23 = [00,00,00,11,00,23,12,24,00,23,24,00,23,12,12,12,24,00,23,12,12,12,24,00,23,12,12,12,24,00,11,11,00,11,00,00]
maze_col24 = [00,00,00,11,00,11,00,11,00,11,11,00,11,00,00,00,11,00,11,00,00,00,11,00,11,23,12,12,21,00,11,11,00,11,00,00]
maze_col25 = [00,00,00,11,00,11,00,11,00,11,11,00,11,00,00,00,11,00,11,00,00,00,11,00,11,11,00,00,00,00,11,11,00,11,00,00]
maze_col26 = [00,00,00,11,00,22,12,21,00,22,21,00,11,00,00,00,11,00,11,00,00,00,11,00,22,21,00,23,24,00,22,21,00,11,00,00]
maze_col27 = [00,00,00,11,00,00,00,00,00,00,00,00,11,00,00,00,11,00,11,00,00,00,11,00,00,00,00,11,11,00,00,00,00,11,00,00]
maze_col28 = [00,00,00,22,12,12,12,12,12,12,12,12,21,00,00,00,11,00,11,00,00,00,22,12,12,12,12,21,22,12,12,12,12,21,00,00]

maze_arr = [maze_col1, maze_col2, maze_col3, maze_col4, maze_col5, maze_col6,
            maze_col7, maze_col8, maze_col9, maze_col10, maze_col11, maze_col12, maze_col13,
            maze_col14, maze_col15, maze_col16, maze_col17, maze_col18, maze_col19, maze_col20,
            maze_col21, maze_col22, maze_col23, maze_col24, maze_col25, maze_col26, maze_col27, maze_col28]

energizer_coordinates_x = [1, 26, 1, 26]
energizer_coordinates_y = [6, 6, 26, 26]

def pythagoras(num1, num2):
    # method receives two numbers and calculates their linear distance
    return math.sqrt(pow(num1, 2) + pow(num2, 2))