import getpass
import paramiko
import sys

import session_manager as sm


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
        session_manager = sm.SessionManager(session, auth_list)

        try:
            with open('hostnames.txt') as hostnames:
                for hostname in hostnames:
                    session_manager.set_hostname(hostname.strip())
                    status = session_manager.manage_telnet_connection()
                    if status:
                        session_manager.run_commands_and_fetch_result()
                        session_manager.manage_ssh_connection()
                    else:
                        status = session_manager.manage_ssh_connection()
                        if status:
                            session_manager.run_commands_and_fetch_result()
            session_manager.exit_session()
        except Exception as ex:
            print(ex)
            sys.exit(1)


if __name__ == '__main__':
    main()
