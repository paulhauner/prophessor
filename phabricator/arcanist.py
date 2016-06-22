from subprocess import Popen, PIPE, STDOUT

class Arcanist():
    def call_and_pipe_in(self, args_list, data_to_be_piped_in):
        """
        Call arcanist, then pipe some data into it
        :param args_list: A list of arguments (don't include 'arc')
        :param data_to_be_piped_in: The data to be piped into the function. Should probably be a string?
        :return: The result of the data piping
        """
        process_params = ['arc'] + args_list
        process = Popen(process_params, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        return process.communicate(input=data_to_be_piped_in)[0]

arc = Arcanist()