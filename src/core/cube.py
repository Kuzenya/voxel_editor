from OpenGL.GL import *
import numpy as np
import pyrr
import ctypes
from typing import List


# ======================================================================
# Base Entity
# ======================================================================

class Entity:
    """
    Базовый объект сцены, содержащий позицию и ориентацию.
    Используется как родитель для любых геометрических объектов.
    """

    def __init__(self, position: List[float], eulers: List[float]):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

    # ------------------------------------------------------------------

    def update(self) -> None:
        """
        Обновление состояния объекта.
        По умолчанию объект слегка вращается — используется как пример.
        """
        self.eulers[1] += 0.25
        if self.eulers[1] > 360:
            self.eulers[1] -= 360

    # ------------------------------------------------------------------

    def get_model_transform(self) -> np.ndarray:
        """
        Создаёт 4×4 модельную матрицу из поворота и позиции.
        Возвращает матрицу в формате numpy.float32.
        """

        model = pyrr.matrix44.create_identity(dtype=np.float32)

        # вращение по оси Y
        rotation = pyrr.matrix44.create_from_axis_rotation(
            axis=[0, 1, 0],
            theta=np.radians(self.eulers[1]),
            dtype=np.float32
        )
        model = pyrr.matrix44.multiply(model, rotation)

        translation = pyrr.matrix44.create_from_translation(
            vec=self.position,
            dtype=np.float32
        )
        model = pyrr.matrix44.multiply(model, translation)

        return model


# ======================================================================
# Cube Mesh
# ======================================================================

class CubeMesh(Entity):
    """
    Геометрия простого куба. Создаёт VAO/VBO и хранит вершины.
    Вершины включают позицию (x, y, z) и UV (s, t).
    Материал назначается позже через Scene.add_cube().
    """

    def __init__(self, position: List[float], eulers: List[float]):
        super().__init__(position, eulers)

        self.is_selected = False
        self.material = None     # параметр устанавливается сценой

        # ---------------------------------------------------------------
        # Буфер вершин куба — 36 треугольников, 5 значений на вершину.
        # ---------------------------------------------------------------
        vertices = np.array([
            # позиции (x, y, z)      UV
            -0.5, -0.5, -0.5,        0, 0,
             0.5, -0.5, -0.5,        1, 0,
             0.5,  0.5, -0.5,        1, 1,
             0.5,  0.5, -0.5,        1, 1,
            -0.5,  0.5, -0.5,        0, 1,
            -0.5, -0.5, -0.5,        0, 0,

            -0.5, -0.5,  0.5,        0, 0,
             0.5, -0.5,  0.5,        1, 0,
             0.5,  0.5,  0.5,        1, 1,
             0.5,  0.5,  0.5,        1, 1,
            -0.5,  0.5,  0.5,        0, 1,
            -0.5, -0.5,  0.5,        0, 0,

            -0.5,  0.5,  0.5,        1, 0,
            -0.5,  0.5, -0.5,        1, 1,
            -0.5, -0.5, -0.5,        0, 1,
            -0.5, -0.5, -0.5,        0, 1,
            -0.5, -0.5,  0.5,        0, 0,
            -0.5,  0.5,  0.5,        1, 0,

             0.5,  0.5,  0.5,        1, 0,
             0.5,  0.5, -0.5,        1, 1,
             0.5, -0.5, -0.5,        0, 1,
             0.5, -0.5, -0.5,        0, 1,
             0.5, -0.5,  0.5,        0, 0,
             0.5,  0.5,  0.5,        1, 0,

            -0.5, -0.5, -0.5,        0, 1,
             0.5, -0.5, -0.5,        1, 1,
             0.5, -0.5,  0.5,        1, 0,
             0.5, -0.5,  0.5,        1, 0,
            -0.5, -0.5,  0.5,        0, 0,
            -0.5, -0.5, -0.5,        0, 1,

            -0.5,  0.5, -0.5,        0, 1,
             0.5,  0.5, -0.5,        1, 1,
             0.5,  0.5,  0.5,        1, 0,
             0.5,  0.5,  0.5,        1, 0,
            -0.5,  0.5,  0.5,        0, 0,
            -0.5,  0.5, -0.5,        0, 1,
        ], dtype=np.float32)

        self.vertex_count = len(vertices) // 5

        # ---------------------------------------------------------------
        # OpenGL VAO/VBO setup
        # ---------------------------------------------------------------
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # layout(location = 0) > позиция
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0)
        )

        # layout(location = 1) > UV координаты
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(
            1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4)
        )

    # ==================================================================

    def arm_for_drawing(self) -> None:
        """Привязывает VAO куба перед отрисовкой."""
        glBindVertexArray(self.vao)

    # ------------------------------------------------------------------

    def draw(self) -> None:
        """Выполняет вызов отрисовки."""
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    # ------------------------------------------------------------------

    def destroy(self) -> None:
        """Удаляет VAO и VBO из памяти OpenGL."""
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
