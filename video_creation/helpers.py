import glob
import os
import re
import shutil
import tempfile
from typing import Dict, Tuple
import subprocess

from moviepy.audio.AudioClip import concatenate_audioclips
import moviepy.editor as mp
from moviepy.editor import TextClip
import translators
from PIL import Image
from rich.console import Console
from rich.progress import track

from utils.cleanup import cleanup
from utils.console import print_step, print_substep
from utils.thumbnail import create_thumbnail
from utils.videos import save_data
from utils import settings
import moviepy.config

import os
from multiprocessing import Pool
from tqdm import tqdm
import glob
import moviepy.editor as editor
from moviepy.video.io.VideoFileClip import VideoFileClip


def process_image_line(img_info):
    i, line_idx, img_path, img_clip_duration, reddit_id = img_info

    # Create the directory if it doesn't exist
    img_clip_dir = f"assets/temp/{reddit_id}/mp4/"
    os.makedirs(img_clip_dir, exist_ok=True)

    # Convert PNG to MP4
    img_clip = editor.ImageClip(img_path, ismask=True, transparent=True)
    img_clip = img_clip.set_duration(img_clip_duration)

    img_clip_path = f"assets/temp/{reddit_id}/mp4/img{i}_line{line_idx}.mp4"
    img_clip.write_videofile(img_clip_path, codec="libx264", audio_codec="aac", fps=24, logger=None, threads=1)

    return img_clip_path


def storymodemethod2(number_of_clips=None, reddit_id=None, audio_clips_durations=None, current_time=None,
                     background_clip=None):
    img_clips = []

    def update_img_composite(result):
        nonlocal background_clip
        img_clip_path, i, line_idx = result
        img_clip = editor.VideoFileClip(img_clip_path)
        print(f"Processing image {i}, line {line_idx}, duration: {img_clip.duration}")

        img_clips.append(img_clip)

        try:
            img_composite = editor.concatenate_videoclips(img_clips, method="compose")
            img_composite = img_composite.set_start(current_time)
            img_composite = img_composite.set_duration(audio_clips_durations[i])

            if background_clip is None:
                background_clip = img_composite
            else:
                try:
                    background_clip = editor.CompositeVideoClip([background_clip, img_composite])
                except Exception as e:
                    print(f"Error concatenating background_clip for image {i}: {e}")
                    background_clip = None
                    raise  # Exit the loop if an error occurs during concatenation

        except Exception as e:
            print(f"Error updating background_clip for image {i}: {e}")
            background_clip = None
            raise  # Exit the loop if an error occurs during concatenation

        return background_clip

    def process_image_lines(i):
        line_idx = 0
        img_clip_paths = []

        total_lines = len(glob.glob(f"assets/temp/{reddit_id}/png/img{i}_line*.png"))
        img_clip_duration = audio_clips_durations[i] / total_lines

        while True:
            img_path = f"assets/temp/{reddit_id}/png/img{i}_line{line_idx}.png"

            if not os.path.exists(img_path):
                break

            img_clip_paths.append((i, line_idx, img_path, img_clip_duration, reddit_id))
            line_idx += 1

        return img_clip_paths

    img_clip_paths_list = list(tqdm(Pool().imap_unordered(process_image_lines, range(number_of_clips)),
                                    total=number_of_clips, desc="Collecting the image files..."))

    # Unpack the iterable returned by process_image_lines
    img_clip_paths_list = [item for sublist in img_clip_paths_list for item in sublist]

    for img_clip_paths in img_clip_paths_list:
        results = list(tqdm(Pool().imap_unordered(process_image_line, img_clip_paths),
                            total=len(img_clip_paths), desc="Processing image lines..."))

        for result in tqdm(results, total=len(results), desc="Updating background_clip..."):
            if isinstance(result, tuple):
                background_clip = update_img_composite(result)

        current_time += audio_clips_durations[img_clip_paths[0][0]]

    # Write the final result to a file
    if background_clip is not None:
        background_clip.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac", threads=1)
    else:
        print("No valid clips found for concatenation. Output video not created.")


def storymodemethod1(number_of_clips=None, reddit_id=None, audio_clips_durations=None, current_time=None,
                     background_clip=None):
    for i in track(range(0, number_of_clips), "Collecting the image files..."):
        line_idx = 0
        img_clips = []

        total_lines = len(glob.glob(f"assets/temp/{reddit_id}/png/img{i}_line*.png"))

        # Calculate the duration for each line based on the total number of lines
        img_clip_duration = audio_clips_durations[i] / total_lines



        while True:
            img_path = f"assets/temp/{reddit_id}/png/img{i}_line{line_idx}.png"

            if not os.path.exists(img_path):
                break



            background_clip = background_clip.overlay(
                image_clips[line_idx],
                enable=f"between(t,{current_time},{current_time + audio_clips_durations[i]})",
                x="(main_w-overlay_w)/2",
                y="(main_h-overlay_h)/2",
            )


        current_time += audio_clips_durations[i]

    # Write the final result to a file
    if background_clip is not None:
        background_clip.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac",
                                        threads=1000)
    else:
        print("No valid clips found for concatenation. Output video not created.")

