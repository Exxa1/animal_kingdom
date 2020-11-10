import pygame, random
import numpy as np

# Colors

NEW_FISH_COLOR = (0, 128, 255)
YOUNG_FISH_COLOR = (15,82,186)
BREEDING_FISH_COLOR = (220,35,157)

NEW_BEAR_COLOR = (150,75,0)
YOUNG_BEAR_COLOR = (165,113,78)
BREEDING_BEAR_COLOR = (150,75,0)
STARVING_BEAR_COLOR = (75,75,75)

NEW_PLANT_COLOR = (0,150,0)
YOUNG_PLANT_COLOR = (75,150,0)
SPREADING_PLANT_COLOR = (120,150,0)

EMPTY_CELL_COLOR = (213, 196, 161)
GRID_COLOR = (30, 30, 60)

FRAMES_PER_SECOND = 60
SPEED = 15


# Fish initial definition
FISH_BREED_AGE = 12     # 12
FISH_OVERCROWDING = 4   # 2
INITIAL_FISH_FOOD = 11 # 10

def new_fish():
    fish = {
        'type': 'fish',
        'age': 0,
        'food': INITIAL_FISH_FOOD,
        'color': NEW_FISH_COLOR,
    }

    return fish

# Plant initial definition
PLANT_SPREADING_AGE = 5  # 8
PLANT_OVERCROWDING = 4 # 10

def new_plant():
    plant = {
        'type': 'plant',
        'age': 0,
        'color': NEW_PLANT_COLOR,
    }

    return plant

# Bear initial definition
BEAR_BREED_AGE = 12  # 8
INITIAL_BEAR_FOOD = 2 # 10

def new_bear():
    bear = {
        'type': 'bear',
        'age': 0,
        'food': INITIAL_BEAR_FOOD,
        'color': NEW_BEAR_COLOR,
    }

    return bear

def new_empty():
    return {
        'type': 'empty',
    }

def initialize_grid(cell_count_x, cell_count_y, fish_count, bear_count, plant_count):
    # create a list with fish fishes, bear bears and the rest (dimx*dimy-fish-bear) are empty  and shuffle them
    content_list = []

    for i in range(fish_count):
        content_list.append(new_fish())
    for i in range(bear_count):
        content_list.append(new_bear())
    for i in range(plant_count):
        content_list.append(new_plant())
    for i in range((cell_count_x * cell_count_y - fish_count - bear_count - plant_count)):
        content_list.append(new_empty())

    random.shuffle(content_list)

    # typecast the into a numpy array and reshape the 1 dimensional array to dimx * dimy
    content_1Darray = np.array(content_list)
    grid = np.reshape(content_1Darray, (cell_count_y, cell_count_x)) # First argument is for which row, the second arg. is for which column in that row

    return grid

def get_neighbours(grid, row_index, column_index):
    # collects the indexes of the neighbouring cells
    row_min, column_min = 0, 0
    row_max, column_max = grid.shape
    row_max, column_max = row_max - 1, column_max - 1 # it's off by one
    # r-1,c-1 | r-1,c  | r-1,c+1
    # --------|--------|---------
    # r  ,c-1 | r  ,c  | r  ,c+1
    # --------|--------|---------
    # r+1,c-1 | r+1,c  | r+1,c+1
    neighbours = []

    # r-1:
    if row_index - 1 >= row_min :
        if column_index - 1 >= column_min: neighbours.append((row_index - 1, column_index - 1))
        neighbours.append((row_index - 1, column_index))  # c is inside the grid
        if column_index + 1 <= column_max: neighbours.append((row_index - 1, column_index + 1))
    # r:
    if column_index - 1 >= column_min: neighbours.append((row_index, column_index - 1))
    # skip center (r,c) since we are listing its neighbour positions
    if column_index + 1 <= column_max: neighbours.append((row_index, column_index + 1))
    # r+1:
    if row_index + 1 <= row_max:
        if column_index - 1 >= column_min: neighbours.append((row_index + 1, column_index - 1))
        neighbours.append((row_index + 1, column_index))  # c is inside cur
        if column_index + 1 <= column_max: neighbours.append((row_index + 1, column_index + 1))
    return neighbours

