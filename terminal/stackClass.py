import pandas as pd
import json
from copy import deepcopy
import ast
from .containerClass import Container
from .containerClass import deserialize as container_deserialize
class Stack:

    def __init__(self, row_name, stack_n_string, container_list, stack_height):
        self.stack_name = row_name+stack_n_string
        self.stack_n_string = stack_n_string
        self.row_name = row_name
        self.stack_height = stack_height
        self.n_containers = 0
        #dict of spot_number :container to keep track of containers
        self.containers = {}

        #if there is an available spot in the stack, and at least one container 
        #this is a dict of {available_spot: container below available spot}
        #for use in finding the dwell time of container
        self.top_spot_container = {}

        #stack_height_available_spot is a dict 
        # {stack_name: height}
        #if the stack is available, otherwise {}
        self.stack_height_available_spot = {}

        # Empty Stack, fill with None
        if len(container_list) == 0:
            self.n_containers = 0
            for x in range(0,stack_height):
                self.containers[self.stack_name+str(x)] = None
            self.stack_height_available_spot = {self.stack_name :0}

        #Non-empty Stack, fill with Some
        #check number of containers in list relative to stack_height
        else:
            self.n_containers = len(container_list)
            if self.n_containers>stack_height:
                raise Exception("Too many containers allocated to stack") 

            for container_position in range (0,self.n_containers):
                self.containers[self.stack_name+str(container_position)] = container_list[container_position]
                self.containers[self.stack_name+str(container_position)].set_location(self.stack_name+str(container_position))

            if self.n_containers<stack_height:
                self.stack_height_available_spot = {self.stack_name : self.n_containers}
                self.top_spot_container = {self.stack_name:self.containers[self.stack_name+str(container_position)].get_synthetic_etd()}

            for i in range(self.n_containers,stack_height):
                self.containers[self.stack_name+str(i)] = None

    def add_container(self, container: Container):
        if self.n_containers>= self.stack_height:
            raise Exception("Trying to add container to full stack")
        # print(f"in add container to stack, adding {container.serialize_in_class()}")
        # print(f"stack n_continers: {self.n_containers}")
        # print(f"stack before: {json.dumps(self.serialize_in_class())}")

        self.containers[self.stack_name+str(self.n_containers)] = container.copy()
        self.containers[self.stack_name+str(self.n_containers)].set_location(self.stack_name+str(self.n_containers))
        self.n_containers+=1

        if self.n_containers<self.stack_height:
            self.stack_height_available_spot = {self.stack_name : self.n_containers}
            self.top_spot_container = {self.stack_name:self.containers[self.stack_name+str(self.n_containers-1)].get_synthetic_etd()}

        else:
            self.stack_height_available_spot = {}
            self.top_spot_container = {}
        # print(f"stack after: {json.dumps(self.serialize_in_class())}")
        return self.stack_height_available_spot, self.top_spot_container


    #returns None if no container was found

    #If reshuffle_external = False
    #returns the container, number of reshuffles, 
    # top_available_spot, top_spot_container, 
    # n_containers in stack, total_moves from removal
    # and []
    # and places containers on top of extracted container back in stack in same order

    #if reshuffle_external = True 
    #returns the same info as above, with addition of list of containers above in reverse order
    #[top_container,second_highest_container...] for the purposes of stacking again
    #containers are removed from stack 
    #empty list is returned if no containers above

    def remove_container(self,location, reshuffle_external):

        # self.stack_height_available_spot = {self.stack_name : self.n_containers}
        # self.top_spot_container = {self.stack_name:self.containers[self.stack_name+str(self.n_containers-1)].get_synthetic_etd()}

        #container location is Char(block)Char(row)Num(stack)Num(position)
        container_position = location[3]

        temp_container = self.containers[location].copy().remove_location()
        self.containers[location] = None

        #collect containers above
        containers_above = []
        for cont_location in range(int(container_position)+1,self.n_containers):
            container_copy = self.containers[self.stack_name+str(cont_location)].copy().remove_location()
            containers_above.append(container_copy)
            self.containers[self.stack_name+str(cont_location)] = None

        #add number of containers to moves, plus container removed as moves

        self.n_containers-=(1+len(containers_above)) if reshuffle_external else 1
        # total_moves = (1+len(containers_above)) if reshuffle_external else (1+2*len(containers_above))
        # total_moves = (1+len(containers_above))
        total_moves = 1
        ### LOOK INTO THIS ###
        # reshuffles = 2*len(containers_above)
        reshuffles = len(containers_above)
        ######################
        # print(f"n_containers in stack: {self.n_containers}")
        if not reshuffle_external:
            index = 0
            for position in range(int(container_position),int(container_position)+len(containers_above)):
                self.containers[self.stack_name+str(position)] = containers_above[index]
                self.containers[self.stack_name+str(position)].set_location(self.stack_name+str(position))
                index+=1
        # print(f"stack_containers: {self.containers}")
        if self.n_containers==0:
            self.stack_height_available_spot = {self.stack_name : self.n_containers}
            self.top_spot_container = {}
        elif self.n_containers<self.stack_height:
            self.stack_height_available_spot = {self.stack_name : self.n_containers}
            self.top_spot_container = {self.stack_name:self.containers[self.stack_name+str(self.n_containers-1)].get_synthetic_etd()}
        else:
            self.stack_height_available_spot = {}
            self.top_spot_container = {}

        if reshuffle_external:
            return_list = containers_above
        else:
            return_list = []

        return temp_container, self.stack_height_available_spot, self.top_spot_container, total_moves, reshuffles, return_list

    def contains_container(self, container_number):
        # print(f"in contains container stack, looking for: {container_number}")
        container_exists = False
        location = None
        for position, container in self.containers.items():
            # print(f"checking position: {position}, container: {container}")
            if container!= None:
                if container_number == container.get_number():
                    # print("container number matched")
                    container_exists = True
                    location = container.get_location()
                    # print(f"container_exists = {container_exists}, container_location = {location}")
                    break

        # print("here")
        return container_exists, location


    def copy(self):
        new_stack = Stack(self.row_name, self.stack_n_string, [], self.stack_height)

        new_stack.n_containers = deepcopy(self.n_containers)

        new_stack.top_spot_container = deepcopy(self.top_spot_container)

        #stack_height_available_spot is a dict 
        # {stack_name: height}
        #if the stack is available, otherwise {}
        new_stack.stack_height_available_spot = deepcopy(self.stack_height_available_spot)

        new_containers = {}
        for stack_position, container in self.containers.items():
            new_containers[stack_position] = container.copy() if container!=None else None
        new_stack.containers = new_containers
        
        return new_stack


    def __str__(self):
        str_list = []
        for spot in reversed(list(self.containers.keys())):

            str_list.append(str(self.containers[spot]))

        return str(str_list)

    def pretty_str(self):
        str_list = []
        for spot in reversed(list(self.containers.keys())):

            str_list.append(str(self.containers[spot]))

        return str_list

    def serialize_in_class(self):
        self_dict = deepcopy(self.__dict__)
        self_dict["containers"] = {position: container.serialize_in_class() for position, container in self_dict['containers'].items() if container != None}

        return self_dict
    
    def get_n_containers(self):
        return self.n_containers

    def get_top_spot_container(self):
        return self.top_spot_container
    
    def get_stack_height_available_spot(self):
        return self.stack_height_available_spot

def deserialize(stack_dict):
    new_stack = Stack(stack_dict["row_name"],stack_dict["stack_n_string"],[],stack_dict["stack_height"])
    new_stack.top_spot_container = stack_dict['top_spot_container']
    new_stack.stack_height_available_spot = stack_dict['stack_height_available_spot']
    new_stack.n_containers = stack_dict["n_containers"]
    new_containers = {}
    for container_location, container in stack_dict["containers"].items():
        new_containers[container_location] = container_deserialize(container)
    
    new_stack.containers = new_containers

    return new_stack





    
        
    