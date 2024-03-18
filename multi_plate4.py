import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pulp import LpVariable, LpProblem, LpMinimize, lpSum

import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pulp import LpVariable, LpProblem, LpMinimize, lpSum
import numpy as np


# Define the Rectangle class
class Rectangle:
    def __init__(self, id, width, height, total_count):
        self.id = id
        self.width = width
        self.height = height
        self.total_count = total_count
        self.placements = []


# Define the plot_total_layout function
def plot_total_layout(boards, bin_width, bin_height):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.add_patch(patches.Rectangle((0, 0), bin_width, bin_height, edgecolor='r', facecolor='none'))

    for board in boards:
        for rect_id, x, y, width, height in board['placements']:
            ax.add_patch(
                patches.Rectangle((x, y), width, height, edgecolor='black', facecolor='skyblue', alpha=0.6,
                                  label=f"ID: {rect_id}"))
            plt.text(x + width / 2, y + height / 2, str(rect_id), ha="center", va="center", color='black')

    plt.xlim(0, bin_width)
    plt.ylim(0, bin_height)
    plt.title('Total Layout')
    plt.gca().set_aspect('equal', adjustable='box')

    # Save the arrangement plot as JPG
    plt.savefig('arrangement_plot.jpg', dpi=300, bbox_inches='tight')

    # Display the plot
    plt.show()


# Define the matrix_shape_result function to display the result in matrix shape
def matrix_shape_result(boards, bin_width, bin_height):
    matrix = np.zeros((bin_height, bin_width), dtype=int)

    for board in boards:
        for rect_id, x, y, width, height in board['placements']:
            matrix[y:y + height, x:x + width] = rect_id

    plt.figure(figsize=(10, 10))
    plt.imshow(matrix, cmap='tab20', vmin=0, vmax=len(boards))
    plt.colorbar(label='Rectangle ID')
    plt.title('Matrix Shape Result')
    plt.axis('off')
    plt.show()

# Define the MIP-based rectangle packing function
def pack_rectangles(rectangles, bin_width, bin_height):
    prob = LpProblem("RectanglePacking", LpMinimize)

    placements = []
    for rect in rectangles:
        for i in range(rect.total_count):
            placement = LpVariable(f"Placement_{rect.id}_{i}", 0, bin_width, cat='Integer')
            prob += placement + rect.width <= bin_width
            prob += placement >= 0
            placements.append((rect.id, placement))

    prob += 0  # Objective function (not relevant for feasibility)

    # Constraint: No overlapping
    for i in range(len(placements)):
        for j in range(i + 1, len(placements)):
            rect1_id, placement1 = placements[i]
            rect2_id, placement2 = placements[j]
            rect1 = next(r for r in rectangles if r.id == rect1_id)
            rect2 = next(r for r in rectangles if r.id == rect2_id)
            prob += (
                    placement1 + rect1.width <= placement2
                    or placement2 + rect2.width <= placement1
            )

    prob.solve()

    boards = []
    for rect in rectangles:
        rect.placements.clear()

    for rect_id, placement in placements:
        rect = next(r for r in rectangles if r.id == rect_id)
        x = int(placement.varValue)
        y = bin_height - int(rect.height)
        width = int(rect.width)
        height = int(rect.height)
        rect.placements.append((x, y, width, height))

    for i in range(len(rectangles)):
        rect = rectangles[i]
        for (x, y, width, height) in rect.placements:
            boards.append({'placements': [(rect.id, x, y, width, height)]})

    return boards


# Define the generate_random_rectangles function
def generate_random_rectangles(num_types, total_count):
    rectangles = []
    for i in range(1, num_types + 1):
        width = round(random.randint(200, 500) / 50) * 50
        height = random.randint(5000, 8000)
        count = total_count // num_types
        rectangles.append(Rectangle(i, width, height, count))
    return rectangles


# Example usage
num_types = 5  # Number of rectangle types
total_count = 50  # Total count for every type
rectangles = generate_random_rectangles(num_types, total_count)
bin_width = 4000
bin_height = 12000

# Run the rectangle packing algorithm
boards = pack_rectangles(rectangles, bin_width, bin_height)

# Plot the total layout
plot_total_layout(boards, bin_width, bin_height)

# Display the matrix shape result
#matrix_shape_result(boards, bin_width, bin_height)
# print the matrix_shape_result
print(matrix_shape_result(boards, bin_width, bin_height))
