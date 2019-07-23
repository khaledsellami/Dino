# Dino
My own implementation of the Google Chrome dinosaur game with a script to train an AI to play it.

## Description
This is a project I did on to learn and implement NEAT (NeuroEvolution of Augmenting Topologies). I have implemented my own version of the Google Chrome dinosaur game using Pygame in addition to a script to train an AI to play the game using multineat.

## Results
After a few generations ( usually after 20 generations ) the AI starts to learn how to play the game and its starts to fluctuate between 700 and 900 from then on.

## Install
This project requires Python 3.7, pygame and multineat installed.

## Usage
To try out the script, simply run the command :
    
    python dino_game.py 

Optional arguments:
    - type ( or m ) : type of the player which can be either human, random or neat (default human)
    if type is neat
        - population ( or p ) : number of genomes in a population (default 100).
        - generations ( or g ) : number of generation to train (default 50).
Example:

    python dino_game.py --type neat -p 50 -g 20

You can tweak the code in order to better customize the inputs.
