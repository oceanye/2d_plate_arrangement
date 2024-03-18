import random

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

#完成多尺寸排布，每个board的利用率最高，但是当数值变大，到1000的数量级时，报错

class Rectangle:
    def __init__(self, id, width, height, max_count):
        self.id = id
        self.width = width
        self.height = height
        self.max_count = max_count
        self.placements = []

def sort_rectangles(rectangles):
    return sorted(rectangles, key=lambda x: x.width * x.height, reverse=True)

def find_placement_for_0(rect, placements, bin_width, bin_height, occupied):
    for x in range(bin_width - rect.width + 1):
        for y in range(bin_height - rect.height + 1):
            if all(not occupied[xi][yi] for xi in range(x, x + rect.width) for yi in range(y, y + rect.height)):
                return x, y
    return None

def optimize_layout_0(rectangles, bin_width, bin_height):
    boards = []
    while any(rect.max_count > 0 for rect in rectangles):
        sorted_rects = sort_rectangles([r for r in rectangles if r.max_count > 0])
        occupied = [[False] * bin_height for _ in range(bin_width)]
        board = []

        for rect in sorted_rects:
            while rect.max_count > 0:
                placement = find_placement_for(rect, rect.placements, bin_width, bin_height, occupied)
                if placement:
                    x, y = placement
                    board.append((rect.id, x, y, rect.width, rect.height))
                    rect.max_count -= 1
                    for xi in range(x, x + rect.width):
                        for yi in range(y, y + rect.height):
                            occupied[xi][yi] = True
                else:
                    break
        boards.append(board)
    return boards

def find_placement_for(rect, bin_width, bin_height, occupied, allow_rotation=True):
    # Try placing the rectangle without rotation
    for orientation in [(rect.width, rect.height), (rect.height, rect.width)] if allow_rotation else [(rect.width, rect.height)]:
        width, height = orientation
        for x in range(bin_width - width + 1):
            for y in range(bin_height - height + 1):
                if all(not occupied[xi][yi] for xi in range(x, x + width) for yi in range(y, y + height)):
                    return x, y, width, height
    return None, None, None, None

def optimize_layout0(rectangles, bin_width, bin_height):
    boards = []
    while any(rect.max_count > 0 for rect in rectangles):
        sorted_rects = sort_rectangles([r for r in rectangles if r.max_count > 0])
        occupied = [[False] * bin_height for _ in range(bin_width)]
        board = []

        for rect in sorted_rects:
            while rect.max_count > 0:
                x, y, placed_width, placed_height = find_placement_for(rect, bin_width, bin_height, occupied)
                if x is not None:
                    board.append((rect.id, x, y, placed_width, placed_height))
                    rect.max_count -= 1
                    for xi in range(x, x + placed_width):
                        for yi in range(y, y + placed_height):
                            occupied[xi][yi] = True
                else:
                    break
        boards.append(board)
    return boards

def plot_all_boards_layout0(boards, bin_width, bin_height, filename="all_boards_layout.jpg"):
    fig, axs = plt.subplots(1, len(boards), figsize=(len(boards) * 5, 5))
    if len(boards) == 1:
        axs = [axs]
    for i, board in enumerate(boards):
        ax = axs[i]
        ax.set_xlim(0, bin_width)
        ax.set_ylim(0, bin_height)
        ax.set_title(f'Board {i+1}')
        for id, x, y, width, height in board:
            ax.add_patch(patches.Rectangle((x, y), width, height, edgecolor='black', facecolor='skyblue', alpha=0.6))
            ax.text(x + width / 2, y + height / 2, str(id), ha="center", va="center", color='black')
        ax.set_aspect('equal')
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


