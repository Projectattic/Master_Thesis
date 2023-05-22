import json
from copy import deepcopy

class Container:

    def __init__(self, container_number,etd,synthetic_etd = 0):

        self.container_number = container_number
        self.etd = etd
        self.synthetic_etd = synthetic_etd
        self.container_location = None
    
    def set_location(self, location):
        self.container_location = location
        return self

    def get_location(self):
        return self.container_location
    
    def remove_location(self):
        self.container_location = None
        return self

    def get_number(self):
        return self.container_number

    def get_etd(self):
        return self.etd
    
    def get_synthetic_etd(self):
        return self.synthetic_etd

    def copy(self):
        new_container = Container(self.container_number, self.etd,self.synthetic_etd)
        new_container.container_location = deepcopy(self.container_location)
        return new_container

    def __str__(self):
        return self.container_number

    def serialize_in_class(self):
        return json.loads(json.dumps(self.__dict__))

    def to_prolog_string(self):
        str_build = """"""
        str_build += f'container({self.container_number.lower()},{self.container_location.lower()},{self.etd})'
        return str_build


def serialize(container):
    return json.dumps(container.__dict__)

def deserialize(container_dict):
    new_container = Container(container_dict['container_number'],container_dict['etd'],container_dict['synthetic_etd'])
    new_container.container_location = container_dict["container_location"]
    return new_container

