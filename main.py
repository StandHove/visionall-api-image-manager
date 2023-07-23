from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
from PIL import Image
from io import BytesIO
import os
import json

app = FastAPI()

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
        
    return JSONResponse(content={"message": "Image upload successful"}, status_code=200)
