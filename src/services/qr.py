import qrcode


def generate_qr_code(url, file_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Зберегти QR-код у зазначений файл
    img.save(file_path)

# Приклад виклику функції з URL і шляхом до файлу
url_to_encode = "https://www.example.com"
output_file_path = "qr_code.png"

generate_qr_code(url_to_encode, output_file_path)
