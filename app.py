from flask import Flask,render_template,url_for, request,session,send_file,redirect
from PIL import Image
import re, os

app = Flask(__name__)
app.secret_key = 'Text_E_D'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/card/encryption', methods=['GET','POST'])
def encryption():
    if request.method == "POST":
        text = request.form.get('text')
        image = request.files['file']
        input_pass = request.form.get('password')
        session['input_pass'] = input_pass

        if image and image.filename.endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(image)
            secret_text = text + " volsiee"
            binary_text = ''.join(format(ord(char), '08b') for char in secret_text)
            pixels = list(img.getdata())
            encoded_pixels = []
            index = 0
            for pixel in pixels:
                r, g, b = pixel

                # Modify the least significant bit (LSB) of each color channel
                if index < len(binary_text):
                    r = (r & 254) | int(binary_text[index])
                    index += 1

                encoded_pixels.append((r, g, b))

            # Create a new image with the hidden text
            encoded_img = Image.new(img.mode, img.size)
            encoded_img.putdata(encoded_pixels)

            # Save the encoded image

            encoded_img.save('encoded_images.png')

            return render_template('encryption.html', result="Image Encoded Successfully")

        else:
            return render_template("encryption.html", result="Please upload a valid image file.")

    return render_template("encryption.html", result=None)



@app.route('/download_encode_image')
def download_encode_image():
    return send_file('encoded_images.png', as_attachment=True)


@app.route('/card/decryption', methods=["GET", "POST"])
def decryption():
    if request.method == "POST":
        dec_pass = request.form.get('password')
        encoded_img = request.files['encoded_image']

        if encoded_img and encoded_img.filename.endswith((".png", ".jpg", ".jpeg")):
            # Extract the binary text from the LSB of each color channel
            # Save the uploaded encoded image temporarily
            # encoded_image_path = os.path.join('temp', encoded_img.filename)
            # encoded_img.save(encoded_image_path)
            encoded_img = Image.open(encoded_img)
            binary_text = ""
            pixels = list(encoded_img.getdata())
            for pixel in pixels:
                r, _, _ = pixel
                binary_text += str(r & 1)

            # Convert the binary text to ASCII
            decoded_text = ''.join(chr(int(binary_text[i:i + 8], 2)) for i in range(0, len(binary_text), 8))
            dec = decoded_text.find("volsiee")

            input_pass = session.get('input_pass', None)
            if input_pass == dec_pass:
                return render_template('decryption.html', result="Decoded Text: " + decoded_text[:dec])
            else:
                return render_template('decryption.html', result="Password incorrect. Cannot Decode")

        else:
            return render_template('decryption.html', result="IT'S NORMAL IMAGE, Nothing too Decode")

    return render_template("decryption.html")


if __name__ == "__main__":
    app.run(debug=True)
