from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QFileDialog, QMessageBox
import json
from odds_calc.betting_app.main_menu import MainMenuWidget
from odds_calc.betting_app.new_creation import NewCreationWidget
from odds_calc.betting_app.vote_input import VoteInputWidget

class VoteApp(QMainWindow):
   def __init__(self):
      super().__init__()
      self.setWindowTitle("投票入力システム")
      self.setGeometry(100, 100, 800, 600)
      self.filename = None
      self.data = None
      self.stack = QStackedWidget()
      self.setCentralWidget(self.stack)
      self.menu_page = MainMenuWidget(self.switch_page)
      self.new_page = NewCreationWidget(self.switch_page)
      self.vote_page = None
      self.stack.addWidget(self.menu_page)
      self.stack.addWidget(self.new_page)

   def switch_page(self, target, data=None, filename=None):
      if target == "menu":
         self.stack.setCurrentWidget(self.menu_page)
      elif target == "new":
         self.stack.setCurrentWidget(self.new_page)
      elif target == "load":
         self.load_json_file()
      elif target == "vote":
         self.data = data
         self.filename = filename
         if self.vote_page:
            self.stack.removeWidget(self.vote_page)
            self.vote_page.deleteLater()
         self.vote_page = VoteInputWidget(self.data, self.filename, self.switch_page)
         self.stack.addWidget(self.vote_page)
         self.stack.setCurrentWidget(self.vote_page)

   def load_json_file(self):
      filename, _ = QFileDialog.getOpenFileName(
         self, "JSONファイルを選択", "", "JSON files (*.json)"
      )
      if not filename:
         return
      try:
         with open(filename, "r", encoding="utf-8") as f:
            self.data = json.load(f)
      except Exception as e:
         QMessageBox.critical(
            self, "エラー", f"JSONファイルの読み込みに失敗しました\n{e}"
         )
         return
      self.filename = filename
      self.switch_page("vote", self.data, self.filename)
