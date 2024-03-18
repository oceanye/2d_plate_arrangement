import matplotlib.pyplot as plt
import matplotlib.patches as patches

class Rectangle:
    def __init__(self, id, width, height, max_count):
        self.id = id
        self.width = width
        self.height = height
        self.max_count = max_count
        self.placements = []

def sort_rectangles(rectangles):
    return sorted(rectangles, key=lambda x: x.width * x.height, reverse=True)

def find_placement_for(rect, placements, bin_width, bin_height, occupied):
    for x in range(bin_width - rect.width + 1):
        for y in range(bin_height - rect.height + 1):
            if all(not occupied[xi][yi] for xi in range(x, x + rect.width) for yi in range(y, y + rect.height)):
                return x, y
    return None

def optimize_layout(rectangles, bin_width, bin_height):
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

def plot_all_boards_layout(boards, bin_width, bin_height, filename="all_boards_layout.jpg"):
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

# Define rectangles and board dimensions
rectangles = [
    Rectangle(1, 30, 40, 20),
    Rectangle(2, 20, 70, 10),
    Rectangle(3, 20, 20, 15),
    Rectangle(4, 15, 50, 15),
    Rectangle(6, 25, 35, 15),
    Rectangle(7, 10, 40, 15),

]

bin_width = 100
bin_height = 100

# Optimize the layout and get the boards
boards = optimize_layout(rectangles, bin_width, bin_height)

# Plot and save all boards' layouts in a single image
plot_all_boards_layout(boards, bin_width, bin_height)
