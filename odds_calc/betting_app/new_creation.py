from PyQt5.QtWidgets import (
   QWidget,
   QVBoxLayout,
   QLabel,
   QLineEdit,
   QPushButton,
   QFileDialog,
   QMessageBox,
)
from odds_calc.betting_app import data_manager
from PyQt5.QtCore import Qt

class NewCreationWidget(QWidget):
   def __init__(self, switch_func):
      super().__init__()
      self.switch_func = switch_func
      self.init_ui()

   def init_ui(self):
      layout = QVBoxLayout()
      label = QLabel("頭数を入力してください")
      label.setAlignment(Qt.AlignCenter)
      label.setStyleSheet("font-size: 14pt;")
      layout.addWidget(label)
      self.horse_edit = QLineEdit()
      self.horse_edit.setText("7")
      self.horse_edit.setMaximumWidth(100)
      layout.addWidget(self.horse_edit, alignment=Qt.AlignCenter)
      btn_create = QPushButton("作成")
      btn_create.clicked.connect(self.create_json)
      layout.addWidget(btn_create, alignment=Qt.AlignCenter)
      btn_back = QPushButton("戻る")
      btn_back.clicked.connect(lambda: self.switch_func("menu"))
      layout.addWidget(btn_back, alignment=Qt.AlignCenter)
      self.setLayout(layout)

   def create_json(self):
      try:
         horse_starters = int(self.horse_edit.text())
      except ValueError:
         QMessageBox.critical(self, "エラー", "頭数は数値で入力してください")
         return
      data = data_manager.create_vote_data_with_bracket(horse_starters)
      filename, _ = QFileDialog.getSaveFileName(
         self, "保存先を選択", "", "JSON files (*.json)"
      )
      if not filename:
         return
      data_manager.save_vote_data(filename, data)
      QMessageBox.information(self, "完了", f"JSONファイルが作成されました\n{filename}")
      self.switch_func("vote", data, filename)
