'* 1\n'

from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from serial.tools import list_ports
import serial 
import sys 
from time import sleep as sl 

class LogicThread(QObject):
    status_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.baudrate = 9600
        self.port = [port.device for port in list_ports.comports()].pop()

        self.motor_running = False
        
        self.adc_vector = []
        self.adc_maxlen = 1024

        self.board = None

        self.thresh = 1000
        self.sensor_deg = 0

    def mean(self,arr):
        self.sensor_deg = sum(arr) / len(arr)

    def main_controller(self):
        if self.board:
            while self.motor_running:
                readed = self.board.readline()

                if readed:
                    decoded = readed.decode().strip().replace('\n','')
                    
                    if decoded.isdigit():
                        decoded = int(decoded)

                        if len(self.adc_vector) == self.adc_maxlen - 1:
                            self.adc_vector.pop(0)
                        
                        self.adc_vector.append(decoded)
                    
                    if len(self.adc_vector) > 1000:
                        self.mean(self.adc_vector)
                        self.motor_controller()
                else:
                    pass
            self.board.write(b'0\n')
            self.status_signal.emit('Manualy stop')
        else:
            pass

    def motor_controller(self):
        if self.board:
            if self.sensor_deg >= self.thresh:
                self.board.write(b'1\n')
                self.status_signal.emit('Motor rotating')
                
            elif self.sensor_deg < self.thresh:
                self.board.write(b'0\n')
                self.status_signal.emit('Motor e-stop')

        else:
            pass

    def initializer(self):
        self.board = serial.Serial(self.port,
                                   self.baudrate)
        sl(4.5)
        while True:
            self.main_controller()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(440,440)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        '''WIDGETS'''
        self.start_btn = QPushButton('start')
        self.stop_btn = QPushButton('stop')
        
        self.motor_status = QLabel('motor durumu: beklemede')
        self.motor_status.setAlignment(Qt.AlignCenter)
    
        main_layout.addWidget(self.motor_status)
        main_layout.addWidget(self.start_btn)
        main_layout.addWidget(self.stop_btn)

        self.logic_worker = LogicThread()
        self.worker_thread = QThread(self)
        self.logic_worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.logic_worker.initializer)
        self.logic_worker.status_signal.connect(self.thread_communication_function)
        self.worker_thread.start()

        self.start_btn.clicked.connect(self.start_motor)
        self.stop_btn.clicked.connect(self.stop_motor)

        self.setCentralWidget(main_widget)


    def start_motor(self):
        self.logic_worker.motor_running = True

    def stop_motor(self):
        self.logic_worker.motor_running = False

    def thread_communication_function(self,data):
        self.motor_status.setText(f'motor durumu: {data}')


if __name__ == "__main__":
    sp = QApplication(sys.argv)
    sw = MainWindow()
    sw.show()
    sys.exit(sp.exec_())
