import getpass
import paramiko
import time
import openpyxl


class ExcelHostItemReader:
    def __init__(self, filename):
        self.filename = filename
        self.workbook = openpyxl.load_workbook(filename)
        self.worksheet = self.workbook.active
        self.count = 1
        self.max_repeats = self.worksheet.max_row

    def __iter__(self):
        return self

    def __next__(self):
        if self.count >= self.max_repeats:
            self.workbook.save(self.filename)
            raise StopIteration
        self.count += 1
        return self

    def __status_to_text(self, status):
        return 'YES' if status else 'NO'

    def get_hostname(self):
        return self.worksheet['A' + str(self.count)].value

    def set_telnet_status(self, status):
        self.worksheet['B' + str(self.count)] = self.__status_to_text(status)

    def set_ssh_status(self, status):
        self.worksheet['C' + str(self.count)] = self.__status_to_text(status)

    def set_version(self, version):
        self.worksheet['D' + str(self.count)] = version

    def set_serial_number(self, serial_number):
        self.worksheet['E' + str(self.count)] = serial_number


def wait_for_response(session):
    while not session.recv_ready():
        time.sleep(1)


def get_response(session):
    response = session.recv(65000).decode('ascii')
    print(response)
    return response


def check_ssh_connection(session, auth_list):
    hostname = auth_list[0]
    auth_list[0] = 'ssh ' + hostname
    response = ''
    for command in auth_list:
        session.send(command.encode('ascii') + b'\n')
        wait_for_response(session)
        get_response(session)
    wait_for_response(session)
    response = get_response(session)
    return response.lower().endswith(hostname.lower() + '#')


def check_telnet_connection(session, auth_list):
    hostname = auth_list[0].split()[1]
    auth_list[0] = 'telnet ' + hostname
    session.send(auth_list[0].encode('ascii') + b'\n')
    wait_for_response(session)
    response = get_response(session)
    if not response.endswith('Username: '):
        return False
    for command in auth_list[1:]:
        session.send(command.encode('ascii') + b'\n')
        wait_for_response(session)
        get_response(session)
    wait_for_response(session)
    response = get_response(session)
    return response.lower().endswith(hostname.lower() + '#')


def run_commands_and_fetch_result(session, item):
    session.send(b'terminal length 0\n')
    wait_for_response(session)
    get_response(session)
    session.send(b'show version | include flash:/\n')
    wait_for_response(session)
    response = get_response(session)
    version = response.split('"')[1].split('/')[-1:][0]
    item.set_version(version)
    session.send(b'show inventory | include SN\n')
    wait_for_response(session)
    response = get_response(session)
    serial_number = response.split()[-2:][0]
    item.set_serial_number(serial_number)
    session.send(b'exit\n')
    wait_for_response(session)
    get_response(session)


hostname = input('Hostname: ')
port = input('Port: ')
username = input('Username: ')
password = getpass.getpass('Password: ')

auth_list = [
    '',
    username,
    password,
]

with paramiko.SSHClient() as ssh:
    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=int(port), username=username, password=password)
    except Exception as ex:
        print(ex.args)

    session = ssh.invoke_shell()

    for item in ExcelHostItemReader('hosts.xlsx'):
        nested_hostname = item.get_hostname()
        auth_list[0] = nested_hostname
        status = check_ssh_connection(session, auth_list)
        item.set_ssh_status(status)
        if status:
            run_commands_and_fetch_result(session, item)
        else:
            status = check_telnet_connection(session, auth_list)
            item.set_telnet_status(status)
            if status:
                run_commands_and_fetch_result(session, item)
