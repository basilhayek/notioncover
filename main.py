import os        # for accessing the API key
import os.path   # for checking if the image file was previously created
import string    # for checking whether the color string is a hexadecimal number

import requests
from flask import Flask, redirect
from flask import send_file      # sends the png file back to the caller 
from PIL import Image, ImageColor, ImageDraw, ImageFont  # builds the image and contains the named colors

import logging

import emoji

import chess
import chess.svg
import cairosvg


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

@app.route('/chess/fen/<fen>')
def draw_chess_fen(fen):
    pass

@app.route('/chess/opening/<opening>')
@app.route('/chess/opening/<opening>/<padding>')
def draw_chess_opening(opening, padding = None):
    boards = {}
    # Notation: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation
    boards['start'] = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    boards['kia'] = 'rnbqkbnr/pppppppp/8/8/4P3/3P1NP1/PPPN1PBP/R1BQ1RK1 b kq - 0 6'
    if opening in boards.keys():
        board = chess.Board(boards[opening])
        svg = chess.svg.board(board)

        return send_svg(svg, padding)

# https://note.nkmk.me/en/python-pillow-add-margin-expand-canvas/
def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = int(width + right * width + left * width)
    new_height = int(height + top * height + bottom * height)
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (int(left * width), int(top * width)))
    return result

def send_svg(svg, padding):
    filename = "./covers/temp.png"
    cairosvg.svg2png(bytestring=svg, write_to=filename)
    if padding == "width":
        img_new = add_margin(Image.open(filename), 0, .25, 0, .25, 'white')
        img_new.save(filename)
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

    # 109 is the required font size for emoji https://github.com/python-pillow/Pillow/issues/3346
    unicode_font = ImageFont.truetype("./static/fonts/NotoColorEmoji.ttf", 109, layout_engine=ImageFont.LAYOUT_RAQM)
    
    # Draw the eomji in the center
    draw.text((750, 150), unicode_text, font=unicode_font, anchor="mm", embedded_color=True, fill='black')

    # Do not persist these
    filename = "./covers/temp.png"
    img.save(filename)

    # Return the image file directly
    return send_file(filename, mimetype='image/png')

@app.route('/string/<string>/<color1>')
@app.route('/string/<string>/<color1>/<color2>')
def draw_string(string, color1, color2=None):
    ''' Route that returns a canvas with a string 
    '''

    logging.info('Handling request for emoji {} {} {}'.format(string, color1, color2))

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

    draw = ImageDraw.Draw(img)
    # Convert string to unicode
    unicode_text = string
    unicode_font = ImageFont.truetype("./static/fonts/Ubuntu-Regular.ttf", 109, layout_engine=ImageFont.LAYOUT_RAQM)
    
    # Draw the eomji in the center
    draw.text((750, 150), unicode_text, font=unicode_font, anchor="mm", embedded_color=True, fill='black')

    # Do not persist these
    filename = "./covers/temp.png"
    img.save(filename)

    # Return the image file directly
    return send_file(filename, mimetype='image/png')


def get_location_type_zoom(type):
    location_type_zooms = {
        'neighborhood': 15,
        'postal_code': 15,
        'airport': 14,
        'locality': 11,
        'natural_feature': 10,
        'administrative_area_level_2': 9,
        'administrative_area_level_1': 8,
        'country': 6,
        'continent': 2
    }

    zoom = location_type_zooms.get(type, 1)
    return zoom


def get_place_zoom(location):
    #TODO: Refactor into class module
    # TODO: Sign request https://developers.google.com/maps/documentation/maps-static/get-api-key#premium-auth
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={}&inputtype=textquery&fields=types&key={}"

    url = url.format(location, api_key)
    resp = requests.get(url)
    data = resp.json()
    
    types = data['candidates'][0]['types']
    logging.debug(types)

    return get_location_type_zoom(types[0])

def get_map(center, zoom, type):
    # TODO: Sign request https://developers.google.com/maps/documentation/maps-static/get-api-key#premium-auth
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if api_key:  
        if zoom is None:
            zoom = get_place_zoom(center)

        # https://www.geeksforgeeks.org/python-get-google-map-image-specified-location-using-google-static-maps-api/
        url = "https://maps.googleapis.com/maps/api/staticmap?"
                
        redirect_url = url + "center=" + center + "&zoom=" + \
                            str(zoom) + "&size=640x640&key=" + \
                            api_key + "&format=png32" + \
                            "&maptype=" + type
        return redirect(redirect_url)
    

@app.route('/satellite/<center>')
@app.route('/satellite/<center>/<zoom>')
def get_satellite(center, zoom=None):
    return get_map(center, zoom, 'satellite')

@app.route('/map/<center>')
@app.route('/map/<center>/<zoom>')
def get_terrain(center, zoom=None):
    return get_map(center, zoom, 'terrain')

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