def optimize_layout(rectangles, bin_width, bin_height, initial_temp=100, cooling_rate=0.95, iterations=1000):
    current_layout = [
        [rect.id, random.randint(0, bin_width - rect.width), random.randint(0, bin_height - rect.height), rect.width,
         rect.height] for rect in rectangles]
    current_fitness = len(current_layout)
    best_layout = current_layout
    best_fitness = current_fitness

    temp = initial_temp
    for i in range(iterations):
        rectangle_index = random.randint(0, len(current_layout) - 1)
        new_layout = current_layout.copy()
        new_layout[rectangle_index] = [current_layout[rectangle_index][0],
                                       random.randint(0, bin_width - current_layout[rectangle_index][3]),
                                       random.randint(0, bin_height - current_layout[rectangle_index][4]),
                                       current_layout[rectangle_index][3], current_layout[rectangle_index][4]]

        occupied = [[any((p[1] <= x < p[1] + p[3]) and (p[2] <= y < p[2] + p[4]) for p in new_layout) for y in
                     range(bin_height)] for x in range(bin_width)]
        if not any(occupied[new_layout[rectangle_index][1]][new_layout[rectangle_index][2]]):
            new_fitness = len(new_layout)
            if new_fitness < current_fitness or math.exp((current_fitness - new_fitness) / temp) > random.random():
                current_layout = new_layout
                current_fitness = new_fitness

            if current_fitness < best_fitness:
                best_layout = current_layout
                best_fitness = current_fitness

        temp *= cooling_rate

    boards = []
    for placement in best_layout:
        rect_id, x, y, width, height = placement
        rect = next((r for r in rectangles if r.id == rect_id), None)
        if rect:
            rect.max_count -= 1
            if rect.max_count == 0:
                rectangles.remove(rect)
            boards.append({'placements': [(rect_id, x, y, width, height)], 'types': {rect_id: 1},
                           'vacancy_rate': (bin_width * bin_height - width * height) / (bin_width * bin_height) * 100})

    return boards

def plot_all_boards_layout(boards, bin_width, bin_height, filename="all_boards_layout.jpg"):
    fig, axs = plt.subplots(1, len(boards), figsize=(len(boards) * 5, 5), constrained_layout=True)
    if len(boards) == 1:
        axs = [axs]
    for i, board in enumerate(boards):
        ax = axs[i]
        ax.set_xlim(0, bin_width)
        ax.set_ylim(0, bin_height)
        ax.set_title(f'Board {i+1}')
        for id, x, y, width, height in board['placements']:
            ax.add_patch(patches.Rectangle((x, y), width, height, edgecolor='black', facecolor='skyblue', alpha=0.6))
            ax.text(x + width / 2, y + height / 2, str(id), ha="center", va="center", color='black')
        ax.set_aspect('equal')
        # Annotation for vacancy rate and count of rectangles
        ax.annotate(f"Vacancy Rate: {board['vacancy_rate']:.2f}%\n" +
                    "\n".join([f"Type {k}: {v}" for k, v in board['types'].items()]),
                    xy=(1, 0.2), xycoords='axes fraction', xytext=(5, -5), textcoords='offset points',
                    ha='right', va='top', fontsize=9)

    plt.savefig(filename)
    plt.show()

    # Print information for each board
    for i, board in enumerate(boards):
        print(f"Board {i+1}: Vacancy Rate = {board['vacancy_rate']:.2f}%, Types = {board['types']}")


# Function to export boards' results as a matrix
def export_boards_as_matrix(boards, rectangles):
    num_boards = len(boards)
    num_rectangles = len(rectangles)

    # Initialize an empty matrix with zeros
    result_matrix = np.zeros((num_boards, num_rectangles), dtype=int)

    for i, board in enumerate(boards):
        for j, rect in enumerate(rectangles):
            result_matrix[i][j] = board['types'].get(rect.id, 0)

    return result_matrix

def generate_random_rectangles0(num_types, width_range=(20, 50), height_range=(50, 80), count_range=(2, 20)):
    rectangles = []
    for i in range(1, num_types + 1):
        width = random.randint(width_range[0], width_range[1])*10
        height = random.randint(height_range[0], height_range[1])*100
        max_count = random.randint(count_range[0], count_range[1])
        rectangles.append(Rectangle(i, width, height, max_count))
    return rectangles



