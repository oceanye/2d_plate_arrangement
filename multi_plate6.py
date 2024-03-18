import random
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches



# 定义板材类
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.area = width * height

    def __repr__(self):
        return f"{self.width}x{self.height}"


# 定义排布方案类
class Solution:
    def __init__(self, rectangles, bin_width, bin_height):
        self.rectangles = rectangles
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.bins = []
        self.fitness = 0

    def place_rectangles(self):
        for rect in self.rectangles:
            placed = False
            for bin in self.bins:
                if bin.can_place(rect):
                    bin.place(rect)
                    placed = True
                    break
            if not placed:
                new_bin = Bin(self.bin_width, self.bin_height)
                new_bin.place(rect)
                self.bins.append(new_bin)
        self.fitness = sum(bin.used_area for bin in self.bins) / (len(self.bins) * self.bin_width * self.bin_height)

    def __repr__(self):
        return f"溶液 {id(self)}: 利用率 {self.fitness:.2%}, 使用 {len(self.bins)} 块板材"

    def plot(self):
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#%06x' % random.randint(0, 0xFFFFFF) for _ in range(len(self.rectangles))]
        for i, bin in enumerate(self.bins):
            for j, rect in enumerate(bin.free_rectangles):
                ax.add_patch(patches.Rectangle((i*self.bin_width, bin.height-rect.height), rect.width, rect.height, linewidth=1, edgecolor='black', facecolor='white'))
            used_height = 0
            for j, rect in enumerate(bin.rectangles):
                ax.add_patch(patches.Rectangle((i*self.bin_width, used_height), rect.width, rect.height, linewidth=1, edgecolor='black', facecolor=colors[j]))
                used_height += rect.height
        ax.set_xlim(0, len(self.bins)*self.bin_width)
        ax.set_ylim(0, self.bin_height)
        ax.set_aspect('equal')
        plt.xlabel('Width')
        plt.ylabel('Height')
        plt.title(f'2D Bin Packing Solution - Utilization: {self.fitness:.2%}')
        plt.show()


class Bin:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.used_area = 0
        self.free_rectangles = [Rectangle(width, height)]
        self.rectangles = []

    def can_place(self, rect):
        for free_rect in self.free_rectangles:
            if (free_rect.width >= rect.width and free_rect.height >= rect.height) or \
                    (free_rect.width >= rect.height and free_rect.height >= rect.width):
                return True
        return False

    def place(self, rect):
        best_rect = None
        best_fit = float('inf')
        for i, free_rect in enumerate(self.free_rectangles):
            if free_rect.width >= rect.width and free_rect.height >= rect.height:
                fit = free_rect.area - rect.area
                if fit < best_fit:
                    best_rect = free_rect
                    best_fit = fit
                    rotation = False
            if free_rect.width >= rect.height and free_rect.height >= rect.width:
                fit = free_rect.area - rect.area
                if fit < best_fit:
                    best_rect = free_rect
                    best_fit = fit
                    rotation = True

        if best_rect is None:
            return False

        self.used_area += rect.area
        if rotation:
            rect.width, rect.height = rect.height, rect.width
        self.rectangles.append(rect)

        if best_rect.width > rect.width:
            self.free_rectangles.append(Rectangle(best_rect.width - rect.width, rect.height))
        if best_rect.height > rect.height:
            self.free_rectangles.append(Rectangle(best_rect.width, best_rect.height - rect.height))
        self.free_rectangles.remove(best_rect)

        self.merge_free_rectangles()
        return True

    def merge_free_rectangles(self):
        for i in range(len(self.free_rectangles)):
            for j in range(i + 1, len(self.free_rectangles)):
                rect1 = self.free_rectangles[i]
                rect2 = self.free_rectangles[j]
                if rect1.width == rect2.width and rect1.height == rect2.height:
                    self.free_rectangles.remove(rect2)
                    return self.merge_free_rectangles()
                if rect1.width == rect2.width and rect1.height + rect2.height == self.height:
                    self.free_rectangles.remove(rect1)
                    self.free_rectangles.remove(rect2)
                    self.free_rectangles.append(Rectangle(rect1.width, self.height))
                    return self.merge_free_rectangles()
                if rect1.height == rect2.height and rect1.width + rect2.width == self.width:
                    self.free_rectangles.remove(rect1)
                    self.free_rectangles.remove(rect2)
                    self.free_rectangles.append(Rectangle(self.width, rect1.height))
                    return self.merge_free_rectangles()


def simulated_annealing(rectangles, bin_width, bin_height, temp=100, cooling_rate=0.98, iterations=10000):
    current_solution = Solution(rectangles, bin_width, bin_height)
    current_solution.place_rectangles()
    best_solution = current_solution

    for i in range(iterations):
        temp *= cooling_rate
        new_solution = Solution(rectangles, bin_width, bin_height)
        random.shuffle(new_solution.rectangles)
        for rect in new_solution.rectangles:
            if random.random() < 0.5:
                rect.width, rect.height = rect.height, rect.width

        # 新的邻域操作: 交换两个板材的位置
        if random.random() < 0.1:
            idx1, idx2 = random.sample(range(len(new_solution.rectangles)), 2)
            new_solution.rectangles[idx1], new_solution.rectangles[idx2] = new_solution.rectangles[idx2], \
            new_solution.rectangles[idx1]

        new_solution.place_rectangles()

        if new_solution.fitness > best_solution.fitness:
            best_solution = new_solution
        else:
            acceptance_prob = math.exp((new_solution.fitness - current_solution.fitness) / temp)
            if random.random() < acceptance_prob:
                current_solution = new_solution

    return best_solution


rectangles = [Rectangle(random.randint(20, 50), random.randint(100, 400)) for _ in range(50)]

solution = simulated_annealing(rectangles, 400, 1200, temp=200, cooling_rate=0.95, iterations=20000)

print(solution)
for i, bin in enumerate(solution.bins):
    print(f"第{i + 1}块板材:")
    for rect in bin.free_rectangles:
        print(f"  空闲区域: {rect}")
    print(f"  利用率: {bin.used_area / (bin.width * bin.height):.2%}")

solution.plot()