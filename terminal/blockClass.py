import pandas as pd
import string
from .rowClass import Row
from .rowClass import deserialize as row_deserialize
from itertools import chain
from copy import deepcopy
import json

class Block:

    def __init__(self,block_name, row_list, n_rows,n_stacks,stack_height):

        self.block_name = block_name
        self.n_rows = n_rows
        self.n_stacks = n_stacks
        self.stack_height = stack_height
        self.max_containers = n_rows*n_stacks*stack_height
        self.rows = {}
        alphabet = list(string.ascii_uppercase)
        
        self.n_containers = 0
        self.n_moves = 0
        self.container_reshuffles = 0
        self.block_utilization = 0

        self.stack_height_available_spot_stacks = []
        #for fuzzylogic - list of available spots and container synthetic_etd below
        #[{spot: container_synthetic_etd}]
        self.top_spot_container_stacks = []

        #Empty block, fill with None
        if len(row_list) == 0:
            for x in range(0, n_rows):
                self.rows[self.block_name+alphabet[x]] = Row(self.block_name,alphabet[x],[],n_stacks,stack_height)
                self.stack_height_available_spot_stacks += self.rows[self.block_name+alphabet[x]].get_stack_height_available_spot_stacks()
            
        else:
            for row in row_list:
                self.n_containers += row.get_n_containers()

            if self.n_containers>self.max_containers:
                raise Exception("Too many containers allocated to terminal")
            
            for x in range(0,len(row_list)):
                self.rows[self.block_name+alphabet[x]] = row_list[x]
                self.stack_height_available_spot_stacks += self.rows[self.block_name+alphabet[x]].get_stack_height_available_spot_stacks()
                self.top_spot_container_stacks += self.rows[self.block_name+alphabet[x]].get_top_spot_container_stacks()

            for i in range(len(row_list),self.n_rows):
                self.rows[alphabet[i]] =  Row(self.block_name,alphabet[i],[],n_stacks,stack_height)
                self.stack_height_available_spot_stacks += self.rows[self.block_name+alphabet[i]].get_stack_height_available_spot_stacks()

        self.block_utilization = self.n_containers/self.max_containers
            
        
    #location is given as "Char(block)Char(row)Number(stack)"
    def add_container(self,container,location):
        # print("in block add container")
        row = location[0:2]
        self.n_containers +=1
        self.n_moves+=1
        self.block_utilization = self.n_containers/self.max_containers
        return self.rows[row].add_container(container,location)
        
    def remove_container(self,location,reshuffle_external):

        row = location[0:2]

        temp_container, stack_height_available_spot, top_spot_container, total_moves, reshuffles, return_list = self.rows[row].remove_container(location,reshuffle_external)
        self.n_containers -=1
        if reshuffle_external:
            # print(f"reshuflles given in block: {reshuffles}")
            self.n_containers-=reshuffles
        self.n_moves+=total_moves
        self.container_reshuffles+=reshuffles
        self.block_utilization = self.n_containers/self.max_containers

        return temp_container, stack_height_available_spot, top_spot_container, total_moves, reshuffles, return_list


    def get_n_containers(self):
        return self.n_containers

    def contains_container(self, container_number):

        for row_n, row in self.rows.items():
            container_exists,location = row.contains_container(container_number)
            if container_exists:
                break
        return container_exists,location

    def __str__(self):
        str_dict = pd.DataFrame()

        for row_pos in self.rows.keys():
            row_str = str(self.rows[row_pos])
            #print(row_str)
            str_dict[self.rows[row_pos].row_name] = row_str

        return str(str_dict)

    def pretty_str(self):
        str_dict = {}

        for row_pos in self.rows.keys():
            row_dict = self.rows[row_pos].pretty_str()
            #print(row_str)
            str_dict[row_pos] = row_dict

        return str_dict

    def copy(self):
        new_block = Block(self.block_name,[],self.n_rows,self.n_stacks,self.stack_height)
        new_block.n_containers = deepcopy(self.n_containers)

        new_block.n_moves = deepcopy(self.n_moves)
        new_block.container_reshuffles = deepcopy(self.container_reshuffles)
        

        new_block.block_utilization = deepcopy(self.block_utilization)

        new_block.stack_height_available_spot_stacks = deepcopy(self.stack_height_available_spot_stacks) 
        #for fuzzylogic - list of available spots and container synthetic_etd below
        #[{spot: container_synthetic_etd}]
        new_block.top_spot_container_stacks = deepcopy(self.top_spot_container_stacks)

        new_rows = {}
        for row_name, row in self.rows.items():
            new_rows[row_name] = row.copy()
        new_block.rows = new_rows

        return new_block


    def get_block_utilization(self):
        return self.block_utilization
    
    def get_stack_height_available_spot_stacks(self):
        return self.stack_height_available_spot_stacks

    def get_top_spot_container_stacks(self):
        return self.top_spot_container_stacks

    def serialize_in_class(self):
        self_dict = deepcopy(self.__dict__)
        self_dict['rows'] = {position: row.serialize_in_class() for position, row in self_dict['rows'].items() }

        return self_dict
    
def deserialize(block_dict):

    new_block = Block(block_dict["block_name"],[],block_dict["n_rows"],block_dict["n_stacks"],block_dict["stack_height"])
    new_block.n_containers = block_dict['n_containers']
    new_block.n_moves = block_dict['n_moves']
    new_block.container_reshuffles = block_dict['container_reshuffles']
    new_block.block_utilization = block_dict['block_utilization']
    new_block.stack_height_available_spot_stacks = block_dict['stack_height_available_spot_stacks']
    new_block.top_spot_container_stacks = block_dict['top_spot_container_stacks']


    new_rows = {}
    for row_number,row in block_dict["rows"].items():
        new_rows[row_number] = row_deserialize(row)
    new_block.rows = new_rows

    return new_block

    