def sort_neighbours(grid, neighbours):
    # divide the neighbours into fish, empty cells and the rest
    fish_neighbours = []
    plant_neighbours = []
    empty_neighbours = []

    for neighbour in neighbours:
        if grid[neighbour]['type'] == 'fish':
            fish_neighbours.append(neighbour)
        elif grid[neighbour]['type'] == 'plant':
            plant_neighbours.append(neighbour)
        else:
            empty_neighbours.append(neighbour)

    return fish_neighbours, plant_neighbours, empty_neighbours

def fish_rules(grid, row_index, column_index, fish_neighbours, plant_neighbours, empty_neighbours):
    if (grid[row_index, column_index]['age'] >= FISH_BREED_AGE):
        grid[row_index, column_index]['color'] = BREEDING_FISH_COLOR
    else:
        grid[row_index, column_index]['color'] = YOUNG_FISH_COLOR

    # if there is a plant eat it
    if len(plant_neighbours) > 0:
        grid[row_index, column_index]['food'] = INITIAL_FISH_FOOD
        row_index_plant, column_index_plant = random.choice(plant_neighbours)
        plant_neighbours.remove((row_index_plant, column_index_plant))
        empty_neighbours.append((row_index_plant, column_index_plant))
        grid[row_index_plant, column_index_plant] = new_empty()
    else:
        # decrease food
        grid[row_index, column_index]['food'] -= 1

    # breeding time
    if (grid[row_index, column_index]['age'] >= FISH_BREED_AGE and len(empty_neighbours) > 0):
        # fish breeds to an empty cell
        row_index_new, column_index_new = random.choice(empty_neighbours)
        grid[row_index_new, column_index_new] = new_fish()
        fish_neighbours.append((row_index_new, column_index_new))
        empty_neighbours.remove((row_index_new, column_index_new))

    # fish dies (overcrowding or starving or natural aging) if there are 2 or more neighbouring fish
    if (len(fish_neighbours) >= FISH_OVERCROWDING) or (grid[row_index, column_index]['food'] <= 0):
        grid[row_index, column_index] = new_empty()
    else:
        random_number = random.randint(7, 60) # Determines whether the fish dies of natural causes or not :)
        fish_age = grid[row_index, column_index]['age']

        if (random_number <= fish_age):
            grid[row_index, column_index] = new_empty()
        elif (len(empty_neighbours) > 0):
            # move fish to an empty cell
            row_index_new, column_index_new = random.choice(empty_neighbours)
            grid[row_index_new, column_index_new] = grid[row_index, column_index]
            grid[row_index, column_index] = new_empty()

    return grid

def bear_rules(grid, row_index, column_index, fish_neighbours, empty_neighbours):
    if grid[row_index, column_index]['age'] >= BEAR_BREED_AGE:
        grid[row_index, column_index]['color'] = BREEDING_BEAR_COLOR
    else:
        grid[row_index, column_index]['color'] = YOUNG_BEAR_COLOR

    if grid[row_index, column_index]['food'] <= 3:
        grid[row_index, column_index]['color'] = STARVING_BEAR_COLOR

    # if there is a fish eat it
    if len(fish_neighbours) > 0:
        grid[row_index, column_index]['food'] = INITIAL_BEAR_FOOD
        row_index_fish, column_index_fish = random.choice(fish_neighbours)
        fish_neighbours.remove((row_index_fish, column_index_fish))
        empty_neighbours.append((row_index_fish, column_index_fish))
        grid[row_index_fish, column_index_fish] = new_empty()
    else:
        # decrease food
        grid[row_index, column_index]['food'] -= 1

    # if the bear is starved it dies
    if grid[row_index, column_index]['food'] <= 0:
        grid[row_index, column_index] = new_empty()
    else:  # if the bear is not dead it, first, tries to breed
        if grid[row_index, column_index]['age'] >= BEAR_BREED_AGE and len(empty_neighbours) > 0:
            # bear breeds to an empty cell
            row_index_new, column_index_new = random.choice(empty_neighbours)
            grid[row_index_new, column_index_new] = new_bear()
            empty_neighbours.remove((row_index_new, column_index_new))

        random_number = random.randint(7, 60) # Determines whether the fish dies of natural causes or not :)
        bear_age = grid[row_index, column_index]['age']

        if (random_number <= bear_age):
            grid[row_index, column_index] = new_empty()
        elif len(empty_neighbours) > 0: # it tries to move
            row_index_new, column_index_new = random.choice(empty_neighbours)
            grid[row_index_new, column_index_new] = grid[row_index, column_index]
            grid[row_index, column_index] = new_empty()

    return grid

