import qrcode

# Data to be encoded in the QR code
data = "Alice Johnson,2nd,Electrical Engineering,Circuits;Electromagnetism;Control Systems"

# Create a QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# Create an image from the QR code
img = qr.make_image(fill='black', back_color='white')

# Save the image to a file
img.save("Alice_Johnson_QR_Code.png")

print("QR code generated and saved as 'Alice_Johnson_QR_Code.png'.")
