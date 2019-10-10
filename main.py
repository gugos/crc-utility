import getpass
import paramiko
import sys
import time
import os
import concurrent.futures

from csv_writer import CSVWriter
from session_manager import SessionManager


def main():
    host = input('Hostname: ')
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
            ssh.connect(host, port=int(port), username=username, password=password)
        except Exception as ex:
            print(ex)
            sys.exit(1)

        session = ssh.invoke_shell()
        dir_path = os.getcwd() + os.sep + time.strftime('%Y-%m-%d_%H:%M') + '_output'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        csv_writer = CSVWriter(dir_path, ['HOSTNAME', 'TELNET', 'SSH', 'VERSION', 'SERIALNUMBER'])
        session_manager = SessionManager(session, auth_list, csv_writer, dir_path)

        try:
            with open('hostnames.txt') as file:
                hostnames = [hostname.rstrip('\n') for hostname in file]
        except Exception as ex:
            print(ex)
            sys.exit(1)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(session_manager.manage, hostnames)
        csv_writer.close()


if __name__ == '__main__':
    main()
