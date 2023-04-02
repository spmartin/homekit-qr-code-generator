from flask import Flask, render_template, request, make_response, send_file
import qrcode
from io import BytesIO
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('form.html')


def generate_homekit_setup_uri(category, password, setup_id, version=0, reserved=0, flags=2):
    base36 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    payload = 0
    payload |= (version & 0x7)

    payload <<= 4
    payload |= (reserved & 0xf)

    payload <<= 8
    payload |= (category & 0xff)

    payload <<= 4
    payload |= (flags & 0xf)

    payload <<= 27
    payload |= (int(password.replace('-', '')) & 0x7fffffff)

    encoded_payload = ''
    for _ in range(9):
        encoded_payload += base36[payload % 36]
        payload //= 36

    return 'X-HM://%s%s' % (''.join(reversed(encoded_payload)), setup_id)


@app.route('/generate', methods=['POST'])
def generate():
    category = int(request.form['category'])
    password = request.form['password']
    setup_id = request.form['setupId']
    only_qr_code = 'only_qr_code' in request.form

    url = generate_homekit_setup_uri(category, password, setup_id)

    qr_code_img = qrcode.make(url,
                              version=1,
                              border=0,
                              error_correction=qrcode.constants.ERROR_CORRECT_M
                              )
    if only_qr_code:
        return serve_pil_image(qr_code_img)

    homekit_qr_image = generate_homekit_qr_image(qr_code_img, password)
    return serve_pil_image(homekit_qr_image)


def generate_homekit_qr_image(qr_code, password):
    image = Image.open("assets/qr_background.png").convert("RGBA")

    qr_image = qr_code.resize((320, 320))
    image.paste(qr_image, (40, 180))

    pair_img_draw = ImageDraw.Draw(image)
    pair_code = password.replace('-', '')

    font = ImageFont.truetype("assets/SF-Mono-Bold.otf", 70)

    for i in range(4):
        pair_img_draw.text((173 + i * 49, 38 - 13), pair_code[i], font=font, fill=(0, 0, 0))
        pair_img_draw.text((173 + i * 49, 88), pair_code[i + 4], font=font, fill=(0, 0, 0))

    return image


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000)
