from constants import labels
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import keras
from keras.optimizers import Adam
from rembg import remove
from PIL import Image

model = keras.models.load_model("v2.h5")
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["acc"],
)

json_config = model.to_json()
with open("model_config.json", "w") as json_file:
    json_file.write(json_config)


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
        # print(f"{top5[idx]} ~> {k}")


filename = "grape_blackrot_1.png"
removed_bg = remove(
    Image.open("random_tests/" + filename),
    alpha_matting=True,
    alpha_matting_foreground_threshold=1,
    alpha_matting_background_threshold=10,
    alpha_matting_erode_size=0,
)
removed_bg.save("cleaned/" + filename)

input_plant = input("Enter name of your plant: ")
predictions = get_prediction(filename, level="all")

# print(predictions)
for i in predictions:
    print(i)
print("\n\n\n")
for i in predictions:
    if input_plant in i:
        print(i.split("~>")[1])
