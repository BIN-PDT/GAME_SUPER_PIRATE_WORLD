from os import walk
from os.path import join
from pygame.image import load


def import_image(*path, alpha=True, format="png"):
    full_path = f"{join(*path)}.{format}"
    surf = load(full_path)
    return surf.convert_alpha() if alpha else surf.convert()


def import_folder_list(*path):
    frames = []
    for folder_path, _, file_names in walk(join(*path)):
        for file_name in sorted(file_names, key=lambda name: int(name.split(".")[0])):
            full_path = join(folder_path, file_name)
            surf = load(full_path).convert_alpha()
            frames.append(surf)
    return frames


def import_folder_dict(*path, subordinate=False):
    frames = {}
    for folder_path, sub_folders, file_names in walk(join(*path)):
        if subordinate:
            for sub_folder in sub_folders:
                frames[sub_folder] = import_folder_list(folder_path, sub_folder)
        else:
            for file_name in file_names:
                full_path = join(folder_path, file_name)
                surf = load(full_path).convert_alpha()
                frames[file_name.split(".")[0]] = surf
    return frames
