from io import BytesIO

import qrcode


class QRCodeService:
    @staticmethod
    def generate_qr_code(url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buf = BytesIO()
        img.save(buf)
        buf.seek(0)

        return buf


# # Приклад виклику функції з URL
# url_to_encode = "https://www.example.com"

# # Створення екземпляру класу QRCodeService
# qr_code_service = QRCodeService()

# # Отримання QR-коду у вигляді картинки
# qr_image = qr_code_service.generate_qr_code(url_to_encode)
