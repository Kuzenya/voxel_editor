import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

from .scene import Scene


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 760

RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_END = 1


# ---------------------------------------------------------------------------
# GLFW INITIALIZATION
# ---------------------------------------------------------------------------

def initialize_glfw():
    """Создаёт окно, инициализирует контекст OpenGL и настраивает GLFW."""

    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")

    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)

    window = glfw.create_window(
        SCREEN_WIDTH, SCREEN_HEIGHT,
        "Voxel editor", None, None
    )
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")

    glfw.make_context_current(window)

    # Включаем отображение курсора
    glfw.set_input_mode(window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_NORMAL)

    # Ставим курсор в центр окна
    glfw.set_cursor_pos(window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    return window


# ---------------------------------------------------------------------------
# SHADER CREATION
# ---------------------------------------------------------------------------

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """Компилирует и линковает шейдерный програм из двух файлов."""
    with open(vertex_filepath, "r") as f:
        vertex_src = f.read()

    with open(fragment_filepath, "r") as f:
        fragment_src = f.read()

    return compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER)
    )


# ---------------------------------------------------------------------------
# GRAPHICS ENGINE
# ---------------------------------------------------------------------------

class Graphics_Engine:
    """
    Класс рендеринга всех объектов сцены.
    Работает вместе с Scene и Material.
    """

    def __init__(self, scene: Scene, scene_file: str = "scenes/scene.txt"):
        self.scene = scene
        self.scene_file = scene_file

        # создаём и активируем шейдер
        self.shader = create_shader(
            vertex_filepath="shaders/vertex.txt",
            fragment_filepath="shaders/fragment.txt"
        )

        # Загрузка сцены
        if not self.scene.import_scene(self.scene_file):
            print("[Graphics_Engine] Scene file not found — creating demo cube")
            self.scene.add_cube(position=[0, 0, -3], eulers=[0, 0, 0])

        self._set_onetime_uniforms()
        self._cache_uniform_locations()

    # ----------------------------------------------------------------------
    # UNIFORMS
    # ----------------------------------------------------------------------

    def _set_onetime_uniforms(self):
        """Устанавливает uniform'ы, которые не меняются во время работы."""
        glUseProgram(self.shader)

        # текстурный слот
        loc_tex = glGetUniformLocation(self.shader, "imageTexture")
        if loc_tex != -1:
            glUniform1i(loc_tex, 0)

        # матрица проекции
        projection = pyrr.matrix44.create_perspective_projection(
            fovy=45.0,
            aspect=SCREEN_WIDTH / SCREEN_HEIGHT,
            near=0.1,
            far=100.0,
            dtype=np.float32
        )
        loc_proj = glGetUniformLocation(self.shader, "projection")
        if loc_proj != -1:
            glUniformMatrix4fv(loc_proj, 1, GL_FALSE, projection)

    def _cache_uniform_locations(self):
        """Читает и кеширует локации uniform-переменных."""
        glUseProgram(self.shader)
        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")

    # ----------------------------------------------------------------------
    # RENDERING
    # ----------------------------------------------------------------------

    def render(self, scene: Scene):
        """Главный метод — рисует всю сцену."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)

        # view-матрица камеры
        cam = scene.camera
        eye = cam.position
        target = cam.position + cam.forwards
        up = cam.up

        view = pyrr.matrix44.create_look_at(eye, target, up, dtype=np.float32)

        if self.viewMatrixLocation != -1:
            glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, view)

        # Рисуем объекты
        for entity in scene.entities:

            # модельная матрица
            if hasattr(entity, "get_model_transform") and self.modelMatrixLocation != -1:
                model = entity.get_model_transform()
                glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model)

            # материал
            material = getattr(entity, "material", None)
            if material:
                material.use(self.shader)
            else:
                # fallback — белый цвет
                loc_color = glGetUniformLocation(self.shader, "materialColor")
                if loc_color != -1:
                    glUniform4fv(loc_color, 1, np.array([1, 1, 1, 1], dtype=np.float32))

            # VBO/VAO binding
            if hasattr(entity, "arm_for_drawing"):
                try:
                    entity.arm_for_drawing()
                except Exception:
                    pass

            # Рисование
            if hasattr(entity, "draw"):
                try:
                    entity.draw()
                except Exception:
                    pass

    # ----------------------------------------------------------------------
    # CLEANUP
    # ----------------------------------------------------------------------

    def quit(self):
        """Освобождает OpenGL-ресурсы."""
        # Удаляем все объекты сцены
        for entity in getattr(self.scene, "entities", []):
            try:
                if hasattr(entity, "destroy"):
                    entity.destroy()
            except Exception:
                pass

            # материал
            try:
                mat = getattr(entity, "material", None)
                if mat:
                    mat.destroy()
            except Exception:
                pass

        # удаляем шейдер
        try:
            glDeleteProgram(self.shader)
        except Exception:
            pass
