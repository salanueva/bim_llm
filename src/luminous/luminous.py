import socket
import json
import struct
import ifcopenshell
import os
import subprocess
import base64
import platform
import uuid


from src.luminous.math_utils import compute_axis, compute_dot_product

class Luminous:

    def __init__(self, address="127.0.0.1", port=9999):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))

        self.hidden_objects = []

    def send_message(self, message):
        json_message = json.dumps(message).encode()
        json_message_len = len(json_message)
        self.socket.sendall(struct.pack("<I", json_message_len) + json_message)

        size_part = b""
        while len(size_part) < 4:
            part = self.socket.recv(4 - len(size_part))
            if not part:
                raise Exception("connection closed")
            size_part += part

        json_message_len = struct.unpack("<I", size_part)[0]

        json_answer = b""

        while len(json_answer) < json_message_len:
            json_answer += self.socket.recv(json_message_len - len(json_answer))

        return json.loads(json_answer)

    def check_status(self, json_out):
        if json_out["status"] == "error":
            raise Exception(json_out["error"])
        return json_out["status"] == "ok"

    def send_command(self, command, args):
        json_object = {"command": command}
        return self.send_message({**json_object, **args})

    def move_to(self, x, y, z):
        json_out = self.send_command("move_to", {"location": [x, y, z]})
        return self.check_status(json_out)

    def move_relative_to(self, x, y, z):
        json_out = self.send_command("move_relative_to", {"location": [x, y, z]})
        return self.check_status(json_out)

    def move_forward(self, amount):
        json_out = self.send_command("move_forward", {"amount": amount})
        return self.check_status(json_out)

    def move_right(self, amount):
        json_out = self.send_command("move_right", {"amount": amount})
        return self.check_status(json_out)

    def move_up(self, amount):
        json_out = self.send_command("move_up", {"amount": amount})
        return self.check_status(json_out)

    def rotate_to(self, pitch, yaw, roll):
        json_out = self.send_command("rotate_to", {"rotation": [pitch, yaw, roll]})
        return self.check_status(json_out)

    def rotate_relative_to(self, pitch, yaw, roll):
        json_out = self.send_command(
            "rotate_relative_to", {"rotation": [pitch, yaw, roll]}
        )
        return self.check_status(json_out)

    def in_sight(self):
        json_out = self.send_command("in_sight", {})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["objects"]

    def move_object_to(self, _id, x, y, z):
        json_out = self.send_command(
            "move_object_to", {"id": _id, "location": [x, y, z]}
        )
        return self.check_status(json_out)

    def move_object_relative_to(self, _id, x, y, z):
        json_out = self.send_command(
            "move_object_relative_to", {"id": _id, "location": [x, y, z]}
        )
        return self.check_status(json_out)

    def rotate_object_to(self, _id, pitch, yaw, roll):
        json_out = self.send_command(
            "rotate_object_to", {"id": _id, "rotation": [pitch, yaw, roll]}
        )
        return self.check_status(json_out)

    def rotate_object_relative_to(self, _id, pitch, yaw, roll):
        json_out = self.send_command(
            "rotate_object_relative_to", {"id": _id, "rotation": [pitch, yaw, roll]}
        )
        return self.check_status(json_out)

    def scale_object_to(self, _id, x, y, z):
        json_out = self.send_command("scale_object_to", {"id": _id, "scale": [x, y, z]})
        return self.check_status(json_out)

    def scale_object_relative_to(self, _id, x, y, z):
        json_out = self.send_command(
            "scale_object_relative_to", {"id": _id, "scale": [x, y, z]}
        )
        return self.check_status(json_out)

    def all_objects(self):
        json_out = self.send_command("all_objects", {})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["objects"]

    def near_objects(self, radius):
        json_out = self.send_command("near_objects", {"radius": radius})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["objects"]

    def near_object_objects(self, _id, radius):
        json_out = self.send_command(
            "near_object_objects", {"id": _id, "radius": radius}
        )
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["objects"]

    def whereami(self):
        json_out = self.send_command("whereami", {})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out

    def get_camera_view(self):
        json_out = self.send_command("get_camera_view", {})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out

    def set_object_color(self, _id, r, g, b):
        json_out = self.send_command(
            "set_object_color", {"id": _id, "color": [r, g, b]}
        )
        return self.check_status(json_out)

    def set_object_visibility(self, _id, visibility):
        json_out = self.send_command(
            "set_object_visibility", {"id": _id, "visibility": visibility}
        )
        if not visibility:
            if _id not in self.hidden_objects:
                self.hidden_objects.append(_id)
        else:
            if _id in self.hidden_objects:
                self.hidden_objects.remove(_id)
        return self.check_status(json_out)
    
    def get_hidden_objects(self):
        return self.hidden_objects

    def distance(self, _id):
        json_out = self.send_command("distance", {"id": _id})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["distance"]

    def distance_object(self, _id, id2):
        json_out = self.send_command("distance_object", {"id": _id, "id2": id2})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["distance"]

    def dot(self, _id, id2):
        json_out = self.send_command("dot", {"id": _id, "id2": id2})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["dot"]

    def front_object(self, distance):
        json_out = self.send_command("front_object", {"distance": distance})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["object"] if "object" in json_out else None

    def start_microphone_capture(self):
        json_out = self.send_command("start_microphone_capture", {})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return None

    def stop_microphone_capture(self):
        json_out = self.send_command("stop_microphone_capture", {})
        if json_out["status"] != "ok":
            raise Exception(json_out["status"])
        return (
            json_out["channels"],
            json_out["sample_rate"],
            base64.b64decode(json_out["samples"]),
        )

    def look_at(self, _id):
        json_out = self.send_command("look_at", {"id": _id})
        return self.check_status(json_out)

    def destroy_object(self, _id):
        json_out = self.send_command("destroy_object", {"id": _id})
        return self.check_status(json_out)

    def text_to_speech(self, text, voice=""):
        json_out = self.send_command("text_to_speech", {"text": text, "voice": voice})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return None

    def get_object_info(self, _id):
        json_out = self.send_command("get_object_info", {"id": _id})
        if json_out["status"] != "ok":
            raise Exception(json_out["error"])
        return json_out["info"]

    def load_ifc(self, filename):
        if platform.system() == "Windows":
            ifc_convert = os.path.join(os.path.dirname(__file__), "IfcConvert.exe")
        else:
            ifc_convert = os.path.join(os.path.dirname(__file__), "IfcConvert.elf64")
        filename_mtime = os.path.getmtime(filename)
        filename_gltf = filename + ".glb"
        filename_gltf_mtime = 0
        if os.path.exists(filename_gltf):
            filename_gltf_mtime = os.path.getmtime(filename_gltf)
        if filename_mtime > filename_gltf_mtime:
            subprocess.run(
                [
                    ifc_convert,
                    "--use-element-guids",
                    "-y",
                    filename,
                    filename + ".glb",
                ]
            )
        filename_abs = os.path.abspath(filename_gltf)

        with open(filename_abs, "rb") as handle:
            b64data = base64.b64encode(handle.read()).decode()

        self.send_command("load_gltf", {"filename": filename_abs, "data": b64data})
        return ifcopenshell.open(filename)
     
    def __compute_reference_vector(self, direction: str, my_rotation: list[float] = None) -> list[float]:
        if my_rotation is None:
            my_rotation = self.whereami()["rotation"]
        pitch, yaw, roll = my_rotation
        forward, right, up = compute_axis(pitch, yaw, roll)
        if direction in ["left", "right"]:
            return right
        elif direction in ["up", "down"]:
            return up
        elif direction in ["forward", "backward"]:
            return forward

    def __entities_info(self, _id, _id2, direction):
        object1_position = self.get_object_info(_id)["location"]
        object2_position = self.get_object_info(_id2)["location"]
        reference_vector = self.__compute_reference_vector(direction=direction)
        return reference_vector, object1_position, object2_position
   
    def __entity_and_my_info(self, _id, direction):
        whereami = self.whereami()
        my_position = whereami["location"]
        object_position = self.get_object_info(_id)["location"]
        reference_vector = self.__compute_reference_vector(direction=direction, my_rotation=whereami['rotation'])
        return reference_vector, my_position, object_position

    def is_entity_to_my_left(self, _id):
        reference_vector, my_position, object_position = self.__entity_and_my_info(_id, "left")
        value = compute_dot_product(reference_vector=reference_vector, my_position=my_position, object_position=object_position)
        return value < 0

    def is_entity_to_my_right(self, _id):
        reference_vector, my_position, object_position = self.__entity_and_my_info(_id, "right")
        value = compute_dot_product(reference_vector=reference_vector, my_position=my_position, object_position=object_position)
        return value > 0

    def is_entity_above_me(self, _id):
        reference_vector, my_position, object_position = self.__entity_and_my_info(_id, "up")
        value = compute_dot_product(reference_vector=reference_vector, my_position=my_position, object_position=object_position)
        return value > 0
    
    def is_entity_below_me(self, _id):
        reference_vector, my_position, object_position = self.__entity_and_my_info(_id, "down")
        value = compute_dot_product(reference_vector=reference_vector, my_position=my_position, object_position=object_position)
        return value < 0
    
    def is_entity_in_front_of_me(self, _id):
        reference_vector, my_position, object_position = self.__entity_and_my_info(_id, "forward")
        value = compute_dot_product(reference_vector=reference_vector, my_position=my_position, object_position=object_position)
        return value > 0
    
    def is_entity_behind_me(self, _id):
        reference_vector, my_position, object_position = self.__entity_and_my_info(_id, "backward")
        value = compute_dot_product(reference_vector=reference_vector, my_position=my_position, object_position=object_position)
        return value < 0

    def is_entity_to_the_left(self, _id, _id2):
        reference_vector, object1_position, object2_position = self.__entities_info(_id, _id2, "left")
        value = compute_dot_product(reference_vector=reference_vector, my_position=object1_position, object_position=object2_position)
        return value < 0

    def is_entity_to_the_right(self, _id, _id2):
        reference_vector, object1_position, object2_position = self.__entities_info(_id, _id2, "right")
        value = compute_dot_product(reference_vector=reference_vector, my_position=object1_position, object_position=object2_position)
        return value > 0

    def is_entity_above(self, _id, _id2):
        reference_vector, object1_position, object2_position = self.__entities_info(_id, _id2, "up")
        value = compute_dot_product(reference_vector=reference_vector, my_position=object1_position, object_position=object2_position)
        return value > 0
    
    def is_entity_below(self, _id, _id2):
        reference_vector, object1_position, object2_position = self.__entities_info(_id, _id2, "down")
        value = compute_dot_product(reference_vector=reference_vector, my_position=object1_position, object_position=object2_position)
        return value < 0
    
    def is_entity_in_front(self, _id, _id2):
        reference_vector, object1_position, object2_position = self.__entities_info(_id, _id2, "forward")
        value = compute_dot_product(reference_vector=reference_vector, my_position=object1_position, object_position=object2_position)
        return value < 0 # This is swapped due to the change in perspective
    
    def is_entity_behind(self, _id, _id2):
        reference_vector, object1_position, object2_position = self.__entities_info(_id, _id2, "backward")
        value = compute_dot_product(reference_vector=reference_vector, my_position=object1_position, object_position=object2_position)
        return value > 0 # This is swapped due to the change in perspective

    def load_prop(self, filename, tags=[], variant=""):

        filename_abs = filename

        with open(filename_abs, "rb") as handle:
            b64data = base64.b64encode(handle.read()).decode()

        prop_id = uuid.uuid4()
        tags.append("Luminous:PropId:" + str(prop_id))

        json_out = self.send_command(
            "load_gltf", {"data": b64data, "tags": tags, "variant": variant}
        )
        self.check_status(json_out)
        return prop_id

    def move_prop_to_wall(self, _id):
        json_out = self.send_command("move_prop_to_wall", {"id": str(_id)})
        return self.check_status(json_out)

    def move_prop_to_floor(self, _id):
        json_out = self.send_command("move_prop_to_floor", {"id": str(_id)})
        return self.check_status(json_out)
    
    def destroy_prop(self, _id):
        json_out = self.send_command("destroy_prop", {"id": str(_id)})
        return self.check_status(json_out)

    def rotate_prop_yaw(self, _id, yaw=90):
        json_out = self.send_command("rotate_prop_yaw", {"id": str(_id), "yaw": yaw})
        return self.check_status(json_out)
     
    def move_prop_up(self, _id, amount):
        json_out = self.send_command("move_prop_up", {"id": str(_id), "amount": amount})
        return self.check_status(json_out)

    def move_prop_right(self, _id, amount):
        json_out = self.send_command(
            "move_prop_right", {"id": str(_id), "amount": amount}
        )
        return self.check_status(json_out)
    
    def move_prop_forward(self, _id, amount):
        json_out = self.send_command(
            "move_prop_forward", {"id": str(_id), "amount": amount}
        )
        return self.check_status(json_out)
    
    def scale_prop(self, _id, amount):
        json_out = self.send_command(
            "scale_prop", {"id": str(_id), "amount": amount}
        )
        return self.check_status(json_out)
    
    def reset(self):
        json_out = self.send_command("reset", {})
        return self.check_status(json_out)
