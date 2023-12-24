import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QPushButton, QFileDialog, QComboBox,QDialog,QCheckBox

import requests
from requests import Session, Request

class HttpRequestBuilderApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Создаем виджеты
        self.ext_data = ''
        self.host_label = QLabel('Host:')
        self.host_edit = QLineEdit()

        self.method_label = QLabel('Method:')
        self.method_combo = QComboBox()
        self.method_combo.addItems(['GET', 'POST', 'PUT', 'DELETE','HEAD','CONNECT','OPTIONS','TRACE','PATCH'])

        self.scheme_label = QLabel('Scheme:')
        self.scheme_edit = QLineEdit()

        self.uri_label = QLabel('URI:')
        self.uri_edit = QLineEdit()

        self.headers_label = QLabel('Headers:')
        self.headers_edit = QTextEdit()

        self.body_label = QLabel('Body:')
        self.body_edit = QTextEdit()

        self.extended_label = QLabel('Extended data:')
        self.exteded_name = QLabel('')
        self.iscrlf =QCheckBox('Add CRLFCRLF after body')
        self.load_file_button = QPushButton('Load Body from File')
        self.load_extended_button = QPushButton('Load Extended binary data from File')
        self.delete_extended_button = QPushButton('Delete Extended data')
        self.send_request_button = QPushButton('Send Request')
        self.save_request_button = QPushButton('Save Request')

        # Создаем компоновщик для размещения виджетов
        layout = QVBoxLayout()
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_edit)
        layout.addWidget(self.method_label)
        layout.addWidget(self.method_combo)
        layout.addWidget(self.scheme_label)
        layout.addWidget(self.scheme_edit)
        layout.addWidget(self.uri_label)
        layout.addWidget(self.uri_edit)
        layout.addWidget(self.headers_label)
        layout.addWidget(self.headers_edit)
        layout.addWidget(self.body_label)
        layout.addWidget(self.body_edit)
        layout.addWidget(self.extended_label)
        layout.addWidget(self.exteded_name)
        layout.addWidget(self.iscrlf)
        layout.addWidget(self.load_file_button)
        layout.addWidget(self.load_extended_button)
        layout.addWidget(self.delete_extended_button)
        layout.addWidget(self.send_request_button)
        layout.addWidget(self.save_request_button)

        # Создаем основной виджет и устанавливаем в него компоновщик
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.headers_edit.setText('User-Agent:Mozilla/5.0\nContent-Length:8')
        self.host_edit.setText('example.com')
        self.scheme_edit.setText('http')
        self.uri_edit.setText('/your_page')
        self.body_edit.setText('YourData')
        # Подключаем обработчики событий
        self.load_file_button.clicked.connect(self.load_body_from_file)
        self.load_extended_button.clicked.connect(self.load_extendend_from_file)
        self.delete_extended_button.clicked.connect(self.delete_extended)        
        self.send_request_button.clicked.connect(self.send_request)
        self.save_request_button.clicked.connect(self.save_request)

        # Устанавливаем заголовок окна
        self.setWindowTitle('HTTP Request Builder')
    
    def load_extendend_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*)')
        if file_path:
            with open(file_path, 'rb') as file:
                self.ext_data = file.read()
                self.exteded_name.setText(file_path)
    def delete_extended(self):
        self.ext_data = ''
        self.exteded_name.setText('')
    def load_body_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*)')
        if file_path:
            with open(file_path, 'rb') as file:
                filebytes = file.read().decode()
                self.body_edit.setPlainText(filebytes)

    def send_request(self):
        url = f"{self.scheme_edit.text()}://{self.host_edit.text()}{self.uri_edit.text()}"
        method = self.method_combo.currentText()
        headers = {header.split(':')[0]: header.split(':')[1] for header in self.headers_edit.toPlainText().split('\n') if header}
        body = self.body_edit.toPlainText().encode()
        if self.ext_data != '':
            if self.iscrlf.isChecked():
                body+=b'\r\n\r\n'
            body+=self.ext_data
        s = Session()
        #s.proxies=proxies
        s.verify=False
        req = Request(method, url, data=body)
        prepped = req.prepare()
        prepped.headers = {}
        s.headers = {}
        for h in prepped.headers:
            del prepped.headers[h]
        for head in headers:
            prepped.headers[head]=headers[head]
        response = s.send(prepped)
        self.show_response(response)

    def save_request(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Request', '', 'All Files (*)')
        if file_path:
            with open(file_path, 'wb') as file:
                file.write(self.get_raw_request())

    def get_raw_request(self):
        method = self.method_combo.currentText()
        headers = ''
        for header in self.headers_edit.toPlainText().split('\n'):
            headers+=header+'\r\n'
        #headers = self.headers_edit.toPlainText()
        body = self.body_edit.toPlainText()
        uri =self.uri_edit.text()
        raw_request = f'{method} {uri} HTTP/1.1\r\n{headers}\r\n{body}'
        return raw_request.encode()

    def show_response(self, response):
        # Пример обработки ответа (можете изменить в соответствии с вашими нуждами)
        response_text = f"Status Code: {response.status_code}\n\n{response.text}"
        response_window = QDialog(self)
        response_window.setWindowTitle('Response')
        response_window.setGeometry(100, 100, 800, 600)

        response_layout = QVBoxLayout()
        response_label = QLabel(response_text)
        response_layout.addWidget(response_label)

        response_window.setLayout(response_layout)
        response_window.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HttpRequestBuilderApp()
    window.show()
    sys.exit(app.exec_())
