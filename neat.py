import os
import random

import pygame
import MultiNEAT as NEAT

from dino import Dino_player,Dino


class Dino_player_neat(Dino_player):
    """Dino player with a neural network for deciding actions."""
    def __init__(self, network, jump_threshold = 0.5):
        self.network = network
        self.jump_threshold = jump_threshold

    def get_action(self, state, current_score):
        """Return True to jump.

        Keyword arguments:
        state -- current state of the game
        current_score -- current score of the game
        """
        state.append(1)
        self.network.Input(state)
        self.network.Activate()
        output = self.network.Output()
        if output[0] < self.jump_threshold:
            return False
        else:
            return True

    def keep_playing(self, current_score):
        """Return True to keep playing.

        Keyword arguments:
        current_score -- current score of the game
        """
        return False


class NEAT_trainer:
    """the class that trains a bot using neat."""

    def __init__(self, population_size = 100, input_size = 9, output_size = 1,
                 generations = 50):
        """Initialize the trainer.

        Keyword arguments:
        population_size -- number of genomes per generation (default 100)
        input_size -- size of the input state + 1 (default 9)
        output_size -- size of the result of the genome neural networks (default 1)
        generations -- number of generations (default 50)
        """
        self.generations = generations
        self.params = NEAT.Parameters()
        self.params.PopulationSize = population_size
        genome = NEAT.Genome(0, input_size, 0, output_size, False,
                     NEAT.ActivationFunction.UNSIGNED_SIGMOID,
                     NEAT.ActivationFunction.UNSIGNED_SIGMOID,
                     0, self.params, 0)
        self.population = NEAT.Population(genome, self.params, True, 1.0, 0)

    def evaluate(self, genome, generation, genome_id):
        """Generate a game, test the genome and return its fitness.

        Keyword arguments:
        genome -- genome to test
        generation -- number of the current generation
        genome_id -- genome id in the current generation
        """
        # create neural network from genome.
        net = NEAT.NeuralNetwork()
        genome.BuildPhenotype(net)
        # create player and .
        player = Dino_player_neat(net)
        text = "generation : " + str(generation) + " || genome : " + str(genome_id)
        the_game = Dino(player, text)
        fitness = the_game.on_execute(start_immediately = True)
        return fitness

    def start_cycle(self, one_by_one = False):
        """Start the cycle.

        Keyword arguments:
        one_by_one -- evaluate the genomes one by one if True (default False)
        """
        if one_by_one:
            # play each genome in a game alone.
            for generation in range(self.generations):
                # retrieve genome list and call evaluation function for each one.
                genome_list = NEAT.GetGenomeList(self.population)
                best_fitness = 0
                print("generation",generation + 1,":")
                print("testing " + str(self.params.PopulationSize) + " genomes : ")
                i = 0
                for genome in genome_list:
                    i += 1
                    print(i, end = " ")
                    net = NEAT.NeuralNetwork()
                    genome.BuildPhenotype(net)
                    fitness = self.evaluate(genome, generation + 1, i)
                    if best_fitness < fitness:
                        best_fitness = fitness
                    genome.SetFitness(fitness)
                # print best fitness and advance to the next generation
                print("best fitness : ", best_fitness)
                print("=======================================")
                self.population.Epoch()
        else:
            # play all of the population at the same time
            for generation in range(self.generations):
                # retrieve genome list and build the players list.
                genome_list = NEAT.GetGenomeList(self.population)
                players = list()
                for genome in genome_list:
                    net = NEAT.NeuralNetwork()
                    genome.BuildPhenotype(net)
                    players.append(Dino_player_neat(net))
                # start game and retrieve fitness list.
                the_game = Dino_NEAT(players, generation)
                fitness = the_game.on_execute()
                if fitness is None:
                    print("Training stopped.")
                    break
                # assign each genome to its corresponding fitness.
                best_fitness = 0
                for i in range(len(fitness)):
                    genome = genome_list[i]
                    if best_fitness < fitness[i]:
                        best_fitness = fitness[i]
                    genome.SetFitness(fitness[i])
                # print best fitness and advance to the next generation
                print("generation",generation,":",best_fitness)
                self.population.Epoch()



