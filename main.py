import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg

class Stock:
    def __init__(self, name, initial_price, color):
        self.name = name
        self.price = initial_price
        self.history = [initial_price]
        self.color = color

    def update_price(self):
        change = random.uniform(-0.1, 0.1)
        self.price *= (1 + change)
        self.history.append(self.price)

class Player:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.portfolio = {}

    def buy(self, stock, quantity):
        cost = stock.price * quantity
        if cost <= self.cash:
            self.cash -= cost
            self.portfolio[stock.name] = self.portfolio.get(stock.name, 0) + quantity
            return True
        return False

    def sell(self, stock, quantity):
        if stock.name in self.portfolio and self.portfolio[stock.name] >= quantity:
            self.cash += stock.price * quantity
            self.portfolio[stock.name] -= quantity
            if self.portfolio[stock.name] == 0:
                del self.portfolio[stock.name]
            return True
        return False

class StockMarketGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Market Simulator")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.init_game()
        self.init_ui()

    def init_game(self):
        self.stocks = self.generate_stocks()
        self.player = Player(1000)
        self.day = 0

    def generate_stocks(self):
        stock_names = ["AAPL", "GOOGL", "MSFT", "AMZN"]
        colors = ['r', 'g', 'b', 'y']
        return [Stock(name, random.uniform(50, 200), color) for name, color in zip(stock_names, colors)]

    def init_ui(self):
        # Stock chart
        self.chart = pg.PlotWidget()
        self.layout.addWidget(self.chart)

        # Stock table
        self.stock_table = QTableWidget(4, 2)
        self.stock_table.setHorizontalHeaderLabels(["Stock", "Price"])
        self.stock_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.stock_table)

        # Player info
        player_info_layout = QHBoxLayout()
        self.cash_label = QLabel(f"Cash: ${self.player.cash:.2f}")
        self.day_label = QLabel(f"Day: {self.day}")
        player_info_layout.addWidget(self.cash_label)
        player_info_layout.addWidget(self.day_label)
        self.layout.addLayout(player_info_layout)

        # Trade controls
        trade_layout = QHBoxLayout()
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("Stock name")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantity")
        self.buy_button = QPushButton("Buy")
        self.sell_button = QPushButton("Sell")
        trade_layout.addWidget(self.stock_input)
        trade_layout.addWidget(self.quantity_input)
        trade_layout.addWidget(self.buy_button)
        trade_layout.addWidget(self.sell_button)
        self.layout.addLayout(trade_layout)

        # Preview label
        self.preview_label = QLabel()
        self.layout.addWidget(self.preview_label)

        # Next day button
        self.next_day_button = QPushButton("Next Day")
        self.layout.addWidget(self.next_day_button)

        # Connect buttons to functions
        self.buy_button.clicked.connect(self.buy_stock)
        self.sell_button.clicked.connect(self.sell_stock)
        self.next_day_button.clicked.connect(self.next_day)
        self.stock_input.textChanged.connect(self.update_preview)
        self.quantity_input.textChanged.connect(self.update_preview)

        # Update UI
        self.update_ui()

        # Start timer for automatic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_day)
        self.timer.start(2000)  # Update every 2 seconds

    def update_ui(self):
        # Update stock table
        for i, stock in enumerate(self.stocks):
            name_item = QTableWidgetItem(stock.name)
            name_item.setForeground(QColor(stock.color))
            self.stock_table.setItem(i, 0, name_item)
            self.stock_table.setItem(i, 1, QTableWidgetItem(f"${stock.price:.2f}"))

        # Update chart
        self.chart.clear()
        for stock in self.stocks:
            pen = pg.mkPen(color=stock.color, width=2)
            self.chart.plot(stock.history, name=stock.name, pen=pen)

        # Update player info
        self.cash_label.setText(f"Cash: ${self.player.cash:.2f}")
        self.day_label.setText(f"Day: {self.day}")

    def update_preview(self):
        stock_name = self.stock_input.text().upper()
        quantity_text = self.quantity_input.text()
        
        if stock_name and quantity_text:
            try:
                quantity = int(quantity_text)
                stock = next((s for s in self.stocks if s.name == stock_name), None)
                if stock:
                    buy_value = stock.price * quantity
                    sell_value = stock.price * quantity
                    self.preview_label.setText(f"Buy: ${buy_value:.2f} | Sell: ${sell_value:.2f}")
                else:
                    self.preview_label.setText("Invalid stock name")
            except ValueError:
                self.preview_label.setText("Invalid quantity")
        else:
            self.preview_label.setText("")

    def buy_stock(self):
        stock_name = self.stock_input.text().upper()
        quantity = int(self.quantity_input.text())
        stock = next((s for s in self.stocks if s.name == stock_name), None)
        
        if stock:
            if self.player.buy(stock, quantity):
                QMessageBox.information(self, "Success", "Purchase successful")
            else:
                QMessageBox.warning(self, "Error", "Not enough cash")
        else:
            QMessageBox.warning(self, "Error", "Invalid stock name")

        self.update_ui()

    def sell_stock(self):
        stock_name = self.stock_input.text().upper()
        quantity = int(self.quantity_input.text())
        stock = next((s for s in self.stocks if s.name == stock_name), None)
        
        if stock:
            if self.player.sell(stock, quantity):
                QMessageBox.information(self, "Success", "Sale successful")
            else:
                QMessageBox.warning(self, "Error", "Not enough stocks")
        else:
            QMessageBox.warning(self, "Error", "Invalid stock name")

        self.update_ui()

    def next_day(self):
        self.day += 1
        for stock in self.stocks:
            stock.update_price()
        self.update_ui()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = StockMarketGame()
    game.show()
    sys.exit(app.exec_())