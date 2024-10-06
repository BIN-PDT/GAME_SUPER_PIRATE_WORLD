from settings import *

from groups import WorldSprite
from sprites import *


class Overworld:
    def __init__(self, tmx_map, assets, data, switch_command):
        self.screen = pygame.display.get_surface()
        self.data = data
        # ASSETS.
        self.switch_command = switch_command
        self.path_surfs = assets["path"]
        # GROUP.
        self.all_sprites = WorldSprite(self.data)
        self.node_sprites = pygame.sprite.Group()
        # SETUP.
        self.load_data(tmx_map, assets)
        self.load_path()
        # CONTROL.
        self.current_node = [
            node for node in self.node_sprites if node.level == self.data.current_level
        ][0]

    def load_data(self, tmx_map, assets):
        # TILES.
        for layer in ("main", "top"):
            for x, y, surface in tmx_map.get_layer_by_name(layer).tiles():
                Sprite(
                    pos=(x * TILE_SIZE, y * TILE_SIZE),
                    surf=surface,
                    groups=self.all_sprites,
                    z=Z_LAYERS["bg tiles"],
                )
        # WATER.
        for row in range(tmx_map.height):
            for col in range(tmx_map.width):
                AnimatedSprite(
                    pos=(col * TILE_SIZE, row * TILE_SIZE),
                    frames=assets["water"],
                    groups=self.all_sprites,
                    z=Z_LAYERS["bg"],
                )
        # OBJECTS.
        for obj in tmx_map.get_layer_by_name("Objects"):
            name = obj.name
            pos = obj.x, obj.y

            if name == "palm":
                AnimatedSprite(
                    pos=pos,
                    frames=assets["palms"],
                    groups=self.all_sprites,
                    animation_speed=randint(4, 6),
                )
            else:
                z = Z_LAYERS["bg tiles"] if name == "stone" else Z_LAYERS["bg details"]
                Sprite(pos, obj.image, self.all_sprites, z)
        # PATHS.
        self.paths = {}
        for obj in tmx_map.get_layer_by_name("Paths"):
            self.paths[obj.properties["end"]] = {
                "start": obj.properties["start"],
                "points": [
                    (int(point.x + TILE_SIZE / 2), int(point.y + TILE_SIZE / 2))
                    for point in obj.points
                ],
            }
        # NODE & PLAYER.
        for obj in tmx_map.get_layer_by_name("Nodes"):
            name = obj.name
            pos = obj.x + TILE_SIZE / 2, obj.y + TILE_SIZE / 2

            if name == "Node":
                paths = {
                    key: value
                    for key, value in obj.properties.items()
                    if key in ("left", "right", "up", "down")
                }

                Node(
                    pos=pos,
                    surf=assets["path"]["node"],
                    groups=(self.all_sprites, self.node_sprites),
                    level=obj.properties["stage"],
                    data=self.data,
                    paths=paths,
                )
                # PLAYER.
                if obj.properties["stage"] == self.data.current_level:
                    self.icon = Icon(pos, assets["icon"], self.all_sprites)

    def load_path(self):
        # PATH TILE (TARGET LEVEL: GRID PATH).
        path_tiles = {}
        for path_key, data in self.paths.items():
            # CONVERT PIXEL POINT TO GRID POINT.
            grid_points = [
                Vector(int(point[0] / TILE_SIZE), int(point[1] / TILE_SIZE))
                for point in data["points"]
            ]
            # STORE THE START POINT.
            path_tiles[path_key] = [grid_points[0]]
            # STORE THE REMAINING POINTS.
            for index, point in enumerate(grid_points):
                if index < len(grid_points) - 1:
                    start_point, end_point = point, grid_points[index + 1]
                    tiles = end_point - start_point
                    # VERTICAL.
                    if tiles.y:
                        direction = 1 if tiles.y > 0 else -1
                        for y in range(direction, int(tiles.y) + direction, direction):
                            path_tiles[path_key].append(start_point + (0, y))
                    # HORIZONTAL.
                    else:
                        direction = 1 if tiles.x > 0 else -1
                        for x in range(direction, int(tiles.x) + direction, direction):
                            path_tiles[path_key].append(start_point + (x, 0))
        # PATH SPRITE.
        for path_key, path in path_tiles.items():
            for index, tile in enumerate(path):
                if 0 < index < len(path) - 1:
                    prev_tile = path[index - 1] - tile
                    next_tile = path[index + 1] - tile
                    if prev_tile.x == next_tile.x:
                        tile_type = "vertical"
                    elif prev_tile.y == next_tile.y:
                        tile_type = "horizontal"
                    else:
                        if (prev_tile.y == -1 and next_tile.x == -1) or (
                            prev_tile.x == -1 and next_tile.y == -1
                        ):
                            tile_type = "tl"
                        elif (prev_tile.y == 1 and next_tile.x == 1) or (
                            prev_tile.x == 1 and next_tile.y == 1
                        ):
                            tile_type = "br"
                        elif (prev_tile.y == 1 and next_tile.x == -1) or (
                            prev_tile.x == -1 and next_tile.y == 1
                        ):
                            tile_type = "bl"
                        elif (prev_tile.y == -1 and next_tile.x == 1) or (
                            prev_tile.x == 1 and next_tile.y == -1
                        ):
                            tile_type = "tr"

                    Path(
                        pos=tile * TILE_SIZE,
                        surf=self.path_surfs[tile_type],
                        groups=self.all_sprites,
                        level=path_key,
                    )

    def input(self):
        if self.current_node:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.current_node.can_move("left"):
                self.move("left")
            if keys[pygame.K_RIGHT] and self.current_node.can_move("right"):
                self.move("right")
            if keys[pygame.K_UP] and self.current_node.can_move("up"):
                self.move("up")
            if keys[pygame.K_DOWN] and self.current_node.can_move("down"):
                self.move("down")
            if keys[pygame.K_RETURN]:
                self.data.current_level = self.current_node.level
                self.switch_command("level")

    def move(self, direction):
        # GET THE TARGET NODE.
        path_key = int(self.current_node.paths[direction][0])
        # CHECK IF GO BACK INSTEAD OF GO TO.
        path_reverse = self.current_node.paths[direction][-1] == "r"
        # GET THE PATH.
        points = self.paths[path_key]["points"]
        path = points if not path_reverse else points[::-1]
        # MOVE TO THE TARGET NODE.
        self.icon.start_move(path)

    def check_current_node(self):
        if not self.icon.path:
            self.current_node = pygame.sprite.spritecollide(
                self.icon, self.node_sprites, False
            )[0]
        else:
            self.current_node = None

    def run(self, dt):
        # UPDATE.
        self.input()
        self.check_current_node()
        self.all_sprites.update(dt)
        # DRAW.
        self.all_sprites.draw(self.icon.rect.center)