class Dino_NEAT:
    """A modified version of the Dino game class which is capable
    of showing multiple non-human players at a time."""

    def __init__(self, players, generation):
        """Initialize the variables and declare constants.

        Keyword arguments:
        players -- list of players
        generation -- number of the current generation
        """
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
        self.jumping_a = False
        self.jumping_d = False
        self.first_frame = True
        self.stop_training = False
        # Initialize rest of variables.
        self.players = list()
        for player in players:
            player_data = dict()
            player_data["player"] = player
            player_data["jumping_a"] = False
            player_data["jumping_d"] = False
            player_data["alive"] = True
            player_data["dino_x"] = self.DINO_INITIAL_X
            player_data["dino_y"] = self.DINO_INITIAL_Y
            player_data["rect"] = None
            player_data["fitness"] = 0
            self.players.append(player_data)
        self.generation = generation
        self.players_alive = len(self.players)
        self.display_surf = None
        self.move_counter = 0
        self.game_time = 0
        self.most_recent_score = 0
        self.obstacle_distance = 0
        self.possible_obstacles = list()
        self.obstacles = list()

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
        for player in self.players:
            player["jumping_a"] = False
            player["jumping_d"] = False
            player["alive"] = True
            player["dino_x"] = self.DINO_INITIAL_X
            player["dino_y"] = self.DINO_INITIAL_Y
            player["rect"] = None
            player["fitness"] = 0
        self.obstacles = list()
        self.obstacle_distance = 0
        self.move_counter = 0
        self.game_time = 0
        self.ground_move = 0
        self.clock.tick(60)

    def jump(self, player):
        """Trigger jumping event if possible."""
        if not(player["jumping_a"] or player["jumping_d"]):
            player["jumping_a"] = True

    def on_event(self, event):
        """Detect events and change flags accordingly."""
        if event.type == pygame.QUIT:
            self.running = False
            self.stop_training = True

    def on_loop(self):
        """Update variables and move objects."""
        dt = self.clock.tick(60)
        self.game_time += dt
        #Update dinosaur locations if jumping.
        for player in self.players:
            if player["alive"]:
                if player["jumping_a"]:
                    if player["dino_y"] <= (
                            self.DINO_INITIAL_Y - self.MAX_JUMP_HEIGHT
                            ):
                        player["jumping_a"] = False
                        player["jumping_d"] = True
                    elif player["dino_y"] <= (self.DINO_INITIAL_Y
                                       - self.MAX_JUMP_HEIGHT/1.5):
                        player["dino_y"] -= self.JUMP_SPEED_A * dt/2
                    else:
                        player["dino_y"] -= self.JUMP_SPEED_A * dt
                if player["jumping_d"]:
                    if player["dino_y"] >= self.DINO_INITIAL_Y:
                        player["jumping_d"] = False
                        player["dino_y"] = self.DINO_INITIAL_Y
                    elif player["dino_y"] <= (self.DINO_INITIAL_Y
                                         - self.MAX_JUMP_HEIGHT/1.5):
                        player["dino_y"] += self.JUMP_SPEED_D * dt/2
                    else:
                        player["dino_y"] += self.JUMP_SPEED_D*dt
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
        generation_text = self.text_font.render(
            "generation " + str(self.generation),
            False,
            (0, 0, 0)
            )
        self.display_surf.blit(
                generation_text,
                (self.display_surf.get_width()//2
                 - generation_text.get_width()//2,0)
                )
        players_alive = self.text_font.render(
            "players alive " + str(self.players_alive),
            False,
            (0, 0, 0)
            )
        self.display_surf.blit(
                players_alive,
                (self.display_surf.get_width()//2
                 - players_alive.get_width()//2,25)
                )
        #Paint Dinosaurs
        for player in self.players:
            if player["alive"]:
                if player["jumping_a"] or player["jumping_d"]:
                    dino_rect = self.display_surf.blit(
                            self.dino_jump,
                            (player["dino_x"], player["dino_y"])
                            )
                else:
                    if int(self.move_counter%2)==1:
                        dino_rect = self.display_surf.blit(
                                self.dino_move_1,
                                (player["dino_x"], player["dino_y"])
                                )
                    else:
                        dino_rect = self.display_surf.blit(
                                self.dino_move_2,
                                (player["dino_x"], player["dino_y"])
                                )
                dino_rect = pygame.Rect(
                        dino_rect.left + self.COLLISION_FORGIVE,
                        dino_rect.top + self.COLLISION_FORGIVE,
                        dino_rect.width - 2 * self.COLLISION_FORGIVE,
                        dino_rect.height - 2 * self.COLLISION_FORGIVE
                        )
                player["rect"] = dino_rect
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
        for player in self.players:
            if player["alive"]:
                for obstacle_rect in obstacle_rects:
                    if player["rect"].colliderect(obstacle_rect):
                        player["alive"] = False
                        player["fitness"]= int(self.game_time/100)
                        break
        # Update screen
        pygame.display.flip()
        # Request next move.
        state = [
            int(self.ground_step),
            closest_obstacle_distance,
            next_closest_obstacle_distance
            ]
        state.extend(closest_obstacle_heights)
        self.players_alive = 0
        for player in self.players:
            if player["alive"]:
                self.players_alive += 1
                next_action = player["player"].get_action(state,
                                    int(self.game_time/100))
                if next_action:
                    self.jump(player)
        if self.players_alive == 0:
            self.running = False

    def on_cleanup(self):
        """Close game"""
        pygame.quit()

    def on_execute(self):
        """Execute game loop"""
        if self.on_init() == False:
            self.running = False
        while( self.running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
        fitness = list()
        for player in self.players:
            fitness.append(player["fitness"])
        if self.stop_training:
            fitness = None
        return fitness


if __name__ == "__main__" :
    cycle = NEAT_trainer()
    cycle.start_cycle()