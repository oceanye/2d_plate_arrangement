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
            rectangles.append((width, height, i, f"{len(rectangles)}-HLS"))
    return rectangles

def read_rectangles_from_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT Size_type, Count, Width, Height, ID_list FROM Plate_table_one")
    rectangles = []
    for row in cursor:
        type_id, amount, width, height, id_list = row
        ids = [f"{id}" for id in id_list.split(',')]
        for id in ids:
            rectangles.append((width, height, type_id, id))
    conn.close()
    return rectangles

def pack_rectangles(rectangles, bin_size):
    packer = rectpack.newPacker(rotation=True, pack_algo=rectpack.MaxRectsBssf)

    for r in rectangles:
        packer.add_rect(width=r[0], height=r[1], rid=r[3])

    total_rect_area = sum(r[0] * r[1] for r in rectangles)
    bin_area = bin_size[0] * bin_size[1]
    max_bins = max(1, int(2 * total_rect_area / bin_area))

    bin_id_template = "BIN_{}"
    bin_count = 0

    while True:
        packer.reset()
        for _ in range(max_bins):
            bin_id = bin_id_template.format(bin_count)
            packer.add_bin(width=bin_size[0], height=bin_size[1], bid=bin_id)
            bin_count += 1
        packer.pack()

        print(f"\nTrying with {max_bins} bins:")
        all_rects = packer.rect_list()
        rectangles_dict = {r[3]: r for r in rectangles}
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            if rid in rectangles_dict:
                rect_data = rectangles_dict[rid]
                print(f"Rectangle {rid} (type {rect_data[2]}, {rect_data[0]}, {rect_data[1]}) is packed in bin {b} at ({x}, {y}), rotated: {w != rect_data[0]}")
            else:
                print(f"Rectangle {rid} not found in the original list")

        if len(packer.rect_list()) == len(rectangles):
            print(f"All rectangles packed in {max_bins} bins")
            break
        else:
            print(f"Could not pack all rectangles in {max_bins} bins")
            max_bins += 1

    return packer

def save_to_dxf(packer, rectangles, bin_size, filename):
    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()

    bin_offset_x = 0
    for i in range(len(packer)):
        bin_rects = [r for r in packer.rect_list() if r[0] == i]
        layer = doc.layers.new(name=f'bin_{i}')
        bin_boundary = msp.add_lwpolyline(
            [(bin_offset_x, 0), (bin_offset_x + bin_size[0], 0), (bin_offset_x + bin_size[0], bin_size[1]),
             (bin_offset_x, bin_size[1]), (bin_offset_x, 0)], dxfattribs={'layer': layer.dxf.name})

        rectangles_dict = {r[3]: r for r in rectangles}
        for rect in bin_rects:
            b, x, y, w, h, rid = rect

            if rid in rectangles_dict:
                rect_data = rectangles_dict[rid]
                type_id = rect_data[2]
                layer_name = f'type_{type_id}'
                if layer_name not in doc.layers:
                    doc.layers.new(name=layer_name)

                msp.add_lwpolyline([(bin_offset_x + x, y), (bin_offset_x + x + w, y), (bin_offset_x + x + w, y + h),
                                    (bin_offset_x + x, y + h), (bin_offset_x + x, y)], dxfattribs={'layer': layer_name})

                text = msp.add_text(str(rid), dxfattribs={
                    'layer': layer_name,
                    'height': min(w, h) / 2,
                    'rotation': 90 if w < h else 0
                })
                text.dxf.insert = (bin_offset_x + x + w / 2, y + h / 2)
                text.dxf.halign = 1
                text.dxf.valign = 2

        bin_offset_x += bin_size[0] + 100

    doc.saveas(filename)

def save_to_database(packer, rectangles, bin_size, db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Plate_table_output
                 (Bin_ID INTEGER,
                 Utilization REAL,
                 Type INTEGER,
                 Width REAL,
                 Height REAL,
                 Is_Rotated INTEGER,
                 Bottom_Left_X REAL,
                 Bottom_Left_Y REAL)''')

    rectangles_dict = {r[3]: r for r in rectangles}
    for i in range(len(packer)):
        bin_rects = [r for r in packer.rect_list() if r[0] == i]
        bin_utilization = sum(r[2] * r[3] for r in bin_rects) / (bin_size[0] * bin_size[1])

        for rect in bin_rects:
            b, x, y, w, h, rid = rect
            if rid in rectangles_dict:
                rect_data = rectangles_dict[rid]
                type_id = rect_data[2]
                is_rotated = 1 if w < h else 0

                c.execute("INSERT INTO Plate_table_output VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (i, bin_utilization, type_id, w, h, is_rotated, x, y))

    conn.commit()
    conn.close()

#通过外部args参数传入 bin_width,bin_height
bin_width = 1000
bin_height = 1000


# 主程序
if __name__ == "__main__":
    num_types = 3
    min_size = 50
    max_size = 200
    min_count = 1
    max_count = 5
    bin_size = (bin_width, bin_height)
    db_file = 'D:\Program Files\GBS_Software\CreateTeklaCNC\Tekla_NCX_database.db'
    output_dxf = 'packed_rectangles.dxf'
    output_db = 'packing_results.db'

    #rectangles = generate_rectangles(num_types, min_size, max_size, min_count, max_count)
    rectangles = read_rectangles_from_db(db_file)  # 从数据库中读取矩形数据
    print(f"Generated {len(rectangles)} rectangles")

    packer = pack_rectangles(rectangles, bin_size)

    #save_to_dxf(packer, rectangles, bin_size, output_dxf)
    #print(f"Packing results saved to {output_dxf}")

    save_to_database(packer, rectangles, bin_size, output_db)
    print(f"Packing results saved to {output_db}")

    all_rects = packer.rect_list()
    print(f"\nFinal result: Packed {len(all_rects)} rectangles in {len(packer)} bins:")

    rectangles_dict = {r[3]: r for r in rectangles}  # 创建一个字典,将矩形ID映射到矩形元组

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
            if rid in rectangles_dict:
                type_id = rectangles_dict[rid][2]
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