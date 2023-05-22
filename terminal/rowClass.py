from .stackClass import Stack
from .stackClass import deserialize as stack_deserialize
import pandas as pd
from copy import deepcopy
from itertools import chain
import ast
import json 

class Row:
    
    def __init__(self,block_name,row_name, stack_list, n_stacks = 5,stack_height = 6):
        self.row_name = block_name+row_name
        self.block_name = block_name

        self.stack_height = stack_height
        self.n_stacks = n_stacks
        self.max_containers = n_stacks*stack_height
        self.stacks = {}
        self.n_containers = 0
        
        self.stack_height_available_spot_stacks = []

        self.top_spot_container_stacks = []

        if len(stack_list) == 0:
            for x in range(0,self.n_stacks):
                self.stacks[self.row_name+str(x)] = Stack(self.row_name,str(x),[],stack_height)
                self.stack_height_available_spot_stacks.append(self.stacks[self.row_name+str(x)].get_stack_height_available_spot())

        else:

            for stack in stack_list:
                self.n_containers += stack.get_n_containers()
                
            if self.n_containers>self.max_containers:
                raise Exception("Too many containers allocated to Row") 

            for x in range (0,len(stack_list)):
                self.stacks[self.row_name+str(x)] = stack_list[x]
                self.stack_height_available_spot_stacks.append(self.stacks[self.row_name+str(x)].get_stack_height_available_spot())
                self.top_spot_container_stacks.append(self.stacks[self.row_name+str(x)].get_top_spot_container())

            for i in range(len(stack_list),self.n_stacks):
                self.stacks[self.row_name+str(i)] = Stack(self.row_name,str(i),[],stack_height)
                self.stack_height_available_spot_stacks.append(self.stacks[self.row_name+str(x)].get_stack_height_available_spot())

    def add_container(self,container,location):
        # print("in row add container")
        self.n_containers+=1

        return  self.stacks[location].add_container(container)

    def remove_container(self, location,reshuffle_external):

        stack_name = location[0:3]
        self.n_containers-=1

        return self.stacks[stack_name].remove_container(location,reshuffle_external)

    def contains_container(self, container_number):

        for stack_n, stack in self.stacks.items():
            container_exists,location = stack.contains_container(container_number)
            if container_exists:
                break

        return container_exists, location

    def __str__(self):
        str_dict = pd.DataFrame()

        for stack_pos in self.stacks.keys():
            stack_str = str(self.stacks[stack_pos])
            #print(row_str)
            str_dict[self.stacks[stack_pos].stack_name] = stack_str

        return str(str_dict)

    def pretty_str(self):
        str_dict = {}

        for stack_pos in self.stacks.keys():
            stack_dict = self.stacks[stack_pos].pretty_str()
            #print(row_str)
            str_dict[stack_pos] = stack_dict

        return str_dict

    def copy(self):

        new_row = Row(self.block_name,self.row_name[:-1],[],self.n_stacks,self.stack_height)

        new_row.n_containers = deepcopy(self.n_containers)
        
        new_row.stack_height_available_spot_stacks = deepcopy(self.stack_height_available_spot_stacks)

        new_row.top_spot_container_stacks = deepcopy(self.top_spot_container_stacks)

        new_stacks = {}
        for stack_name, stack in self.stacks.items():
            new_stacks[stack_name] = stack.copy()
        new_row.stacks = new_stacks

        return new_row

    def serialize_in_class(self):
        self_dict  = deepcopy(self.__dict__)
        self_dict['stacks'] = {position: stack.serialize_in_class() for position, stack in self_dict['stacks'].items() }

        return self_dict
    
    def get_stack_height_available_spot_stacks(self):
        return self.stack_height_available_spot_stacks

    def get_top_spot_container_stacks(self):
        return self.top_spot_container_stacks
    
    def get_n_containers(self):
        return self.n_containers


def deserialize(row_dict):

    #self,block_name,row_name, stack_list, n_stacks = 5,stack_height = 6
    new_row = Row(row_dict["block_name"],row_dict["row_name"],[],row_dict["n_stacks"],row_dict["stack_height"])

    new_row.n_containers = row_dict['n_containers']
    new_row.stack_height_available_spot_stacks = row_dict['stack_height_available_spot_stacks']
    new_row.top_spot_container_stacks = row_dict['top_spot_container_stacks']


    new_stacks = {}
    for stack_number,stack in row_dict["stacks"].items():
        new_stacks[stack_number] = stack_deserialize(stack)
    new_row.stacks = new_stacks

    return new_row




