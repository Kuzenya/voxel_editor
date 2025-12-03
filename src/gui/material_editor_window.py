import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit
from src.core.material import Material


class MaterialEditorWindow(QWidget):
    """
    Окно редактирования материала для выделенных объектов сцены.
    Позволяет изменять компоненты RGBA и применяет их ко всем выделенным объектам.
    """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Изменить материал")
        self.setMinimumWidth(220)

        layout = QVBoxLayout()

        # Словарь для хранения полей ввода RGBA
        self.fields: dict[str, QLineEdit] = {}

        # Создаем поля ввода для R, G, B, A
        for comp in ["R", "G", "B", "A"]:
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{comp}:"))
            edit = QLineEdit("50")  # значение по умолчанию 50 → 0.5
            edit.setMaxLength(6)
            self.fields[comp] = edit
            row.addWidget(edit)
            layout.addLayout(row)

        # Кнопка "Применить"
        apply_btn = QPushButton("Применить")
        apply_btn.clicked.connect(self.apply_material)
        layout.addWidget(apply_btn)

        self.setLayout(layout)

    # ----------------------------------------------------------------------
    # Material Application
    # ----------------------------------------------------------------------

    def apply_material(self):
        """
        Применяет новые значения RGBA ко всем выделенным объектам.
        Формула: value = (input % 101) / 100.0
        Обрабатывает как целые, так и десятичные значения, безопасно.
        """

        selected = self.app.scene.get_all_selected()
        if not selected:
            print("[MaterialEditor] Нет выделенных объектов")
            return

        def parse_field(name: str) -> float:
            txt = self.fields[name].text().strip()
            if txt == "":
                return 0.5  # default value
            try:
                value = float(txt)
            except ValueError:
                raise ValueError(f"Поле {name} должно быть числом")
            return (value % 101.0) / 100.0

        try:
            r, g, b, a = (parse_field(comp) for comp in ["R", "G", "B", "A"])
        except ValueError as e:
            print("[MaterialEditor] Ошибка:", e)
            return

        print(f"[MaterialEditor] Применяем RGBA = {r:.2f}, {g:.2f}, {b:.2f}, {a:.2f} к {len(selected)} объектам")

        # Обновляем материал каждого выделенного объекта
        for obj in selected:
            if hasattr(obj, "material") and isinstance(obj.material, Material):
                obj.material.color = np.array([r, g, b, a], dtype=np.float32)
            else:
                obj.material = Material(r, g, b, a)

        # Закрываем окно после применения
        self.close()
