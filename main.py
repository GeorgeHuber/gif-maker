#module imports
from PIL import Image,ImageEnhance
import os
import shutil
import requests
import random
from wand.image import Image as wandImage
from flask import Flask, flash, request, redirect, url_for,send_file,render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import numpy as np
import colorsys

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

#file imports
from save_transparent import save_transparent_gif

#root filePath
# absolute path to this file
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# absolute path to this file's root directory
PARENT_DIR = str(os.path.join(FILE_DIR, os.pardir) )[:-2]


print(PARENT_DIR," server")
name = "steam" #name of gif to be created
remove_bg = True #should remove background
new_api_key = "439a1a4fe50d00ce52fc021a7a2c925ec92002a9" #secret
start_server = True #start server or make it normally
key = "123456789ABCD" #hashing key

def makeRelative(path):
  return PARENT_DIR + path


#function to return file path for frame given frame number < 256
def formatPath(i):
  string = name+"/"+str(key[i//len(key)])+str(key[i%len(key)])+".png"
  return makeRelative(string)



#function for creating gif
def process_image(option="pop-up"):
  #testing purposed remove later
  #return 'static/output/test0.gif'
  global name
  
  print(option)
  #exits program if no images are in the input folder
  if(len(os.listdir(makeRelative("gif_templates")))==0):
    print("no image available")
    exit(400)

  #finds name of input file
  filename = os.listdir(makeRelative("gif_templates"))[0]
  i=0
  #depreciatedapi_key ="UCqcRFyPsxtDiQR5mwehWtK6"
  
  images=[]

  #prevents naming duplicates
  while os.path.isfile(makeRelative("static/output/"+name+str(i)+".gif")):
    i+=1
  name = name+str(i)
  if(os.path.isdir(makeRelative(name))):
    os.removedirs(makeRelative(name))
  os.mkdir(makeRelative(name))


  if remove_bg:
    """depreciated
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open("gif_templates/"+filename,"rb")},
        data={'size': 'auto',"format":"png"},
        headers={'X-Api-Key': api_key},
    )
    """
    #calls photoroom api
    response = requests.post(
    'https://sdk.photoroom.com/v1/segment',
    headers={'x-api-key': new_api_key},
    files={'image_file': open(makeRelative("gif_templates/"+filename), 'rb')},
    )

    if response.status_code == requests.codes.ok:
        with open(makeRelative('gif_pngs/'+filename), 'wb') as out:
            out.write(response.content)
    else:
        print("Error:", response.status_code, response.text)
    #moves input file to used template folder
    os.rename(makeRelative("gif_templates/"+filename), makeRelative("used_gif_templates/"+filename))

  

  im = Image.open(makeRelative("gif_pngs/"+filename))


  width, height = im.size

  if option == "pop-up":
    left = 0
    top = 0
    right = width
    bottom = height
    img_height=height
    step=height/6
    i=0

    def adjust(image):
        image = image.convert('RGBA')
        width, height = image.size
        new_width = right
        new_height = img_height
        new_image = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
        upper = (new_height - image.size[1])
        new_image.paste(image, (0, upper))
        return new_image

    while bottom>0:
      cropped = im.crop((left, top, right, bottom))
      images.append(formatPath(i))
      cropped.save(formatPath(i))
      bottom-=step
      i+=1
    bottom=1
    cropped = im.crop((left, top, right, bottom))

    for j in range(5):
      images.append(formatPath(i))
      cropped.save(formatPath(i))
      i+=1

    while bottom<height*.75:
      cropped = im.crop((left, top, right, bottom))
      images.append(formatPath(i))
      cropped.save(formatPath(i))
      bottom+=step
      i+=1

    bottom=height
    cropped = im.crop((left, top, right, bottom))

    for j in range(5):
      images.append(formatPath(i))
      cropped.save(formatPath(i))
      i+=1
    print(len(images), images)
  
  elif option =="rainbow":
    def shift_hue(arr, hout):
        r, g, b, a = np.rollaxis(arr, axis=-1)
        h, s, v = rgb_to_hsv(r, g, b)
        h = hout
        r, g, b = hsv_to_rgb(h, s, v)
        arr = np.dstack((r, g, b, a))
        return arr

    def colorize(image, hue):
        """
        Colorize PIL image `original` with the given
        `hue` (hue within 0-360); returns another PIL image.
        """
        img = image.convert('RGBA')
        arr = np.array(np.asarray(img).astype('float'))
        new_img = Image.fromarray(shift_hue(arr, hue/360.).astype('uint8'), 'RGBA')

        return new_img
    converter = ImageEnhance.Color(im)
    root = converter.enhance(2)
    root = im
    i=0
    for j in range(36):
      images.append(formatPath(i))
      img = colorize(root,j*10)
      img.save(formatPath(i))
      i+=1
  else:
    return makeRelative("static/output/nonexistent.png")

  #take list of image frames and turns them into gif
  raw =[]
  for x in images:
    frame = adjust(Image.open(x).copy()) if option=="pop-up" else Image.open(x).copy()
    raw.append(frame)
    frame.save(x)
    print(frame)
  step = random.randint(140,180) if option=="pop-up" else random.randint(40,80)
  save_transparent_gif(raw,step,makeRelative(f'static/output/{name}.gif'))          
  #remove temporary file_tree
  shutil.rmtree(makeRelative(name))
  print("successfully created gifs")
  return f'static/output/{name}.gif'



def main ():
  if(start_server):
    #initialize app
    app = Flask(__name__)

    #server configuration
    UPLOAD_FOLDER = makeRelative('gif_templates')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    #allows cross origin requests
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config["SECRET_KEY"] = "2"

    #main ui display
    @app.route("/")
    def index():
      return render_template('index.html') 

    #image processing part routed to /makeGif
    @app.route('/makeGif', methods=['GET', 'POST'])
    @cross_origin()
    def upload_file():
        if request.method == 'POST':
            # check if the post request has the file part
            file = request.files['pictureFile']
            #no file was submited
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
                print("no file")
            #in the event an image was passed as part of the request
            if file:
                #saves file to upload folder and reads blob
                filename = secure_filename(file.filename)
                file.save(UPLOAD_FOLDER+"/" +filename)
                print("found file")
                f = open(UPLOAD_FOLDER+"/"+filename,"rb")
                blob = f.read()
                f.close()

                #converts base64 to jpeg
                with wandImage(blob = blob) as img:
                  img.format = 'jpeg'
                  img.save(filename=UPLOAD_FOLDER+"/"+filename+".jpg")
                #removes temporary image
                os.remove(UPLOAD_FOLDER+"/"+filename)

                print("starting gif creation")
                #creates gif
                print(request.form)
                filename = process_image(option=request.form["gifType"])
                
                return filename
        return(''' <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        
        ''')
    port = int(os.environ.get('PORT', 33507))
    app.run( # Starts the site
        host='0.0.0.0',  # EStablishes the host, required for repl to detect the site
        port=port# select the port the machine hosts on.
      )

  else:
    process_image()

if __name__ == "__main__":  # Makes sure this is the main process
  main()