def generate_random_rectangles(num_types, total_count, width_range=(200, 500), height_range=(5000, 8000), count_range=(2, 20)):
    rectangles = []
    for i in range(1, num_types + 1):
        #width is round(random.randint(width_range[0], width_range[1])/50)*50


        width = round(random.randint(width_range[0], width_range[1])/50)
        height = round(random.randint(height_range[0], height_range[1])/100)
        max_count = random.randint(count_range[0], count_range[1])
        total_count_for_type = total_count // num_types
        rectangles.append(Rectangle(i, width, height, total_count_for_type))
        print(f"Type {i}: width = {width}, height = {height}, count = {total_count_for_type}")
    return rectangles


def generate_neighbor_solution(solution, rectangles, bin_width, bin_height):
    new_solution = solution.copy()
    board_index = random.randint(0, len(new_solution) - 1)
    board = new_solution[board_index]

    operation = random.choice(['swap', 'move'])
    if operation == 'swap':
        if len(board['placements']) >= 2:
            rect1_index, rect2_index = random.sample(range(len(board['placements'])), 2)
            board['placements'][rect1_index], board['placements'][rect2_index] = board['placements'][rect2_index], \
            board['placements'][rect1_index]
    elif operation == 'move':
        if len(board['placements']) >= 1:
            rect_index = random.randint(0, len(board['placements']) - 1)
            rect_id, _, _, _, _ = board['placements'].pop(rect_index)
            rect = next((r for r in rectangles if r.id == rect_id), None)
            if rect:
                occupied = [
                    [any((p[1] <= x < p[1] + p[3]) and (p[2] <= y < p[2] + p[4]) for p in board['placements']) for y in
                     range(bin_height)] for x in range(bin_width)]
                placement = find_placement_for(rect, bin_width, bin_height, occupied)
                if placement:
                    x, y, placed_width, placed_height = placement
                    board['placements'].append((rect.id, x, y, placed_width, placed_height))

    return new_solution


def simulated_annealing(rectangles, bin_width, bin_height, initial_temp=100, cooling_rate=0.95, iterations=1000):
    current_solution = optimize_layout(rectangles, bin_width, bin_height)
    current_cost = len(current_solution)
    best_solution = current_solution
    best_cost = current_cost

    temp = initial_temp
    for i in range(iterations):
        new_solution = generate_neighbor_solution(current_solution, rectangles, bin_width, bin_height)
        new_cost = len(new_solution)
        cost_diff = new_cost - current_cost

        if cost_diff < 0 or math.exp(-cost_diff / temp) > random.random():
            current_solution = new_solution
            current_cost = new_cost

        if current_cost < best_cost:
            best_solution = current_solution
            best_cost = current_cost

        temp *= cooling_rate

    return best_solution


# Define rectangles and board dimensions
rectangles0 = [
    Rectangle(1, 30, 43, 20),
    Rectangle(2, 22, 70, 10),
    Rectangle(3, 20, 20, 15),
    Rectangle(4, 15, 50, 15),
    Rectangle(6, 25, 35, 15),
    Rectangle(7, 10, 40, 15),
    Rectangle(8, 20, 30, 5),

    Rectangle(9, 30, 40, 20),
    Rectangle(10, 20, 70, 10),


]

rectangles = generate_random_rectangles(10,50)

bin_width = 80
bin_height = 120

# Optimize the layout and get the boards
#boards = optimize_layout(rectangles, bin_width, bin_height)
#boards = simulated_annealing(rectangles, bin_width, bin_height)


boards = optimize_layout(rectangles, bin_width, bin_height)

# Export the boards' results as a matrix
result_matrix = export_boards_as_matrix(boards, rectangles)
print(result_matrix)


# Plot and save all boards' layouts in a single image
plot_all_boards_layout(boards, bin_width, bin_height)
