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

EMPTY_CELL_COLOR = (213, 196, 161)
GRID_COLOR = (30, 30, 60)

FRAMES_PER_SECOND = 60
SPEED = 15


# Fish initial definition
FISH_BREED_AGE = 12     # 12
FISH_OVERCROWDING = 2   # 2

def new_fish():
    fish = {
        'type': 'fish',
        'age': 0,
        'color': NEW_FISH_COLOR,
    }

    return fish

# Bear initial definition
BEAR_BREED_AGE = 8  # 8
INITIAL_BEAR_FOOD = 8

def new_bear():
    bear = {
        'type': 'bear',
        'age': 0,
        'food': INITIAL_BEAR_FOOD,
        'col': NEW_BEAR_COLOR,
    }

    return bear

def new_empty():
    return {
        'type': 'empty',
    }

def initialize_grid(cell_count_x, cell_count_y, fish_count, bear_count):
    # create a list with fish fishes, bear bears and the rest (dimx*dimy-fish-bear) are empty  and shuffle them
    content_list = []

    for i in range(fish_count):
        content_list.append(new_fish())
    for i in range(bear_count):
        content_list.append(new_bear())
    for i in range((cell_count_x * cell_count_y - fish_count - bear_count)):
        content_list.append(new_empty())

    random.shuffle(content_list)

    # typecast the into a numpy array and reshape the 1 dimensional array to dimx * dimy
    content_1Darray = np.array(content_list)
    grid = np.reshape(content_1Darray, (cell_count_y, cell_count_x)) # First argument is for which row, the second arg. is for which column in that row

    return grid

def get_neighbors(grid, row_index, column_index):
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

def sort_neighbours(grid, cell_neighbours):
    # divide the neighbours into fish, empty cells and the rest
    fish_neighbours = []
    empty_neighbours = []
    rest_neighbours = []

    for neighbour in neighbours:
        if grid[neighbour]['type'] == 'fish':
            fish_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == 'bear':
            rest_neighbours.append(neighbour)
        else:
            empty_neighbours.append(neighbour)

    return fish_neighbours, empty_neighbours

def fish_rules(grid, row_index, column_index, fish_neighbours, empty_neighbours):
    if (grid[row_index, column_index]['age'] >= FISH_BREED_AGE):
        grid[row_index, column_index]['color'] = BREEDING_FISH_COLOR
    else:
        grid[row_index, column_index]['color'] = YOUNG_FISH_COLOR

    # breeding time
    if (grid[row_index, column_index]['age'] >= FISH_BREED_AGE and len(empty_neighbours) > 0):
        # fish breeds to an empty cell
        row_index_new, column_index_new = random.choice(empty_neighbours)
        grid[row_index_new, column_index_new] = new_fish()
        fish_neighbours.append((row_index_new, column_index_new))
        empty_neighbours.remove((row_index_new, column_index_new))

    # fish dies (overcrowding) if there are 2 or more neighbouring fish
    if (len(fish_neighbours) >= FISH_OVERCROWDING):
        grid[row_index, column_index] = new_empty()

    # if it does not die
    elif (len(neighbour_empty) > 0):
        # move fish to an empty cell
        row_index_new, column_index_new = random.choice(empty_neighbours)
        grid[row_index_new, column_index_new] = cur[row_index, column_index]
        grid[row_index, column_index] = new_empty()

    return grid

def bear_rules(cur,r,c,neighbour_fish, neighbour_empty):
    if cur[r, c]['age'] >= bear_breed_age:
        cur[r, c]['col'] = col_breeding_bear
    else:
        cur[r, c]['col'] = col_young_bear

    if cur[r, c]['food'] <= 3:
        cur[r, c]['col'] = col_starving_bear
    # if there is a fish eat it
    if len(neighbour_fish) > 0:
        cur[r, c]['food'] = bear_starvation
        r_fish, c_fish = random.choice(neighbour_fish)
        neighbour_fish.remove((r_fish, c_fish))
        neighbour_empty.append((r_fish, c_fish))
        cur[r_fish, c_fish] = empty()
    else:
        # decrease food
        cur[r, c]['food'] -= 1

    # if the bear is starved it dies
    if cur[r, c]['food'] <= 0:
        cur[r, c] = empty()
    else:  # if the bear is not dead it, first, tries to breed
        if cur[r, c]['age'] >= bear_breed_age and len(neighbour_empty) > 0:
            # fish breeds to an empty cell
            r_new, c_new = random.choice(neighbour_empty)
            cur[r_new, c_new] = new_bear()
            neighbour_empty.remove((r_new, c_new))
        # it tries to move
        if len(neighbour_empty) > 0:
            r_new, c_new = random.choice(neighbour_empty)
            cur[r_new, c_new] = cur[r, c]
            cur[r, c] = empty()
    return cur

def update_grid(surface, grid):
    # for each cell
    for row_index, column_index in np.ndindex(grid.shape):
        # if there is a bear or a fish
        if (grid[row_index, column_index]['type'] != 'empty'):
            # update age (both age the same)
            grid[row_index, column_index]['age'] += 1

            # calculate neighbours and find the empty and the fish neighbours (other bears are not important, currently)
            neighbours = get_neighbours(grid, row_index, column_index)
            fish_neighbours, empty_neighbours = sort_neighbours(grid, neighbours)

            # if it is a fish
            if (grid[row_index, column_index]['type'] == 'fish'):
                grid = fish_rules(grid, row_index, column_index, fish_neighbours, empty_neighbours)

            # if it is a bear
            elif (grid[row_index, column_index]['type'] == 'bear'):
                grid = bear_rules(grid, row_index, column_index, fish_neighbours, empty_neighbours)
    return grid

def draw_grid(surface, grid, sz):
    for row_index, column_index in np.ndindex(grid.shape):
        cell_color = EMPTY_CELL_COLOR
        if grid[row_index, column_index]['type'] != 'empty':
            cell_color = grid[row_index, column_index]['color']
        pygame.draw.rect(surface, cell_color, (column_index * sz, row_index * sz, sz - 1, sz - 1))

def main(cell_count_x, cell_count_y, cell_size, fish_count, bear_count):
    pygame.init()
    surface = pygame.display.set_mode((cell_count_x * cell_size, cell_count_y * cell_size))
    pygame.display.set_caption("Animal Kingdom")

    grid = initialize_grid(cell_count_x, cell_count_y, fish_count, bear_count)

    clock = pygame.time.Clock()
    speed_count = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(col_grid)
        if (speed_count % SPEED == 0):
            grid = update_grid(surface, grid)
        draw_grid(surface, grid, cell_size)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)
        speed_count += 1

if __name__ == "__main__":
    fish_count = 10
    bear_count = 3

    cell_count_x = 40
    cell_count_y = 10
    cell_size = 16

    main(cell_count_x, cell_count_y, cell_size, fish_count, bear_count)
