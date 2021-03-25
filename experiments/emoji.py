from PIL import Image, ImageDraw, ImageFont

import emoji

back_ground_color = (255, 255, 255)
font_color = (0, 0, 0)

unicode_text = emoji.emojize(':thumbs_up:') #u"\U0001f618"
im = Image.new("RGB", (1500, 300), back_ground_color)
draw = ImageDraw.Draw(im)
unicode_font = ImageFont.truetype("NotoColorEmoji.ttf", 109, layout_engine=ImageFont.LAYOUT_RAQM)
draw.text((750, 150), unicode_text, font=unicode_font, anchor="mm", embedded_color=True, fill=font_color)
im.save('test.png')