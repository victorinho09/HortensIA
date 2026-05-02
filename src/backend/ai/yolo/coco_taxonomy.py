from enum import Enum

class COCOSupercategory(str,Enum):
    """
    Official COCO supercategories for object detection classes
    """
    PERSON = "person"
    VEHICLE = "vehicle"
    OUTDOOR = "outdoor"
    ANIMAL = "animal"
    ACCESSORY = "accessory"
    SPORTS = "sports"
    KITCHEN = "kitchen"
    FOOD = "food"
    FURNITURE = "furniture"
    ELECTRONIC = "electronic"
    APPLIANCE = "appliance"
    INDOOR = "indoor"

COCO_CLASS_TO_SUPERCATEGORY: dict[str,COCOSupercategory] = {
    "person": COCOSupercategory.PERSON,
    "bicycle": COCOSupercategory.VEHICLE,
    "car": COCOSupercategory.VEHICLE,
    "motorcycle": COCOSupercategory.VEHICLE,
    "airplane": COCOSupercategory.VEHICLE,
    "bus": COCOSupercategory.VEHICLE,
    "train": COCOSupercategory.VEHICLE,
    "truck": COCOSupercategory.VEHICLE,
    "boat": COCOSupercategory.VEHICLE,
    "traffic light": COCOSupercategory.OUTDOOR,
    "fire hydrant": COCOSupercategory.OUTDOOR,
    "stop sign": COCOSupercategory.OUTDOOR,
    "parking meter": COCOSupercategory.OUTDOOR,
    "bench": COCOSupercategory.OUTDOOR,
    "bird": COCOSupercategory.ANIMAL,
    "cat": COCOSupercategory.ANIMAL,
    "dog": COCOSupercategory.ANIMAL,
    "horse": COCOSupercategory.ANIMAL,
    "sheep": COCOSupercategory.ANIMAL,
    "cow": COCOSupercategory.ANIMAL,
    "elephant": COCOSupercategory.ANIMAL,
    "bear": COCOSupercategory.ANIMAL,
    "zebra": COCOSupercategory.ANIMAL,
    "giraffe": COCOSupercategory.ANIMAL,
    "backpack": COCOSupercategory.ACCESSORY,
    "umbrella": COCOSupercategory.ACCESSORY,
    "handbag": COCOSupercategory.ACCESSORY,
    "tie": COCOSupercategory.ACCESSORY,
    "suitcase": COCOSupercategory.ACCESSORY,
    "frisbee": COCOSupercategory.SPORTS,
    "skis": COCOSupercategory.SPORTS,
    "snowboard": COCOSupercategory.SPORTS,
    "sports ball": COCOSupercategory.SPORTS,
    "kite": COCOSupercategory.SPORTS,
    "baseball bat": COCOSupercategory.SPORTS,
    "baseball glove": COCOSupercategory.SPORTS,
    "skateboard": COCOSupercategory.SPORTS,
    "surfboard": COCOSupercategory.SPORTS,
    "tennis racket": COCOSupercategory.SPORTS,
    "bottle": COCOSupercategory.KITCHEN,
    "wine glass": COCOSupercategory.KITCHEN,
    "cup": COCOSupercategory.KITCHEN,
    "fork": COCOSupercategory.KITCHEN,
    "knife": COCOSupercategory.KITCHEN,
    "spoon": COCOSupercategory.KITCHEN,
    "bowl": COCOSupercategory.KITCHEN,
    "banana": COCOSupercategory.FOOD,
    "apple": COCOSupercategory.FOOD,
    "sandwich": COCOSupercategory.FOOD,
    "orange": COCOSupercategory.FOOD,
    "broccoli": COCOSupercategory.FOOD,
    "carrot": COCOSupercategory.FOOD,
    "hot dog": COCOSupercategory.FOOD,
    "pizza": COCOSupercategory.FOOD,
    "donut": COCOSupercategory.FOOD,
    "cake": COCOSupercategory.FOOD,
    "chair": COCOSupercategory.FURNITURE,
    "couch": COCOSupercategory.FURNITURE,
    "potted plant": COCOSupercategory.FURNITURE,
    "bed": COCOSupercategory.FURNITURE,
    "dining table": COCOSupercategory.FURNITURE,
    "toilet": COCOSupercategory.FURNITURE,
    "tv": COCOSupercategory.ELECTRONIC,
    "laptop": COCOSupercategory.ELECTRONIC,
    "mouse": COCOSupercategory.ELECTRONIC,
    "remote": COCOSupercategory.ELECTRONIC,
    "keyboard": COCOSupercategory.ELECTRONIC,
    "cell phone": COCOSupercategory.ELECTRONIC,
    "microwave": COCOSupercategory.APPLIANCE,
    "oven": COCOSupercategory.APPLIANCE,
    "toaster": COCOSupercategory.APPLIANCE,
    "sink": COCOSupercategory.APPLIANCE,
    "refrigerator": COCOSupercategory.APPLIANCE,
    "book": COCOSupercategory.INDOOR,
    "clock": COCOSupercategory.INDOOR,
    "vase": COCOSupercategory.INDOOR,
    "scissors": COCOSupercategory.INDOOR,
    "teddy bear": COCOSupercategory.INDOOR,
    "hair drier": COCOSupercategory.INDOOR,
    "toothbrush": COCOSupercategory.INDOOR,
}

def calculate_detection_supercategory(class_name: str) -> COCOSupercategory:
    """
    Resolve the official COCO supercategory for a detected class name.
    """
    try: 
        return COCO_CLASS_TO_SUPERCATEGORY[class_name]
    except KeyError as exc:
        raise ValueError(f"Unknown COCO class name: {class_name}") from exc