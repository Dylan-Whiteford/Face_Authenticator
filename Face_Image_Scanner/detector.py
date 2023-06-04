# detector.py

from PIL import Image, ImageDraw
from pathlib import Path
from collections import Counter

import face_recognition
import pickle
import argparse
import os
import uuid


import cv2

PATH = os.path.dirname(os.path.realpath(__file__))
DEFAULT_ENCODINGS_PATH = Path(PATH+"/output/encodings.pkl")

#Path("images/training").mkdir(exist_ok=True)
#Path("output").mkdir(exist_ok=True)
#Path("images/validation").mkdir(exist_ok=True)

parser = argparse.ArgumentParser(description="Recognize faces in an image")
parser.add_argument("--train", action="store_true", help="Train on input data")
parser.add_argument(
    "--validate", action="store_true", help="Validate trained model"
)
parser.add_argument(
    "--test", action="store_true", help="Test the model with an unknown image"
)
parser.add_argument(
    "-m",
    action="store",
    default="hog",
    choices=["hog", "cnn"],
    help="Which model to use for training: hog (CPU), cnn (GPU)",
)
parser.add_argument(
    "-f", action="store", help="Path to an image with an unknown face"
)
args = parser.parse_args()

def encode_known_faces(
    model: str = "hog", encodings_location: Path = DEFAULT_ENCODINGS_PATH
) -> None:
    names = []
    encodings = []
    for filepath in Path("images/training").glob("*/*"):
        name = filepath.parent.name
        image = face_recognition.load_image_file(filepath)



def encode_known_faces(
    model: str = "hog", encodings_location: Path = DEFAULT_ENCODINGS_PATH
) -> None:
    names = []
    encodings = []

    for filepath in Path("images/training").glob("*/*"):
        name = filepath.parent.name
        image = face_recognition.load_image_file(filepath)

        face_locations = face_recognition.face_locations(image, model=model)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        for encoding in face_encodings:
            names.append(name)
            encodings.append(encoding)

    name_encodings = {"names": names, "encodings": encodings}
    with encodings_location.open(mode="wb") as f:
        pickle.dump(name_encodings, f)

def recognize_faces(
    image_location: str,
    model: str = "hog",
    encodings_location: Path = DEFAULT_ENCODINGS_PATH,
    display_mode: bool = True,
) -> None:
    with encodings_location.open(mode="rb") as f:
        loaded_encodings = pickle.load(f)

    input_image = face_recognition.load_image_file(image_location)

    input_face_locations = face_recognition.face_locations(
        input_image, model=model
    )
    input_face_encodings = face_recognition.face_encodings(
        input_image, input_face_locations
    )

    pillow_image = Image.fromarray(input_image)
    draw = ImageDraw.Draw(pillow_image)

    faces_found = 0
    new_faces_found = 0
    for bounding_box, unknown_encoding in zip(
        input_face_locations, input_face_encodings
    ):
        faces_found += 1
        face_id = _recognize_face(unknown_encoding, loaded_encodings)
        dir_path = "images/training/"+face_id+"/"
        if not face_id:

            new_faces_found += 1
            # Genereate unique ID
            face_id = uuid.uuid4()
            os.makedirs(dir_path)

        # Get a count of photots for the user. This will act as the name for the new image
        photoID = 0
        # Iterate directory
        for path in os.listdir(dir_path):
            # check if current path is a file
            if os.path.isfile(os.path.join(dir_path, path)):
                photoID += 1

        # Dont save more than 10 images per user
        if(photoID < 10):
            cropped_image = pillow_image.crop(bounding_box)
            cropped_image.save(dir_path + str(photoID) + '.jpg')

        if(display_mode):
            _display_face(draw, bounding_box, face_id)
    del draw
    if(display_mode):
        pillow_image.show()


def _recognize_face(unknown_encoding, loaded_encodings):
    boolean_matches = face_recognition.compare_faces(
        loaded_encodings["encodings"], unknown_encoding
    )
    votes = Counter(
        name
        for match, name in zip(boolean_matches, loaded_encodings["names"])
        if match
    )
    if votes:
        return votes.most_common(1)[0][0]


BOUNDING_BOX_COLOR = "blue"
TEXT_COLOR = "white"

def _display_face(draw, bounding_box, name):
    top, right, bottom, left = bounding_box
    draw.rectangle(((left, top), (right, bottom)), outline=BOUNDING_BOX_COLOR)
    text_left, text_top, text_right, text_bottom = draw.textbbox(
        (left, bottom), name
    )
    draw.rectangle(
        ((text_left, text_top), (text_right, text_bottom)),
        fill="blue",
        outline="blue",
    )
    draw.text(
        (text_left, text_top),
        name,
        fill="white",
    )

def validate(model: str = "hog"):
    for filepath in Path("images/validation").rglob("*"):
        if filepath.is_file():
            recognize_faces(
                image_location=str(filepath.absolute()), model=model
            )

if __name__ == "__main__":
    if args.train:
        encode_known_faces(model=args.m)
    if args.validate:
        validate(model=args.m)
    if args.test:
        recognize_faces(image_location=args.f, model=args.m)



