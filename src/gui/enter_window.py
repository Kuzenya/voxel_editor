from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton


class SimpleInputDialog(QDialog):
    """
    Простое модальное окно для ввода текста (например, имени файла).
    """

    def __init__(self, default_text: str = ""):
        super().__init__()
        self.setWindowTitle("Введите имя файла")

        # Здесь будет сохранён результат после закрытия окна
        self.result_text: str | None = None

        # --- Layout ---
        layout = QVBoxLayout()

        # Текстовое поле для ввода
        self.line_edit = QLineEdit()
        self.line_edit.setText(default_text)
        layout.addWidget(self.line_edit)

        # Кнопка OK для подтверждения ввода
        ok_button = QPushButton("OK")
        layout.addWidget(ok_button)
        ok_button.clicked.connect(self.on_ok)

        # Устанавливаем layout
        self.setLayout(layout)

        # Enter в поле также подтверждает ввод
        self.line_edit.returnPressed.connect(self.on_ok)

    # ----------------------------------------------------------------------
    # Handlers
    # ----------------------------------------------------------------------

    def on_ok(self):
        """
        Сохраняет введённый текст и закрывает диалог с кодом accept().
        """
        self.result_text = self.line_edit.text().strip()
        self.accept()


