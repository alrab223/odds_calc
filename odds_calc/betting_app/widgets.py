from PyQt5.QtWidgets import QComboBox


class HorseNumberSelector(QComboBox):
   def __init__(self, min_val, max_val, parent=None):
      super().__init__(parent)
      self.setFixedWidth(60)
      for i in range(min_val, max_val + 1):
         self.addItem(str(i))

   def getValue(self):
      return int(self.currentText())
