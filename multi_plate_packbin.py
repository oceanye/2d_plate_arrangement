import random
from pulp import LpVariable, LpProblem, LpMaximize, LpBinary

class Rectangle:
    def __init__(self, id, width, height, max_count):
        self.id = id
        self.width = width
        self.height = height
        self.max_count = max_count

# Function to generate random rectangles
def generate_random_rectangles(num_types, total_count, width_range=(200, 500), height_range=(5000, 8000), count_range=(2, 20)):
    rectangles = []
    for i in range(1, num_types + 1):
        width = random.randint(width_range[0], width_range[1])
        height = random.randint(height_range[0], height_range[1])
        max_count = random.randint(count_range[0], count_range[1])
        total_count_for_type = total_count // num_types
        rectangles.append(Rectangle(i, width, height, total_count_for_type))
        print(f"Type {i}: width = {width}, height = {height}, count = {total_count_for_type}")
    return rectangles

# Define rectangles and container dimensions
rectangles = generate_random_rectangles(10, 50)  # Adjust as needed
bin_width = 100
bin_height = 100

# Create a MILP problem
problem = LpProblem("BinPackingProblem", LpMaximize)

# Define decision variables: x[i][j] represents whether rectangle i is placed in bin j
x = {}
for rect in rectangles:
    for j in range(len(rectangles)):
        x[(rect.id, j)] = LpVariable(f"x_{rect.id}_{j}", 0, 1, LpBinary)

# Define decision variables for positions (upper-left corner of each rectangle within bins)
pos_x = {}
pos_y = {}
for rect in rectangles:
    for j in range(len(rectangles)):
        pos_x[(rect.id, j)] = LpVariable(f"pos_x_{rect.id}_{j}", 0, bin_width - rect.width)
        pos_y[(rect.id, j)] = LpVariable(f"pos_y_{rect.id}_{j}", 0, bin_height - rect.height)

# Define the objective function: maximize the number of placed rectangles
problem += sum(x[(rect.id, j)] for rect in rectangles for j in range(len(rectangles)))

# Add constraints: Each rectangle can be placed at most once and the total area of rectangles in a bin cannot exceed the bin's area.
for j in range(len(rectangles)):
    problem += sum(x[(rect.id, j)] for rect in rectangles) <= 1  # Each rectangle can be placed at most once

for i in range(len(rectangles)):
    problem += sum(rect.width * rect.height * x[(rect.id, j)] for rect in rectangles for j in range(len(rectangles))) <= bin_width * bin_height  # Total area constraint

# Add constraints to ensure proper arrangement within bins
for rect in rectangles:
    for j in range(len(rectangles)):
        problem += pos_x[(rect.id, j)] + rect.width <= bin_width * x[(rect.id, j)]  # Rectangle within bin width
        problem += pos_y[(rect.id, j)] + rect.height <= bin_height * x[(rect.id, j)]  # Rectangle within bin height

# Solve the MILP problem
problem.solve()

# Extract and process the placement results
placement_result = [[] for _ in range(len(rectangles))]
for var in problem.variables():
    if var.varValue == 1:
        rect_id, bin_id = var.name.split("_")[1:]
        placement_result[int(rect_id) - 1].append(int(bin_id))

# Process the placement_result as needed
for i, bins in enumerate(placement_result):
    if bins:
        print(f"Rectangle {i + 1} is placed in bins {', '.join(map(str, bins))}")
    else:
        print(f"Rectangle {i + 1} is not placed in any bin")
