from flask import Flask
from flask import send_file     # sends the png file back to the caller 
from PIL import Image, ImageColor  # builds the image and contains the named colors
import os.path  # for checking if the image file was previously created
import string   # for checking whether the color string is a hexadecimal number
import logging

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
    return app.send_static_file('html/index.html')

@app.route('/gradient/<top_color>/<bottom_color>')
def gradient(top_color, bottom_color):
    ''' Route that returns a canvas with a gradient from the top_color to the bottom_color '''
    logging.debug('Handling request for gradient {} -> {}'.format(top_color, bottom_color))

    # First make sure the colors are either a six digit hexadecimal or named color
    # If neither is true, return gray or white
    top_color = check_color(top_color, 'gray')
    bottom_color = check_color(bottom_color, 'white')

    filename = './gradient/{}.{}.png'.format(top_color, bottom_color)
    
    # Only create the image if it doesn't exist
    if not os.path.isfile(filename):
        logging.info('Creating cover for gradient {} -> {}'.format(top_color, bottom_color))
        img = generate_gradient(top_color, bottom_color, 1500, 300)
        img.save(filename)
    
    return send_file(filename, mimetype='image/png')

@app.route('/solid/<color>')
def solid_color(color):
    ''' Route that returns a canvas with a single color '''
    logging.debug('Handling request for solid {}'.format(color))

    # First make sure this is either a six digit hexadecimal or named color
    # If neither is true, return gray
    color = check_color(color, 'gray')

    filename = './solid/{}.png'.format(color)

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
