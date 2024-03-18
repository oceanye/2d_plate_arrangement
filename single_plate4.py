import random
from rectpack import newPacker
from deap import base, creator, tools, algorithms

# 定义问题
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# 定义问题的参数
NUM_RECTANGLES_PER_TYPE = 5
NUM_RECTANGLE_TYPES = 5
BOARD_WIDTH = 20
BOARD_HEIGHT = 20

# 生成随机小矩形
rectangles = [(random.randint(1, 5), random.randint(1, 5)) for _ in range(NUM_RECTANGLES_PER_TYPE * NUM_RECTANGLE_TYPES)]

# 定义适应度函数
def fitness(individual):
    packer = newPacker()
    for rect, count in zip(rectangles, individual):
        for _ in range(count):
            packer.add_rect(*rect, rid=None)

    packer.add_bin(BOARD_WIDTH, BOARD_HEIGHT)

    # Pack rectangles into the bin
    packer.pack()

    # Calculate vacant space
    vacant_space = packer[0].used_area()

    return vacant_space,

# 定义遗传算法参数
toolbox = base.Toolbox()
toolbox.register("individual", lambda: random.choices(range(6), k=NUM_RECTANGLES_PER_TYPE * NUM_RECTANGLE_TYPES))
toolbox.register("population", tools.initRepeat, list, toolbox.individual, n=50)
toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=5, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# 创建初始种群
population = toolbox.population()

# 运行遗传算法
algorithms.eaMuPlusLambda(population, toolbox, mu=50, lambda_=200, cxpb=0.7, mutpb=0.2, ngen=100, stats=None, halloffame=None)

# 打印最优解
best_individual = tools.selBest(population, k=1)[0]
print("Best Individual:", best_individual)
fitness_value = fitness(best_individual)[0]
print("Vacant Space:", fitness_value)

# 打印最终排布方式
packer = newPacker()
for rect, count in zip(rectangles, best_individual):
    for _ in range(count):
        packer.add_rect(*rect, rid=None)

packer.add_bin(BOARD_WIDTH, BOARD_HEIGHT)
packer.pack()

for rect in packer[0]:
    print(f"Rectangle - Size: {rect.width}x{rect.height} - Position: {rect.position}")

# 可以根据具体情况进行调整和扩展
