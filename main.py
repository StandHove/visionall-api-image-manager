from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
from PIL import Image
from io import BytesIO
import os
import json

app = FastAPI()#docs_url=None)

@app.get("/")
async def welcome():
    return {"welcome message":"This web API is used and made by https://vision-all.com for managing images."}

@app.get("/admin/listdir/")
async def admin_get_dirs(password: str, directory:str=None):
    with open("password.txt", 'r') as file:
        pw = file.read()
    if(password==pw):
        if directory != None:
            return os.listdir(directory)
        else: return os.listdir()
    else:
        return JSONResponse(content={"message": "wrong password"}, status_code=500)

@app.get("/admin/image/")
async def admin_get_image(password: str, ip:str ,id: int):
    with open("password.txt", 'r') as file:
        pw = file.read()
    if(password==pw):
        with open(f"{ip}/data.json", "r") as f:
            donnees = json.load(f)
        image_path = f"{ip}/{id}{donnees[str(id)]['filetype']}"
        return FileResponse(image_path)
    else:
        return JSONResponse(content={"message": "wrong password"}, status_code=500)
    
@app.get("/admin/data")
async def admin_get_data(password: str, ip:str):
    with open("password.txt", 'r') as file:
        pw = file.read()
    if(password==pw):
        with open(f"{ip}/data.json", "r") as f:
            donnees = json.load(f)
            return JSONResponse(content=donnees)
    else:
        return JSONResponse(content={"message": "wrong password"}, status_code=500)


@app.get("/data/")
async def get_data(request: Request):
    try:
        with open(f"{request.client.host}/data.json", "r") as f:
            donnees = json.load(f)
            return JSONResponse(content=donnees)
    except:
        return JSONResponse(content={"message": "Json file dosnt exist"}, status_code=400)

@app.get("/image/{id}")
async def get_image(request: Request, id:int):
    try:
        with open(f"{request.client.host}/data.json", "r") as f:
            donnees = json.load(f)
        image_path = f"{request.client.host}/{id}{donnees[str(id)]['filetype']}"
        return FileResponse(image_path)
    except:
        return JSONResponse(content={"message": "Image dosnt exist or json data dosnt exist or you changed your ip"}, status_code=400)
    

@app.post("/upload/")
async def upload_image(request: Request, prompt: str, image: UploadFile = File(...)):
    
    date_actuelle = datetime.now()
    date_string = date_actuelle.strftime("%Y-%m-%d %H:%M:%S")
    
    nom_fichier, extension = os.path.splitext(image.filename)
    image_pil = Image.open(BytesIO(await image.read()))
    taille_x, taille_y = image_pil.size

    os.makedirs(request.client.host, exist_ok=True)
    files_names = os.listdir(request.client.host)
    image_path = ""
    data_path = f"{request.client.host}/data.json"
    if(len(files_names)>0):
        with open(data_path, "r") as f:
            donnees = json.load(f)
            print(donnees)
            donnees["last_id"] += 1
            donnees[donnees["last_id"]] = {"prompt" : prompt,
                                        "date" : date_string,
                                        "filetype" : extension,
                                        "filename" : nom_fichier,
                                        "size" : f"{taille_x}x{taille_y}"}
            
            image_path = f"{request.client.host}/{str(donnees['last_id'])}{extension}" 
    else:
        donnees = {
            "last_id" : 0,
            0 : {
                    "prompt" : prompt,
                    "date": date_string,
                    "filetype" : extension,
                    "filename" : nom_fichier,
                    "size" : f"{taille_x}x{taille_y}"
                }
        }
        image_path = f"{request.client.host}/0{extension}"

    

    with open(data_path, "w") as f:
        json.dump(donnees, f)
    
    # Enregistrer l'image dans un répertoire spécifique sur le serveur (par exemple, 'images/')
    image_pil.save(image_path)
    #with open(image_path, "wb") as file:
     #   file.write(image.file.read())
        
    return JSONResponse(content={"message": "Image upload successful", "id":donnees["last_id"]}, status_code=200)


@app.post("/resize/")
async def resize_image(request: Request, x:int, y:int, length:int, width:int ,image: UploadFile = File(...)):
    
    image_pil = Image.open(BytesIO(await image.read()))

    # Redimensionner l'image

    image_coupee = image_pil.crop((x, y, x+length, y+width))

    date_actuelle = datetime.now()
    date_string = date_actuelle.strftime("%Y-%m-%d %H:%M:%S")
    
    nom_fichier, extension = os.path.splitext(image.filename)
    taille_x, taille_y = image_coupee.size

    os.makedirs(request.client.host, exist_ok=True)
    files_names = os.listdir(request.client.host)
    image_path = ""
    data_path = f"{request.client.host}/data.json"
    if(len(files_names)>0):
        with open(data_path, "r") as f:
            donnees = json.load(f)
            donnees["last_id"] += 1
            donnees[donnees["last_id"]] = {"prompt" : "croped image",
                                        "date" : date_string,
                                        "filetype" : extension,
                                        "filename" : nom_fichier,
                                        "size" : f"{taille_x}x{taille_y}"}
            
            image_path = f"{request.client.host}/{str(donnees['last_id'])}{extension}" 
    else:
        donnees = {
            "last_id" : 0,
            0 : {
                    "prompt" : "croped image",
                    "date": date_string,
                    "filetype" : extension,
                    "filename" : nom_fichier,
                    "size" : f"{taille_x}x{taille_y}"
                }
        }
        image_path = f"{request.client.host}/0{extension}"

    

    with open(data_path, "w") as f:
        json.dump(donnees, f)
    
    # Enregistrer l'image dans un répertoire spécifique sur le serveur (par exemple, 'images/')
    image_coupee.save(image_path)
    #with open(image_path, "wb") as file:
     #   file.write(image.file.read())
        
    #return JSONResponse(content={"message": "Image upload successful", "id" : donnees["last_id"]}, status_code=200)
    return FileResponse(image_path)

