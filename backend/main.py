from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)


from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL
import bcrypt
import json
import pickle as pkl
import numpy as np

from tensorflow import keras
import tensorflow as tf
import cv2

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173", "http://localhost:5173/predict_expression"],
)


# __locations = None
__data_coloumn = None
__Model = None
IMG_SIZE = 225


@app.route("/")
def Home():
    return jsonify({"message": f"prediction :"}), 201


@app.route("/predict_plant_health", methods=["POST"])
def predict():

    file = request.files["image"]
    print("Received file:", file.filename)
    
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img_input_2 = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    input_img_21 = tf.keras.preprocessing.image.img_to_array(img_input_2)
    input_img_21_array = tf.expand_dims(input_img_21, 0)

    prediction = __Model.predict(input_img_21_array)

    confidence = round(100 * np.max(prediction[0]))

    # Step 4: Predict
    # prediction = __Model.predict(input_img_array)
    print("prediction", prediction)

    # Step 5: Extract result
    value = np.argmax(prediction)
    # confidence = np.max(prediction[0])
    
    print(confidence)
    
    if confidence < 0.6:
        print("Uncertain prediction")
        confidence = 0
    else:
        confidence = np.max(prediction[0])
        
        
    
    return (
        jsonify(
            {
                "message": f"prediction : {value}, "
                f"plant disease name : {__data_coloumn[value]}, "
                f"confidence : {confidence}",
                "desease_name": f"{__data_coloumn[value]}",
                "confidence": f"{confidence}",
                "prediction": f"{value}",
            }
        ),
        201,
    )


def load_saved_artifacts():
    global __data_coloumn
    global __Model

    with open(
        r"E:\aiml main projects\plant_health_detection\backend\model\plant_column.json",
        "r",
    ) as f:
        __data_coloumn = json.load(f)["column"]

    __Model = keras.models.load_model(
        r"E:\aiml main projects\plant_health_detection\backend\model\plant_status_detector_v3.1.keras"
    )
    print("artifects loaded")


if __name__ == "__main__":
    load_saved_artifacts()
    app.run(debug=True, port=4000)
