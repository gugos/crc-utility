import os
import time
from collections import OrderedDict

import commands_manager as cm


def print_log(get_response):
    def wrapper(*args, **kwargs):
        response = get_response(*args, **kwargs)
        print(response)
        return response
    return wrapper


class SessionManager:
    def __init__(self, session, auth_list, csv_writer, dir_path):
        self.__session = session
        self.__auth_list = auth_list
        self.__csv_writer = csv_writer
        self.__dir_path = dir_path
        self.__commands_manager = cm.CommandsManager()
        self.__commands_list = self.__commands_manager.get_commands_list()

    def manage(self, hostname):
        fieldnames = self.__csv_writer.get_fieldnames()
        values_dict = OrderedDict(zip(fieldnames, [''] * len(fieldnames)))
        values_dict['HOSTNAME'] = hostname
        telnet_status = self.__manage_telnet_connection(hostname)
        if telnet_status:
            self.__run_commands_and_fetch_result(hostname)
            ssh_status = self.__manage_ssh_connection(hostname)
        else:
            ssh_status = self.__manage_ssh_connection(hostname)
            if ssh_status:
                self.__run_commands_and_fetch_result(hostname)
        values_dict['TELNET'] = self.__status_to_text(telnet_status)
        values_dict['SSH'] = self.__status_to_text(ssh_status)
        self.__csv_writer.add_to_csv(values_dict)

    def __status_to_text(self, status):
        return 'YES' if status else 'NO'

    def __run_commands_and_fetch_result(self, values_dict):
        with open(self.__dir_path + os.sep + values_dict['HOSTNAME'] + '_log', 'w') as log_file:
            for command in self.__commands_list:
                response = self.__run_command_and_get_response(command.get_command())
                log_file.write(response)
                if not command.is_simple_command():
                    values_dict[command.get_command_type()] = command.retrieve_result(response)
        log_file.close()

    def __run_command_and_get_response(self, command):
        self.__session.send(command)
        results = self.__get_response()
        return results

    @print_log
    def __get_response(self):
        max_seconds = 5
        buf_size = 1024

        start = round(time.time())
        response = ''
        self.__session.setblocking(0)
        while True:
            if self.__session.recv_ready():
                data = self.__session.recv(buf_size).decode('ascii')
                response += data
            if self.__session.exit_status_ready():
                break
            now = round(time.time())
            if now - start > max_seconds:
                break
            output = response.rstrip()
            if len(output) > 0 and (output[-1] == '#' or output[-1] == '>'):
                break
            time.sleep(0.2)

        if self.__session.recv_ready():
            data = self.__session.recv(buf_size)
            response += data.decode('ascii')

        return response

    def __manage_ssh_connection(self, hostname):
        self.__auth_list[0] = 'ssh ' + hostname
        response = ''
        for command in self.__auth_list:
            response = self.__run_command_and_get_response(command.encode('ascii') + b'\n')
        status = response.lower().endswith(hostname.lower() + '#')
        return status

    def __manage_telnet_connection(self, hostname):
        self.__auth_list[0] = 'telnet ' + hostname
        response = self.__run_command_and_get_response(self.__auth_list[0].encode('ascii') + b'\n')
        if not response.endswith('username: '):
            return False
        for command in self.__auth_list[1:]:
            response = self.__run_command_and_get_response(command.encode('ascii') + b'\n')
        status = response.lower().endswith(hostname.lower() + '#')
        return status

