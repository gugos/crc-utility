class Command:
    def __init__(self, command):
        self.__command = command

    def get_command(self):
        return self.__command

    def is_simple_command(self):
        return True


class VersionCommand(Command):
    def is_simple_command(self):
        return False

    def get_command_type(self):
        return 'VERSION'

    def retrieve_result(self, command_output):
        command_output = 'version'
        return command_output


class SerialNumberCommand(Command):
    def is_simple_command(self):
        return False

    def get_command_type(self):
        return 'SERIALNUMBER'

    def retrieve_result(self, command_output):
        command_output = 'serial_number'
        return command_output
