
from PIL import Image as Img
import pyocr
import pyocr.builders
import io
import pytesseract

tool = pyocr.get_available_tools()[0]
lang = tool.get_available_languages()[1]


with Img(filename="./Alakanty_Akhil_Reddy.pdf", resolution=300) as img:
 img.compression_quality = 99
 img.save(filename="sample_scan.jpg")

text = pytesseract.image_to_string(Image.open('sample_scan.jpg'))

# for img in image_jpeg.sequence:
#     img_page = Image(image=img)
#     req_image.append(img_page.make_blob('jpeg'))
# for img in req_image: 
#     txt = tool.image_to_string(
#         PI.open(io.BytesIO(img)),
#         lang=lang,
#         builder=pyocr.builders.TextBuilder()
#     )
#     final_text.append(txt)
#     final_file.write(txt)

print(text)