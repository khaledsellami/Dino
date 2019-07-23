import random
import os

import pygame


class Dino_player:
    """Basic player class for the Dino game."""

    def get_action(self, state, current_score):
        """Return True to jump.

        Keyword arguments:
        state -- current state of the game
        current_score -- current score of the game
        """
        return False

    def keep_playing(self, current_score):
        """Return True to keep playing.

        Keyword arguments:
        current_score -- current score of the game
        """
        return True


class Dino_player_random(Dino_player):
    """Random player class for the Dino game."""

    def __init__(self, jump_probabilty = 0.3):
        self.jump_probability = jump_probabilty

    def get_action(self, state, current_score):
        """Return True to jump.

        Keyword arguments:
        state -- current state of the game
        current_score -- current score of the game
        """
        gen_num = random.uniform(0,1)
        if gen_num < self.jump_probability:
            return True
        else:
            return False


class Dino:
    """The main class of the Google Chrome Dinosaur game."""

    def __init__(self, player, text = None):
        """Initialize the variables and declare constants.

        Keyword arguments:
        player -- variable of Dino_player type
        text -- text to be displayed during the game
        """
        assert isinstance(player, Dino_player)
        # Declare constants.
        self.SIZE = self.WEIGHT, self.HEIGHT = 640, 400
        self.DINO_INITIAL_X = 100
        self.DINO_INITIAL_Y = 250
        self.MAX_JUMP_HEIGHT = 100
        self.JUMP_SPEED_A = 0.5
        self.JUMP_SPEED_D = 0.5
        self.DINO_MOVE_SPEED = 0.1
        self.GROUND_INITIAL_SPEED = 6
        self.COLLISION_FORGIVE = 8
        # Initialize flags.
        self.running = True
        self.playing = False
        self.jumping_a = False
        self.jumping_d = False
        self.first_frame = True
        self.rendered = False
        # Initialize rest of variables.
        self.player = player
        self.text = text
        self.display_surf = None
        self.move_counter = 0
        self.game_time = 0
        self.most_recent_score = 0
        self.obstacle_distance = 0
        self.possible_obstacles = list()
        self.obstacles = list()
        self.start_playing_event = pygame.event.Event(
                pygame.USEREVENT, attr1='start_playing'
                )

    def on_init(self):
        """Initialize the pygame specific variables
        and load the images.
        """
        script_dir = os.path.dirname(__file__)
        # Initialize the main window.
        pygame.init()
        logo = pygame.image.load(os.path.join(script_dir, "images/dino.jpg"))
        pygame.display.set_icon(logo)
        pygame.display.set_caption("Dino")
        self.display_surf = pygame.display.set_mode(
                self.SIZE, pygame.HWSURFACE | pygame.DOUBLEBUF
                )
        # Initialize the clock and the font system.
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self.text_font = pygame.font.SysFont('Comic Sans MS', 20)
        self.instuction_up = self.text_font.render(
                        "Press the UP arrow to jump",
                        False,
                        (0, 0, 0)
                        )
        # Load the ground image, split it and save the fragments in a list.
        ground = pygame.image.load(os.path.join(script_dir,
                                                "images/ground.png"))
        ground.set_colorkey((64, 202, 201))
        self.ground_parts = []
        x, y, dx, dy = 0, 0, 1, ground.get_height()
        self.ground = ground
        while x<ground.get_width():
            rect = pygame.Rect((x,y,dx,dy))
            ground_part = pygame.Surface(rect.size).convert()
            ground_part.blit(ground, (0, 0), rect)
            ground_part.set_colorkey((64,202,201))
            self.ground_parts.append(ground_part)
            x += dx
        #Load the obstacle sprites.
        cactus_b_1 = pygame.image.load(
                os.path.join(script_dir, "images/cactus_b_1.png")
                ).convert()
        cactus_b_1.set_colorkey((64,202,201))
        self.possible_obstacles.append(cactus_b_1)
        cactus_s_1 = pygame.image.load(
                os.path.join(script_dir, "images/cactus_s_1.png")
                ).convert()
        cactus_s_1.set_colorkey((64,202,201))
        self.possible_obstacles.append(cactus_s_1)
        #Load the dinosaur sprites and initialize the rest of the variables.
        self.dino_move_1 = pygame.image.load(
                os.path.join(script_dir, "images/dino_move_1.png")
                ).convert()
        self.dino_move_1.set_colorkey((64,202,201))
        self.dino_move_2 = pygame.image.load(
                os.path.join(script_dir, "images/dino_move_2.png")
                ).convert()
        self.dino_move_2.set_colorkey((64,202,201))
        self.dino_jump = pygame.image.load(
                os.path.join(script_dir, "images/dino_jump.png")
                ).convert()
        self.dino_jump.set_colorkey((64,202,201))
        self.dino_dead = pygame.image.load(
                os.path.join(script_dir, "images/dino_dead.png")
                ).convert()
        self.dino_dead.set_colorkey((64,202,201))
        self.dino_y = self.DINO_INITIAL_Y
        self.dino_x = self.DINO_INITIAL_X
        self.running = True

    def reinit(self):
        """Reinitialize the flags and variables."""
        self.dino_y = self.DINO_INITIAL_Y
        self.dino_x = self.DINO_INITIAL_X
        self.obstacles = list()
        self.obstacle_distance = 0
        self.move_counter = 0
        self.game_time = 0
        self.ground_move = 0
        self.playing = True
        self.jumping_a = False
        self.jumping_d = False
        self.clock.tick(60)

    def jump(self):
        """Trigger jumping event if possible."""
        if not(self.jumping_a or self.jumping_d):
            self.jumping_a = True

    def stop(self):
        """Stop playing."""
        self.playing = False

    def exit_game(self):
        self.running = False

    def play(self):
        """Start playing."""
        if not self.playing:
            pygame.event.post(self.start_playing_event)

    def on_event(self, event):
        """Detect events and change flags accordingly."""
        if event.type == pygame.QUIT:
            self.running = False
        if event == self.start_playing_event:
            self.reinit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.jump()
            if event.key == pygame.K_s and not(self.playing):
                self.reinit()

    def on_loop(self):
        """Update variables and move objects."""
        if self.playing:
            dt = self.clock.tick(60)
            self.game_time += dt
            #Update dinosaur location if jumping.
            if self.jumping_a:
                if self.dino_y <= (self.DINO_INITIAL_Y-self.MAX_JUMP_HEIGHT):
                    self.jumping_a = False
                    self.jumping_d = True
                elif self.dino_y<=(self.DINO_INITIAL_Y
                                   - self.MAX_JUMP_HEIGHT/1.5):
                    self.dino_y -= self.JUMP_SPEED_A*dt/2
                else:
                    self.dino_y -= self.JUMP_SPEED_A*dt
            if self.jumping_d:
                if self.dino_y >= self.DINO_INITIAL_Y:
                    self.jumping_d = False
                    self.dino_y = self.DINO_INITIAL_Y
                elif self.dino_y <= (self.DINO_INITIAL_Y
                                     - self.MAX_JUMP_HEIGHT/1.5):
                    self.dino_y += self.JUMP_SPEED_D*dt/2
                else:
                    self.dino_y += self.JUMP_SPEED_D*dt
            #Update dinosaur movement animaton
            self.move_counter += self.DINO_MOVE_SPEED
            if self.move_counter >= 10:
                self.move_counter = 0
            #Update ground location
            self.ground_step = (
                    self.GROUND_INITIAL_SPEED
                    * ( 0.125*(self.game_time//10000) + 1)
                    )
            self.ground_parts = (
                    self.ground_parts[int(self.ground_step):]
                    + self.ground_parts[:int(self.ground_step)]
                    )
            #Generate obstacles and update their location
            self.obstacle_distance += int(self.ground_step)
            if 300 < self.obstacle_distance <= 900:
                gen_num = random.uniform(0,1)
                if gen_num < 0.05 :
                    generate_obstacles = True
                else:
                    generate_obstacles = False
            elif 900 < self.obstacle_distance:
                generate_obstacles = True
            else:
                generate_obstacles = False
            if generate_obstacles:
                number_obstacles = random.randint(1,4)
                last_x = self.display_surf.get_width()
                for i in range(number_obstacles):
                    chosen_obstacle = random.choice(self.possible_obstacles)
                    self.obstacles.append([
                            chosen_obstacle,
                            [last_x, self.DINO_INITIAL_Y +
                                self.dino_move_1.get_height() -
                                chosen_obstacle.get_height()]
                            ])
                    last_x += chosen_obstacle.get_width()
                self.obstacle_distance = 0
            obstacles=list()
            for obstacle in self.obstacles:
                obstacle[1][0] -= int(self.ground_step)
                if not obstacle[1][0] + obstacle[0].get_width() <= 0 :
                    obstacles.append(obstacle)
            self.obstacles = obstacles

    def on_render(self):
        """Clear screen and repaint objects with updated data."""
        #Clear screen
        self.display_surf.fill((255,255,255))
        #Paint ground
        ground_x=0
        for ground in self.ground_parts:
            self.display_surf.blit(ground, (ground_x,self.DINO_INITIAL_Y+35))
            ground_x += ground.get_width()
        #Paint instruction text
        score = self.text_font.render(
                str(int(self.game_time/100)),
                False,
                (0, 0, 0)
                )
        self.display_surf.blit(
                score,
                (self.display_surf.get_width() - (5+score.get_width()), 0)
                )
        if not self.playing:
            if self.first_frame:
                instuction = self.text_font.render(
                        "Press 's' to start",
                        False,
                        (0, 0, 0)
                        )
            else:
                instuction = self.text_font.render(
                        "Press 's' to restart",
                        False,
                        (0, 0, 0)
                        )
            self.display_surf.blit(
                    instuction,
                    (self.display_surf.get_width()//2
                     - instuction.get_width()//2,0)
                    )
            self.display_surf.blit(
                    self.instuction_up,
                    (self.display_surf.get_width()//2
                     - self.instuction_up.get_width()//2,25)
                    )
        elif self.text is not None:
            text = self.text_font.render(
                        self.text,
                        False,
                        (0, 0, 0)
                        )
            self.display_surf.blit(
                    text,
                    (self.display_surf.get_width()//2
                     - text.get_width()//2,0)
                    )
        #Paint Dinosaur
        if self.playing:
            if self.jumping_a or self.jumping_d:
                dino_rect = self.display_surf.blit(
                        self.dino_jump,
                        (self.dino_x, self.dino_y)
                        )
            else:
                if int(self.move_counter%2)==1:
                    dino_rect = self.display_surf.blit(
                            self.dino_move_1,
                            (self.dino_x, self.dino_y)
                            )
                else:
                    dino_rect = self.display_surf.blit(
                            self.dino_move_2,
                            (self.dino_x, self.dino_y)
                            )
        else:
            if self.first_frame:
                dino_rect = self.display_surf.blit(
                        self.dino_jump,
                        (self.dino_x, self.dino_y)
                        )
                self.first_frame = False
            else:
                dino_rect = self.display_surf.blit(
                        self.dino_dead,
                        (self.dino_x,self.dino_y)
                        )
        dino_rect = pygame.Rect(
                dino_rect.left + self.COLLISION_FORGIVE,
                dino_rect.top + self.COLLISION_FORGIVE,
                dino_rect.width - 2 * self.COLLISION_FORGIVE,
                dino_rect.height - 2 * self.COLLISION_FORGIVE
                )
        #Paint obstacles
        obstacle_rects = list()
        closest_obstacle = 0
        closest_obstacle_distance = None
        closest_obstacle_heights = [0,0,0,0,0]
        next_closest_obstacle_distance = None
        i = 0
        for obstacle in self.obstacles:
            if closest_obstacle is not None :
                obstacle_rect = self.display_surf.blit(
                        obstacle[0],
                        (obstacle[1][0], obstacle[1][1])
                        )
                obstacle_rect = pygame.Rect(
                        obstacle_rect.left + self.COLLISION_FORGIVE,
                        obstacle_rect.top + self.COLLISION_FORGIVE,
                        obstacle_rect.width - 2 * self.COLLISION_FORGIVE,
                        obstacle_rect.height - 2 * self.COLLISION_FORGIVE
                        )
                if closest_obstacle == 0:
                    if dino_rect.left <= obstacle_rect.right:
                        obstacle_rects.append(obstacle_rect)
                        closest_obstacle = (obstacle_rect.right
                                            + self.COLLISION_FORGIVE)
                        closest_obstacle_distance = (obstacle_rect.left
                                            - dino_rect.right)
                        closest_obstacle_heights[i] = obstacle_rect.top
                        previous_top = obstacle_rect.top
                        i += 1
                else:
                    if closest_obstacle == (obstacle_rect.left
                                            -  self.COLLISION_FORGIVE):
                        obstacle_rects.append(obstacle_rect)
                        closest_obstacle += (obstacle_rect.width
                                            + 2 * self.COLLISION_FORGIVE)
                        closest_obstacle_heights[i] = max(
                                obstacle_rect.top,
                                previous_top
                                )
                        previous_top = obstacle_rect.top
                        i += 1
                    else:
                        closest_obstacle = None
                        closest_obstacle_heights[i] = previous_top
            else:
                obstacle_rect = self.display_surf.blit(
                        obstacle[0],
                        (obstacle[1][0], obstacle[1][1])
                        )
                obstacle_rect = pygame.Rect(
                        obstacle_rect.left + self.COLLISION_FORGIVE,
                        obstacle_rect.top + self.COLLISION_FORGIVE,
                        obstacle_rect.width - 2 * self.COLLISION_FORGIVE,
                        obstacle_rect.height - 2 * self.COLLISION_FORGIVE
                        )
                if next_closest_obstacle_distance is None:
                    next_closest_obstacle_distance = (
                            obstacle_rect.left - dino_rect.right
                            )
        if next_closest_obstacle_distance is None:
            next_closest_obstacle_distance = (
                    self.display_surf.get_width() - dino_rect.right
                    )
        if closest_obstacle_distance is None:
            closest_obstacle_distance = (
                    self.display_surf.get_width() - dino_rect.right
                    )
        # Detect collision
        for obstacle_rect in obstacle_rects:
            if dino_rect.colliderect(obstacle_rect):
                self.playing = False
                if self.running:
                    self.running = self.player.keep_playing(int(self.game_time/100))
                break
        # Update screen.
        pygame.display.flip()
        # Request next move.
        if self.playing:
            state = [
                    int(self.ground_step),
                    closest_obstacle_distance,
                    next_closest_obstacle_distance
                    ]
            state.extend(closest_obstacle_heights)
            next_action = self.player.get_action(state, int(self.game_time/100))
            if next_action:
                self.jump()

    def on_cleanup(self):
        """Close game"""
        pygame.quit()
        self.most_recent_score = int(self.game_time/100)

    def on_execute(self, start_immediately = False):
        """Execute game loop

        Keyword arguments:
        start_immediately -- start playing without waiting for player
                            input (default False)
        """
        #try:
        if self.on_init() == False:
            self.running = False
        self.playing = start_immediately
        while( self.running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            self.rendered = True
        self.on_cleanup()
        """
        except Exception as err:
            pygame.quit()
            print(err)
        """
        return self.most_recent_score

if __name__ == "__main__" :
    player = Dino_player()
    theDino = Dino(player)
    theDino.on_execute()