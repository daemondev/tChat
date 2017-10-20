import pyscreenshot
from io import BytesIO
from base64 import b64encode
from json import dumps

img_buffer = BytesIO()
pyscreenshot.grab().save(img_buffer, 'PNG', quality=5)
img_buffer.seek(0)
s = img_buffer.getvalue()
b = b64encode(s)
