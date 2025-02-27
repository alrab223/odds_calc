from PyQt5.QtWidgets import (
   QWidget,
   QVBoxLayout,
   QHBoxLayout,
   QTabWidget,
   QTableWidget,
   QTableWidgetItem,
   QHeaderView,
   QMenu,
   QPushButton,
   QLabel,
   QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor, QBrush
import json
from odds_calc.betting_app.widgets import HorseNumberSelector
from odds_calc.betting_app.utils import get_frame_for_horse
from odds_calc.odds.calculator import Odds


class VoteInputWidget(QWidget):
   def __init__(self, data, filename, switch_func):
      super().__init__()
      self.data = data
      self.filename = filename
      self.switch_func = switch_func
      self.odds_calculator = Odds()
      self.tab_names = {
         "win": "単勝",
         "place": "複勝",
         "quinella": "馬連",
         "bracket_quinella": "枠連",
         "quinella_place": "ワイド",
         "exacta": "馬単",
         "trio": "三連複",
         "trifecta": "三連単",
      }
      self.trifecta_loaded = False
      self.table_widgets = {}
      self.filter_controls = {}
      self.full_data = {}
      for key in self.data:
         if key == "horse_starters":
            continue
         self.full_data[key] = list(self.data[key].items())
      self.init_ui()

   # 以下、init_ui, create_table_for_key, update_table, compute_odds, etc.
   # は元のコードと同様の実装とします。
   # 例:
   def init_ui(self):
      main_layout = QVBoxLayout()
      top_btn_layout = QHBoxLayout()
      btn_save_top = QPushButton("保存")
      btn_save_top.clicked.connect(self.save_votes)
      top_btn_layout.addStretch()
      top_btn_layout.addWidget(btn_save_top)
      main_layout.addLayout(top_btn_layout)

      self.tabs = QTabWidget()
      self.tabs.currentChanged.connect(self.on_tab_changed)
      main_layout.addWidget(self.tabs)

      for key in self.data:
         if key == "horse_starters":
            continue
         if key == "bracket_quinella" and self.data["horse_starters"] < 8:
            continue
         tab_name = self.tab_names.get(key, key)
         tab = QWidget()
         layout = QVBoxLayout()
         filter_layout = QHBoxLayout()
         if key not in ["trio", "trifecta"]:
            selector = HorseNumberSelector(1, self.data["horse_starters"])
            filter_layout.addWidget(selector)
            btn_filter = QPushButton("フィルタ")
            btn_filter.clicked.connect(lambda _, b=key: self.apply_filter(b))
            btn_reset = QPushButton("リセット")
            btn_reset.clicked.connect(lambda _, b=key: self.reset_filter(b))
            filter_layout.addWidget(btn_filter)
            filter_layout.addWidget(btn_reset)
            self.filter_controls[key] = {"selector": selector}
         else:
            selector1 = HorseNumberSelector(1, self.data["horse_starters"])
            selector2 = HorseNumberSelector(1, self.data["horse_starters"])
            filter_layout.addWidget(selector1)
            filter_layout.addWidget(selector2)
            btn_filter = QPushButton("フィルタ")
            btn_filter.clicked.connect(lambda _, b=key: self.apply_filter(b))
            btn_reset = QPushButton("リセット")
            btn_reset.clicked.connect(lambda _, b=key: self.reset_filter(b))
            filter_layout.addWidget(btn_filter)
            filter_layout.addWidget(btn_reset)
            self.filter_controls[key] = {"selector1": selector1, "selector2": selector2}
         filter_layout.addStretch()
         layout.addLayout(filter_layout)

         if key == "trifecta":
            self.table_widgets[key] = None
            layout.addWidget(QLabel("タブが選択されるとデータを読み込みます"))
         else:
            table = self.create_table_for_key(key, self.full_data[key])
            self.table_widgets[key] = table
            table.itemChanged.connect(self.on_table_item_changed)
            layout.addWidget(table)
         tab.setLayout(layout)
         self.tabs.addTab(tab, tab_name)

      bottom_layout = QHBoxLayout()
      btn_save_bottom = QPushButton("保存")
      btn_save_bottom.clicked.connect(self.save_votes)
      bottom_layout.addWidget(btn_save_bottom)
      btn_back = QPushButton("メニューに戻る")
      btn_back.clicked.connect(lambda: self.switch_func("menu"))
      bottom_layout.addWidget(btn_back)
      main_layout.addLayout(bottom_layout)

      self.setLayout(main_layout)

   def create_table_for_key(self, bet_type, data_list):
      table = QTableWidget()
      table.setProperty("bet_type", bet_type)
      table.setColumnCount(3)
      table.setRowCount(len(data_list))
      table.setHorizontalHeaderLabels(["買い目", "票数", "オッズ"])
      header = table.horizontalHeader()
      header.setSectionResizeMode(0, QHeaderView.Interactive)
      header.resizeSection(0, 100)
      header.setSectionResizeMode(1, QHeaderView.Interactive)
      header.resizeSection(1, 120)
      header.setSectionResizeMode(2, QHeaderView.Interactive)
      header.resizeSection(2, 100)
      header.sectionClicked.connect(
         lambda col, b=bet_type: self.handle_header_clicked(b, col)
      )
      odds_map = self.compute_odds(bet_type)
      for row, (vote_key, vote_value) in enumerate(data_list):
         item_key = QTableWidgetItem(vote_key)
         item_key.setFlags(Qt.ItemIsEnabled)
         if bet_type in ["win", "place"]:
            try:
               horse = int(vote_key)
               total = self.data["horse_starters"]
               frame = get_frame_for_horse(horse, total)
               color_map = {
                  1: "white",
                  2: "black",
                  3: "red",
                  4: "blue",
                  5: "yellow",
                  6: "green",
                  7: "orange",
                  8: "pink",
               }
               if frame in color_map:
                  item_key.setBackground(QBrush(QColor(color_map[frame])))
                  if color_map[frame] in ["black", "blue"]:
                     item_key.setForeground(QBrush(QColor("white")))
            except Exception:
               pass
         table.setItem(row, 0, item_key)
         item_value = QTableWidgetItem(str(vote_value))
         table.setItem(row, 1, item_value)
         odds_str = odds_map.get(vote_key, "0")
         item_odds = QTableWidgetItem(odds_str)
         item_odds.setFlags(Qt.ItemIsEnabled)
         table.setItem(row, 2, item_odds)
      return table

   def update_table(self, bet_type, new_data):
      table = self.table_widgets.get(bet_type)
      if table is None:
         return
      table.blockSignals(True)
      table.setRowCount(len(new_data))
      odds_map = self.compute_odds(bet_type)
      for row, (vote_key, vote_value) in enumerate(new_data):
         item_key = QTableWidgetItem(vote_key)
         item_key.setFlags(Qt.ItemIsEnabled)
         if bet_type in ["win", "place"]:
            try:
               horse = int(vote_key)
               total = self.data["horse_starters"]
               frame = get_frame_for_horse(horse, total)
               color_map = {
                  1: "white",
                  2: "black",
                  3: "red",
                  4: "blue",
                  5: "yellow",
                  6: "green",
                  7: "orange",
                  8: "pink",
               }
               if frame in color_map:
                  item_key.setBackground(QBrush(QColor(color_map[frame])))
                  if color_map[frame] in ["black", "blue"]:
                     item_key.setForeground(QBrush(QColor("white")))
            except Exception:
               pass
         table.setItem(row, 0, item_key)
         item_value = QTableWidgetItem(str(vote_value))
         table.setItem(row, 1, item_value)
         odds_str = odds_map.get(vote_key, "0")
         item_odds = QTableWidgetItem(odds_str)
         item_odds.setFlags(Qt.ItemIsEnabled)
         table.setItem(row, 2, item_odds)
      table.blockSignals(False)

   def compute_odds(self, bet_type):
      odds_mapping = {}
      if bet_type in [
         "win",
         "exacta",
         "quinella",
         "bracket_quinella",
         "trio",
         "trifecta",
      ]:
         wrapped = self.data
         odds_list = self.odds_calculator._calculate_basic_odds(wrapped, bet_type)
         for key, odd in zip(self.data[bet_type].keys(), odds_list):
            odds_mapping[key] = str(odd)
         for key in self.data[bet_type].keys():
            if key not in odds_mapping:
               odds_mapping[key] = "0"
      elif bet_type == "place":
         wrapped = self.data
         odds_list = self.odds_calculator.calculate_Place_Odds(wrapped)
         keys = list(self.data["place"].keys())
         for i, key in enumerate(keys):
            odds_mapping[key] = f"{odds_list[i][0]}~{odds_list[i][1]}"
      elif bet_type == "quinella_place":
         wrapped = self.data
         odds_dict = self.odds_calculator.calculate_Quinella_Place_Odds(wrapped)
         for key, vote in self.data["quinella_place"].items():
            tup = tuple(map(int, key.split("-")))
            if tup in odds_dict:
               val = odds_dict[tup]
               odds_mapping[key] = f"{val[0]}~{val[1]}"
            else:
               odds_mapping[key] = "0.0"
      return odds_mapping

   def update_all_odds(self):
      current_tab_index = self.tabs.currentIndex()
      if current_tab_index == -1:
         return
      current_bet_type = None
      for key, name in self.tab_names.items():
         if name == self.tabs.tabText(current_tab_index):
            current_bet_type = key
            break
      if current_bet_type and current_bet_type in self.table_widgets:
         table = self.table_widgets[current_bet_type]
         if table:
            odds_map = self.compute_odds(current_bet_type)
            table.blockSignals(True)
            for row in range(table.rowCount()):
               key_item = table.item(row, 0)
               if key_item:
                  key = key_item.text()
                  new_odds = odds_map.get(key, "0")
                  odds_item = table.item(row, 2)
                  if odds_item:
                     odds_item.setText(new_odds)
            table.blockSignals(False)

   def on_table_item_changed(self, item):
      table = item.tableWidget()
      bet_type = table.property("bet_type")
      if item.column() != 1:
         return
      row = item.row()
      key_item = table.item(row, 0)
      if not key_item:
         return
      key = key_item.text()
      try:
         value = int(item.text())
      except ValueError:
         value = 0
      self.data[bet_type][key] = value
      table.blockSignals(True)
      odds_map = self.compute_odds(bet_type)
      new_odds = odds_map.get(key, "0")
      odds_item = table.item(row, 2)
      if odds_item is None:
         odds_item = QTableWidgetItem(new_odds)
         odds_item.setFlags(Qt.ItemIsEnabled)
         table.setItem(row, 2, odds_item)
      else:
         odds_item.setText(new_odds)
      table.blockSignals(False)
      # 票数変更時に即時全体のオッズを更新する
      self.update_all_odds()

   def apply_filter(self, bet_type):
      full = self.full_data.get(bet_type, [])
      if bet_type in ["trio", "trifecta"]:
         selector1 = self.filter_controls[bet_type]["selector1"]
         selector2 = self.filter_controls[bet_type]["selector2"]
         val1 = str(selector1.getValue())
         val2 = str(selector2.getValue())
         filtered = [
            (k, v) for k, v in full if (val1 in k.split("-") and val2 in k.split("-"))
         ]
      else:
         selector = self.filter_controls[bet_type]["selector"]
         val = str(selector.getValue())
         filtered = [
            (k, v) for k, v in full if any(item == val for item in k.split("-"))
         ]
      self.update_table(bet_type, filtered)

   def reset_filter(self, bet_type):
      if bet_type in ["trio", "trifecta"]:
         self.filter_controls[bet_type]["selector1"].setCurrentIndex(0)
         self.filter_controls[bet_type]["selector2"].setCurrentIndex(0)
      else:
         self.filter_controls[bet_type]["selector"].setCurrentIndex(0)
      self.update_table(bet_type, self.full_data[bet_type])

   def handle_header_clicked(self, bet_type, col):
      table = self.table_widgets.get(bet_type)
      if table is None:
         return
      menu = QMenu()
      if col == 1:
         action1 = menu.addAction("票数昇順")
         action2 = menu.addAction("票数降順")
      elif col == 0:
         action1 = menu.addAction("馬番昇順")
         action2 = menu.addAction("馬番降順")
      action = menu.exec_(QCursor.pos())
      if action:
         rows = table.rowCount()
         data = []
         for row in range(rows):
            key_item = table.item(row, 0)
            val_item = table.item(row, 1)
            if key_item is None or val_item is None:
               continue
            try:
               vote_val = int(val_item.text())
            except ValueError:
               vote_val = 0
            data.append((key_item.text(), vote_val))
         if col == 1:
            if action.text() == "票数昇順":
               data.sort(key=lambda x: x[1])
            else:
               data.sort(key=lambda x: x[1], reverse=True)
         elif col == 0:
            if action.text() == "馬番昇順":
               data.sort(key=lambda x: [int(i) for i in x[0].split("-")])
            else:
               data.sort(key=lambda x: [int(i) for i in x[0].split("-")], reverse=True)
         self.update_table(bet_type, data)

   def on_tab_changed(self, index):
      if (
         self.tabs.tabText(index) == self.tab_names.get("trifecta")
         and not self.trifecta_loaded
      ):
         self.load_trifecta_tab()
         self.trifecta_loaded = True

   def load_trifecta_tab(self):
      trifecta_index = None
      for i in range(self.tabs.count()):
         if self.tabs.tabText(i) == self.tab_names.get("trifecta"):
            trifecta_index = i
            break
      if trifecta_index is None:
         return
      self.tabs.removeTab(trifecta_index)
      new_tab = QWidget()
      new_layout = QVBoxLayout(new_tab)
      filter_layout = QHBoxLayout()
      selector1 = HorseNumberSelector(1, self.data["horse_starters"])
      selector2 = HorseNumberSelector(1, self.data["horse_starters"])
      filter_layout.addWidget(selector1)
      filter_layout.addWidget(selector2)
      btn_filter = QPushButton("フィルタ")
      btn_filter.clicked.connect(lambda _, b="trifecta": self.apply_filter(b))
      btn_reset = QPushButton("リセット")
      btn_reset.clicked.connect(lambda _, b="trifecta": self.reset_filter(b))
      filter_layout.addWidget(btn_filter)
      filter_layout.addWidget(btn_reset)
      filter_layout.addStretch()
      new_layout.addLayout(filter_layout)
      self.filter_controls["trifecta"] = {
         "selector1": selector1,
         "selector2": selector2,
      }
      table = self.create_table_for_key("trifecta", self.full_data["trifecta"])
      self.table_widgets["trifecta"] = table
      table.itemChanged.connect(self.on_table_item_changed)
      new_layout.addWidget(table)
      new_tab.setLayout(new_layout)
      self.tabs.insertTab(trifecta_index, new_tab, self.tab_names.get("trifecta"))

   def save_votes(self):
      for bet_type, table in self.table_widgets.items():
         if table is None:
            continue
         row_count = table.rowCount()
         for row in range(row_count):
            key_item = table.item(row, 0)
            val_item = table.item(row, 1)
            if key_item is None or val_item is None:
               continue
            key_str = key_item.text()
            try:
               value = int(val_item.text())
            except ValueError:
               value = 0
            self.data[bet_type][key_str] = value
      try:
         with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
         QMessageBox.information(self, "保存完了", "票数が保存されました")
      except Exception as e:
         QMessageBox.critical(self, "保存エラー", f"票数の保存に失敗しました\n{e}")
