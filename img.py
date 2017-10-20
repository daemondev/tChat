from io import StringIO as cStringIO
import PIL.Image
import io

image_data = None

def imagetopy(image, output_file):
    with open(image, 'rb') as fin:
        image_data = fin.read()

    with open(output_file, 'w') as fout:
        fout.write('image_data = '+ repr(image_data))

def pytoimage(pyfile):
    pymodule = __import__(pyfile)
    img = PIL.Image.open(io.BytesIO(pymodule.image_data))
    img.save("img.png")
    img.show()

if __name__ == '__main__':
    imagetopy('ok.png', 'image.py')
    pytoimage('image')
