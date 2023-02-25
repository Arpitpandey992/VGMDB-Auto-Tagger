import subprocess


def remove_every_second_frame(input_file_path, output_file_path):
    command = ["ffmpeg", "-i", input_file_path, "-vf", "select='not(mod(n,2))'", "-c:v", "copy", output_file_path]
    subprocess.call(command)


# example usage
input_file_path = "/run/media/arpit/DATA/Music/Visual Novels/Key Sounds Label/KSLM／V/[KSLM-0008] KSL Live World 2016 ~the Animation Charlotte & Rewrite~ [BDRip 1920x1080 x264 FLAC] [Beatrice-Raws]/[Beatrice-Raws] KSL Live World 2016 ~the Animation Charlotte & Rewrite~ [BDRip 1920x1080 x264 FLAC].mkv"
output_file_path = "/run/media/arpit/DATA/Music/Visual Novels/Key Sounds Label/KSLM／V/[KSLM-0008] KSL Live World 2016 ~the Animation Charlotte & Rewrite~ [BDRip 1920x1080 x264 FLAC] [Beatrice-Raws]/[Beatrice-Raws] KSL Live World 2016 ~the Animation Charlotte & Rewrite~ [BDRip 1920x1080 x264 FLAC]_out.mkv"
remove_every_second_frame(input_file_path, output_file_path)
