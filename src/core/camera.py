import numpy as np
from typing import List


class Camera:
    """
    Простая свободная камера для навигации по 3D-сцене.

    Атрибуты:
        position : np.ndarray — текущая позиция камеры
        theta    : float      — угол поворота по горизонтали (yaw)
        phi      : float      — угол поворота по вертикали (pitch)
        forwards : np.ndarray — нормализованный вектор направления взгляда
        right    : np.ndarray — вектор вправо
        up       : np.ndarray — вектор вверх
    """

    def __init__(self, position: List[float]):
        self.position = np.array(position, dtype=np.float32)

        # Углы ориентации камеры (в градусах)
        self.theta = 0.0   # yaw — горизонтальный поворот
        self.phi = 0.0     # pitch — вертикальный поворот

        self.update_vectors()

    # ----------------------------------------------------------------------

    def update_vectors(self):
        """
        Обновляет векторы направления камеры.
        Вызывается после изменения theta или phi.
        """

        yaw = np.radians(self.theta)
        pitch = np.radians(self.phi)

        # Вектор направления (вперёд)
        self.forwards = np.array([
            np.cos(yaw) * np.cos(pitch),
            np.sin(yaw) * np.cos(pitch),
            np.sin(pitch)
        ], dtype=np.float32)

        # Глобальный верх мира (ось Z)
        global_up = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        # Перпендикулярные векторы камеры
        self.right = np.cross(self.forwards, global_up)
        self.up = np.cross(self.right, self.forwards)

        # Нормализация
        self.right /= np.linalg.norm(self.right) + 1e-8
        self.up /= np.linalg.norm(self.up) + 1e-8
        self.forwards /= np.linalg.norm(self.forwards) + 1e-8
