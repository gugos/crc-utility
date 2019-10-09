import command as cmd


class CommandsManager:
    def __init__(self):
        self.__commands_list = [
            cmd.Command(b'terminal length 0\n'),
            cmd.VersionCommand(b'show version | include flash:/\n'),
            cmd.SerialNumberCommand(b'show inventory | include SN\n'),
        ]

        with open('commands.txt') as commands:
            for command in commands:
                command = command.rstrip('\n')
                self.__commands_list.append(cmd.Command(command.encode('ascii') + b'\n'))

        self.__commands_list.append(cmd.Command(b'exit\n'))

    def get_commands_list(self):
        return self.__commands_list

