import pygame as pg
import time
from random import randint
from Settings import *
from pygame import mixer

class Player(pg.sprite.Sprite):
    # class represents the main character – Pac-man
    def __init__(self, start, face):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.image.load(face + ".png")
        self.image = pg.transform.scale(self.image, (character_size, character_size))

        # initializing coordinates
        self.rect = self.image.get_rect()
        self.rect.center = (
            (start[0] * cell_size + (cell_size // 2)), (start[1] * cell_size + (cell_size // 2)))
        self.x = int(self.rect.center[0] // cell_size)  # array coordinates
        self.y = int(self.rect.center[1] // cell_size)  # array coordinates

        # Pacman's hitbox(for collisions with ghosts)
        self.hitbox = [self.rect.center[0] - (cell_size // 2), self.rect.center[0] + (cell_size // 2),
                       self.rect.center[1] - (cell_size // 2),
                       self.rect.center[1] + (cell_size // 2)]
        # variable to see where pacman is facing
        self.face = face
        # if at start, initialize frightened mode timer
        if self.x == 14 and self.y == 26:
            self.start_frightened_mode = -1

    def update(self):
        # method called once every frame and checks essentials

        # getting input from user
        self.get_movement()

        # trying to collect pellet
        self.collect_pellet()

        # changing directions (initializing new pacman to change the asset)
        if self.at_cell_center():
            if self.face != "no":
                self.__init__((self.x, self.y), self.face)
            if not self.can_move(self.face):
                self.face = "no"

        # moving the player according to checked parameters
        self.move()

    def get_movement(self):
        # method receives key press from player and applies to movement
        keys = pg.key.get_pressed()
        if not g.waiting:  # if should be able to move
            # if player is at end of tunnel and needs to be teleported
            if self.y == 17 and self.face == "right" and self.rect.center[0] > total_width - character_size:
                self.teleport()
            elif self.y == 17 and self.face == "left" and self.rect.center[0] < int(3 * device_size):
                self.teleport()

            # receiving key presses from user to move player
            elif keys[pg.K_LEFT] and self.can_move("left") and self.at_cell_center():
                self.face = "left"
            elif keys[pg.K_RIGHT] and self.can_move("right") and self.at_cell_center():
                self.face = "right"
            elif keys[pg.K_UP] and self.can_move("up") and self.at_cell_center():
                self.face = "up"
            elif keys[pg.K_DOWN] and self.can_move("down") and self.at_cell_center():
                self.face = "down"
        # pausing the game if the escape key is pressed
        if keys[pg.K_ESCAPE] and not g.paused:
            g.paused = True
            g.show_event_screen(3)

    def move(self):
        # method defines Pac-man's speed and direction

        # if playing and can move in a certain direction
        if not g.waiting and self.face != "no":
            if self.face == "left":
                self.rect.x -= pacman_vel
            elif self.face == "down":
                self.rect.y += pacman_vel
            elif self.face == "right":
                self.rect.x += pacman_vel
            elif self.face == "up":
                self.rect.y -= pacman_vel

            # updating coordinates and hitbox accordingly
            self.x = int(self.rect.center[0] // cell_size)
            self.y = int(self.rect.center[1] // cell_size)
            self.hitbox = [self.rect.center[0] - (cell_size // 2), self.rect.center[0] + (cell_size // 2),
                           self.rect.center[1] - (cell_size // 2),
                           self.rect.center[1] + (cell_size // 2)]

    def at_cell_center(self):
        # method checks if Pac-man is at the center of a tile
        x_center = abs(self.rect.center[0] - g.b.map[self.x][self.y].get_center().x) < 3
        y_center = abs(self.rect.center[1] - g.b.map[self.x][self.y].get_center().y) < 3
        return x_center and y_center

    def can_move(self, face):
        # method checks if possible to move in a certain direction

        # if at ends of teleport tunnel
        if self.y == 17 and self.face == "right" and self.rect.center[0] > total_width - character_size / 4:
            return True
        elif self.y == 17 and self.face == "left" and self.rect.center[0] < character_size / 4:
            return True

        # if there isn't a wall in the direction of the player
        elif face == "left" and maze_arr[self.x - 1][self.y] == 0:
            return True
        elif face == "right" and maze_arr[self.x + 1][self.y] == 0:
            return True
        elif face == "down" and maze_arr[self.x][self.y + 1] == 0:
            return True
        elif face == "up" and maze_arr[self.x][self.y - 1] == 0:
            return True
        return False

    def collect_pellet(self):
        # method collects pellet or energizer and calculates score and sets ghosts to frightened mode if energizer was eaten

        # if pellet found
        if self.within_hitbox() and g.b.map[self.x][self.y].has_pellet():
            g.b.map[self.x][self.y].collected = True  # remembering that pellet was collected
            g.pellets += 1  # for clyde and inky to now when to exit the ghost house at the start of the game
            g.calculate_score()
            if g.b.map[self.x][self.y].has_energizer:
                mixer.music.load("eat_fruit.wav")
                mixer.music.play()
                self.start_frightened_mode = g.elapsed_time  # start 7 second timer for the ghosts to be in frightened mode
                g.blinky.turn_mode("frightened")
                g.pinky.turn_mode("frightened")
                g.clyde.turn_mode("frightened")
                g.inky.turn_mode("frightened")
                self.ghost_count = 1

    def teleport(self):
        # method teleports player depending on direction
        if self.face == "right":
            self.rect.x = 0
        else:
            self.rect.x = (map_width-1)*cell_size
    def within_hitbox(self):
        # method determines if center of cell is in pacman's hitbox
        x = self.x * cell_size + cell_size // 2
        y = self.y * cell_size + cell_size // 2
        if self.hitbox[0] < x < self.hitbox[1] and self.hitbox[2] < y < self.hitbox[3]:
            return True


class Ghost(pg.sprite.Sprite):
    # class representing all of the ghosts In the game (blinky, pinky, clyde and inky)
    def __init__(self, name, point, target, face, mode):
        pg.sprite.Sprite.__init__(self)
        # draws the ghost depending on name or if it's in frightened mode
        if mode == "frightened":
            self.image = pg.image.load('blue_ghost.png')
        else:
            self.image = pg.image.load(name + '.png')

        # if eaten, the ghost will be of a smaller size
        if mode == "eaten":
            self.image = pg.transform.scale(self.image, (character_size // 2, character_size // 2))
        else:
            self.image = pg.transform.scale(self.image, (character_size, character_size))

        # initializing stats
        self.name = name
        self.scatter_target = Point(target.getX(), target.getY())
        self.target = Point(target.getX(), target.getY())
        self.mode = mode
        self.face = face
        self.vel = chase_vel
        self.free_time = 0

        # initial position
        self.rect = self.image.get_rect()
        self.rect.center = ((point[0] * cell_size + (cell_size // 2)), (point[1] * cell_size + (cell_size // 2)))

        self.x = int(self.rect.center[0] // cell_size)  # array coordinates
        self.y = int(self.rect.center[1] // cell_size)  # array coordinates

        # initial hit box
        self.hitbox = [self.rect.center[0] - (cell_size // 2), self.rect.center[0] + (cell_size // 2),
                       self.rect.center[1] - (cell_size // 2),
                       self.rect.center[1] + (cell_size // 2)]

    def update(self):
        # method checks assentials once every frame
        if not g.waiting:
            # when entering the ghost house
            if 10 < self.x < 17 and self.y == 16 and self.mode == "eaten" and self.face == "down":
                self.__init__(self.name, (self.x, self.y), caged_target, "left", "caged")
                self.free_time = g.elapsed_time + 5

            # when exited ghost house
            elif self.y == 14 and self.mode == "caged" and self.at_cell_center():
                self.define_mode()

            # when time to exit the ghost house, go up
            if self.mode == "caged" and self.free_time <= g.elapsed_time and (
                    self.x == 14 or self.x == 13) and self.at_cell_center():
                if self.name != "clyde" and self.name != "inky":
                    self.face = "up"
                elif (self.name == "clyde" and g.pellets >= 30) or (self.name == "inky" and g.pellets >= 80):
                    self.face = "up"

            # if exited the ghost house
            if (self.y == 14 and self.at_cell_center()) or self.mode != "caged":
                self.define_target()
                if self.mode == "chase" or self.mode == "scatter" or self.mode == "frightened":
                    if self.mode != "frightened":
                        self.define_mode()
                    self.kill_or_be_killed()

            # if frightened mode time ran out
            if g.pacman.start_frightened_mode != -1 and g.pacman.start_frightened_mode < g.elapsed_time - 7 and self.mode == "frightened":
                self.define_mode()
                self.define_target()
                self.__init__(self.name, (self.x, self.y), self.target, self.face, self.mode)
                if g.no_frightened_ghosts():
                    g.pacman.start_frightened_mode = -1

            # if ghost has to change directions
            if self.at_cell_center():
                if g.b.map[self.x][self.y].is_crossroad():
                    self.face = self.decision()
                elif not self.can_move(self.face):
                    self.turn()

            # moving ghost
            self.move()

    def turn(self):
        # method changes direction of ghost if hits wall and can move in only one direction (not crossroads)
        if g.b.map[self.x][self.y - 1].type == 0 and self.face != "down":
            self.face = "up"
        elif g.b.map[self.x - 1][self.y].type == 0 and self.face != "right":
            self.face = "left"
        elif g.b.map[self.x][self.y + 1].type == 0 and self.face != "up":
            self.face = "down"
        elif g.b.map[self.x + 1][self.y].type == 0 and self.face != "left":
            self.face = "right"
        else:
            self.face = "no"

    def decision(self):
        # method decides where ghost should go when entered a crossroads
        if self.face == "up":
            opposite_face = 2
        elif self.face == "left":
            opposite_face = 3
        elif self.face == "down":
            opposite_face = 0
        else:
            opposite_face = 1

        # when in frightened mode, ghost decides randomly where to go
        if self.mode == "frightened":
            direction = randint(0, 3)
            correct = False
            while not correct:
                correct = True
                if direction == opposite_face:
                    correct = False
                if direction == 0 and g.b.map[self.x][self.y - 1].type != 0:
                    correct = False
                elif direction == 1 and g.b.map[self.x - 1][self.y].type != 0:
                    correct = False
                elif direction == 2 and g.b.map[self.x][self.y + 1].type != 0:
                    correct = False
                elif direction == 3 and g.b.map[self.x + 1][self.y].type != 0:
                    correct = False
                if not correct:
                    direction = randint(0, 3)

        # any other mode, the linear distance from the possible tiles to it's target is messured
        # and moves in the direction in which the distance in minimal
        else:
            distances = [-1, -1, -1, -1]  # up, left, down, right
            # calculating distance from every possible direction
            if self.can_move("up") and self.face != "down":
                distances[0] = pythagoras((self.x - self.target.getX()), (self.y - 1 - self.target.getY()))
            if self.can_move("left") and self.face != "right":
                distances[1] = pythagoras((self.x - 1 - self.target.getX()), (self.y - self.target.getY()))
            if self.can_move("down") and self.face != "up":
                distances[2] = pythagoras((self.x - self.target.getX()), (self.y + 1 - self.target.getY()))
            if self.can_move("right") and self.face != "left":
                distances[3] = pythagoras((self.x + 1 - self.target.getX()), (self.y - self.target.getY()))

            # choosing a direction
            closest = pythagoras(26, 33)  # the greatest distance possible
            direction = 0
            for i in range(len(distances)):
                if distances[i] < closest and distances[i] != -1:
                    closest = distances[i]
                    direction = i

        # returning string value of direction
        if direction == 0:
            return "up"
        elif direction == 1:
            return "left"
        elif direction == 2:
            return "down"
        else:
            return "right"

    def chase_target(self):
        # methods decides where to go when at a crossroads according to ghost personalities

        # Blinky's behaviour - sets target directly at pacman
        if self.name == "blinky":
            self.target.setX(g.pacman.x)
            self.target.setY(g.pacman.y)

        # Pinky's behaviour - set target 4 tiles in front of pacman unless he's facing up, then
        # set target to 4 above and 4 to the left
        elif self.name == "pinky":
            if g.pacman.face == "up":
                self.target.setX(g.pacman.x - 4)
                self.target.setY(g.pacman.y - 4)
            elif g.pacman.face == "left":
                self.target.setX(g.pacman.x - 4)
                self.target.setY(g.pacman.y)
            elif g.pacman.face == "down":
                self.target.setX(g.pacman.x)
                self.target.setY(g.pacman.y + 4)
            else:
                self.target.setX(g.pacman.x + 4)
                self.target.setY(g.pacman.y)

        # clyde's behaviour - sets target directly at pacman unless at a 8 tiles radius from
        # pacman, then target will be the ghost's scatter target
        elif self.name == "clyde":
            if pythagoras(self.x - g.pacman.x, self.y - g.pacman.y) < 8:
                self.target.setX(clyde_target.getX())
                self.target.setY(clyde_target.getY())
            else:
                self.target.setX(g.pacman.x)
                self.target.setY(g.pacman.y)

        # inky's behaviour - find tile 2 tiles in front of pacman unless he's facing, then the
        # tile 2 above and 2 to the left. then messures the verctor to Blinky, flips it and sets target there
        else:
            intermediate = Point(0, 0)
            if g.pacman.face == "up":
                intermediate.setX(g.pacman.x - 2)
                intermediate.setY(g.pacman.y - 2)
            elif g.pacman.face == "left":
                intermediate.setX(g.pacman.x - 2)
                intermediate.setY(g.pacman.y)
            elif g.pacman.face == "down":
                intermediate.setX(g.pacman.x)
                intermediate.setY(g.pacman.y + 2)
            elif g.pacman.face == "right":
                intermediate.setX(g.pacman.x + 2)
                intermediate.setY(g.pacman.y)
            x_distance = g.pacman.x - g.blinky.x
            y_distance = g.pacman.y - g.blinky.y

            if x_distance > 0:
                self.target.setX(intermediate.getX() - x_distance)
            else:
                self.target.setX(intermediate.getX() + x_distance)
            if y_distance > 0:
                self.target.setY(intermediate.getY() + y_distance)
            else:
                self.target.setY(intermediate.getY() - y_distance)

    def at_cell_center(self):
        # method checks if ghost is at the center of a tile
        x_center = abs(self.rect.center[0] - g.b.map[self.x][self.y].get_center().x) < 2
        y_center = abs(self.rect.center[1] - g.b.map[self.x][self.y].get_center().y) < 2
        return x_center and y_center

    def can_move(self, face):
        # method checks if possible to move in a certain direction

        # if at either end of tunnel
        if self.y == 17 and self.face == "right" and self.rect.center[0] > total_width - character_size / 2:
            self.teleport()
        elif self.y == 17 and self.face == "left" and self.rect.center[0] < 2:
            self.teleport()

        # if next tile is free
        elif face == "left" and maze_arr[self.x - 1][self.y] == 0:
            return True
        elif face == "right" and maze_arr[self.x + 1][self.y] == 0:
            return True
        elif face == "down" and maze_arr[self.x][self.y + 1] == 0:
            return True
        elif face == "up" and maze_arr[self.x][self.y - 1] == 0:
            return True

        # entering and exiting the ghost house
        elif face == "up" and maze_arr[self.x][self.y - 1] == 30 and self.mode == "caged":
            return True
        elif face == "down" and maze_arr[self.x][
            self.y + 1] == 30 and self.mode == "eaten" and self.target.getY() != 14:
            return True
        return False

    def define_mode(self):
        # method sets mode of ghost according to times in "mode_times"
        if g.elapsed_time >= 7:
            if self.mode != g.cur_mode:
                self.turn_around();
            self.mode = g.cur_mode
        elif self.mode == "caged":
            self.mode = "scatter"

    def define_target(self):
        # method sets ghost's target according to it's mode
        if self.mode == "chase":
            self.chase_target()

        # each ghost has own scatter target in the corners of the map (see settings file)
        elif self.mode == "scatter":
            if self.name == "blinky":
                target = Point(blinky_target.getX(), blinky_target.getY())
            elif self.name == "pinky":
                target = Point(pinky_target.getX(), pinky_target.getY())
            elif self.name == "clyde":
                target = Point(clyde_target.getX(), clyde_target.getY())
            else:
                target = Point(inky_target.getX(), inky_target.getY())
            self.target.setX(target.getX())
            self.target.setY(target.getY())

    def kill_or_be_killed(self):
        # method either kills pacman or sends ghost to eaten mode if they collide
        if self.collide():
            # if ghost is eatable
            if self.mode == "frightened":

                mixer.music.load('eat_ghost.wav')
                mixer.music.play()

                g.print_eat_score(self.x, self.y, g.elapsed_time)
                self.turn_mode("eaten")
                g.pacman.ghost_count *= 2

            # if can eat pacman
            elif self.mode == "chase" or self.mode == "scatter":
                # delay of 2 seconds
                mixer.music.load('death.wav')
                mixer.music.play()

                start = g.elapsed_time
                while start > g.elapsed_time - 2:
                    g.elapsed_time = time.time() - g.start_time
                g.killed = True
                g.lives -= 1
                if g.lives == -1:
                    g.game_over = True
                else:
                    g.reset()

    def teleport(self):
        # method teleports ghost to other end of teleport tunnel depending on direction
        if self.face == "right":
            self.__init__(self.name, (0, self.y), self.target, self.face, self.mode)
            if self.mode == "frightened":
                self.vel = frightened_vel
        else:
            self.__init__(self.name, (((total_width - ((map_width-1)*cell_size)) // cell_size), self.y), self.target,
                          self.face, self.mode)
            if self.mode == "frightened":
                self.vel = frightened_vel

    def turn_around(self):
        # method changes directions of ghost 180 degrees
        if self.face == "up":
            self.face = "down"
        elif self.face == "left":
            self.face = "right"
        elif self.face == "down":
            self.face = "up"
        elif self.face == "left":
            self.face = "right"

    def move(self):
        # method moving ghost across the map
        if self.y == 17 and self.face == "right" and self.rect.center[0] > total_width - character_size:
            self.teleport()
        elif self.y == 17 and self.face == "left" and self.rect.center[0] < int(3 * device_size):
            self.teleport()

        if self.face == "left":
            self.rect.x -= self.vel
        elif self.face == "down":
            self.rect.y += self.vel
        elif self.face == "right":
            self.rect.x += self.vel
        elif self.face == "up":
            self.rect.y -= self.vel

        # updating coordinates and hitbox
        self.x = int(self.rect.center[0] // cell_size)
        self.y = int(self.rect.center[1] // cell_size)
        self.hitbox = [self.rect.center[0] - (cell_size // 2), self.rect.center[0] + (cell_size // 2),
                       self.rect.center[1] - (cell_size // 2),
                       self.rect.center[1] + (cell_size // 2)]

    def turn_mode(self, mode):
        # method turn ghost in to received mode

        if mode == "frightened":
            if self.mode == "chase" or self.mode == "scatter":
                if self.mode != "frightened":
                    self.turn_around()
                self.__init__(self.name, (self.x, self.y), self.target, self.face, mode)
                self.vel = frightened_vel
        else:
            self.__init__(self.name, (self.x, self.y), eaten_target, self.face, mode)
            self.vel = eaten_vel

    def collide(self):
        # method determines if ghost and player collided or not using hitboxes
        if self.hitbox[0] < g.pacman.hitbox[1] < self.hitbox[1] and self.y == g.pacman.y:
            return True
        elif self.hitbox[0] < g.pacman.hitbox[0] < self.hitbox[1] and self.y == g.pacman.y:
            return True
        elif self.hitbox[2] < g.pacman.hitbox[2] < self.hitbox[3] and self.x == g.pacman.x:
            return True
        elif self.hitbox[2] < g.pacman.hitbox[3] < self.hitbox[3] and self.x == g.pacman.x:
            return True
        return False


class Tile:
    # class represents each tile in the game
    def __init__(self, x, y):
        self.type = maze_arr[x][y]  # setting type of tile according to 2d array (see setting file)
        for i in range(len(energizer_coordinates_x)):
            if x == energizer_coordinates_x[i] and y == energizer_coordinates_y[i]:
                self.has_energizer = True
                break
            else:
                self.has_energizer = False
        self.x = x  # counting from the left
        self.y = y  # counting from the top
        self.collected = False

    def get_center(self):
        # method return center of cell
        center_x = self.x * cell_size + (cell_size // 2)
        center_y = self.y * cell_size + (cell_size // 2)
        return Point(center_x, center_y)

    def in_maze(self):
        # method determines if cell is inside the maze
        if not 2 < self.y < 33:
            return False
        # if in ghost house
        elif 10 < self.x < 17 and 15 < self.y < 19:
            return False
        # if in bumps
        elif (0 <= self.x < 5 or 22 < self.x < 28) and (12 < self.y < 16 or 18 < self.y < 22):
            return False
        # if in closed walls
        elif self.y == 6 and (2 < self.x < 5 or 7 < self.x < 11 or 16 < self.x < 20 or 22 < self.x < 25):
            return False
        return True

    def has_pellet(self):
        # method determines if cell has a pellet or an energizer
        # if cell is a wall
        if not self.in_maze() or self.type != 0:
            return False
        # if at pacman's starting position
        elif self.y == 26 and (12 < self.x < 15):
            return False
        # if in portal tunnel
        elif self.y == 17 and (self.x != 6 and self.x != 21):
            return False
        # if around ghost house
        elif (8 < self.x < 19 and (11 < self.y < 17 or 17 < self.y < 23)) or (
                14 < self.y < 20 and (6 < self.x < 14 or 14 < self.x < 21)):
            return False

        # if already collected by player
        elif self.collected:
            return False
        else:
            return True

    def is_crossroad(self):
        # method determines if cell is an intersection(if it has more than one possible direction to move to)

        ways_counter = 0
        if not self.in_maze() or not 0 < self.x < 27:
            return False
        if g.b.map[self.x][self.y - 1].type == 30:
            return True
        if g.b.map[self.x][self.y + 1].type == 30:
            return True
        if g.b.map[self.x + 1][self.y].type == 0:
            ways_counter += 1
        if g.b.map[self.x - 1][self.y].type == 0:
            ways_counter += 1
        if g.b.map[self.x][self.y + 1].type == 0:
            ways_counter += 1
        if g.b.map[self.x][self.y - 1].type == 0:
            ways_counter += 1

        if ways_counter > 2:
            return True
        return False

    # method not used in the game, only in development (to create: "pac-man file")
    def draw(self):
        # method draws the cell depending on tile's type (method was used to create intial maze asset)
        pass
        tile_type = maze_arr[self.x][self.y]
        if (tile_type == 11):  # horizontal wall
            pg.draw.line(g.screen, wall_color, ((self.x * cell_size), (self.y * cell_size + cell_size / 2)),
                         ((self.x * cell_size + cell_size), (self.y * cell_size + cell_size / 2)), wall_width)
        elif (tile_type == 12):  # vertical wall
            pg.draw.line(g.screen, wall_color, ((self.x * cell_size + cell_size / 2), (self.y * cell_size)),
                         ((self.x * cell_size + cell_size / 2), (self.y * cell_size + cell_size)), wall_width)
        elif (tile_type == 21):  # top_left corner
            pg.draw.line(g.screen, wall_color, ((self.x * cell_size), (self.y * cell_size + cell_size / 2)),
                         ((self.x * cell_size + cell_size / 2), (self.y * cell_size)), corner_width)
        elif (tile_type == 22):  # bottom_left corner
            pg.draw.line(g.screen, wall_color, ((self.x * cell_size), (self.y * cell_size + cell_size / 2)),
                         ((self.x * cell_size + cell_size / 2), (self.y * cell_size + cell_size)), corner_width)
        elif (tile_type == 23):  # bottom_right corner
            pg.draw.line(g.screen, wall_color, ((self.x * cell_size + cell_size / 2), (self.y * cell_size + cell_size)),
                         ((self.x * cell_size + cell_size), (self.y * cell_size + cell_size / 2)), corner_width)
        elif (tile_type == 24):  # top_right corner
            pg.draw.line(g.screen, wall_color, ((self.x * cell_size + cell_size), (self.y * cell_size + cell_size / 2)),
                         ((self.x * cell_size + cell_size / 2), (self.y * cell_size)), corner_width)
        elif (tile_type == 30):  # ghost house gate
            pg.draw.line(g.screen, gate_color, ((self.x * cell_size), (self.y * cell_size + cell_size / 2)),
                         ((self.x * cell_size + cell_size), (self.y * cell_size + cell_size / 2)), gate_width)


class Board:
    # the class represents the board of the game, containing all the tiles
    def __init__(self):
        self.map = []
        # board is a 2d array of tile objects
        for x in range(map_width):
            col = []
            for y in range(map_height):
                col.append(Tile(x, y))
            self.map.append(col)

    # method not used in the game, only to create maze asset
    def draw(self):
        pass
        # method draws all cells
        for x in range(map_width):
            for y in range(map_height):
                self.map[x][y].draw()


class Game:
    # the main class of the game representing the game itself and all of the classes above are used in it
    def __init__(self):
        self.b = Board()  # creating board of game
        pg.init()
        pg.mixer.init()
        # creating a window
        self.screen = pg.display.set_mode((total_width, total_height))
        pg.display.set_caption(title)
        self.clock = pg.time.Clock()  # creating a clock to render game

        # initializing game status variables
        self.waiting = True
        self.running = True
        self.game_won = False
        self.game_over = False
        self.paused = False
        # initializing score variables
        self.high_score = 0

    def new(self, high_score):
        # method starts new game
        self.score = 0
        self.pellets = 0
        self.ghost_score = 0
        self.lives = initial_lives
        self.high_score = high_score
        self.all_sprites = pg.sprite.Group()

        self.pacman = Player(pacman_start, "left")  # creating pacman object

        # creating ghost objects
        self.cur_mode = "scatter"
        self.blinky = Ghost("blinky", blinky_start, blinky_target, "left", "scatter")
        self.pinky = Ghost("pinky", pinky_start, pinky_target, "left", "caged")
        self.clyde = Ghost("clyde", clyde_start, clyde_target, "left", "caged")
        self.inky = Ghost("inky", inky_start, inky_target, "left", "caged")

        # adding characters to sprites
        self.all_sprites.add(self.pacman, self.blinky, self.pinky, self.clyde, self.inky)

        # setting all pellets and energizers as not collected
        for x in range(map_width):
            for y in range(map_height):
                self.b.map[x][y].collected = False
        self.run()

    def run(self):
        # game loop
        self.playing = True
        self.killed = False
        self.game_over = False
        self.waiting = True
        # starting times
        self.start_time = time.time() + 5
        self.ready_start_time = time.time()

        if self.waiting and self.playing:
            mixer.music.load('intro_music.wav')
            mixer.music.play()

        while self.playing:
            self.elapsed_time = time.time() - self.start_time
            self.clock.tick(fps)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # method updates game once every frame
        self.define_mode()
        self.all_sprites.update()

    def events(self):
        # method reacts to events while playing

        # if game lost or won
        if self.game_over or self.game_won:
            if self.game_won:
                self.show_event_screen(1)
            else:
                self.show_event_screen(2)
            for x in range(map_width):
                for y in range(map_height):
                    self.b.map[x][y].collected = False

        # if game was quit
        for self.event in pg.event.get():
            if self.event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                    self.running = False

    def draw(self):
        # method draws all needed elements once every frame

        # drawing maze
        maze_image = pg.image.load('pac-man maze.png')
        maze_image = pg.transform.scale(maze_image, (total_width, total_height))
        self.screen.blit(maze_image, (0, 0))

        # draws elements
        self.print_score()
        self.print_lives()
        self.print_high_score()

        if self.elapsed_time < 0:
            self.show_ready_screen()
        else:
            self.waiting = False

        # drawing the pellets
        self.pellet_left = False
        for x in range(map_width):
            for y in range(map_height):
                if self.b.map[x][y].has_pellet():
                    self.pellet_left = True
                    if self.b.map[x][y].has_pellet():
                        if not g.b.map[x][y].has_energizer:
                            pg.draw.circle(g.screen, pellet_color,
                                           (g.b.map[x][y].get_center().getX(), g.b.map[x][y].get_center().getY()),
                                           pellet_size)
                        else:
                            pg.draw.circle(g.screen, pellet_color,
                                           (g.b.map[x][y].get_center().getX(), g.b.map[x][y].get_center().getY()),
                                           pellet_size * 3)
        if not self.pellet_left:
            g.game_won = True
        self.all_sprites.draw(self.screen)

        pg.display.flip()

    def show_event_screen(self, event):
        instructions_font = pg.font.Font('freesansbold.ttf', cell_size)
        instructions_text = instructions_font.render("press 'R' to restart, 'Q' to quit", True, pause_text_color,
                                                     pause_screen_color)
        if event == 1:
            font = pg.font.Font('freesansbold.ttf', 50 + int(10 * device_size))
            text = font.render("VICTORY", True, (0, 255, 0), pause_screen_color)
        elif event == 2:
            font = pg.font.Font('freesansbold.ttf', 38 + int(10 * device_size))
            text = font.render("GAME OVER", True, (255, 0, 0), pause_screen_color)
        else:
            font = pg.font.Font('freesansbold.ttf', 50 + int(10 * device_size))
            text = font.render("PAUSED", True, white, pause_screen_color)
            instructions_font = pg.font.Font('freesansbold.ttf', cell_size)
            instructions_text = instructions_font.render("press 'C' to continue, 'Q' to quit", True,
                                                         pause_text_color, pause_screen_color)
            self.paused_start = time.time()
        text_rect = text.get_rect()
        text_rect.center = (total_width // 2, total_height // 2)
        instructions_text_rect = instructions_text.get_rect()
        instructions_text_rect.center = (total_width // 2, total_height // 2 + 75)
        # waiting for input from user
        while self.game_over or self.game_won or self.paused:
            mixer.music.pause()
            if self.paused:
                self.paused_time = time.time() - self.paused_start
            for self.event in pg.event.get():
                if self.event.type == pg.QUIT:
                    pg.quit()
                if self.event.type == pg.KEYDOWN:
                    if self.event.key == pg.K_q:
                        pg.quit()
                        quit()
                    if self.paused:
                        if self.event.key == pg.K_c:
                            self.paused = False
                            self.start_time += self.paused_time
                            mixer.music.unpause()
                    else:
                        if self.event.key == pg.K_r:
                            self.game_over = False
                            self.game_won = False
                            if self.score > self.high_score:
                                self.new(self.score)
                            else:
                                self.new(self.high_score)
            # drawing game over window
            pg.draw.rect(self.screen, contour_color, (screen_from_x, screen_from_y, screen_till_x, screen_till_y))
            pg.draw.rect(self.screen, pause_screen_color,
                         (screen_from_x + 10, screen_from_y + 10, screen_till_x - 20, screen_till_y - 20))
            self.screen.blit(text, text_rect)
            self.screen.blit(instructions_text, instructions_text_rect)
            pg.display.update()
            self.clock.tick(7)

    def show_ready_screen(self):
        # method writes "ready" when pacman respawns
        score_font = pg.font.Font('freesansbold.ttf', cell_size)
        score_text = score_font.render("READY!", True, pellet_color, black)
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (cell_size * 14, (cell_size * 20) + device_size * 10)
        g.screen.blit(score_text, score_text_rect)

    def calculate_score(self):
        # method calculates game score
        g.score = 0

        # score from pellets and energizers
        for x in range(map_width):
            for y in range(map_height):
                if g.b.map[x][y].collected:
                    if g.b.map[x][y].has_energizer:
                        g.score += 50
                    else:
                        g.score += 10

        # score from eaten ghosts
        self.score += self.ghost_score

        # setting new high score if old one is beaten
        if self.score > self.high_score:
            self.high_score = self.score

    def print_score(self):
        # method prints game score onto screen
        score_font = pg.font.Font('freesansbold.ttf', (cell_size * 2))
        score_text = score_font.render(str(self.score), True, white, black)
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (cell_size * 5, cell_size * 2.5 - 12)
        self.screen.blit(score_text, score_text_rect)

    def print_lives(self):
        # method prints lives onto screen using an array of pacman characters
        for i in range(self.lives):
            self.lives_image = pg.transform.scale(pg.image.load('right.png'), (cell_size * 2, cell_size * 2))
            self.screen.blit(self.lives_image, (((1 + (i * 2)) * cell_size), 34 * cell_size))

    def print_high_score(self):
        # method prints high score onto screen
        #  "high score" text
        score_font = pg.font.Font('freesansbold.ttf', cell_size)
        score_text = score_font.render("HIGH SCORE", True, white, black)
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (cell_size * 14, cell_size * 0.5)
        self.screen.blit(score_text, score_text_rect)

        # actual high score of game
        score_font = pg.font.Font('freesansbold.ttf', cell_size)
        score_text = score_font.render(str(self.high_score), True, white, black)
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (cell_size * 14, cell_size * 1.5)
        self.screen.blit(score_text, score_text_rect)

    def reset(self):
        # method resets all characters to starting positions and runs game
        self.blinky.__init__("blinky", blinky_start, blinky_target, "left", "scatter")
        self.pinky.__init__("pinky", pinky_start, pinky_target, "left", "caged")
        self.clyde.__init__("clyde", clyde_start, clyde_target, "left", "caged")
        self.inky.__init__("inky", inky_start, inky_target, "left", "caged")
        self.pacman.__init__(pacman_start, "left")
        self.run()

    def define_mode(self):
        # method defines current ghost mode according to "mode_times"
        if mode_times[0] <= self.elapsed_time < mode_times[1]:
            self.cur_mode = "scatter"
        elif mode_times[1] <= self.elapsed_time < mode_times[2]:
            self.cur_mode = "chase"
        elif mode_times[2] <= self.elapsed_time < mode_times[3]:
            self.cur_mode = "scatter"
        elif mode_times[3] <= self.elapsed_time < mode_times[4]:
            self.cur_mode = "chase"
        elif mode_times[4] <= self.elapsed_time < mode_times[5]:
            self.cur_mode = "scatter"
        elif mode_times[5] <= self.elapsed_time < mode_times[6]:
            self.cur_mode = "chase"
        elif mode_times[6] <= self.elapsed_time < mode_times[7]:
            self.cur_mode = "scatter"
        else:
            self.cur_mode = "chase"

    def print_eat_score(self, x, y, start):
        # method prints the score gathered from eating ghost onto screen
        score = 200 * g.pacman.ghost_count
        self.ghost_score += score
        while start > self.elapsed_time - 0.5:
            ghost_score_font = pg.font.Font('freesansbold.ttf', cell_size)
            ghost_score_text = ghost_score_font.render(str(score), True, ghost_score_color)
            ghost_score_text_rect = ghost_score_text.get_rect()
            ghost_score_text_rect.center = (x * cell_size, y * cell_size + cell_size // 2)
            self.screen.blit(ghost_score_text, ghost_score_text_rect)
            pg.display.flip()
            self.elapsed_time = time.time() - self.start_time
        self.calculate_score()

    def no_frightened_ghosts(self):
        # method determines if there are ghosts in frightened mode
        if g.blinky.mode != "frightened" and g.pinky.mode != "frightened" and g.clyde.mode != "frightened" and g.inky.mode != "frightened":
            return True
        return False


g = Game()
while g.running:
    g.new(g.high_score)
pg.quit()
