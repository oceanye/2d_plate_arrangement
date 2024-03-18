import rectpack
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import ezdxf
import sqlite3


def generate_rectangles(num_types, min_size, max_size, min_count, max_count):
    rectangles = []
    for i in range(num_types):
        width = random.randint(min_size, max_size)
        height = random.randint(min_size, max_size)
        count = random.randint(min_count, max_count)
        for j in range(count):
            rectangles.append((width, height, i, len(rectangles)))
    return rectangles


def read_rectangles_from_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT Type, amount, width, height, id_list FROM tbl_plate")
    rectangles = []
    for row in cursor:
        type_id, amount, width, height, id_list = row
        ids = [int(id) for id in id_list.split(',')]
        for id in ids:
            rectangles.append((width, height, type_id, id))
    conn.close()
    return rectangles

def pack_rectangles_0(rectangles, bin_size):
    packer = rectpack.newPacker(rotation=True, pack_algo=rectpack.MaxRectsBssf)

    for r in rectangles:
        packer.add_rect(width=r[0], height=r[1], rid=r[3])

    total_rect_area = sum(r[0] * r[1] for r in rectangles)
    bin_area = bin_size[0] * bin_size[1]
    max_bins = max(1, int(2 * total_rect_area / bin_area))

    while True:
        packer.reset()
        for _ in range(max_bins):
            packer.add_bin(width=bin_size[0], height=bin_size[1])
        packer.pack()

        print(f"\nTrying with {max_bins} bins:")
        all_rects = packer.rect_list()
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            print(
                f"Rectangle {rid} (type {rectangles[rid][2]}, {rectangles[rid][0]}, {rectangles[rid][1]}) is packed in bin {b} at ({x}, {y}), rotated: {w != rectangles[rid][0]}")

        if len(packer.rect_list()) == len(rectangles):
            print(f"All rectangles packed in {max_bins} bins")
            break
        else:
            print(f"Could not pack all rectangles in {max_bins} bins")
            max_bins += 1

    return packer


def pack_rectangles(rectangles, bin_size, target_utilization):
    packer = rectpack.newPacker(rotation=True, pack_algo=rectpack.MaxRectsBssf)

    for r in rectangles:
        packer.add_rect(width=r[0], height=r[1], rid=r[3])

    total_rect_area = sum(r[0] * r[1] for r in rectangles)
    bin_area = bin_size[0] * bin_size[1]
    max_bins = max(1, int(2 * total_rect_area / bin_area))

    while True:
        packer.reset()
        for _ in range(max_bins):
            packer.add_bin(width=bin_size[0], height=bin_size[1])

        packed_bins = 0
        current_bin_area = 0
        for rect in rectangles:
            packer.pack()
            all_rects = packer.rect_list()
            bin_rects = [r for r in all_rects if r[0] == packed_bins]
            current_bin_area = sum(r[3] * r[4] for r in bin_rects)
            utilization = current_bin_area / bin_area * 100

            if utilization >= target_utilization:
                packed_bins += 1
                current_bin_area = 0

            packer.add_rect(width=rect[0], height=rect[1], rid=rect[3])

        packer.pack()

        print(f"\nTrying with {max_bins} bins and target utilization {target_utilization}%:")
        all_rects = packer.rect_list()
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            print(
                f"Rectangle {rid} (type {rectangles[rid][2]}, {rectangles[rid][0]}, {rectangles[rid][1]}) is packed in bin {b} at ({x}, {y}), rotated: {w != rectangles[rid][0]}")

        if len(packer.rect_list()) == len(rectangles):
            print(f"All rectangles packed in {packed_bins + 1} bins with target utilization {target_utilization}%")
            break
        else:
            print(f"Could not pack all rectangles in {max_bins} bins with target utilization {target_utilization}%")
            max_bins += 1

    return packer


def save_to_dxf(packer, rectangles, bin_size, filename):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()

    bin_offset_x = 0  # bin在x方向上的偏移量
    for i in range(len(packer)):
        bin_rects = [r for r in packer.rect_list() if r[0] == i]

        # 创建一个新的图层用于当前bin
        layer = doc.layers.new(name=f'bin_{i}')

        # 绘制bin的边界
        bin_boundary = msp.add_lwpolyline(
            [(bin_offset_x, 0), (bin_offset_x + bin_size[0], 0), (bin_offset_x + bin_size[0], bin_size[1]),
             (bin_offset_x, bin_size[1]), (bin_offset_x, 0)], dxfattribs={'layer': layer.dxf.name})

        for rect in bin_rects:
            b, x, y, w, h, rid = rect

            # 获取矩形的类型ID
            type_id = rectangles[rid][2]

            # 创建或获取对应于矩形类型的图层
            layer_name = f'type_{type_id}'
            if layer_name not in doc.layers:
                doc.layers.new(name=layer_name)

            # 绘制矩形
            msp.add_lwpolyline([(bin_offset_x + x, y), (bin_offset_x + x + w, y), (bin_offset_x + x + w, y + h),
                                (bin_offset_x + x, y + h), (bin_offset_x + x, y)], dxfattribs={'layer': layer_name})

            # 在矩形中心添加文本标签
            text = msp.add_text(str(rid), dxfattribs={
                'layer': layer_name,
                'height': min(w, h) / 2,
                'rotation': 90 if w < h else 0
            })
            text.dxf.insert = (bin_offset_x + x + w / 2, y + h / 2)  # 设置文本的插入点,应用偏移量
            text.dxf.halign = 1  # 设置文本的水平对齐方式为居中对齐
            text.dxf.valign = 2  # 设置文本的垂直对齐方式为居中对齐

        bin_offset_x += bin_size[0] + 100  # 为下一个bin增加偏移量,并在bin之间留出更大的空间

    doc.saveas(filename)

