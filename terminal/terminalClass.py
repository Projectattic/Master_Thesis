import pandas as pd
import string
from .blockClass import Block
from .blockClass import deserialize as block_deserialize
from itertools import chain
from copy import deepcopy
import json

class Terminal:

    def __init__(self, block_list, n_blocks = 5, n_rows = 5,n_stacks = 5,stack_height =6):

        self.n_blocks = n_blocks
        self.n_rows = n_rows
        self.n_stacks = n_stacks
        self.stack_height = stack_height
        self.max_containers = n_blocks*n_rows*n_stacks*stack_height
        self.blocks = {}
        alphabet = list(string.ascii_uppercase)

        self.n_containers = 0
        self.n_moves = 0
        self.container_reshuffles = 0
        self.peak_block_utilization = 0
        #{block_name:block_utilization}
        self.block_utilizations = {}

        self.stack_height_available_spot_stacks = []
        #for fuzzylogic - list of available spots and container synthetic_etd below
        #[{spot: container_synthetic_etd}]
        self.top_spot_container_stacks = []
        

        if len(block_list) == 0:
            for x in range(0, n_blocks):
                self.blocks[alphabet[x]] = Block(alphabet[x],[],n_rows,n_stacks,stack_height)
                self.stack_height_available_spot_stacks+= self.blocks[alphabet[x]].get_stack_height_available_spot_stacks()
                self.block_utilizations[alphabet[x]] = self.blocks[alphabet[x]].get_block_utilization()

        else:
            for block in block_list:
                self.n_containers += block.get_n_containers()

            if self.n_containers>self.max_containers:
                raise Exception("Too many containers allocated to terminal")
            
            for x in range(0,len(block_list)):
                self.blocks[alphabet[x]] = block_list[x]
                self.stack_height_available_spot_stacks+= self.blocks[alphabet[x]].get_stack_height_available_spot_stacks() 
                self.top_spot_container_stacks+= self.blocks[alphabet[x]].get_top_spot_container_stacks()                                   
                self.block_utilizations[alphabet[x]] = self.blocks[alphabet[x]].get_block_utilization()
                if self.block_utilizations[alphabet[x]] > self.peak_block_utilization:
                    self.peak_block_utilization = self.block_utilizations[alphabet[x]]

            for i in range(len(block_list),self.n_rows):
                self.blocks[alphabet[i]] =  Block(alphabet[i],[],n_rows,n_stacks,stack_height)
                self.stack_height_available_spot_stacks+= self.blocks[alphabet[i]].get_stack_height_available_spot_stacks() 
                self.block_utilizations[alphabet[i]] = self.blocks[alphabet[x]].get_block_utilization()

    def add_container(self,container,location):
        # print("in terminal add_container")
        # print(f"adding container {container.container_number} to location: {location}")
        block = location[0:1]
        self.purge_location(location)
        stack_height_available_spot, top_spot_container = self.blocks[block].add_container(container,location)
        # print(stack_height_available_spot)
        # print(top_spot_container)
        self.block_utilizations[block] = self.blocks[block].get_block_utilization()
        if self.block_utilizations[block] > self.peak_block_utilization:
                    self.peak_block_utilization = self.block_utilizations[block]


        if stack_height_available_spot:
            # print(f"stack_h: {stack_height_available_spot}")
            new_stack_height = list(stack_height_available_spot.values())[0]
            if new_stack_height< self.stack_height:
                self.stack_height_available_spot_stacks.append(stack_height_available_spot)
            # print(f"stack_hs: {self.stack_height_available_spot_stacks}")
        if top_spot_container:
            stack = list(stack_height_available_spot.keys())[0]
            new_stack_height = self.blocks[stack[0]].rows[stack[0:2]].stacks[stack].n_containers +1
            if new_stack_height< self.stack_height:
                self.top_spot_container_stacks.append(top_spot_container)                                
        self.n_containers +=1
        self.n_moves+=1


        
    def remove_container(self,container_number,reshuffle_external):
        container_exists, location_det = self.contains_container(container_number)

        if not container_exists:
            return None,[]
        else:
            # print(f"container exists, location found:{location_det} ")
            block = location_det[0]
            location = location_det[:-1]

            self.purge_location(location)
            temp_container, stack_height_available_spot, top_spot_container, total_moves, reshuffles, return_list = self.blocks[block].remove_container(location_det,reshuffle_external)

            self.block_utilizations[block] = self.blocks[block].get_block_utilization()
            if stack_height_available_spot:
                self.stack_height_available_spot_stacks.append(stack_height_available_spot)
            if top_spot_container:
                self.top_spot_container_stacks.append(top_spot_container)                                
            self.n_containers +=1
            self.n_moves+=total_moves
            self.container_reshuffles += reshuffles

            return_list.reverse()

            return temp_container, return_list
        

    def contains_container(self, container_number):

        for block_n, block in self.blocks.items():
            container_exists,location = block.contains_container(container_number)
            if container_exists:
                break
        return container_exists,location


    def __str__(self):
        str_dict = pd.DataFrame()

        for block_pos in self.blocks.keys():
            block_str = str(self.blocks[block_pos])
            #print(row_str)
            str_dict[self.blocks[block_pos].block_name] = block_str

        return str(str_dict)
    
    def pretty_str(self):
        str_dict = {}

        for block_pos in self.blocks.keys():
            block_dict = self.blocks[block_pos].pretty_str()
            #print(row_str)
            str_dict[block_pos] = block_dict

        return json.dumps(str_dict,indent=4)


    def copy(self):
        new_terminal = Terminal([],self.n_blocks,self.n_rows,self.n_stacks,self.stack_height)
        new_terminal.n_containers = deepcopy(self.n_containers)
        new_terminal.n_moves =  deepcopy(self.n_moves)
        new_terminal.container_reshuffles =  deepcopy(self.container_reshuffles)
        new_terminal.peak_block_utilization =  deepcopy(self.peak_block_utilization)
        new_terminal.block_utilizations =   deepcopy(self.block_utilizations)

        new_terminal.stack_height_available_spot_stacks =   deepcopy(self.stack_height_available_spot_stacks)

        new_terminal.top_spot_container_stacks =   deepcopy(self.top_spot_container_stacks)


        new_blocks = {}
        for block_name, block in self.blocks.items():
            new_blocks[block_name] = block.copy()
        new_terminal.blocks = new_blocks

        return new_terminal
    

    def serialize_in_class(self):
        self_dict = deepcopy(self.__dict__)
        self_dict['blocks'] = {position: block.serialize_in_class() for position, block in self_dict['blocks'].items() }

        return self_dict
    

    def get_highest_stacks(self):
        max_value = max(self.collect_vals())

        highest_stacks = []
        for i in  self.stack_height_available_spot_stacks:
            if list(i.values())[0] == max_value:
                highest_stacks.append(list(i.keys())[0])
        return highest_stacks
    
    def get_lowest_stacks(self):
        min_value = min(self.collect_vals())

        lowest_stacks = []
        for i in  self.stack_height_available_spot_stacks:
            if list(i.values())[0] == min_value:
                lowest_stacks.append(list(i.keys())[0])
        return lowest_stacks

    def get_empty_stacks(self):
        # print(f"in_terminal get empty stacks")
        empty_stacks = []
        # print(f"stack_heights: \n {self.stack_height_available_spot_stacks}")
        for i in  self.stack_height_available_spot_stacks:
            # print(f"i: {i}")
            # print(f"list(i.values())[0] {list(i.values())[0]}")
            if list(i.values())[0] == 0:
                empty_stacks.append(list(i.keys())[0])
        return empty_stacks

    def get_available_stacks(self):
        available_stacks = self.collect_keys()

        return available_stacks
    
    def get_top_spot_container_stacks(self):
        return self.top_spot_container_stacks
    
    def get_block_utilizations(self):
        return self.block_utilizations

    def collect_keys(self):
        keys = []
        if self.stack_height_available_spot_stacks:
            keys = [list(i.keys())[0] for i in self.stack_height_available_spot_stacks]
        return keys
    
    def collect_vals(self):
        vals = []
        if self.stack_height_available_spot_stacks:
            vals = [list(i.values())[0] for i in self.stack_height_available_spot_stacks]
        return vals
        
    def purge_location(self,location):

        for i in range(len(self.stack_height_available_spot_stacks)):
            if location in self.stack_height_available_spot_stacks[i].keys():
                del self.stack_height_available_spot_stacks[i]
                break

        for y in range(len(self.top_spot_container_stacks)):
            if location in self.top_spot_container_stacks[y].keys():
                del self.top_spot_container_stacks[y]
                break
    
    def reset_moves(self):
        self.n_moves = 0

def deserialize(terminal_dict):

    new_terminal = Terminal([],terminal_dict["n_blocks"],terminal_dict["n_rows"],terminal_dict["n_stacks"],terminal_dict["stack_height"])
    new_terminal.n_containers = terminal_dict['n_containers']
    new_terminal.n_moves = terminal_dict['n_moves']
    new_terminal.container_reshuffles = terminal_dict['container_reshuffles']
    new_terminal.peak_block_utilization = terminal_dict['peak_block_utilization']
    new_terminal.block_utilizations = terminal_dict['block_utilizations']
    new_terminal.stack_height_available_spot_stacks = terminal_dict['stack_height_available_spot_stacks']
    new_terminal.top_spot_container_stacks = terminal_dict['top_spot_container_stacks']

    new_blocks = {}
    for block_number,block in terminal_dict["blocks"].items():
        new_blocks[block_number] = block_deserialize(block)
    new_terminal.blocks = new_blocks

    return new_terminal


