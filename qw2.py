import mss
import mss.tools
from datetime import datetime
from PIL import Image
from io import BytesIO
from array import array
from PIL import Image as ImageModule
from PIL import ImageTk
from datetime import datetime, timedelta
from PIL import ImageFile

def getscreen():
	with mss.mss() as sct:
		monitor = sct.monitors[1]
		im = sct.grab(monitor)
		raw_bytes = mss.tools.to_png(im.rgb, (1280,720))
		im1 = Image.open(BytesIO(raw_bytes))
		im1 = im1.resize((1280,720))
		img_byte_arr = BytesIO()
		im1.save(img_byte_arr, format='JPEG', optimize=True, subsampling=0, quality=10)
		return img_byte_arr.getvalue()
    
time1 = datetime.now()
out1 = getscreen()
print(datetime.now()-time1)
