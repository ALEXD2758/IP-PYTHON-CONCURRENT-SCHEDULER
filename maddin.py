import asyncio
import json
import time
from typing import NamedTuple
import logging
import concurrent.futures

from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, \
    QHeaderView
import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class AnotherWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tableWidget = QTableWidget()
        self.title = 'PyQt5 - QTableWidget'
        self.left = 0
        self.top = 0
        self.width = 300
        self.height = 200

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

        # Show window
        self.show()

    def createTable(self):
        # Row count
        self.tableWidget.setRowCount(4)

        # Column count
        self.tableWidget.setColumnCount(2)

        self.tableWidget.setHorizontalHeaderLabels(['Task', 'Status'])

        self.tableWidget.setItem(0, 0, QTableWidgetItem("Name"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("City"))
        self.tableWidget.setItem(1, 0, QTableWidgetItem("Aloysius"))
        self.tableWidget.setItem(1, 1, QTableWidgetItem("Indore"))
        self.tableWidget.setItem(2, 0, QTableWidgetItem("Alan"))
        self.tableWidget.setItem(2, 1, QTableWidgetItem("Bhopal"))
        self.tableWidget.setItem(3, 0, QTableWidgetItem("Arnavi"))
        self.tableWidget.setItem(3, 1, QTableWidgetItem("Mandsaur"))

        # Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

    def addTableRow(self, table, row_data):
            row = table.rowCount()
            table.setRowCount(row+1)
            col = 0
            for item in row_data:
                cell = QTableWidgetItem(str(item))
                table.setItem(row, col, cell)
                col += 1


class Example(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None
        self.initUI()

    def initUI(self):
        self.btn_quit_window()
        self.btn_open_window()
        self.window_instantiation()

    def window_instantiation(self):
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Quit button')
        self.show()

    def btn_quit_window(self):
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(QApplication.instance().quit)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(25, 50)

    def btn_open_window(self):
        qbtn = QPushButton('Open report', self)
        qbtn.clicked.connect(self.show_new_window)
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(25, 100)

    def show_new_window(self):
        if self.w is None:
            self.w = AnotherWindow()
        self.w.show()

    def show_new_window1(self):
        if self.w is None:
            self.w = AnotherWindow()
        self.w.show()


class Tasks(NamedTuple):
    name: str
    type: str
    arguments: str
    dependencies: list


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

def coroutinemain(n):
    log = logging.getLogger(f"{n['name']}".upper())
    time.sleep(5)
    if "dependencies" in n:
        count = len(n['dependencies'])
        if count > 0:
            log.info('Started:')
            #start here the dependencies in a loop (calling coro1 or coro2)
            log.info(f'dependency array exist with: {count} item(s)')
            return f"{n['name']} : Failed"
        elif count == 0:
            return f"{n['name']} : OK"
    else:
        log.info('Started:')
        log.info('Ended:')
        return f"{n['name']} : OK"

    #completed, pending = await asyncio.wait(blocking_tasks)




async def run_blocking_tasks(executor):
    log = logging.getLogger('run_blocking_tasks')
    log.info('starting')

    with open('C:/Users/alex_/Documents/GIT REPOS/Scheduler/data/input1.json') as file:
        loaded_data = json.load(file)
    file.close

    # I should write down a while loop that take the loaded_data (with the 9 tasks) and each time that it executes
    # a task, send back a OK message and remove that element from loaded_data
    # from that while-loop and as long as there is a task inside the list
    # send back a FAILED message if there is an exception
    # all should happen inside blocking_tasks, I think
    # while length of list is still bigger
    log.info('creating executor tasks')
    loop = asyncio.get_event_loop()
    blocking_tasks = [
        loop.run_in_executor(executor, coroutinemain, i)
        # for i in range(6)
        for i in loaded_data["tasks"]
    ]
    log.info('waiting for executor tasks')
    completed, pending = await asyncio.wait(blocking_tasks)
    results = [t.result() for t in completed]
    # results = [t.result() for t in completed]
    log.info('results: {!r}'.format(results))

    log.info('exiting')


if __name__ == '__main__':
    # Configure logging to show the name of the thread
    # where the log message originates.
    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(message)18s %(name)s',
        stream=sys.stderr,
    )
    # Create a limited thread pool.
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=36,
    )

    event_loop = asyncio.get_event_loop()
    try:
        event_loop.run_until_complete(
            run_blocking_tasks(executor)
        )
    finally:
        event_loop.close()
    # start_time = time.time()
    # asyncio.run(mainrr())
    # end_time = time.time()
    # print(end_time - start_time)
    # readinputjson()
    # main()