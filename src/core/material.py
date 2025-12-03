from OpenGL.GL import *
import numpy as np


class Material:
    """
    Простой материал RGBA без текстур.
    Отправляет цвет в шейдер через uniform `materialColor`.
    """

    def __init__(self, r: float = 0.5, g: float = 0.5, b: float = 0.5, a: float = 1.0):
        # Храним цвет в numpy-массиве для удобной передачи в OpenGL
        self.color = np.array([r, g, b, a], dtype=np.float32)

    # ------------------------------------------------------------------

    def use(self, shader_program: int | None = None) -> None:
        """
        Активирует материал, отправляя uniform 'materialColor'.
        shader_program — ID шейдера, в который будут переданы данные.
        """
        if shader_program is None:
            return

        loc_color = glGetUniformLocation(shader_program, "materialColor")
        if loc_color != -1:
            glUniform4fv(loc_color, 1, self.color)

    # ------------------------------------------------------------------

    def destroy(self) -> None:
        """Материал не создаёт OpenGL-ресурсов, поэтому тут пусто."""
        pass
