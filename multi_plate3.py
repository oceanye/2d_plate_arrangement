import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class Rectangle:
    def __init__(self, id, width, height, total_count):
        self.id = id
        self.width = width
        self.height = height
        self.total_count = total_count
        self.placements = []

def generate_random_rectangles(num_types, total_count, width_range=(200, 500), height_range=(3000, 8000)):
    rectangles = []
    for i in range(1, num_types + 1):
        width = round(random.randint(width_range[0], width_range[1])/50)*50
        height = random.randint(height_range[0], height_range[1])
        total_count_for_type = total_count // num_types
        rectangles.append(Rectangle(i, width, height, total_count_for_type))
        # print details
        print(f"Type {i}: width = {width}, height = {height}, count = {total_count_for_type}")
    return rectangles


def optimize_layout(rectangles, bin_width, bin_height, occupied_grid):
    total_area = bin_width * bin_height
    boards = []
    while any(rect.total_count > 0 for rect in rectangles):
        sorted_rects = sort_rectangles([r for r in rectangles if r.total_count > 0])
        board = {'placements': [], 'types': {}, 'vacancy_rate': 0}
        used_area = 0

        placed = False  # Flag to track if any rectangle was placed in this iteration

        for rect in sorted_rects:
            while rect.total_count > 0:
                x, y, placed_width, placed_height = find_placement_for(rect, bin_width, bin_height, occupied_grid)
                if x is not None:
                    board['placements'].append((rect.id, x, y, placed_width, placed_height))
                    rect.total_count -= 1
                    used_area += placed_width * placed_height
                    board['types'][rect.id] = board['types'].get(rect.id, 0) + 1
                    occupied_grid.mark_occupied(x, y, placed_width, placed_height)

                    # Debug: Print placement details
                    print(f"Placed Rectangle {rect.id} at ({x}, {y}) with dimensions ({placed_width}, {placed_height})")
                    print(f"Remaining count for Rectangle {rect.id}: {rect.total_count}")

                    placed = True  # Set the flag to indicate placement
                else:
                    break  # No more rectangles of this type can be placed
            if not placed:
                break  # No more rectangles of any type can be placed

        # Check if no rectangles were placed in this iteration
        if not placed:
            break  # Break out of the loop if no rectangles can be placed

        board['vacancy_rate'] = (1 - used_area / total_area) * 100
        boards.append(board)

        # Debug: Print board information after each iteration
        print(f"Vacancy Rate after iteration: {board['vacancy_rate']:.2f}%")
    return boards


class QuadTree:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.children = [None, None, None, None]  # NW, NE, SW, SE
        self.occupied = False

    def split(self):
        half_width = self.width // 2
        half_height = self.height // 2
        self.children[0] = QuadTree(self.x, self.y, half_width, half_height)  # NW
        self.children[1] = QuadTree(self.x + half_width, self.y, half_width, half_height)  # NE
        self.children[2] = QuadTree(self.x, self.y + half_height, half_width, half_height)  # SW
        self.children[3] = QuadTree(self.x + half_width, self.y + half_height, half_width, half_height)  # SE

    def insert(self, x, y, x2, y2):
        if x >= self.x and x2 <= self.x + self.width and y >= self.y and y2 <= self.y + self.height:
            if self.occupied:
                return
            if self.width == 1 and self.height == 1:
                self.occupied = True
            else:
                if not any(self.children):
                    self.split()
                for child in self.children:
                    child.insert(x, y, x2, y2)

    def query(self, width, height):
        if self.occupied:
            return [(self.x, self.y)]
        if width > self.width or height > self.height:
            return []
        if width <= self.width and height <= self.height and all(self.children):
            return [(self.x, self.y)]
        positions = []
        for child in self.children:
            if child:
                positions.extend(child.query(width, height))
        return positions



class OccupancyGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[False] * height for _ in range(width)]

    def is_occupied(self, x, y, width, height):
        for i in range(x, x + width):
            for j in range(y, y + height):
                if self.grid[i][j]:
                    return True
        return False

    def mark_occupied(self, x, y, width, height):
        for i in range(x, x + width):
            for j in range(y, y + height):
                self.grid[i][j] = True

# Update find_placement_for function
def find_placement_for(rect, bin_width, bin_height, occupied_grid, allow_rotation=True):
    for orientation in [(rect.width, rect.height), (rect.height, rect.width)] if allow_rotation else [(rect.width, rect.height)]:
        width, height = orientation
        for x in range(bin_width - width + 1):
            for y in range(bin_height - height + 1):
                if not occupied_grid.is_occupied(x, y, width, height):
                    return x, y, width, height
    return None, None, None, None


def sort_rectangles(rectangles):
    return sorted(rectangles, key=lambda x: x.width * x.height, reverse=True)

def plot_layout(rectangles, bin_width, bin_height, title='Final Layout'):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.add_patch(patches.Rectangle((0, 0), bin_width, bin_height, edgecolor='r', facecolor='none'))

    for rect in rectangles:
        for x, y, width, height in rect.placements:
            ax.add_patch(
                patches.Rectangle((x, y), width, height, edgecolor='black', facecolor='skyblue', alpha=0.6,
                                  label=f"ID: {rect.id}"))
            plt.text(x + width / 2, y + height / 2, str(rect.id), ha="center", va="center", color='black')

    plt.xlim(0, bin_width)
    plt.ylim(0, bin_height)
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

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
    plt.show()


def generate_arrangement_matrix(boards, num_types):
    arrangement_matrix = np.zeros((len(boards), num_types), dtype=int)

    for i, board in enumerate(boards):
        for rect_id, count in board['types'].items():
            arrangement_matrix[i][rect_id - 1] = count  # Subtract 1 to account for 0-based indexing

    return arrangement_matrix

# Example usage:
num_types = 15  # Number of rectangle types
total_count = 30  # Total count for every type
rectangles = generate_random_rectangles(num_types, total_count)
bin_width = 4000
bin_height = 12000

# Initialize the 'occupied' matrix with True values
occupied = [[True] * bin_height for _ in range(bin_width)]
# Initialize the Quadtree with the root node as occupied
quadtree = QuadTree(0, 0, bin_width, bin_height)
quadtree.occupied = True

#boards = optimize_layout(rectangles, bin_width, bin_height, occupied, quadtree)


# Initialize the occupancy grid
occupancy_grid = OccupancyGrid(bin_width, bin_height)

# Run the optimization
boards = optimize_layout(rectangles, bin_width, bin_height, occupancy_grid)


for i, board in enumerate(boards):
    print(f"Board {i + 1}:")
    for type_id, count in board['types'].items():
        print(f"  Type {type_id}: {count} rectangles")
    print(f"  Vacancy Rate: {board['vacancy_rate']:.2f}%")

# Assuming you have already run the optimization and have 'boards' list
plot_total_layout(boards, bin_width, bin_height)

arrangement_matrix = generate_arrangement_matrix(boards, num_types)

# Print the arrangement matrix
print("Arrangement Matrix:")
print(arrangement_matrix)