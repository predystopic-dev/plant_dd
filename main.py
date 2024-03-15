from fastapi import FastAPI, Depends, Header, Request, HTTPException, File, UploadFile
from typing import Annotated
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime
from constants import labels
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import keras
from keras.optimizers import Adam
from rembg import remove
from PIL import Image

app = FastAPI()

model = keras.models.load_model("v2.h5")
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["acc"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Cleaning up")


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def preprocess_image(file):
    path = "cleaned/"
    img = image.load_img(path + file, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return tf.keras.applications.mobilenet_v2.preprocess_input(img_array_expanded_dims)


def get_prediction(image, level="all"):
    preprocessed_image = preprocess_image(image)
    predictions = model.predict(preprocessed_image)

    ind = np.argpartition(predictions[0], -10)[-10:]
    result = np.argmax(predictions[0])
    top10 = predictions[0][ind]

    if level == "single":
        for k, v in labels.items():
            if v == result:
                return k
    else:
        list_of_predictions = []
        for k, v in labels.items():
            if v in np.sort(ind):
                idx = np.where(ind == v)[0]
                list_of_predictions.append(f"{top10[idx]} ~> {k}")
        return list_of_predictions

import json

@app.post("/")
async def create_upload_file(file: UploadFile, plant_name: str):
    os.makedirs("cleaned", exist_ok=True)
    with open(f"cleaned/{file.filename}", "wb") as buffer:
        buffer.write(file.file.read())


    with open('disease_info.json') as f:
        data = json.load(f)   
    
    # disease_info = {}
    # for item in data:
    #     if item.get("disease_name") == "disease_name":
    #         disease_info = item
    #         break
    
    
    # predictions = get_prediction(file, level="all")
    predictions = get_prediction(f"{file.filename}", level="all")
    print(file.filename, predictions, plant_name)
    results = []
    max_confidence = 0.0
    for i in predictions:
        confidence = float(i.split("~>")[0][1:-2])
        if plant_name in i and "healthy" not in i:
            disease_name= i.split("~>")[1].strip()
            for item in data:
                if item.get("disease_name")==disease_name:
                    description=item.get("description")
                    prevention=item.get("prevention")
                    supplement_name=item.get("supplement_name")
                    supplement_link=item.get("supplement_link")
                    continue
            max_confidence = max(max_confidence, confidence)
            results.append(
                {
                    "disease_name": disease_name,
                    "confidence": float(i.split("~>")[0][1:-2]),
                    "is_plant": True,
                    "description":description,
                    "prevention":prevention,
                    "supplement_name":supplement_name,
                    "supplement_link":supplement_link,
                }
            )
        elif plant_name in i and "healthy" in i:
            max_confidence = max(max_confidence, confidence)
            results.append(
                {
                    "disease_name": "healthy",
                    "confidence": float(i.split("~>")[0][1:-2]),
                    "is_plant": True,
                }
            )
        else:
            continue
    if results == []:
        return [{"disease_name": "Not found", "confidence": 0.0}]
    if max_confidence < 0.5:
        return [{"disease_name": "Not found", "confidence": 0.0, "is_plant": False}]
    results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    return results



if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
