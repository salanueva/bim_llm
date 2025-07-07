
SANDBOX_PROMPT = """
Your task is to fulfill a query given by the user in a 3D environment. The query will involve getting some information about a specific entity (or a group of them) or changing some of its/their features. 

To get the query done, you will need to write Python code. There are 3 different Python classes that are usable for the queries at hand.
* The Luminous class gives us the ability to interact with the sandbox, getting information about the scene and applying changes to it. 
  - Function names with the 'object' substring affect just BIM entities (e.g. walls, doors), whereas the ones with 'prop' affect only props (e.g chairs)
* The IFC class is useful to determine the type of an object/entity of the scene, that is, defining whether the object is a wall, a window...
* The Entity class defines each object's name, type and id. 

Objects returned by the Luminous functions are dictionaries containing just these keys: "id" (str), "location" (list[float]), "rotation" (list[float]) and "color" (list[float]).

Apart from that, you can add props and transform them. The Luminous class contains many functions with 'prop' in its name to do so. The list of the available props are the following:
* Barn Lamp: "data/props/AnisotropyBarnLamp.glb"
* Boom box: "data/props/BoomBox.glb"
* Purple chair: "data/props/ChairDamaskPurplegold.glb"
* Plant: "data/props/DiffuseTransmissionPlant.glb"
* Velvet sofa: "data/props/GlamVelvetSofa.glb"
* Iridescence lamp: "data/props/IridescenceLamp.glb"
* Punctual lamp: "data/props/LightsPunctualLamp.glb"
* Sheen chair: "data/props/SheenChair.glb"
* Leather sofa: "data/props/SheenWoodLeatherSofa.glb"
* Pouf: "data/props/SpecularSilkPouf.glb"
* Sunglasses: "data/props/SunglassesKhronos.glb"
* Toy car: "data/props/ToyCar.glb"
* Water bottle: "data/props/WaterBottle.glb"

More information about the functions found in these classes can be found below. 

{api_documentation}

The following buildings can be loaded. but load them only when prompted to do so:

* House: "data/ifc/AC20-FZK-Haus.ifc"
* School: "data/ifc/Technical_school-current_m.ifc"
* Office: "data/ifc/Office Building.ifc"

In the code you generate, you will consider that the following variables are already instantiated:

```python
l = Luminous()
ifc = IFC(l.load_ifc("data/ifc/AC20-FZK-Haus.ifc"))
```

Moreover, you must not give any explanation outside the code.
""".strip()

SANDBOX_VERBALIZATION_PROMPT = """
A user made an initial query. If its outcome is positive, state the changes made in the scene. Otherwise, mention that there was an error and the query could not be fulfilled. Answer using only ONE sentence.

User query: {query}
Outcome: {outcome}
""".strip()


