# main.py

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objs as go
import plotly.io as pio
import sys

class PlotlyWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. Erstelle einen Plotly-Plot
        fig = go.Figure(
            data=[go.Bar(x=["A", "B", "C"], y=[4, 7, 2])],
            layout_title_text="Beispiel Plotly Plot"
        )
        
        # 2. Generiere HTML-Code des Plots (ohne externe Dateien)
        html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")

        # 3. Lade das HTML im QWebEngineView
        self.setHtml(html)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plotly in PySide6 Demo")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Füge das Plotly-Widget zum Layout hinzu
        plotly_widget = PlotlyWidget()
        layout.addWidget(plotly_widget)
        
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
