from PIL import Image, ImageDraw, ImageFont
import requests
import io
import base64
import json
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import conf

def addWatermark(fileName, text):
    r = requests.get('https://api.telegram.org/file/bot'+str(conf.BOT_TOKEN)+'/'+str(fileName))
    image_bytes = io.BytesIO(r.content)
    fontPath = 'AARDV.ttf'

    image = Image.open(image_bytes).convert('RGBA')
    w, h = image.size

    txt = Image.new('RGBA', image.size, (255,255,255,0))

    font = ImageFont.truetype(fontPath, conf.FONT_SIZE)
    d = ImageDraw.Draw(txt)

    textwidth, textheight = d.textsize(text, font)

    x = w/2 - textwidth/2
    y1 = h - (h/1.3)
    y2 = h - (h/2)
    y3 = h - (h/5)
    d.text((x, y1), text, font=font, fill=(255,255,255,conf.FONT_OPACITY))
    d.text((x, y2), text, font=font, fill=(255,255,255,conf.FONT_OPACITY))
    d.text((x, y3), text, font=font, fill=(255,255,255,conf.FONT_OPACITY))

    result = Image.alpha_composite(image, txt)

    # result.show()

    img_byte_arr = io.BytesIO()
    result.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": conf.IMG_BB_KEY,
        "image": base64.b64encode(img_byte_arr),
    }
    try:
        upload = requests.post(url, payload)
        ups = json.loads(upload.text)
        return {
            "status": 'success',
            "imageUrl": ups['data']['url']
        }
    except requests.exceptions.HTTPError as err:
        print(err)
        return {
            "status": 'failed'
        }

app = Flask(__name__)
api = Api(app)

class SolveIdle(Resource):
    def get(self):
        return {'message' : 'Active' }

class AddWatermark(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('fileName',
        required=True,
        help="Filename can't be blank"
    )
    parser.add_argument('text',
        required=True,
        help="Text watermark can't be blank"
    )

    def post(self):
        data = AddWatermark.parser.parse_args()
        return addWatermark(data['fileName'], data['text'])

api.add_resource(AddWatermark, '/watermark')
api.add_resource(SolveIdle, '/')

if __name__=='__main__':        
    #Run the applications
    app.run(debug=True)