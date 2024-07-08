import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QWidget, QLabel

main_folder = r"/home/mstimberg/test_files"

replacements = {"." : ". \\pau=500\\"}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI de Philippe")
        # Make window fullscreen
        self.showMaximized()

        self.layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.file_label = QLabel("")
        self.layout.addWidget(self.file_label)
        self.textbox = QTextEdit()
        self.layout.addWidget(self.textbox)

        # Buttons
        self.buttons = QHBoxLayout()
        self.pause_button = QPushButton("+ pauses")
        self.pause_button.clicked.connect(self.add_pauses)
        self.buttons.addWidget(self.pause_button)
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save)
        self.buttons.addWidget(self.save_button)
        self.close_button = QPushButton("Fermer")
        self.close_button.clicked.connect(self.close)
        self.buttons.addWidget(self.close_button)
        self.layout.addLayout(self.buttons)
        self.filename = None
        self.style()

    def add_pauses(self):
        text = self.textbox.toPlainText()
        for replacement in replacements.items():
            text = text.replace(*replacement)
        self.textbox.setPlainText(text)


    def save(self):
        with open(self.filename, "w") as f:
            f.write(self.textbox.toPlainText())

    def load_file(self, file):
        self.filename = file
        with open(file, "r") as f:
            self.textbox.setPlainText(f.read())
        self.file_label.setText(os.path.splitext(os.path.basename(file))[0])


def last_file_from_folder():
    # Get the file that was last modified
    files = os.listdir(main_folder)
    files = [f for f in files if f.endswith(".txt")]
    files = [os.path.join(main_folder, f) for f in files]
    files = [(f, os.path.getmtime(f)) for f in files]
    files = sorted(files, key=lambda x: x[1])
    return files[-1][0]


def style(app):
    app.setStyleSheet("""QWidget {
                            font-size: 30px;
                         }
                      
                         QPushButton {
                            padding: 10px;
                         }""")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.load_file(last_file_from_folder())
    style(app)
    app.exec_()
    