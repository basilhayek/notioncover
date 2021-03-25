import os.path  # for checking if the image file was previously created
import string   # for checking whether the color string is a hexadecimal number

from flask import Flask, redirect
from flask import send_file      # sends the png file back to the caller 
from PIL import Image, ImageColor, ImageDraw, ImageFont  # builds the image and contains the named colors

import logging

import emoji

logging.basicConfig(filename='./logs/app.log', format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('notioncover starting...')
    
app = Flask(__name__)

def generate_gradient(
        colour1: str, colour2: str, width: int, height: int) -> Image:
    """Generate a vertical gradient.
       Code by Artemis
       https://stackoverflow.com/questions/32530345/pil-generating-vertical-gradient-image
    """
    base = Image.new('RGB', (width, height), colour1)
    top = Image.new('RGB', (width, height), colour2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            mask_data.append(int(255 * (y / height)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def check_color(color, fallback = 'white'):
    ''' Checks to ensure we have a valid color, otherwise returns a default color '''

    # Check the named colors
    if color in ImageColor.colormap.keys():
        return color
    
    # Check if six digit hex
    if all(c in string.hexdigits for c in color):
        if len(color) == 6:
            return '#{}'.format(color)

    logging.info("Color {} not found, returning {}".format(color, fallback))
    return fallback

@app.route('/')
def root():
    #return app.send_static_file('html/index.html')
    return redirect("https://www.notion.so/basilhayek/Covers-for-Notion-32e8918fbc3f46f6a8006f21a747cb96", code=302)

@app.route('/gradient/<top_color>/<bottom_color>')
def draw_gradient(top_color, bottom_color):
    ''' Route that returns a canvas with a gradient from the top_color to the bottom_color '''
    logging.debug('Handling request for gradient {} -> {}'.format(top_color, bottom_color))

    # First make sure the colors are either a six digit hexadecimal or named color
    # If neither is true, return gray or white
    top_color = check_color(top_color, 'gray')
    bottom_color = check_color(bottom_color, 'white')

    filename = './covers/gradient/{}.{}.png'.format(top_color, bottom_color)
    
    # Only create the image if it doesn't exist
    if not os.path.isfile(filename):
        logging.info('Creating cover for gradient {} -> {}'.format(top_color, bottom_color))
        img = generate_gradient(top_color, bottom_color, 1500, 300)
        img.save(filename)
    
    return send_file(filename, mimetype='image/png')

@app.route('/emoji/<emojistring>/<color1>')
@app.route('/emoji/<emojistring>/<color1>/<color2>')
def draw_emoji(emojistring, color1, color2=None):
    ''' Route that returns a canvas with an emoji 
        References: 
        * https://stackoverflow.com/questions/64253461/insert-colorful-emoji-into-an-imagepython
        * https://github.com/python-pillow/Pillow/pull/4955
    '''

    logging.info('Handling request for emoji {} {} {}'.format(emojistring, color1, color2))

    # Fall back to gray if color1 is invalid
    color1 = check_color(color1, 'gray')    

    if color2 is None:
        # Create a 1500x300 solid canvas
        img = Image.new('RGB', (1500, 300), color = color1)
    else:
        # Fall back to white if color2 is invalid
        color2 = check_color(color2, 'white')

        # create a 1500x300 gradient canvas
        img = generate_gradient(color1, color2, 1500, 300)

    # Turn the emojistring into the unicode character code for the emoji
    unicode_text = emoji.emojize(':{}:'.format(emojistring), use_aliases=True)
    logging.info('emojistring {} -> {}'.format(emojistring, unicode_text))
    
    draw = ImageDraw.Draw(img)

    # 109 is the required font https://github.com/python-pillow/Pillow/issues/3346
    unicode_font = ImageFont.truetype("./static/fonts/NotoColorEmoji.ttf", 109, layout_engine=ImageFont.LAYOUT_RAQM)
    
    # Draw the eomji in the center
    draw.text((750, 150), unicode_text, font=unicode_font, anchor="mm", embedded_color=True, fill='black')

    # Do not persist these
    filename = "./covers/temp.png"
    img.save(filename)

    # Return the image file directly
    return send_file(filename, mimetype='image/png')


@app.route('/solid/<color>')
def draw_solid_color(color):
    ''' Route that returns a canvas with a single color '''
    logging.debug('Handling request for solid {}'.format(color))

    # First make sure this is either a six digit hexadecimal or named color
    # If neither is true, return gray
    color = check_color(color, 'gray')

    filename = './covers/solid/{}.png'.format(color)

    # Only create the image if it doesn't exist
    if not os.path.isfile(filename):
        logging.info('Creating cover for solid {}'.format(color))
        # 1500x300 is the recommended canvas size
        img = Image.new('RGB', (1500, 300), color = color)
        img.save(filename)

    # Return the image file directly
    return send_file(filename, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='3000')
