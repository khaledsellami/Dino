import sys

from dino import Dino, Dino_player, Dino_player_random
from neat import NEAT_trainer


def verify_arguments():
    arguments = dict()
    player_types = ["human", "random", "neat"]
    if len(sys.argv) == 1:
        return arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--type" or arg == "-t":
            if i+1<len(sys.argv) and not "type" in arguments:
                arguments["type"] = sys.argv[i+1]
                del sys.argv[i]
                del sys.argv[i]
                if arguments["type"] not in player_types:
                    return None
                elif arguments["type"] != "neat":
                    break
                if i < len(sys.argv):
                    arg=sys.argv[i]
                else:
                    break
            else:
                return None
        if "type" in arguments:
            if arg == "--population" or arg == "-p":
                if i+1 < len(sys.argv) and not "population" in arguments:
                    try:
                        arguments["population"] = int(sys.argv[i+1])
                    except TypeError:
                        return None
                    del sys.argv[i]
                    del sys.argv[i]
                    if i < len(sys.argv):
                        arg=sys.argv[i]
                    else:
                        break
                else:
                    return None
            if arg == "--generations" or arg == "-g":
                if i+1 < len(sys.argv) and not "generations" in arguments:
                    try:
                        arguments["generations"] = int(sys.argv[i+1])
                    except TypeError:
                        return None
                    del sys.argv[i]
                    del sys.argv[i]
                    if i < len(sys.argv):
                        arg = sys.argv[i]
                    else:
                        break
                else:
                    return None
            if arg == "--population" or arg == "-p":
                if i+1 < len(sys.argv) and not "population" in arguments:
                    try:
                        arguments["population"] = int(sys.argv[i+1])
                    except TypeError:
                        return None
                    del sys.argv[i]
                    del sys.argv[i]
                    if i < len(sys.argv):
                        arg=sys.argv[i]
                    else:
                        break
                else:
                    return None
    if len(arguments) != 0 and len(sys.argv) == 1:
        return arguments
    else:
        return None


if __name__ == "__main__" :
    arguments = verify_arguments()
    if arguments is None:
        print(f'Usage: python {sys.argv[0]} [ --type (human|random|neat \
                       [--population <size>] [--generations <size>]) ] ')
    elif "type" in arguments:
        if arguments["type"] == "human":
            player = Dino_player()
            theDino = Dino(player)
            theDino.on_execute()
        elif arguments["type"] == "random":
            player = Dino_player_random()
            theDino = Dino(player)
            theDino.on_execute()
        else:
            data = dict()
            if "population" in arguments:
                data["population_size"] = arguments["population"]
            if "generations" in arguments:
                data["generations"] = arguments["generations"]
            cycle = NEAT_trainer(**data)
            cycle.start_cycle()
    else:
        player = Dino_player()
        theDino = Dino(player)
        theDino.on_execute()






