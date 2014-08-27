"""alien_simulation.py : Runs simulations of aliens romaing around
a non-existant world. """

import sys
import random

WORLD_FILENAME = 'world_map_small.txt'
MAX_ITERATIONS = 10000

class SimulationException(Exception):
    """ Exception class, used when a simulation can no longer
        proceed for any particular reason. """

    def __init__(self, error_message):
        super(SimulationException, self).__init__()
        self.error_message = error_message

class City(object):
    """ Class which represents a city in the world. """

    def __init__(self, city_name, ):
        self.city_name = city_name
        self.city_neighbours = dict()
        self.occupied_alien = None
        self.destroyed = False

class Alien(object):
    """ Class which represents an alien. """

    def __init__(self, alien_number):
        self.alien_number = alien_number
        self.destroyed = False
        self.occupied_city = None

def print_out_final_world(world_map):
    """ Prints out the world in the state provided, in the format identical
        to the input file. """

    for city in world_map:
        output_line = city
        for neighbour, direction in world_map[city].city_neighbours.iteritems():
            output_line += " {0}={1}".format(direction, neighbour)
        print output_line

def generate_initial_positions(world_map, alien_list):
    """ Generates the initial positions of the aliens in the world. Destroys
        cities and aliens immediately if an alien is assigned a city which
        already is resident to another alien. """

    for alien in alien_list:
        random_city = world_map[random.choice(world_map.keys())]
        if random_city.occupied_alien is None:
            random_city.occupied_alien = alien
            alien.occupied_city = random_city
        else:
            world_map = destroy_aliens_and_city(world_map, random_city, alien)
            alien.destroyed = True
            random_city.occupied_alien.destroyed = True
            if len(world_map) == 0:
                raise SimulationException("The world has been destroyed during "
                                          "the initial placement of aliens!")

    # Get rid of destroyed aliens, as we no longer need them
    alien_list = [alien for alien in alien_list if alien.destroyed is False]

    return world_map, alien_list

def destroy_aliens_and_city(world_map, random_city, alien):
    """ Destroys a city and the aliens that have fought there. """

    print "{0} has been destroyed by alien {1} and alien {2}!".format(
        random_city.city_name, random_city.occupied_alien.alien_number,
        alien.alien_number)

    neighbour_names = world_map[random_city.city_name].city_neighbours

    for city_name in neighbour_names:
        del world_map[city_name].city_neighbours[random_city.city_name]

    del world_map[random_city.city_name]

    return world_map

def run_simulation(world_map, alien_list):
    """ Entry point for the main simulation of aliens wondering
        around the world, killing each other if they land on an
        already inhabited city. """

    run_count = 0
    world_map, alien_list = generate_initial_positions(world_map, alien_list)

    # Run up until the maximum number of iterations, or until the world
    # is destroyed. On each pass, deal with each active Alien separately,
    # making it move randomly to a neighbour city where it is able to
    while run_count < MAX_ITERATIONS and len(world_map) > 0:
        for alien in alien_list:
            # Don't need to process the Alien if it has already been destrpyed
            # in this pass
            if alien.destroyed == False:
                current_city = alien.occupied_city
                # If there are no neighbours, then the city is "trapped", and
                # the alien can't move from it, nor can an alien move towards it
                if len(world_map[current_city.city_name].city_neighbours) > 0:
                    next_random_key = random.choice(
                        world_map[current_city.city_name].
                        city_neighbours.keys())
                    next_city = world_map[next_random_key]
                    if next_city.occupied_alien is None:
                        alien.occupied_city = next_city
                        next_city.occupied_alien = alien
                    else:
                        world_map = destroy_aliens_and_city(world_map,
                                                            next_city, alien)
                        alien.destroyed = True
                        next_city.occupied_alien.destroyed = True

                current_city.occupied_alien = None

        # Remove the aliens that are no longer alive
        alien_list = [alien for alien in alien_list if alien.destroyed is False]
        run_count += 1

    print_out_final_world(world_map)

def generate_aliens(number_to_generate):
    """ Generates the required number of aliens to place
        on the world. """

    alien_list = []

    for i in xrange(number_to_generate):
        alien_list.append(Alien(i))

    return alien_list

def read_in_world_file(map_filename):
    """ Reads in a map file to generate the world, populated with
        cities. """

    world_map = dict()
    map_file = open(map_filename, 'r')

    for line in map_file.readlines():
        split_line = line.rstrip().split(" ")
        new_city = City(split_line[0])

        for i in xrange(1, len(split_line)):
            neighbour_city = split_line[i]
            split_neighbour = neighbour_city.split("=")
            new_city.city_neighbours[split_neighbour[1]] = split_neighbour[0]

        world_map[split_line[0]] = new_city

    map_file.close()

    return world_map

if __name__ == "__main__":
    # First argument is the script name, so remove it.
    sys.argv.pop(0)
    if len(sys.argv) != 1:
        print "Specify the number of aliens to run in the simulation"
        sys.exit(-1)
    else:
        try:
            NUMBER_OF_ALIENS = int(sys.argv[0])
        except ValueError:
            print "Number of aliens must be an integer!"
            sys.exit(-1)

    ALIENS = generate_aliens(NUMBER_OF_ALIENS)
    FULL_WORLD_MAP = read_in_world_file(WORLD_FILENAME)

    try:
        run_simulation(FULL_WORLD_MAP, ALIENS)
    except SimulationException as ex:
        print ex.error_message
    