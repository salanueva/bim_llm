import ifcopenshell
import ifcopenshell.util.element


class Entity:

    def __init__(self, entity):
        self.entity = entity
        self._guid = entity.GlobalId if not isinstance(entity, dict) else entity["id"]

    @property
    def name(self):
        return self.entity.Name

    @property
    def type(self):
        return self.entity.is_a()

    @property
    def guid(self):
        return self._guid

    def is_wall(self):
        return self.entity.is_a("IfcWall")

    def is_column(self):
        return self.entity.is_a("IfcColumn")

    def is_beam(self):
        return self.entity.is_a("IfcBeap")

    def is_ramp(self):
        return self.entity.is_a("IfcRamp")

    def is_window(self):
        return self.entity.is_a("IfcWindow")

    def is_stair(self):
        return self.entity.is_a("IfcStair")

    def is_roof(self):
        return self.entity.is_a("IfcRoof")

    def is_door(self):
        return self.entity.is_a("IfcDoor")

    def is_slab(self):
        return self.entity.is_a("IfcSlab")

    def is_footing(self):
        return self.entity.is_a("IfcFooting")


class IFC:

    def __init__(self, filename_or_model):
        if isinstance(filename_or_model, str):
            self.model = ifcopenshell.open(filename_or_model)
        else:
            self.model = filename_or_model

    def get_by_guid(self, guid):
        return Entity(self.model.by_guid(guid))

    def find_by_type(self, _type):
        for entity in self.model.by_type(_type):
            yield Entity(entity)

    def find_all_walls(self):
        return self.find_by_type("IfcWall")

    def find_all_columns(self):
        return self.find_by_type("IfcColumn")

    def find_all_beams(self):
        return self.find_by_type("IfcBeam")

    def find_all_ramps(self):
        return self.find_by_type("IfcRamp")

    def find_all_windows(self):
        return self.find_by_type("IfcWindow")

    def find_all_stairs(self):
        return self.find_by_type("IfcStair")

    def find_all_roofs(self):
        return self.find_by_type("IfcRoof")

    def find_all_doors(self):
        return self.find_by_type("IfcDoor")

    def find_all_slabs(self):
        return self.find_by_type("IfcSlab")

    def find_all_footings(self):
        return self.find_by_type("IfcFooting")
