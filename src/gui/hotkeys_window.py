from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

class HotkeysWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Подсказка по горячим клавишам")
        self.setMinimumSize(500, 600)

        # Основной цветовой стиль окна
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #d3d3d3;
                font-size: 14px;
            }
            QLabel {
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Заголовок
        title = QLabel("Горячие клавиши и инструкции")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Текст инструкции
        instructions = QLabel(self._get_text())
        instructions.setWordWrap(True)
        instructions.setFont(QFont("Arial", 12))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(instructions)
        scroll.setStyleSheet("QScrollArea { background-color: #2b2b2b; }")

        layout.addWidget(scroll)

    def _get_text(self):
        """Возвращает текст инструкции и горячих клавиш."""
        return (
            "Навигация камеры:\n"
            "  • W — движение вперёд\n"
            "  • S — движение назад\n"
            "  • A — смещение влево\n"
            "  • D — смещение вправо\n"
            "  • Перемещение мыши + Shift — поворот камеры\n\n"
            "Работа с объектами:\n"
            "  • N + X/Y/Z — добавить воксель по выбранной оси\n"
            "  • G + X/Y/Z — переместить выделенный воксель\n"
            "  • Delete — удалить выделенный воксель\n"
            "  • Левая кнопка мыши — выбор вокселя\n\n"
            "Материалы:\n"
            "  • C — открыть окно редактирования цвета\n"
            "      (R, G, B, A — параметры цвета от 1 до 100)\n\n"
            "Сцена:\n"
            "  • O — открыть список объектов сцены\n"
            "  • M — сохранить сцену в файл\n"
            "  • Ctrl + M — загрузить сохранённую сцену\n"
            "  • Escape — выход из приложения\n\n"
            "Все сохраняемые проекты размещаются в папке 'Scene'.\n"
            "Рекомендуется регулярно сохранять изменения."
        )
