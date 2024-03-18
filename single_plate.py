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
    sorted_rects = sort_rectangles(rectangles)
    occupied = [[False] * bin_height for _ in range(bin_width)]
    optimization_steps = []  # To record optimization steps

    for rect in sorted_rects:
        for _ in range(rect.max_count):
            placement = find_placement_for(rect, rect.placements, bin_width, bin_height, occupied)
            if placement:
                x, y = placement
                rect.placements.append((x, y))
                for xi in range(x, x + rect.width):
                    for yi in range(y, y + rect.height):
                        occupied[xi][yi] = True
                # Record the current step
                occupied_count = sum(sum(row) for row in occupied)
                empty_count = bin_width * bin_height - occupied_count
                optimization_steps.append({'step': len(optimization_steps)+1, 'empty_area': empty_count})
    return optimization_steps


def plot_layout(rectangles, bin_width, bin_height, title='Final Layout'):
    fig, ax = plt.subplots(figsize=(8, 8))
    # 绘制大容器
    ax.add_patch(patches.Rectangle((0, 0), bin_width, bin_height, edgecolor='r', facecolor='none'))

    # 遍历每个矩形并绘制
    for rect in rectangles:
        for x, y in rect.placements:
            ax.add_patch(
                patches.Rectangle((x, y), rect.width, rect.height, edgecolor='black', facecolor='skyblue', alpha=0.6,
                                  label=f"ID: {rect.id}"))
            # 在矩形中央显示 ID
            plt.text(x + rect.width / 2, y + rect.height / 2, str(rect.id), ha="center", va="center", color='black')

    plt.xlim(0, bin_width)
    plt.ylim(0, bin_height)
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


# Define rectangles with constraints
rectangles = [
    Rectangle(1, 30, 40, 20),
    Rectangle(2, 40, 70, 10),
    Rectangle(3, 20, 20, 15),
    Rectangle(4, 15, 10, 15),
    Rectangle(5, 10, 50, 15),
]

bin_width = 100
bin_height = 120
optimization_steps = optimize_layout(rectangles, bin_width, bin_height)

# Display optimization steps and empty areas
for step in optimization_steps:
    print(f"Step {step['step']}: Empty Area = {step['empty_area']}")

# Optional: Plot the optimization process (empty area over steps)
plt.figure(figsize=(8, 4))
plt.plot([step['step'] for step in optimization_steps], [step['empty_area'] for step in optimization_steps], marker='o')
plt.xlabel('Optimization Step')
plt.ylabel('Empty Area')
plt.title('Optimization Process - Empty Area Over Steps')
plt.grid(True)
plt.show()

plot_layout(rectangles, bin_width, bin_height)