def plant_rules(grid, row_index, column_index, plant_neighbours, empty_neighbours):
    # change color
    if (grid[row_index, column_index]['age'] >= PLANT_SPREADING_AGE):
        grid[row_index, column_index]['color'] = SPREADING_PLANT_COLOR
    else:
        grid[row_index, column_index]['color'] = YOUNG_PLANT_COLOR

    # spread
    if (grid[row_index, column_index]['age'] >= PLANT_SPREADING_AGE and len(empty_neighbours) > 0):
        # plant spread to an empty cell
        row_index_new, column_index_new = random.choice(empty_neighbours)
        grid[row_index_new, column_index_new] = new_plant()
        plant_neighbours.append((row_index_new, column_index_new))
        empty_neighbours.remove((row_index_new, column_index_new))

    # overcrowd
    # chance to dies
    if (len(plant_neighbours) >= PLANT_OVERCROWDING):
        grid[row_index, column_index] = new_empty()
    else:
        random_number = random.randint(7, 60) # Determines whether the fish dies of natural causes or not :)
        plant_age = grid[row_index, column_index]['age']

        if (random_number <= plant_age):
            grid[row_index, column_index] = new_empty()

    return grid

def update_grid(surface, grid):
    # for each cell
    for row_index, column_index in np.ndindex(grid.shape):
        # if there is a bear or a fish
        if (grid[row_index, column_index]['type'] != 'empty'):
            # update age (both age the same)
            grid[row_index, column_index]['age'] += 1

            # calculate neighbours and find the empty and the fish neighbours (other bears are not important, currently)

            neighbours = get_neighbours(grid, row_index, column_index)
            fish_neighbours, plant_neighbours, empty_neighbours = sort_neighbours(grid, neighbours)

            # if it is a fish
            if (grid[row_index, column_index]['type'] == 'fish'):
                grid = fish_rules(grid, row_index, column_index, fish_neighbours, plant_neighbours, empty_neighbours)

            # if it is a bear
            elif (grid[row_index, column_index]['type'] == 'bear'):
                grid = bear_rules(grid, row_index, column_index, fish_neighbours, empty_neighbours)

            # if it is a plant
            elif (grid[row_index, column_index]['type'] == 'plant'):
                grid = plant_rules(grid, row_index, column_index, plant_neighbours, empty_neighbours)
    return grid

def draw_grid(surface, grid, cell_size):
    for row_index, column_index in np.ndindex(grid.shape):
        cell_color = EMPTY_CELL_COLOR
        if grid[row_index, column_index]['type'] != 'empty':
            cell_color = grid[row_index, column_index]['color']
        pygame.draw.rect(surface, cell_color, (column_index * cell_size, row_index * cell_size, cell_size - 1, cell_size - 1))

def main(cell_count_x, cell_count_y, cell_size, fish_count, bear_count, plant_count):
    pygame.init()
    surface = pygame.display.set_mode((cell_count_x * cell_size, cell_count_y * cell_size))
    pygame.display.set_caption("Animal Kingdom")

    grid = initialize_grid(cell_count_x, cell_count_y, fish_count, bear_count, plant_count)

    clock = pygame.time.Clock()
    speed_count = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(GRID_COLOR)
        if (speed_count % SPEED == 0):
            grid = update_grid(surface, grid)
        draw_grid(surface, grid, cell_size)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)
        speed_count += 1

if __name__ == "__main__":
    fish_count = 10
    bear_count = 3
    plant_count = 10

    cell_count_x = 40
    cell_count_y = 10
    cell_size = 16

    main(cell_count_x, cell_count_y, cell_size, fish_count, bear_count, plant_count)
