import re
import textwrap
import os

from PIL import Image, ImageDraw, ImageFont
from rich.progress import track
from TTS.engine_wrapper import process_text
import textwrap
import random

def form_lines(words, min_words_per_line=2, max_words_per_line=4):
    lines = []
    current_index = 0

    while current_index < len(words):
        # Determine the number of words for the current line (random in the specified range)
        line_length = random.randint(min_words_per_line, max_words_per_line)
        line_words = words[current_index:current_index + line_length]

        # Join the selected words to create a line
        line = ' '.join(line_words)

        # Add the line to the list
        lines.append(line)

        # Move to the next set of words
        current_index += line_length

    return lines


def draw_multiple_line_text(
    image, text, font, text_color, padding, wrap=50, transparent=False
) -> None:
    """
    Draw multiline text over given image
    """
    draw = ImageDraw.Draw(image)
    Fontperm = font.getsize(text)
    image_width, image_height = image.size
    lines = textwrap.wrap(text, width=wrap)
    y = (image_height / 2) - (((Fontperm[1] + (len(lines) * padding) / len(lines)) * len(lines)) / 2)
    for line in lines:
        line_width, line_height = font.getsize(line)
        if transparent:
            shadowcolor = "black"
            for i in range(1, 5):
                draw.text(
                    ((image_width - line_width) / 2 - i, y - i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 + i, y - i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 - i, y + i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
                draw.text(
                    ((image_width - line_width) / 2 + i, y + i),
                    line,
                    font=font,
                    fill=shadowcolor,
                )
        draw.text(((image_width - line_width) / 2, y), line, font=font, fill=text_color)
        y += line_height + padding


def imagemaker(theme, reddit_obj: dict, txtclr, padding=5, transparent=False) -> None:
    """
    Render Images for video
    """
    title = process_text(reddit_obj["thread_title"], False)
    texts = reddit_obj["thread_post"]
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    if transparent:
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)
    else:
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)  # for title
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), 100)
    size = (1920, 1080)

    image = Image.new("RGBA", size, theme)

    # for title
    draw_multiple_line_text(image, title, tfont, txtclr, padding, wrap=30, transparent=transparent)

    image.save(f"assets/temp/{id}/png/title.png")

    # Iterate through the texts
    for idx, text in track(enumerate(texts), "Rendering Image"):
        # Split text into lines with a maximum of 2 to 4 words


        lines = form_lines(text.split(), min_words_per_line=4, max_words_per_line=6)
        # print(text.split())
        # print(lines)

        # Create a new image for each line of text
        for line_idx, line in enumerate(lines):
            image = Image.new("RGBA", size, theme)
            line = process_text(str(line), False)

            # Modify draw function to accept a list of lines
            draw_multiple_line_text(image, str(line), font, txtclr, padding, wrap=30, transparent=transparent)

            # Adjust the saving logic to include line index
            image.save(f"assets/temp/{id}/png/img{idx}_line{line_idx}.png")


    # for idx, text in track(enumerate(texts), "Rendering Image"):
    #     image = Image.new("RGBA", size, theme)
    #     text = process_text(text, False)
    #     draw_multiple_line_text(image, text, font, txtclr, padding, wrap=30, transparent=transparent)
    #     image.save(f"assets/temp/{id}/png/img{idx}.png")


def imagemaker2(theme, reddit_obj: dict, txtclr, padding=5, transparent=False) -> None:
    """
    Render Images for video
    """
    title = process_text(reddit_obj["thread_title"], False)
    texts = reddit_obj["thread_post"]
    id = re.sub(r"[^\w\s-]", "", reddit_obj["thread_id"])

    if transparent:
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)
    else:
        tfont = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 100)  # for title
        font = ImageFont.truetype(os.path.join("fonts", "Roboto-Regular.ttf"), 100)
    size = (1920, 1080)

    image = Image.new("RGBA", size, theme)

    # for title
    draw_multiple_line_text(image, title, tfont, txtclr, padding, wrap=30, transparent=transparent)

    image.save(f"assets/temp/{id}/png/title.png")

    for idx, text in track(enumerate(texts), "Rendering Image"):
        image = Image.new("RGBA", size, theme)
        text = process_text(text, False)
        draw_multiple_line_text(image, text, font, txtclr, padding, wrap=30, transparent=transparent)
        image.save(f"assets/temp/{id}/png/img{idx}.png")


def to_words(texts):
    new_texts = []
    for text in texts:
        new_texts = new_texts + text.split()
    return new_texts