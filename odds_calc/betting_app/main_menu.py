from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout


class MainMenuWidget(QWidget):
   def __init__(self, switch_func):
      super().__init__()
      self.switch_func = switch_func
      self.init_ui()

   def init_ui(self):
      self.setStyleSheet("""
         QWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f5e1a4, stop:1 #d4a373);
         }
         QPushButton {
            background-color: #f0c040;
            border: 2px solid #d09030;
            border-radius: 5px;
            padding: 10px;
            font-size: 14pt;
         }
         QPushButton:hover {
            background-color: #f0d080;
         }
         QPushButton:pressed {
            background-color: #d09030;
         }
      """)
      layout = QHBoxLayout()
      layout.setContentsMargins(50, 50, 50, 50)
      layout.setSpacing(20)

      subtitle_label = QLabel("さあ、熱いレースに参加しましょう！")
      subtitle_label.setAlignment(Qt.AlignCenter)
      subtitle_label.setStyleSheet("font-size: 16pt; color: #4a2a0a;")
      layout.addWidget(subtitle_label)

      # ボタンを中央に配置するために水平レイアウトを使用
      btn_layout = QVBoxLayout()
      btn_layout.setSpacing(20)
      btn_layout.setAlignment(Qt.AlignCenter)

      btn_new = QPushButton("新規作成")
      btn_new.setFixedWidth(200)
      btn_new.clicked.connect(lambda: self.switch_func("new"))
      btn_layout.addWidget(btn_new)

      btn_load = QPushButton("JSONロード")
      btn_load.setFixedWidth(200)
      btn_load.clicked.connect(lambda: self.switch_func("load"))
      btn_layout.addWidget(btn_load)

      layout.addLayout(btn_layout)
      self.setLayout(layout)