def save_to_database(packer, rectangles, bin_size, db_name):
    # 连接到SQLite数据库(如果数据库不存在,则创建一个新的)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 创建表Plate_table_output(如果不存在)
    c.execute('''CREATE TABLE IF NOT EXISTS Plate_table_output
                 (Bin_ID INTEGER,
                 Utilization REAL,
                 Type INTEGER,
                 Width REAL,
                 Height REAL,
                 Is_Rotated INTEGER,
                 Bottom_Left_X REAL,
                 Bottom_Left_Y REAL)''')

    for i in range(len(packer)):
        bin_rects = [r for r in packer.rect_list() if r[0] == i]
        bin_utilization = sum(r[2] * r[3] for r in bin_rects) / (bin_size[0] * bin_size[1])

        for rect in bin_rects:
            b, x, y, w, h, rid = rect
            type_id, _, _ = rectangles[rid]
            is_rotated = 1 if w < h else 0

            c.execute("INSERT INTO Plate_table_output VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (i, bin_utilization, type_id, w, h, is_rotated, x, y))

    conn.commit()
    conn.close()

num_types = 10
min_size = 200
max_size = 5000
min_count = 5
max_count = 20
bin_size = (5000, 15000)

rectangles = generate_rectangles(num_types, min_size, max_size, min_count, max_count)
rectangles = read_rectangles_from_db('plate_layout.db')


print(f"Generated {len(rectangles)} rectangles:")
for r in rectangles:
    print(f"Rectangle (type {r[2]}, id {r[3]}): ({r[0]}, {r[1]})")


target_utilization = 95
#packer = pack_rectangles(rectangles, bin_size, target_utilization)
packer = pack_rectangles_0(rectangles, bin_size)

all_rects = packer.rect_list()
print(f"\nFinal result: Packed {len(all_rects)} rectangles in {len(packer)} bins:")
for i in range(len(packer)):
    bin_rects = [r for r in all_rects if r[0] == i]
    bin_area = bin_size[0] * bin_size[1]
    packed_area = sum(r[3] * r[4] for r in bin_rects)
    utilization = packed_area / bin_area * 100
    print(f"\nBin {i} - Utilization: {utilization:.2f}%")
    print("Contains rectangles:")
    type_counts = {}
    for rect in bin_rects:
        b, x, y, w, h, rid = rect
        type_id = rectangles[rid][2]
        if type_id not in type_counts:
            type_counts[type_id] = []
        type_counts[type_id].append(rid)
    for type_id, rect_ids in type_counts.items():
        print(f"Type {type_id}: {rect_ids}")

unpacked_rects = [r for r in rectangles if r[3] not in [rect[5] for rect in all_rects]]
print(f"\n{len(unpacked_rects)} rectangles could not be packed:")
for rect in unpacked_rects:
    print(f"Rectangle (type {rect[2]}, id {rect[3]}, {rect[0]}, {rect[1]}) is not packed")

if len(packer) == 1:
    fig, ax = plt.subplots(figsize=(5, 5))
    for rect in all_rects:
        b, x, y, w, h, rid = rect
        ax.add_patch(patches.Rectangle((x, y), w, h, facecolor='blue', edgecolor='black', alpha=0.5))
    ax.set_title(f"Bin 0")
    ax.set_xlim(0, bin_size[0])
    ax.set_ylim(0, bin_size[1])
    ax.set_aspect('equal')
else:
    fig, axs = plt.subplots(1, len(packer), figsize=(5 * len(packer), 5))
    for i in range(len(packer)):
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            if b == i:
                axs[i].add_patch(patches.Rectangle((x, y), w, h, facecolor='blue', edgecolor='black', alpha=0.5))
        axs[i].set_title(f"Bin {i}")
        axs[i].set_xlim(0, bin_size[0])
        axs[i].set_ylim(0, bin_size[1])
        axs[i].set_aspect('equal')




plt.tight_layout()
plt.show()


dxf_filename = 'packing_result.dxf'
save_to_dxf(packer, rectangles, bin_size, dxf_filename)
print(f"Packing result saved to {dxf_filename}")

db_name = 'plate_layout.db'
save_to_database(packer, rectangles, bin_size, db_name)
print(f"Packing result saved to {db_name}")