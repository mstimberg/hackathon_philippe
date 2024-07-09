import datetime
import os

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QWidget,
    QLabel,
    QTabWidget,
    QListWidget,
    QLineEdit,
    QFileDialog,
    QToolButton,
    QStyledItemDelegate,
)
from PyQt5.QtGui import QTextCharFormat, QSyntaxHighlighter, QFont, QPixmap, QIcon
from PyQt5.QtCore import QRegularExpression, Qt, QSize
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME
import docx 
from appdirs import user_data_dir


STYLE = """
QWidget {
   font-size: 30px;
   background: 383B3C;
}
QListWidget {
    alternate-background-color: white;
    background-color: #f1f0f0;
    selection-color: black;
    selection-background-color: #ffb55d;
}
QTabWidget {
    background: #066791
}
QTabBar {
    icon-size: 48px 48px;
}
QTabBar::tab {
    padding: 10px;
    padding-top: 15px;
    padding-bottom: 15px;
}
QLineEdit {
    padding-top: 15px;
    padding-bottom: 15px;
}
"""

SCROLL_SIZE_TEXT = 750
SCROLL_SIZE_FILES = 500

main_folder = r"C:\Users\phili\Documents\Communicator 5\Philippe prédiction\My Text Files"

replacements = {
    "." : ". \\pau=500\\",
    "," : ", \\pau=100\\",
    ":" : ": \\pau=200\\",
    ";" : "; \\pau=200\\",
    "!" : "! \\pau=200\\",
    "?" : "? \\pau=200\\",
    "..." : "... \\pau=500\\"
}

def icon_fname(icon):
    return os.path.join(os.path.dirname(__file__), "icons", icon)

class PauseHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        keyword_format = QTextCharFormat()
        # keyword_format.setForeground(Qt.darkBlue)
        keyword_format.setFontWeight(QFont.Bold)

        rule = QRegularExpression(r"\\pau=\d+\\")
        rule_iterator = rule.globalMatch(text)
        while rule_iterator.hasNext():
            match = rule_iterator.next()
            self.setFormat(match.capturedStart(), match.capturedLength(), keyword_format)


class CustomDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        originalSize = super(CustomDelegate, self).sizeHint(option, index)
        # Set the height to a fixed value, keep the original width
        return QSize(originalSize.width(), 100) 


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI de Philippe")
        # Make window fullscreen
        self.showMaximized()
        self.showFullScreen()
        self.wrapper_layout = QHBoxLayout()
        self.central_layout = QVBoxLayout()
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout()
        top_bar.setLayout(top_bar_layout)
        self.title = QLabel("Insertion de pauses")
        top_bar_layout.addWidget(self.title)
        self.close_button = QPushButton(icon=QIcon(icon_fname("close.svg")))
        self.close_button.setIconSize(QSize(64, 64))
        top_bar_layout.addStretch()
        self.close_button.clicked.connect(self.close)
        top_bar_layout.addWidget(self.close_button)
        self.central_layout.addWidget(top_bar)
        self.layout = QHBoxLayout()
        top_bar.setStyleSheet("background-color: #066791; color: white; padding: 10px;")

        self.central_widget = QWidget()
        self.wrapper_layout.addLayout(self.central_layout)
        self.central_widget.setLayout(self.wrapper_layout)
        self.central_layout.addLayout(self.layout)
        self.wrapper_layout.addSpacing(275)
        self.setCentralWidget(self.central_widget)

        # Tabbed interface for files
        self.file_tabs = QTabWidget()
        self.file_tabs.setStyleSheet("")
        # Add a tab for recent files
        self.recent_with_buttons = QWidget()
        recent_layout = QHBoxLayout()
        self.recent_file_list = QListWidget()
        self.recent_file_list.setSpacing(10)
        self.recent_file_list.setWordWrap(True)
        recent_layout.addWidget(self.recent_file_list)
        recent_buttons = QVBoxLayout()
        recent_buttons.addStretch()
        caret_up = QIcon(icon_fname("chevron-up.svg"))
        caret_down = QIcon(icon_fname("chevron-down.svg"))
        self.recent_up_button = QPushButton(icon=caret_up)
        self.recent_up_button.setIconSize(QSize(48, 48))
        self.recent_up_button.setMinimumWidth(64)
        self.recent_down_button = QPushButton(icon=caret_down)
        self.recent_down_button.setIconSize(QSize(48, 48))
        self.recent_down_button.setMinimumWidth(64)
        self.recent_up_button.clicked.connect(lambda: self.recent_file_list.verticalScrollBar().setValue(self.recent_file_list.verticalScrollBar().value() - SCROLL_SIZE_FILES))
        self.recent_down_button.clicked.connect(lambda: self.recent_file_list.verticalScrollBar().setValue(self.recent_file_list.verticalScrollBar().value() + SCROLL_SIZE_FILES))
        recent_buttons.addWidget(self.recent_up_button)
        recent_buttons.addWidget(self.recent_down_button)
        recent_layout.addLayout(recent_buttons)
        self.recent_with_buttons.setLayout(recent_layout)
        recent_icon = QIcon(icon_fname("clock.svg"))
        self.file_tabs.addTab(self.recent_with_buttons, recent_icon, "Fichiers récents")
        search_widget = QWidget()
        search_layout_with_buttons = QHBoxLayout()
        search_layout = QVBoxLayout()
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Mots-clés...")
        self.search_entry.textChanged.connect(self.search)
        self.search_file_list = QListWidget()
        self.search_file_list.setSpacing(10)
        self.search_file_list.setWordWrap(True)
        search_layout.addWidget(self.search_entry)
        search_layout.addWidget(self.search_file_list)
        search_layout_with_buttons.addLayout(search_layout)
        search_button_layout = QVBoxLayout()
        self.clear_search_button = QToolButton(self)
        self.clear_search_button.setText("Supprimer\nrecherche")
        self.clear_search_button.setIcon(QIcon(icon_fname("delete.svg")))
        self.clear_search_button.setIconSize(QSize(64, 64))
        self.clear_search_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.clear_search_button.clicked.connect(lambda: self.search_entry.clear())
        search_button_layout.addWidget(self.clear_search_button)
        search_button_layout.addStretch()
        self.search_up_button = QPushButton(icon=caret_up)
        self.search_up_button.setIconSize(QSize(48, 48))
        self.search_down_button = QPushButton(icon=caret_down)
        self.search_down_button.setIconSize(QSize(48, 48))
        self.search_up_button.clicked.connect(lambda: self.search_file_list.verticalScrollBar().setValue(self.search_file_list.verticalScrollBar().value() - SCROLL_SIZE_FILES))
        self.search_down_button.clicked.connect(lambda: self.search_file_list.verticalScrollBar().setValue(self.search_file_list.verticalScrollBar().value() + SCROLL_SIZE_FILES))
        search_button_layout.addWidget(self.search_up_button)
        search_button_layout.addWidget(self.search_down_button)
        search_layout_with_buttons.addLayout(search_button_layout)
        search_widget.setLayout(search_layout_with_buttons)
        search_icon = QIcon(icon_fname("recherche-mot-clé.svg"))
        self.file_tabs.addTab(search_widget, search_icon, "Mot-clé")
        self.layout.addWidget(self.file_tabs, stretch=2)

        self.text_layout = QVBoxLayout()
        self.text_title_layout = QHBoxLayout()
        filename = QLabel("Fichier: ")
        self.file_label = QLabel("")
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet("font-weight: bold;")
        self.text_title_layout.addWidget(filename)
        self.text_title_layout.addWidget(self.file_label)
        self.text_title_layout.addStretch()

        self.text_area = QWidget()
        layout = QHBoxLayout()
        self.textbox = QTextEdit()
        layout.addWidget(self.textbox)
        self.text_layout.addLayout(self.text_title_layout)
        self.text_layout.addLayout(layout)

        # Buttons
        self.buttons = QVBoxLayout()
        self.pause_button = QToolButton(self)
        self.pause_button.setText("Insérer pauses")
        keyboard_icon = QIcon(icon_fname("keyboard.svg"))
        self.pause_button.setIcon(keyboard_icon)
        self.pause_button.setIconSize(QSize(64, 64))
        self.pause_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.pause_button.clicked.connect(self.add_pauses)
        self.buttons.addWidget(self.pause_button)
        self.save_button = QToolButton(self)
        self.save_button.setText("Enregistrer")
        save_icon = QIcon(icon_fname("save.svg"))
        self.save_button.setIconSize(QSize(64, 64))
        self.save_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.save_button.setIcon(save_icon)
        self.save_button.clicked.connect(self.save)
        self.buttons.addWidget(self.save_button)
        self.buttons.addStretch()
        self.text_up_button = QPushButton(icon=caret_up)
        self.text_up_button.setIconSize(QSize(48, 48))
        self.text_down_button = QPushButton(icon=caret_down)
        self.text_down_button.setIconSize(QSize(48, 48))
        # Scroll area on button push
        self.text_up_button.clicked.connect(lambda: self.textbox.verticalScrollBar().setValue(self.textbox.verticalScrollBar().value() - SCROLL_SIZE_TEXT))
        self.text_down_button.clicked.connect(lambda: self.textbox.verticalScrollBar().setValue(self.textbox.verticalScrollBar().value() + SCROLL_SIZE_TEXT))
        self.buttons.addWidget(self.text_up_button)
        self.buttons.addWidget(self.text_down_button)
        layout.addLayout(self.buttons)
        self.text_area.setLayout(layout)
        self.text_area.setStyleSheet("background: #066791")
        self.layout.addLayout(self.text_layout, stretch=3)
        self.filename = None
        self.highlighter = PauseHighlighter(self.textbox.document())
        self.style()

        if os.path.exists(main_folder):
            self.folder = main_folder
        else:
            # Ask the user to select a folder
            folder = QFileDialog.getExistingDirectory(self, "Sélectionnez un dossier")
            self.folder = folder

        self.files = os.listdir(self.folder)
        self.files = [(f, os.path.getmtime(os.path.join(self.folder, f))) for f in self.files]
        self.files = sorted(self.files, key=lambda x: x[1])
        delegate = CustomDelegate()
        self.recent_file_list.setItemDelegate(delegate)
        self.recent_file_list.addItems(
            [os.path.splitext(f)[0] for f, mtime in self.files]
        )
        self.recent_file_list.itemClicked.connect(self.change_file)
        self.recent_file_list.setAlternatingRowColors(True)
        self.recent_file_list.setCurrentRow(0)
        self.recent_file_list.setWordWrap(True)

        self.load_file(os.path.join(self.folder, self.find_file(self.recent_file_list.currentItem().text())))

        self.search_file_list.itemClicked.connect(self.change_file)
        self.search_file_list.addItems(sorted([os.path.splitext(f)[0] for f, mtime in self.files]))
        self.search_file_list.setAlternatingRowColors(True)

        index_path = os.path.join(user_data_dir("recherche", "TOM"), "indexdir")
        if not os.path.exists(index_path):
            os.makedirs(index_path)
        schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True), modified=DATETIME(stored=True))
        self.search_index = index.create_in(index_path, schema)
        writer = self.search_index.writer()
        for fname, mtime in self.files:
            full_fname = os.path.join(self.folder, fname)
            content = self.open_file(full_fname)
            writer.add_document(title=os.path.splitext(fname)[0],
                                path=full_fname,
                                content=content,
                                modified=datetime.datetime.fromtimestamp(mtime))
        writer.commit()

    def find_file(self, fname):
        for f, mtime in self.files:
            if os.path.splitext(f)[0] == fname:
                return f
        return None

    def open_file(self, full_fname):
        try:
            if full_fname.endswith(".txt"):
                with open(full_fname, "r", encoding="utf-8") as f:
                    content = f.read()
            elif full_fname.endswith(".docx"):
                doc = docx.Document(full_fname)
                content = '\n'.join([para.text for para in doc.paragraphs])
            else:
                print(f"file format for {full_fname} not supported")
                content = "[Format de fichier non supporté]"
        except Exception as e:
            print(f"Error opening {full_fname}: {e}")
            content = "[Erreur lors de l'ouverture du fichier]"

        return content

    def search(self):
        with self.search_index.searcher() as searcher:
            query = self.search_entry.text()
            if not query.endswith(" "):
                query += "*"
            results = searcher.find("title", query, limit=20)
            results_content = searcher.find("content", query, limit=20)
            results.upgrade_and_extend(results_content)
            self.search_file_list.clear()
            self.search_file_list.addItems([hit["title"] for hit in results])

    def add_pauses(self):
        text = self.textbox.toPlainText()
        for replacement in replacements.items():
            text = text.replace(*replacement)
        self.textbox.setPlainText(text)

    def change_file(self, item):
        file = os.path.join(self.folder, self.find_file(item.text()))  
        self.load_file(file)

    def save(self):
        with open(self.filename, "w") as f:
            f.write(self.textbox.toPlainText())

    def load_file(self, file):
        content = self.open_file(file)
        self.textbox.setPlainText(content)
        self.file_label.setText(os.path.splitext(os.path.basename(file))[0])
        self.save_button.setEnabled(content is not None and len(content)>0 and not content.startswith("["))

def style(app):
    app.setStyleSheet(STYLE)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    style(app)
    app.exec_()
