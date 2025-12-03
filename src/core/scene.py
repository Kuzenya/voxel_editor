import numpy as np
from typing import List
import os

from .cube import Entity, CubeMesh
from .camera import Camera
from .material import Material


class Scene:
    """
    Основной класс сцены, содержащий объекты и камеру.
    Позволяет добавлять/удалять объекты, управлять камерой и сохранять/загружать сцену.
    """

    def __init__(self):
        # Список всех объектов: CubeMesh, Entity и др.
        self.entities: list = []

        # Камера по умолчанию
        self.camera = Camera(position=[0, 0, 2])

    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------

    def update(self, rate: float = 1.0):
        """Обновляет все объекты сцены, например, вращение кубов."""
        for entity in self.entities:
            if hasattr(entity, "eulers"):
                entity.eulers[1] += 0.25 * rate
                if entity.eulers[1] > 360:
                    entity.eulers[1] -= 360

    # ----------------------------------------------------------------------
    # CAMERA CONTROL
    # ----------------------------------------------------------------------

    def move_player(self, dPos):
        """Сдвиг камеры (игрока)."""
        self.move(dPos)

    def spin_player(self, dTheta, dPhi):
        """Вращение камеры (игрока)."""
        self.spin(dTheta, dPhi)

    def move(self, dPos):
        """Реализация сдвига камеры."""
        dPos = np.array(dPos, dtype=np.float32)
        self.camera.position += dPos

    def spin(self, dTheta, dPhi):
        """Реализация вращения камеры с ограничением pitch."""
        self.camera.theta = (self.camera.theta + dTheta) % 360
        self.camera.phi = np.clip(self.camera.phi + dPhi, -89, 89)
        self.camera.update_vectors()

    # ----------------------------------------------------------------------
    # OBJECT MANAGEMENT
    # ----------------------------------------------------------------------

    def add_cube(
        self,
        position: List[float],
        eulers: List[float],
        color=np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32),
    ) -> CubeMesh:
        """
        Создаёт и добавляет куб в сцену с собственным материалом.
        Возвращает ссылку на объект CubeMesh.
        """
        cube = CubeMesh(position=position, eulers=eulers)
        try:
            cube.material = Material(color[0], color[1], color[2], color[3])
        except Exception as e:
            print("[Scene] Failed to create material for cube:", e)
            cube.material = None

        self.entities.append(cube)
        cube.is_selected = True
        return cube

    def remove_entity_by_index(self, index: int) -> bool:
        """Удаляет объект по индексу и освобождает ресурсы."""
        if 0 <= index < len(self.entities):
            ent = self.entities[index]
            self._destroy_entity(ent)
            del self.entities[index]
            return True
        return False

    def remove_entity(self, entity) -> bool:
        """Удаляет объект сцены по ссылке."""
        if entity not in self.entities:
            return False
        self._destroy_entity(entity)
        self.entities.remove(entity)
        return True

    def _destroy_entity(self, entity):
        """Освобождает ресурсы объекта и его материала."""
        try:
            if hasattr(entity, "destroy"):
                entity.destroy()
        except Exception:
            pass

        try:
            if hasattr(entity, "material") and entity.material:
                entity.material.destroy()
        except Exception:
            pass

    def get_all_selected(self) -> list:
        """Возвращает список всех выделенных объектов."""
        return [e for e in self.entities if getattr(e, "is_selected", 0)]

    # ----------------------------------------------------------------------
    # SCENE SAVE / LOAD
    # ----------------------------------------------------------------------

    def export_scene(self, filepath: str = "scenes/scene.txt") -> bool:
        """Сохраняет текущую сцену в текстовый файл."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write("# Scene file v1\n")
                for ent in self.entities:
                    etype = "CUBE" if isinstance(ent, CubeMesh) else "ENTITY"
                    pos = ent.position
                    eul = ent.eulers
                    c = getattr(ent.material, "color", np.array([1.0, 1.0, 1.0, 1.0]))
                    line = f"{etype} {pos[0]} {pos[1]} {pos[2]}  {eul[0]} {eul[1]} {eul[2]}  {c[0]} {c[1]} {c[2]} {c[3]}\n"
                    f.write(line)
            print(f"[Scene] Exported to {filepath}")
            return True
        except Exception as e:
            print("[Scene] Export failed:", e)
            return False

    def import_scene(self, filepath: str = "scenes/scene.txt") -> bool:
        """Загружает сцену из текстового файла, очищая текущие объекты."""
        if not os.path.exists(filepath):
            print("[Scene] Import failed: file not found", filepath)
            return False

        try:
            self.entities.clear()
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()
                    etype = parts[0]
                    px, py, pz = map(float, parts[1:4])
                    ex, ey, ez = map(float, parts[4:7])
                    r, g, b, a = map(float, parts[7:11])

                    if etype == "CUBE":
                        cube = self.add_cube(
                            position=[px, py, pz],
                            eulers=[ex, ey, ez],
                            color=np.array([r, g, b, a], dtype=np.float32)
                        )
                        cube.is_selected = False
                    elif etype == "ENTITY":
                        ent = Entity(position=[px, py, pz], eulers=[ex, ey, ez])
                        ent.material = Material(r, g, b, a)
                        self.entities.append(ent)

            print(f"[Scene] Imported from {filepath}")
            return True
        except Exception as e:
            print("[Scene] Import failed:", e)
            return False
