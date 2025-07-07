from abc import ABC
import logging

from src.luminous.luminous import Luminous
from src.luminous.luminous_ifc import IFC, Entity



class SandboxHandler(ABC):

    def __init__(self):
                
        self.sandbox = Luminous() 
        self.ifc = None

    @classmethod
    def from_ifc(cls, ifc_filename: str) -> "SandboxHandler":
        sandbox = cls()
        sandbox.reset_ifc(ifc_filename)
        return sandbox
    

    def reset_ifc(self, ifc_filename: str) -> None:
        self.sandbox.reset()
        self.ifc = IFC(self.sandbox.load_ifc(ifc_filename))
        

    def __call__(self, code: str) -> str:

        variables = {"l": self.sandbox, "ifc": self.ifc, "IFC": IFC, "Entity": Entity}
        logging.debug("Attempting to execute code...")
        try:
            exec(code, variables)
            self.ifc = variables["ifc"]
        except Exception as e:
            logging.error("Error executing code: %s", e)
            return "There was an error when trying to fulfill the query."
        logging.debug("Code executed successfully!")
        return "The query was successfully followed."