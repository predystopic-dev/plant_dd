import numpy as np
import tensorflow as tf
import keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.optimizers import Adam
from constants import labels

model = keras.models.load_model("v2.h5")

json_config = model.to_json()
with open("model_config.json", "w") as json_file:
    json_file.write(json_config)

model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="categorical_crossentropy",
    metrics=["acc"],
)
# print(model.summary())


def preprocess_image(file):
    path = "random_tests/"
    img = image.load_img(path + file, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array_expanded_dims = np.expand_dims(img_array, axis=0)
    return tf.keras.applications.mobilenet_v2.preprocess_input(img_array_expanded_dims)


def get_prediction(image, level="all"):
    preprocessed_image = preprocess_image(image)
    predictions = model.predict(preprocessed_image)

    ind = np.argpartition(predictions[0], -5)[-5:]
    result = np.argmax(predictions[0])
    top5 = predictions[0][ind]

    if level == "single":
        for k, v in labels.items():
            if v == result:
                return k
    else:
        for k, v in labels.items():
            if v in np.sort(ind):
                idx = np.where(ind == v)[0]
                print(f"{top5[idx]} ~> {k}")


ans = get_prediction("late_blight_potato_1.jpg", level="all")
print(ans)
