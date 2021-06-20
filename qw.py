import pyautogui
from PIL import Image
from io import BytesIO
from array import array

screen = pyautogui.screenshot()
w, h = screen.size
koef = 1080/w
screen.resize((1080, int(h*koef)))
output = BytesIO()
screen.save(output, format='JPEG', optimize=True, subsampling=0, quality=10)
screen.save('output.jpg', format='JPEG', optimize=True, subsampling=0, quality=10)

output.seek(0)
ba = bytearray(output.read())

print(len(ba))
#img = Image.open(output)
img = Image.open(BytesIO(ba))
img.save('savepath.jpg', format='JPEG', optimize=True, subsampling=0, quality=1)
