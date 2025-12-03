import sys
import glfw
from core.app import App
from gui.hotkeys_window import HotkeysWindow
from core.graphics_engine import initialize_glfw


if __name__ == "__main__":
    """
    Точка входа в программу.
    Инициализирует GLFW, создает главное приложение и запускает цикл рендеринга.
    """

    try:
        # Инициализация GLFW и создание окна OpenGL
        window = initialize_glfw()

        # Создание основного приложения с переданным окном
        my_app = App(window)

        # Вызов окна с подсказками
        win = HotkeysWindow()
        win.show()

        # Запуск главного цикла приложения
        my_app.run()



    except Exception as e:
        print("Fatal error:", e)
        glfw.terminate()
        sys.exit(1)

