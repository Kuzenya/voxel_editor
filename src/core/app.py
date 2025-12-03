import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
import numpy as np
from PySide6.QtWidgets import QApplication
from .graphics_engine import Graphics_Engine
from src.gui.material_editor_window import MaterialEditorWindow
from src.gui.object_list_window import ObjectListWindow
from src.gui.enter_window import SimpleInputDialog
from .scene import Scene


# ---------- Константы ----------
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 760

RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_END = 1


class App:
    """
    Главный класс приложения.
    Управляет окном, обработкой ввода, Qt-диалогами, сценой и рендером.
    """

    def __init__(self, window):
        self.window = window
        self.renderer = None

        # Основная 3D-сцена
        self.scene = Scene()

        # Параметры времени
        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.frameTime = 16.7
        self.numFrames = 0

        # Размер шага для привязки кубов к сетке
        self.GRID_SIZE = 1.0

        # Таблица для расчёта направления камеры по WASD
        self.walk_offset_lookup = {
            1: 0, 2: 90, 3: 45, 4: 180, 6: 135,
            7: 90, 8: 270, 9: 315, 11: 0, 12: 225,
            13: 270, 14: 180
        }

        self._set_up_opengl()
        self.renderer = Graphics_Engine(self.scene)

        # Режим перемещения выбранных кубов
        self.move_mode = False
        self.move_axis = None
        self.selected_entities = []
        self.selected_entity = None

        # Окна Qt
        self.object_window = None
        self.qt_app = QApplication([])

    # --------------------------------------------------------------------
    #                   ИНИЦИАЛИЗАЦИЯ OPENGL
    # --------------------------------------------------------------------

    def _set_up_opengl(self):
        """Начальная настройка OpenGL."""
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

    # --------------------------------------------------------------------
    #                    ОКНА ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА
    # --------------------------------------------------------------------

    def toggle_object_window(self):
        """Показ/скрытие окна со списком объектов сцены."""
        if self.object_window is None:
            self.object_window = ObjectListWindow(self.scene)
            self.object_window.show()
        else:
            if self.object_window.isVisible():
                self.object_window.close()
            else:
                self.object_window.show()

    def rebuild_object_window(self):
        """Обновляет список объектов в окне."""
        if self.object_window is not None:
            self.object_window.rebuild_list()

    def open_material_editor(self):
        """Открывает окно редактирования материала выбранных объектов."""
        if hasattr(self, "material_editor") and self.material_editor is not None:
            self.material_editor.show()
            self.material_editor.raise_()
            return

        self.material_editor = MaterialEditorWindow(self)
        self.material_editor.show()

    # --------------------------------------------------------------------
    #                              ЦИКЛ
    # --------------------------------------------------------------------

    def run(self):
        """Главный цикл приложения."""
        running = True
        while running:
            self.qt_app.processEvents()

            if (glfw.window_should_close(self.window) or
                glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS):
                break

            self.handle_keys()
            self.handle_mouse()

            glfw.poll_events()
            self.renderer.render(self.scene)

            glfw.swap_buffers(self.window)
            self.calculateFramerate()

        self.quit()

    # --------------------------------------------------------------------
    #                        ОБРАБОТКА КЛАВИАТУРЫ
    # --------------------------------------------------------------------

    def handle_keys(self):
        """Обрабатывает движение игрока, перемещение кубов и команды интерфейса."""

        # ---------------- Движение игрока WASD ----------------
        combo = 0
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS: combo += 1
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS: combo += 2
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS: combo += 4
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS: combo += 8

        if combo in self.walk_offset_lookup:
            direction = self.walk_offset_lookup[combo]
            angle = np.deg2rad(self.scene.camera.theta + direction)
            scale = (self.frameTime / 16.7)

            dPos = [scale * np.cos(angle), scale * np.sin(angle), 0.0]
            self.scene.move_player(dPos)

        # ---------------- Переключение режима перемещения куба ----------------
        g_pressed = glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_G) == GLFW_CONSTANTS.GLFW_PRESS
        n_pressed = glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_N) == GLFW_CONSTANTS.GLFW_PRESS

        if g_pressed or n_pressed:
            if not self.move_mode:
                self.selected_entities = self.scene.get_all_selected()

                for selected_entity in self.selected_entities:
                    self.selected_entity = selected_entity

                    # Клонирование объекта (N)
                    if n_pressed:
                        pos = list(self.selected_entity.position)
                        eulers = list(self.selected_entity.eulers)
                        color = tuple(self.selected_entity.material.color)
                        self.selected_entity.is_selected = False

                        self.selected_entity = self.scene.add_cube(pos, eulers, color)
                        self.rebuild_object_window()

                if self.selected_entity:
                    self.move_mode = True
                    self.move_axis = None

        # ---------------- Выбор оси перемещения ----------------
        if self.move_mode:
            if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_X) == GLFW_CONSTANTS.GLFW_PRESS:
                self.move_axis = 'X'
            elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_Y) == GLFW_CONSTANTS.GLFW_PRESS:
                self.move_axis = 'Y'
            elif glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_Z) == GLFW_CONSTANTS.GLFW_PRESS:
                self.move_axis = 'Z'

        # ---------------- Окна интерфейса ----------------
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_O) == GLFW_CONSTANTS.GLFW_PRESS:
            self.toggle_object_window()
            self.rebuild_object_window()

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_C) == GLFW_CONSTANTS.GLFW_PRESS:
            self.open_material_editor()

        # ---------------- Удаление объектов ----------------
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_DELETE) == GLFW_CONSTANTS.GLFW_PRESS:
            for e in self.scene.get_all_selected():
                self.scene.remove_entity(e)

        # ---------------- Импорт/экспорт сцены ----------------
        m_pressed = glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_M) == GLFW_CONSTANTS.GLFW_PRESS
        ctrl_pressed = (
            glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_LEFT_CONTROL) == GLFW_CONSTANTS.GLFW_PRESS or
            glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_RIGHT_CONTROL) == GLFW_CONSTANTS.GLFW_PRESS
        )

        if m_pressed:
            dialog = SimpleInputDialog(default_text="scene.txt")
            if dialog.exec():
                filename = dialog.result_text
                if filename:
                    path = "scenes/" + filename
                    if ctrl_pressed:
                        self.scene.import_scene(path)
                    else:
                        self.scene.export_scene(path)

    # --------------------------------------------------------------------
    #                             МЫШЬ
    # --------------------------------------------------------------------

    def handle_mouse(self):
        """Обрабатывает вращение камеры и перемещение кубов."""

        # ----------- Вращение камеры при зажатом Shift ------------
        shift_pressed = (
            glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_LEFT_SHIFT) == GLFW_CONSTANTS.GLFW_PRESS or
            glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_RIGHT_SHIFT) == GLFW_CONSTANTS.GLFW_PRESS
        )

        if shift_pressed:
            glfw.set_input_mode(self.window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN)
            x, y = glfw.get_cursor_pos(self.window)

            rate = self.frameTime / 16.7
            theta_inc = rate * ((SCREEN_WIDTH / 2) - x) * 0.1
            phi_inc = rate * ((SCREEN_HEIGHT / 2) - y) * 0.1

            self.scene.spin_player(theta_inc, phi_inc)
            glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        else:
            glfw.set_input_mode(self.window, GLFW_CONSTANTS.GLFW_CURSOR, GLFW_CONSTANTS.GLFW_CURSOR_NORMAL)

        # ----------- Выход из режима перемещения ПКМ ------------
        if self.move_mode and glfw.get_mouse_button(
                self.window, GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_RIGHT) == GLFW_CONSTANTS.GLFW_PRESS:

            self.move_mode = False
            self.move_axis = None
            self.selected_entities = []
            self.selected_entity = None
            return

        # ----------- Перемещение кубов по выбранной оси ------------
        if self.move_mode and self.move_axis and self.selected_entity:
            x, y = glfw.get_cursor_pos(self.window)

            nx = (x / SCREEN_WIDTH - 0.5) * 2
            ny = (y / SCREEN_HEIGHT - 0.5) * 2

            max_dist = 20.0

            if self.move_axis == 'X':
                new_pos = round((nx * max_dist) / self.GRID_SIZE) * self.GRID_SIZE
                for e in self.selected_entities:
                    e.position[0] = new_pos

            elif self.move_axis == 'Y':
                new_pos = round((-ny * max_dist) / self.GRID_SIZE) * self.GRID_SIZE
                for e in self.selected_entities:
                    e.position[1] = new_pos

            elif self.move_axis == 'Z':
                new_pos = round((-ny * max_dist) / self.GRID_SIZE) * self.GRID_SIZE
                for e in self.selected_entities:
                    e.position[2] = new_pos

    # --------------------------------------------------------------------
    #                           FPS
    # --------------------------------------------------------------------

    def calculateFramerate(self):
        """Подсчёт FPS и обновление заголовка окна."""
        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime

        if delta >= 1.0:
            fps = max(1, int(self.numFrames / delta))
            glfw.set_window_title(self.window, f"Running at {fps} fps")

            self.lastTime = self.currentTime
            self.numFrames = 0
            self.frameTime = 1000.0 / fps

        self.numFrames += 1

    # --------------------------------------------------------------------

    def quit(self):
        """Освобождение ресурсов и завершение приложения."""
        if self.renderer:
            self.renderer.quit()
        glfw.terminate()
