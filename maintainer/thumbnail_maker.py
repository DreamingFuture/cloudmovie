from PIL import Image
import time
import os


def thumbnail_maker(path, stills):
    try:
        im = Image.open(path)
    except OSError:
        return -1

    half_height = im.size[1] / 2
    half_width = im.size[0] / 2

    min_size = half_width if half_width < half_height else half_height

    try:
        im2 = im.crop((
            half_width - min_size,
            half_height - min_size,
            half_width + min_size,
            half_height + min_size,
        ))
    except OSError:
        return -1

    if im2.size[1] < 180:
        pass
    else:
        try:
            im2.thumbnail([180, 180])
        except OSError:
            return -1

    path = path.replace("stills", "stills_thumbnail")
    if not os.path.exists(os.path.split(path)[0]):
        try:
            os.makedirs(os.path.split(path)[0])
        except FileExistsError:
            pass
        
    im2.save(path)


def main(stills):
    while 1:
        if stills:
            try:
                path = stills.pop()
            except IndexError:
                continue
            thumbnail_maker(path, stills)

        time.sleep(2)
