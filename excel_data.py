import openpyxl
import os


class ExcelData:
    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.path_to_file = self.dir_path + os.sep + 'data.xlsx'
        self.workbook = openpyxl.Workbook()
        self.workbook.save(self.path_to_file)
        self.workbook = openpyxl.load_workbook(self.path_to_file)
        self.worksheet = self.workbook.active
        self.count = 1

        self.worksheet['A' + str(self.count)] = 'HOSTNAMES'
        self.worksheet['B' + str(self.count)] = 'TELNET'
        self.worksheet['C' + str(self.count)] = 'SSH'
        self.worksheet['D' + str(self.count)] = 'VERSION'
        self.worksheet['E' + str(self.count)] = 'SERIALNUMBER'

    def next_row(self):
        self.count += 1

    def close(self):
        self.workbook.save(self.path_to_file)

    def status_to_text(self, status):
        return 'YES' if status else 'NO'

    def set_hostname(self, hostname):
        self.worksheet['A' + str(self.count)] = hostname

    def set_telnet_status(self, status):
        self.worksheet['B' + str(self.count)] = self.status_to_text(status)

    def set_ssh_status(self, status):
        self.worksheet['C' + str(self.count)] = self.status_to_text(status)

    def set_version(self, version):
        self.worksheet['D' + str(self.count)] = version

    def set_serial_number(self, serial_number):
        self.worksheet['E' + str(self.count)] = serial_number

