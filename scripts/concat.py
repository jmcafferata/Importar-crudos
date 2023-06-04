import os
import subprocess

def generate_list_file(videos, list_file):
    with open(list_file, 'w') as f:
        for video in videos:
            f.write(f"file '{video}'\n")

def merge_videos(video_folder, output_file):
    # List all video files in the folder
    videos = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith('.mp4') or f.endswith('.MP4')]

    # Generate mylist.txt
    list_file = 'mylist.txt'
    generate_list_file(videos, list_file)

    #set the output file path to be the google drive folder
    output_file = os.path.join(video_folder, output_file)

    # Run the ffmpeg command to merge the videos
    cmd = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", "-vcodec", "h264_nvenc", output_file]
    subprocess.run(cmd)

    # Remove the list_file
    os.remove(list_file)

