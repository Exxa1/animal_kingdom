import pygame, random
import numpy as np

col_new_fish = (0, 128, 255)
col_young_fish = (15,82,186)
col_breeding_fish = (220,35,157)

col_new_bear = (150,75,0)
col_young_bear = (165,113,78)
col_breeding_bear = (150,75,0)
col_starving_bear = (75,75,75)

col_empty = (213, 196, 161)
col_grid = (30, 30, 60)

FRAMES_PER_SECOND = 60
SPEED = 15
ID = 0
# Fish initial definition
fish_breed_age = 12     # 12
fish_overcrowding = 2   # 2
def new_fish():
    global ID
    fish = {'type': 'fish', 'id':ID, 'age': 0, 'col':col_new_fish}
    ID += 1
    return fish

# Bear initial definition
bear_breed_age = 8      # 8
bear_starvation = 10    # 10
def new_bear():
    global ID
    bear = {'type': 'bear', 'id':ID, 'age': 0, 'food': bear_starvation, 'col':col_new_bear}
    ID += 1
    return bear

def empty():
    return {'type': 'empty'}

def init(dimx, dimy, fish, bear):
    # create a list with fish fishes, bear bears and the rest (dimx*dimy-fish-bear) are empty  and shuffle them
    content_list = []
    for i in range(fish):
        content_list.append(new_fish())
    for i in range(bear):
        content_list.append(new_bear())
    for i in range((dimx * dimy - fish - bear)):
        content_list.append(empty())
    random.shuffle(content_list)
    # typecast the into a numpy array and reshape the 1 dimensional array to dimx * dimy
    content_1Darray = np.array(content_list)
    cells = np.reshape(content_1Darray, (dimy, dimx)) # the shape information is given in an  odd order
    return cells

def get_neighbors(cur, r, c):
    r_min, c_min = 0 , 0
    r_max, c_max = cur.shape
    r_max, c_max = r_max -1 , c_max-1 # it's off by one
    # r-1,c-1 | r-1,c  | r-1,c+1
    # --------|--------|---------
    # r  ,c-1 | r  ,c  | r  ,c+1
    # --------|--------|---------
    # r+1,c-1 | r+1,c  | r+1,c+1
    neighbours = []
    # r-1:
    if r-1 >= r_min :
        if c-1 >= c_min: neighbours.append((r-1,c-1))
        neighbours.append((r-1,c))  # c is inside cur
        if c+1 <= c_max: neighbours.append((r - 1, c+1))
    # r:
    if c-1 >= c_min: neighbours.append((r,c-1))
    # skip center (r,c) since we are listing its neighbour positions
    if c + 1 <= c_max: neighbours.append((r,c+1))
    # r+1:
    if r + 1 <= r_max:
        if c - 1 >= c_min: neighbours.append((r+1,c-1))
        neighbours.append((r+1, c))  # c is inside cur
        if c + 1 <= c_max: neighbours.append((r+1,c+1))
    return neighbours

def neighbour_fish_empty_rest(cur,neighbours):
    # divide the neighbours into fish, empty cells and the rest
    fish_neighbours =[]
    empty_neighbours =[]
    rest_neighbours=[]
    for neighbour in neighbours:
        if cur[neighbour]['type'] == "fish":
            fish_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == "bear":
            rest_neighbours.append(neighbour)
        else:
            empty_neighbours.append(neighbour)

    return fish_neighbours, empty_neighbours # we currently don't need:  rest_neighbours



def fish_rules(cur,r,c,neighbour_fish, neighbour_empty):
    if cur[r, c]['age'] >= 12:
        cur[r, c]['col'] = col_breeding_fish
    else:
        cur[r, c]['col'] = col_young_fish

    # breeding
    if (cur[r, c]['age'] >= 12 and len(neighbour_empty) > 0):
        # fish breeds to an empty cell
        r_new, c_new = random.choice(neighbour_empty)
        cur[r_new, c_new] = new_fish()
        neighbour_fish.append((r_new, c_new))
        neighbour_empty.remove((r_new, c_new))
    # # the dies (overcrowding) if there are 2 or more neighbouring fish
    if len(neighbour_fish) >= fish_overcrowding:
        cur[r, c] = empty()
    # if it does not die
    elif len(neighbour_empty) > 0:
        # move fish to an empty cell
        r_new, c_new = random.choice(neighbour_empty)
        cur[r_new, c_new] = cur[r, c]
        cur[r, c] = empty()

    return cur

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

def update(surface, cur, sz):
    # for each cell
    for r, c in np.ndindex(cur.shape):
        # if there is a bear or a fish
        if cur[r, c]['type'] == "fish" or cur[r, c]['type'] == "bear":
            # update age (both age the same)
            cur[r, c]['age'] += 1
            # calculate neighbours and find the empty and the fish neighbours (other bears are not important, currently)
            neighbours = get_neighbors(cur, r, c)
            neighbour_fish, neighbour_empty = neighbour_fish_empty_rest(cur, neighbours)

            # if it is a fish
            if cur[r, c]['type'] == "fish":
                cur = fish_rules(cur, r, c, neighbour_fish, neighbour_empty)

            # if it is a bear
            elif cur[r, c]['type'] == "bear":
                cur = bear_rules(cur, r, c, neighbour_fish, neighbour_empty)
    return cur

def draw_grid(surface,cur,sz):
    for r, c in np.ndindex(cur.shape):
        col = col_empty
        if cur[r, c]['type'] != 'empty':
            col = cur[r, c]['col']
        pygame.draw.rect(surface, col, (c * sz, r * sz, sz - 1, sz - 1))

def main(dimx, dimy, cellsize,fish,bear):
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Animal Kingdom")

    cells = init(dimx, dimy,fish,bear)

    clock = pygame.time.Clock()
    speed_count = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(col_grid)
        if(speed_count % SPEED == 0):
            cells = update(surface, cells, cellsize)
        draw_grid(surface, cells, cellsize)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)
        speed_count = speed_count +1

if __name__ == "__main__":
    fish = 10
    bear = 3
    main(40, 10, 16,fish,bear)