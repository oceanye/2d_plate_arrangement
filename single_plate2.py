from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches

#use or-tools, 但是 规模到1000+依然会有问题
#只能处理垂直拍不的情况，不能适应横着摆放的情况

def plot_layout(rectangles, bin_width, bin_height, title='Final Layout', save_path='final_layout.jpg'):
    fig, ax = plt.subplots(figsize=(10, 8))  # Adjusted for additional text space
    bin_area = bin_width * bin_height
    occupied_area = 0
    board_types = set()

    ax.add_patch(patches.Rectangle((0, 0), bin_width, bin_height, edgecolor='r', facecolor='none'))

    for rect in rectangles:
        for x, y in rect.placements:
            ax.add_patch(
                patches.Rectangle((x, y), rect.width, rect.height, edgecolor='black', facecolor='skyblue', alpha=0.6))
            plt.text(x + rect.width / 2, y + rect.height / 2, str(rect.id), ha="center", va="center", color='black')
            occupied_area += rect.width * rect.height
            board_types.add(rect.id)

    vacant_area = bin_area - occupied_area
    vacant_ratio = vacant_area / bin_area * 100
    board_types_str = ', '.join([str(bt) for bt in sorted(board_types)])

    # Annotations for vacant ratio and board types
    plt.text(bin_width + 10, bin_height / 2, f"Vacant Ratio: {vacant_ratio:.2f}%\nBoard Types: {board_types_str}",
             verticalalignment='center', fontsize=12)

    plt.xlim(0, bin_width + 20)  # Adjusted to accommodate text
    plt.ylim(0, bin_height)
    plt.title(title)
    plt.gca().set_aspect('equal', adjustable='box')

    # Turn off axis visibility to clean up the appearance
    plt.axis('off')

    # Save the figure
    plt.savefig(save_path, format='jpg', dpi=300, bbox_inches='tight')

    # Close the plot figure to free memory
    plt.close(fig)


class Rectangle:
    def __init__(self, id, width, height, max_count):
        self.id = id
        self.width = width
        self.height = height
        self.max_count = max_count
        self.placements = []

class ORToolsRectanglePacker:
    def __init__(self, bin_width, bin_height, rectangles):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.rectangles = rectangles
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = []
        self.optimization_steps = []  # To store detailed procedure information

    def pack(self):
        for rect in self.rectangles:
            for i in range(rect.max_count):
                # Decision variables for position
                x_var = self.model.NewIntVar(0, self.bin_width, f'x_{rect.id}_{i}')
                y_var = self.model.NewIntVar(0, self.bin_height, f'y_{rect.id}_{i}')
                # Decision variable for rotation (0: no rotation, 1: rotated 90 degrees)
                rot_var = self.model.NewBoolVar(f'rot_{rect.id}_{i}')
                # Adjust width and height based on rotation
                width = rect.width if rot_var == 0 else rect.height
                height = rect.height if rot_var == 0 else rect.width
                # Ensure the rectangle fits within the bin dimensions, considering rotation
                self.model.Add(x_var + width <= self.bin_width)
                self.model.Add(y_var + height <= self.bin_height)
                self.variables.append((rect, x_var, y_var, rot_var))

        # Constraint to prevent overlap
        for i in range(len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                rect1, x1, y1, _ = self.variables[i]
                rect2, x2, y2, _ = self.variables[j]

                left = self.model.NewBoolVar(f'left_{i}_{j}')
                right = self.model.NewBoolVar(f'right_{i}_{j}')
                above = self.model.NewBoolVar(f'above_{i}_{j}')
                below = self.model.NewBoolVar(f'below_{i}_{j}')

                self.model.Add(x1 + rect1.width <= x2).OnlyEnforceIf(left)
                self.model.Add(x2 + rect2.width <= x1).OnlyEnforceIf(right)
                self.model.Add(y1 + rect1.height <= y2).OnlyEnforceIf(above)
                self.model.Add(y2 + rect2.height <= y1).OnlyEnforceIf(below)

                self.model.AddBoolOr([left, right, above, below])
        # Set a time limit for the solver
        self.solver.parameters.max_time_in_seconds = 120  # 5 minutes

        # Solve the model
        status = self.solver.Solve(self.model)
        
        if status == cp_model.FEASIBLE:
            print("Feasible solution found.")
        elif status == cp_model.OPTIMAL:
            print("Optimal solution found.")
        else:
            print("No solution found within the time limit.")
            
        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for rect, x_var, y_var, i in self.variables:
                x = self.solver.Value(x_var)
                y = self.solver.Value(y_var)
                rect.placements.append((x, y))
                self.optimization_steps.append(f"Rectangle {rect.id} Instance {i}: Placed at ({x}, {y})")
        else:
            print("No solution found.")
        return status  # Return the solving status

    def log_optimization_steps(self):
        # Log the detailed procedure information
        for step in self.optimization_steps:
            print(step)

# Define your rectangles and initialize the packer
rectangles = [
    Rectangle(1, 30, 405, 10),
    Rectangle(2, 20, 708, 10),
    Rectangle(3, 20, 208, 10),
    Rectangle(4, 15, 505, 10),
    Rectangle(5, 10, 550, 10),
]

bin_width = 400
bin_height = 1200

packer = ORToolsRectanglePacker(bin_width, bin_height, rectangles)
status = packer.pack()

# Plot the final layout and log optimization steps
plot_layout(rectangles, bin_width, bin_height)

if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    packer.log_optimization_steps()
else:
    print("Failed to find a feasible solution.")
