from PyQt5 import Qt
from colVars import ColVars as Col

app = Qt.QApplication([])
wid = Qt.QWidget()
lab = Qt.QLabel(Col.CGREENBG + 'hello' + Col.CEND, wid)
wid.show()
app.exec_()
