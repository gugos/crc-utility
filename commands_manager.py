class CommandsManager:
    def __init__(self):
        self.commands_list = [
            b'terminal length 0\n',
            ('version', b'show version | include flash:/\n'),
            ('serial_number', b'show inventory | include SN\n'),
        ]

        with open('commands.txt') as commands:
            for command in commands:
                command = command.strip()
                self.commands_list.append(command.encode('ascii') + b'\n')

        self.commands_list.append(b'exit\n')

    def get_commands_list(self):
        return self.commands_list

    def get_version(self, response):
#        return response.split('"')[1].split('/')[-1:][0] if response else ''
        return ''

    def get_serial_number(self, response):
#        return response.split()[-2:][0] if response else ''
        return ''