API_DOCS = """
from ifcopenshell import file
from collections.abc import Generator

class Luminous:

    def __init__(self, address: str = "127.0.0.1", port: int = 9999):
        # Class initializer, which makes connection to the sandbox in the specified ip address and port

    def move_to(self, x: float, y: float, z: float) -> bool:
        # Moves the camera to the specified global coordinates, returning True after success (False otherwise)

    def move_relative_to(self, x: float, y: float, z: float) -> bool:
        # Moves the camera relatively, adding the x, y and z coordinates to the current values and returning True after success

    def move_forward(self, amount: float) -> bool:
        # Moves the camera forward the specified value (backward if negative) and returns True after success

    def move_right(self, amount: float) -> bool:
        # Moves the camera right the specified value (left if negative) and returns True after success

    def move_up(self, amount: float) -> bool:
        # Moves the camera up the specified value (below if negative) and returns True after success

    def rotate_to(self, pitch: float, yaw: float, roll: float) -> bool:
        # Rotates the camera to the specified global rotation values in degrees, returning True after success

    def rotate_relative_to(self, pitch: float, yaw: float, roll: float) -> bool:
        # Rotates the camera adding the input arguments to the current values, returning True after success

    def in_sight(self) -> list[dict]:
        # Returns a list of objects that are in the field of view of the camera

    def move_object_to(self, _id: str, x: float, y: float, z: float) -> bool:
        # Moves the object with the specified _id to the specified global coordinates, returning True after success

    def move_object_relative_to(self, _id: str, x: float, y: float, z: float) -> bool:
        # Moves the object with the specified _id relatively, adding the specified rotation values to the current ones and returning True after success

    def rotate_object_to(self, _id: str, pitch: float, yaw: float, roll: float) -> bool:
        # Rotates the object with the specified _id to the specified rotation values, returning True after success

    def rotate_object_relative_to(self, _id: str, pitch: float, yaw: float, roll: float) -> bool:
        # Rotates the object with the specified _id relatively, adding the specified rotation values to the current ones and returning True after success

    def scale_object_to(self, _id: str, x: float, y: float, z: float) -> bool:
        # Scales the object with the specified _id to the specified scale values, returning True after success

    def scale_object_relative_to(self, _id: str, x: float, y: float, z: float) -> bool:
        # Scales the object with the specified _id relatively, multiplying the specified scale values to the current ones and returning True after success

    def all_objects(self) -> list[dict]:
        # Returns a list of all objects in the scene

    def near_objects(self, radius: float) -> list[dict]:
        # Returns a list of objects inside the specified radius with the camera at the center. The list is ordered from closest to farthest.

    def near_object_objects(self, _id: str, radius: float) -> dict:
        # Returns a list of objects inside the specified radius with the object _id at the center. The list is ordered from closest to farthest.

    def whereami(self) -> dict:
        # Returns a dict with the current position of the camera

    def get_camera_view(self) -> dict:
        # Returns a dict with the current camera position and rotations

    def set_object_color(self, _id: str, r: float, g: float, b: float) -> bool:
        # Sets the rgb color of the object with the specified _id

    def set_object_visibility(self, _id: str, visibility: bool) -> bool:
        # Sets the visibility of the object with the specified _id
    
    def get_hidden_objects(self) -> list[str]:
        # Returns a list of ids of the objects that are currently hidden in the scene

    def distance(self, _id: str) -> float:
        # Returns the distance between the object with the specified _id and the camera in cm

    def distance_object(self, _id: str, id2: str) -> float:
        # Returns the distance between two objects with _id and _id2 in cm

    def dot(self, _id: str, id2: str) -> float:
        # Computes the dot product between the two vectors pointing at the objects _id and _id2

    def front_object(self, distance: float) -> dict:
        # Returns the object in front of the camera if there is one closer than the specified distance

    def look_at(self, _id: str) -> bool:
        # Rotates the camera to look at the object with the specified _id

    def destroy_object(self, _id: str) -> bool:
        # Removes the object with the specified _id and return True after success

    def text_to_speech(self, text: str, voice: str = ""):
        # Converts the text into speech and plays the audio in the sandbox

    def get_object_info(self, _id: str) -> dict:
        # Returns relevant information of the object with specified _id

    def load_ifc(self, filename: str) -> file:
        # Loads the ifc file containing a building given the filename. Returns an IFC file object
    
    def reset(self):
        # Destroys all exisiting entities.
 
    def is_entity_to_my_left(self, _id: str) -> bool:
        # Returns whether the object with specified _id is to the left of the camera (it could be out of the field of view)

    def is_entity_to_my_right(self, _id: str) -> bool:
        # Returns whether the object with specified _id is to the right of the camera (it could be out of the field of view)

    def is_entity_above_me(self, _id: str) -> bool:
        # Returns whether the object with specified _id is above the camera (it could be out of the field of view)
    
    def is_entity_below_me(self, _id: str) -> bool:
        # Returns whether the object with specified _id is below the camera (it could be out of the field of view)
    
    def is_entity_in_front_of_me(self, _id: str) -> bool:
        # Returns whether the object with specified _id is in front of the camera (it could be out of the field of view)
    
    def is_entity_behind_me(self, _id: str) -> bool:
        # Returns whether the object with specified _id is behind the camera (it could be out of the field of view)

    def is_entity_to_the_left(self, _id: str, _id2: str) -> bool:
        # Returns whether the first object with _id is to the left of the second object with _id2

    def is_entity_to_the_right(self, _id: str, _id2: str) -> bool:
        # Returns whether the first object with _id is to the right of the second object with _id2

    def is_entity_above(self, _id: str, _id2: str) -> bool:
        # Returns whether the first object with _id is above the second object with _id2
    
    def is_entity_below(self, _id: str, _id2: str) -> bool:
        # Returns whether the first object with _id is below the second object with _id2
    
    def is_entity_in_front(self, _id: str, _id2: str) -> bool:
        # Returns whether the first object with _id is in front of the second object with _id2
    
    def is_entity_behind(self, _id: str, _id2: str) -> bool:
        # Returns whether the first object with _id is behind the second object with _id2
    
    def destroy_prop(self, _id: str) -> bool:
        # Rotates the prop with the specified _id and returns True after success.

    def rotate_prop_yaw(self, _id: str, yaw: float = 90) -> bool:
        # Rotates the prop with the specified _id the specified value in the y axis and returns True after success.
    
    def scale_prop(self, _id: str, amount: float) -> bool:
        # Scales the prop with the specified _id to the specified value and returns True after success.

    def move_prop_up(self, _id: str, amount: float) -> bool:
        # Moves the prop with the specified _id the specified amount (in centimeters) in the y axis and returns True after success.

    def move_prop_right(self, _id: str, amount: float) -> bool:
        # Rotates the prop with the specified _id the specified amount (in centimeters) in the x axis and returns True after success.
    
    def move_prop_forward(self, _id: str, amount: float) -> bool:
        # Moves the prop with the specified _id the specified amount (in centimeters) in the z axis and returns True after success.

    def move_prop_to_wall(self, _id: str) -> bool:
        # Moves the prop with the specified _id to the nearest wall in the direction of the camera, returning True after success.

    def move_prop_to_floor(self, _id: str) -> bool:
        # Moves the prop with the specified _id to the floor in the direction of the camera, returning True after success.
    
    def reset(self) -> bool:
        # Resets the sandbox, removing all objects and resetting the camera position and rotation. Returns True after success.
    
    def load_prop(self, filename: str, tags: list[str] = [], variant: str = "") -> str:
        # Loads a prop from the specified filename, with the given tags and variant. Returns the id of the loaded prop.
    
        
class Entity:

    def __init__(self, entity):
        # Initializes Entity class with the given entity, which can be obtained from the IFC class' functions.

    @property
    def name(self) -> str:
        # Returns its name

    @property
    def type(self) -> str:
        # Returns its IFC type

    @property
    def guid(self) -> str:
        # Returns its global id

    def is_wall(self) -> bool:
        # Returns true if entity is wall

    def is_column(self) -> bool:
        # Returns true if entity is column

    def is_beam(self) -> bool:
        # Returns true if entity is beam

    def is_ramp(self) -> bool:
        # Returns true if entity is ramp

    def is_window(self) -> bool:
        # Returns true if entity is window

    def is_stair(self) -> bool:
        # Returns true if entity is stair

    def is_roof(self) -> bool:
        # Returns true if entity is roof

    def is_door(self) -> bool:
        # Returns true if entity is door

    def is_slab(self) -> bool:
        # Returns true if entity is slab

    def is_footing(self) -> bool:
        # Returns true if entity is footing


class IFC:

    def __init__(self, filename_or_model):
        # Initializes IFC model

    def get_by_guid(self, guid: str) -> Entity:
        # Returns entity by guid

    def find_by_type(self, _type: str) -> Generator[Entity]:
        # Returns a generator with entities of the specified _type

    def find_all_walls(self) -> Generator[Entity]:
        # Returns a generator with wall entities

    def find_all_columns(self) -> Generator[Entity]:
        # Returns a generator with column entities

    def find_all_beams(self) -> Generator[Entity]:
        # Returns a generator with beam entities

    def find_all_ramps(self) -> Generator[Entity]:
        # Returns a generator with ramp entities

    def find_all_windows(self) -> Generator[Entity]:
        # Returns a generator with window entities

    def find_all_stairs(self) -> Generator[Entity]:
        # Returns a generator with stair entities

    def find_all_roofs(self) -> Generator[Entity]:
        # Returns a generator with roof entities

    def find_all_doors(self) -> Generator[Entity]:
        # Returns a generator with door entities

    def find_all_slabs(self) -> Generator[Entity]:
        # Returns a generator with slab entities

    def find_all_footings(self) -> Generator[Entity]:
        # Returns a generator with footing entities
""".strip()


