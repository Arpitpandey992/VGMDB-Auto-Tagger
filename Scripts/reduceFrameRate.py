import subprocess


def remove_every_second_frame(input_file_path, output_file_path):
    command = ["ffmpeg", "-i", input_file_path, "-vf", "select='not(mod(n,2))'", "-c:v", "copy", output_file_path]
    subprocess.call(command)


# example usage
input_file_path = ""
output_file_path = ""
remove_every_second_frame(input_file_path, output_file_path)
