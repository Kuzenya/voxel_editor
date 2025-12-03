from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea
from PySide6.QtCore import Qt


class ObjectListWindow(QWidget):
    """
    Окно со списком объектов сцены.
    Позволяет выделять объекты кликом по кнопкам и подсвечивает выделенные.
    """

    def __init__(self, scene):
        super().__init__()
        self.setWindowTitle("Object List")
        self.resize(200, 400)

        self.scene = scene
        self.buttons: list[QPushButton] = []

        self._build_ui()

    # ----------------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------------

    def _build_ui(self):
        """Создаёт ScrollArea с вертикальным layout для списка объектов."""
        self.main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(scroll)

        content = QWidget()
        self.scroll_layout = QVBoxLayout(content)
        scroll.setWidget(content)

        self.rebuild_list()

    def clear_layout(self, layout):
        """Полностью очищает переданный layout от виджетов."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    # ----------------------------------------------------------------------
    # Object List Management
    # ----------------------------------------------------------------------

    def rebuild_list(self):
        """Перестраивает список кнопок по текущим объектам сцены."""
        self.clear_layout(self.scroll_layout)
        self.buttons.clear()

        for index, entity in enumerate(self.scene.entities):
            name = f"voxel.{index}"

            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.entity_ref = entity  # ссылка на объект сцены
            btn.index = index

            # подсветка выделенных объектов
            if getattr(entity, "is_selected", False):
                btn.setStyleSheet("background-color: yellow;")
                btn.setChecked(True)
            else:
                btn.setStyleSheet("background-color: lightgray;")
                btn.setChecked(False)

            btn.clicked.connect(lambda checked, b=btn: self.toggle_selection(b))

            self.scroll_layout.addWidget(btn)
            self.buttons.append(btn)

        self.scroll_layout.addStretch()

    def toggle_selection(self, btn):
        """Меняет состояние выделения объекта и обновляет цвет кнопки."""
        entity = btn.entity_ref
        entity.is_selected = not entity.is_selected

        if entity.is_selected:
            btn.setStyleSheet("background-color: yellow;")
        else:
            btn.setStyleSheet("background-color: lightgray;")