CHAT_API_EXAMPLES = [
    {
        "role": "user",
        "content": "Destroy all walls of the scene.",
    },
    {
        "role": "assistant",
        "content": """
```python
# Destroy all walls
for wall in ifc.find_all_walls():
    l.destroy_object(wall.guid)
```
""".strip()
    },
    {
        "role": "user",
        "content": "Set the color of the nearest door and the farthest window to blue.",
    },
    {
        "role": "assistant",
        "content": """
```python
# Only take objects in sight into account
ids_in_sight = [object["id"] for object in l.in_sight()]

# Create two ordered lists, for doors and for windows
door_ids, window_ids = [], []
for object in l.near_objects(3000):
    entity = ifc.get_by_guid(object["id"])
    if entity.guid in ids_in_sight:
        if entity.is_window():
            window_ids.append(entity.guid)
        if entity.is_door():
            door_ids.append(entity.guid)

# Identify the nearest door and the furthest window and paint them blue
if len(window_ids) > 0:
    nearest_door_id = door_ids[0]
    farthest_window_id = window_ids[-1]
    l.set_object_color(_id=nearest_door_id, r=0.0, g=0.0, b=1.0)
    l.set_object_color(_id=farthest_window_id, r=0.0, g=0.0, b=1.0)
```
""".strip()
    },
    {
        "role": "user",
        "content": "Hide the door to my left.",
    },
    {
        "role": "assistant",
        "content": """
```python
# Get ids of all doors
door_ids = [door.guid for door in ifc.find_all_doors()]

# Iterate over all objects in sight and hide the door to the left
for object in l.in_sight():
    entity_id = object["id"]
    if entity_id in door_ids:
        if l.is_entity_to_my_left(entity_id):
            l.set_object_visibility(entity_id, False)
            break
```
""".strip()
    },
    {
        "role": "user",
        "content": "Load the school.",
    },
    {
        "role": "assistant",
        "content": """
```python
l.reset()
ifc = IFC(l.load_ifc("data/ifc/Technical_school-current_m.ifc"))
```
""".strip()
    },
    {
        "role": "user",
        "content": "Place a chair in front of me and a lamp near it.",
    },
    {
        "role": "assistant",
        "content": """
```python
# Add the lamp
lamp_path = "data/props/IridescenceLamp.glb"
lamp_id = l.load_prop(lamp_path)

chair_path = "data/props/ChairDamaskPurplegold.glb"
chair_id = l.load_prop(chair_path)

# Move the lamp to the floor
l.move_prop_to_floor(chair_id)

# To properly place the chair near the lamp, place it on the floor and then move it nearby
l.move_prop_to_floor(lamp_id)
l.move_prop_forward(lamp_id, 100) # Move the lamp 1 meter forward
l.move_prop_right(lamp_id, 100) # Move the lamp 1 meter to the right
```
""".strip()
    },
    {
        "role": "user",
        "content": "Put a sheen chair on the floor and an iridescence lamp on the wall, moving it 0.5 meters to the left.",
    },
    {
        "role": "assistant",
        "content": """
```python
# Load the chair and position it on the floor
chair_id = l.load_prop("data/props/Sheenchair.glb")
l.move_prop_to_floor(chair_id)

# Load the lamp, position it on the wall and move it to the left
lamp_id = l.load_prop("data/props/IridescenceLamp.glb")
l.move_prop_to_wall(lamp_id)
l.move_prop_right(lamp_id, -50)  # Move it 0.5 meters to the left
```
""".strip()
    },
    {
        "role": "user",
        "content": "Focus my view at the window to the right of the door.",
    },
    {
        "role": "assistant",
        "content": """
```python
# Find the mentioned door
door_ids = [entity.guid for entity in ifc.find_all_doors()]
door_id = None
for entity in l.in_sight():
    if entity["id"] in door_ids:
        door_id = entity["id"]

# Find the window to the right of the mentioned door
if door_id is not None: 
    window_ids = [entity.guid for entity in ifc.find_all_windows()]
    window_id = None
    for entity in l.in_sight():
        if entity["id"] in window_ids and l.is_entity_to_the_right(entity["id"], door_id):
            window_id = entity["id"]

    # Look at the identified window
    if window_id is not None:
        l.look_at(window_id)
```
""".strip()
    },
]

# EXTRA API (not used by LLM)
""" 
def start_microphone_capture(self):
    # Starts recording the microphone

def stop_microphone_capture(self) -> tuple[int, int, bytes]:
    # Stops recording the microphone and returns a tuple containing the number of channels, sample rate and byte stream
"""