import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QWidget, QLabel, QTabWidget, QScrollArea, QListWidget
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QFont
from PyQt5.QtCore import QRegularExpression, Qt

STYLE = """QWidget {
   font-size: 30px;
}"""

main_folder = r"/home/mstimberg/test_files"

replacements = {"." : ". \\pau=500\\"}

class PauseHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.darkBlue)
        keyword_format.setFontWeight(QFont.Bold)

        rule = QRegularExpression(r"\\pau=\d+\\")
        rule_iterator = rule.globalMatch(text)
        while rule_iterator.hasNext():
            match = rule_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), keyword_format)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI de Philippe")
        # Make window fullscreen
        self.showMaximized()

        self.central_layout = QVBoxLayout()
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout()
        top_bar.setLayout(top_bar_layout)
        self.title = QLabel("Insertion de pauses")
        top_bar_layout.addWidget(self.title)
        self.close_button = QPushButton("X")
        top_bar_layout.addStretch()
        self.close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(self.close_button)
        self.central_layout.addWidget(top_bar)
        self.layout = QHBoxLayout()
        top_bar.setStyleSheet("background-color: darkblue; color: white; padding: 10px;")

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.addLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # Tabbed interface for files
        self.file_tabs = QTabWidget()
        # Add a tab for recent files
        self.scroll_recent = QScrollArea()
        self.recent_file_list = QListWidget()
        self.scroll_recent.setWidget(self.recent_file_list)
        self.scroll_recent.setWidgetResizable(True)
        self.scroll_recent.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_recent.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.file_tabs.addTab(self.scroll_recent, "Fichiers récents")
        self.file_search = QWidget()
        self.file_tabs.addTab(self.file_search, "Recherche")
        self.layout.addWidget(self.file_tabs, stretch=1)

        self.text_layout = QVBoxLayout()
        self.text_title_layout = QHBoxLayout()
        filename = QLabel("Fichier: ")
        self.file_label = QLabel("")

        self.file_label.setStyleSheet("font-weight: bold;")
        self.text_title_layout.addWidget(filename)
        self.text_title_layout.addWidget(self.file_label)
        self.text_title_layout.addStretch()

        self.text_area = QHBoxLayout()
        self.textbox = QTextEdit()
        self.text_area.addWidget(self.textbox)
        self.text_layout.addLayout(self.text_title_layout)
        self.text_layout.addLayout(self.text_area)

        # Buttons
        self.buttons = QVBoxLayout()
        self.pause_button = QPushButton("+ pauses")
        self.pause_button.clicked.connect(self.add_pauses)
        self.buttons.addWidget(self.pause_button)
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save)
        self.buttons.addWidget(self.save_button)
        self.buttons.addStretch()
        self.text_area.addLayout(self.buttons)
        self.layout.addLayout(self.text_layout, stretch=2)
        self.filename = None
        self.highlighter = PauseHighlighter(self.textbox.document())
        self.style()
        self.files = os.listdir(main_folder)
        files = [(f, os.path.getmtime(os.path.join(main_folder, f))) for f in self.files]
        files = sorted(files, key=lambda x: x[1])
        self.recent_file_list.addItems([os.path.splitext(f)[0] for f, mtime in files])
        self.recent_file_list.itemClicked.connect(self.change_file)
        self.recent_file_list.setAlternatingRowColors(True)
        self.recent_file_list.setStyleSheet("alternate-background-color: white;background-color: #eeeeee;");

    def add_pauses(self):
        text = self.textbox.toPlainText()
        for replacement in replacements.items():
            text = text.replace(*replacement)
        self.textbox.setPlainText(text)

    def change_file(self, item):
        file = os.path.join(main_folder, item.text() + ".txt")  
        self.load_file(file)

    def select_file(self):
        pass

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
    app.setStyleSheet(STYLE)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    style(app)
    window.load_file(last_file_from_folder())
    app.exec_()
    