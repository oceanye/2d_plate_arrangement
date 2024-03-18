from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class Rectangle:
    def __init__(self, id, width, height, max_count):
        self.id = id
        self.width = width
        self.height = height
        self.max_count = max_count
        self.placements = []  # Store placements (x, y)

class ORToolsRectanglePacker:
    def __init__(self, bin_width, bin_height, rectangles):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.rectangles = rectangles
        self.model = cp_model.CpModel()

    def pack(self):
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 300  # Time limit

        for rect in self.rectangles:
            for i in range(rect.max_count):
                x_var = self.model.NewIntVar(0, self.bin_width - 1, f'x_{rect.id}_{i}')
                y_var = self.model.NewIntVar(0, self.bin_height - 1, f'y_{rect.id}_{i}')

                # Ensure the rectangle fits within the bin
                self.model.Add(x_var + rect.width <= self.bin_width)
                self.model.Add(y_var + rect.height <= self.bin_height)

                rect.placements.append((x_var, y_var))

        # Add non-overlapping constraints
        self.add_non_overlap_constraints()

        # Solve the model
        status = solver.Solve(self.model)
        return solver  # Return the solver instance after solving

    def add_non_overlap_constraints(self):
        for i, rect1 in enumerate(self.rectangles):
            for j in range(rect1.max_count):
                x1, y1 = rect1.placements[j]

                for k, rect2 in enumerate(self.rectangles):
                    if k <= i:  # Avoid duplicate and self-comparison constraints
                        continue
                    for l in range(rect2.max_count):
                        x2, y2 = rect2.placements[l]

                        # Add non-overlapping constraints
                        overlap_var = self.model.NewBoolVar(f'overlap_{rect1.id}_{i}_{rect2.id}_{l}')
                        self.model.Add(x1 + rect1.width <= x2).OnlyEnforceIf([overlap_var.Not()])
                        self.model.Add(x2 + rect2.width <= x1).OnlyEnforceIf([overlap_var.Not()])
                        self.model.Add(y1 + rect1.height <= y2).OnlyEnforceIf([overlap_var.Not()])
                        self.model.Add(y2 + rect2.height <= y1).OnlyEnforceIf([overlap_var.Not()])


def plot_layout(rectangles, bin_width, bin_height, solver, title='Final Layout', save_path='final_layout.jpg'):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.add_patch(patches.Rectangle((0, 0), bin_width, bin_height, edgecolor='r', facecolor='none'))

    for rect in rectangles:
        for x_var, y_var in rect.placements:
            x_val = solver.Value(x_var)
            y_val = solver.Value(y_var)

            ax.add_patch(patches.Rectangle((x_val, y_val), rect.width, rect.height, edgecolor='black', facecolor='skyblue', alpha=0.6))
            plt.text(x_val + rect.width / 2, y_val + rect.height / 2, f'{rect.id}', ha="center", va="center", color='black')

    plt.xlim(0, bin_width)
    plt.ylim(0, bin_height)
    plt.title(title)
    plt.axis('off')
    plt.savefig(save_path, format='jpg', dpi=300, bbox_inches='tight')
    plt.show()

    # Print the detailed arranged rectangles with their corner coordinates
    for rect in rectangles:
        for x_var, y_var in rect.placements:
            x_val = solver.Value(x_var)
            y_val = solver.Value(y_var)

            print(f'{rect.id}: ({x_val}, {y_val}), ({x_val + rect.width}, {y_val}), '
                  f'({x_val + rect.width}, {y_val + rect.height}), ({x_val}, {y_val + rect.height})')

# Example usage
rectangles = [
    Rectangle(1, 40, 400, 10),
    Rectangle(2, 20, 700, 10),
    Rectangle(3, 20, 200, 10),
    Rectangle(4, 15, 500, 10),
    Rectangle(5, 10, 500, 10),
]

bin_width = 400
bin_height = 1200

packer = ORToolsRectanglePacker(bin_width, bin_height, rectangles)
solver = packer.pack()

# Plot the final layout and record the corner of every rectangle
plot_layout(rectangles, bin_width, bin_height, solver)
