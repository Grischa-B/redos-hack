import tkinter
import pyautogui
from PIL import Image
from io import BytesIO
from array import array
from PIL import Image as ImageModule
from PIL import ImageTk
from datetime import datetime, timedelta

tk = tkinter.Tk()
screen_width = tk.winfo_screenwidth()
screen_height = tk.winfo_screenheight()
canvas = tkinter.Canvas(tk, width=screen_width, height=screen_height)
canvas.pack()

def getscreen():
    screen = pyautogui.screenshot()
    w, h = screen.size
    koef = 1080/w
    screen.resize((1080, int(h*koef)))
    output = BytesIO()
    screen.save(output, format='JPEG', optimize=True, subsampling=0, quality=10)
    output.seek(0)
    return bytearray(output.read())

# ENTRY
scr = getscreen()
image = Image.open(BytesIO(scr))
photo = ImageTk.PhotoImage(image)
image = canvas.create_image(0, 0, anchor='nw',image=photo)
tk.mainloop()
