import os
import time

import excel_data as ed
import commands_manager as cm


class SessionManager:
    def __init__(self, session, auth_list):
        self.session = session
        self.auth_list = auth_list
        self.commands_manager = cm.CommandsManager()
        self.commands_list = self.commands_manager.get_commands_list()
        self.hostname = ''

        self.dir_path = os.getcwd() + os.sep + time.strftime('%Y%m%d') + '_output'
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
        self.excel_data = ed.ExcelData(self.dir_path)

    def run_commands_and_fetch_result(self):
        self.excel_data.set_hostname(self.hostname)
        with open(self.dir_path + os.sep + self.hostname + '_log', 'w') as log_file:
            for item in self.commands_list:
                if isinstance(item, tuple):
                    command_type = item[0]
                    command = item[1]
                    response = self.run_command_and_get_response(command)
                    log_file.write(response)
                    if command_type == 'version':
                        result = self.commands_manager.get_version(response)
                        self.excel_data.set_version(result)
                    elif command_type == 'serial_number':
                        result = self.commands_manager.get_serial_number(response)
                        self.excel_data.set_serial_number(result)
                else:
                    command = item
                    response = self.run_command_and_get_response(command)
                    log_file.write(response)
        log_file.close()

    def run_command_and_get_response(self, command):
        self.session.send(command)
        results = self.get_response()
        print(results)
        return results

    def get_response(self):
        max_seconds = 5
        buf_size = 1024

        start = round(time.time())
        response = ''
        self.session.setblocking(0)
        while True:
            if self.session.recv_ready():
                data = self.session.recv(buf_size).decode('ascii')
                response += data
            if self.session.exit_status_ready():
                break
            now = round(time.time())
            if now - start > max_seconds:
                break
            output = response.rstrip()
            if len(output) > 0 and (output[-1] == '#' or output[-1] == '>'):
                break
            time.sleep(0.2)

        if self.session.recv_ready():
            data = self.session.recv(buf_size)
            response += data.decode('ascii')

        return response

    def set_hostname(self, hostname):
        self.excel_data.next_row()
        self.hostname = hostname

    def manage_ssh_connection(self):
        self.auth_list[0] = 'ssh ' + self.hostname
        response = ''
        for command in self.auth_list:
            response = self.run_command_and_get_response(command.encode('ascii') + b'\n')
        status = response.lower().endswith(self.hostname.lower() + '#')
        self.excel_data.set_ssh_status(status)
        return status

    def manage_telnet_connection(self):
        self.auth_list[0] = 'telnet ' + self.hostname
        response = self.run_command_and_get_response(self.auth_list[0].encode('ascii') + b'\n')
        if not response.endswith('username: '):
            self.excel_data.set_telnet_status(False)
            return False
        for command in self.auth_list[1:]:
            response = self.run_command_and_get_response(command.encode('ascii') + b'\n')
        status = response.lower().endswith(self.hostname.lower() + '#')
        self.excel_data.set_telnet_status(status)
        return status

    def exit_session(self):
        self.excel_data.close()
