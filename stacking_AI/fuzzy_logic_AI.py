import random
from terminal.terminalClass import Terminal
from terminal.containerClass import deserialize
from fuzzy_logic.fuzzy_variable_input import FuzzyInputVariable
from fuzzy_logic.fuzzy_variable_output import FuzzyOutputVariable
from fuzzy_logic.fuzzy_system import FuzzySystem
import math

class FuzzyLogicAI:

    def __init__(self,terminal: Terminal,moves):
        self.terminal = terminal.copy()
        self.moves = moves
        self.max_synthetic_etd = moves['max_synthetic_etd']
        self.debug = False

    def move(self,step):
        moves_in = self.moves[str(step)]["enter"]
        moves_out = self.moves[str(step)]["exit"]

        moves_in = list(map(deserialize,moves_in))
        moves_out = list(map(deserialize,moves_out))

        for container in moves_out:
            names_moves_out = [cont.container_number for cont in moves_out]
            if self.debug:
                print(f"names moves out: {names_moves_out}")

            returned_container, reshuffle_containers = self.terminal.remove_container(container.get_number(),True)

            if len(reshuffle_containers)>0:
                if self.debug:
                    print(f"reshuffling {len(reshuffle_containers)} containers")

            for container_reshuffled in reshuffle_containers:

                if container_reshuffled.container_number not in names_moves_out:
                    if self.debug:
                        print("container was not in moves out, apparently")
                    self.add_container(container)
                else:
                    self.terminal.container_reshuffles -=2 #container was due to be taken out anyway, remove the reshuffles that have already been counted
        

        for container in moves_in:
            self.add_container(container)

    
    def add_container(self, container):
        if self.debug:
            print(f"adding_container: {str(container)}")
        best_block = self.get_best_block()
        empty_stacks_in_block = self.get_empty_stacks_in_block(best_block)

        if empty_stacks_in_block:
            best_position = random.choice(empty_stacks_in_block)
            if self.debug:
                print(f"there were empty spots in block so chose: {best_position}")
            
        else:
            if self.debug:
                print(f"best block found: {best_block}")
            positions_in_block = self.get_positions_in_block(best_block)
            if self.debug:
                print(f"positions in block: {positions_in_block}")
            best_position = self.get_best_position(container.get_synthetic_etd(), positions_in_block)
            if self.debug:
                print(f"best position found in block: {best_position}")

            if best_position == "":
                highest_stacks = self.terminal.get_highest_stacks()

                best_position = random.choice(highest_stacks)

        if self.debug:
            print(f"chosen_spot: {best_position}")

        self.terminal.add_container(container,best_position)


    def get_best_block(self):

        highest_VoG_found = 0
        highest_VoG_block = ""

        for block_name, block_utilization in self.terminal.get_block_utilizations().items():

            block_VoG = self.get_block_VoG(block_utilization)
            if self.debug:
                print(f"block {block_name} VoG found: {block_VoG}")
            if block_VoG>highest_VoG_found:
                highest_VoG_block = block_name
                highest_VoG_found = block_VoG
                if self.debug:
                    print(f"block VoG highest found")
        
        return highest_VoG_block
    
    def get_positions_in_block(self, block_name):
        if self.debug:
            print("getting positions in block")
        positions_in_block = []

        for item in self.terminal.get_top_spot_container_stacks():
            if self.debug:
                print(f"looking at top container stack item: {item}")
            for stack_name,etd in item.items():
                if self.debug:
                    print(f"stack name: {stack_name}")
                if stack_name[0] == block_name:
                    if self.debug:
                        print("stack name matches block name")
                    positions_in_block.append({stack_name: etd})
        if self.debug:
            print(f"returning positions in block: {positions_in_block}")
        return positions_in_block
    
    def get_best_position(self,etd_check,position_list):
        if self.debug:
            print("looking for best position in block")
        highest_VoG_found = 0
        highest_VoG_stack = ""
        for item in position_list:
            if self.debug:
                print(f"looking at item: {item}")
            for stack_name, etd in item.items():
                if self.debug:
                    print(f"stack_name: {stack_name} | etd: {etd}")
                stack_height = self.get_stack_height(stack_name)
                if self.debug:
                    print(f"stack height: {stack_height}")
                normalized_ETD = self.get_normalized_ETD(etd_check,etd)
                if self.debug:
                    print(f"normalized ETD: {normalized_ETD}")
                stack_VoG = self.get_stack_VoG(stack_height,normalized_ETD)
                if self.debug:
                    print(f"stack_VoG: {stack_VoG}")
                if stack_VoG>highest_VoG_found:
                    if self.debug:
                        print("highest_stack VoG found so far")
                    highest_VoG_stack = stack_name
                    highest_VoG_found = stack_VoG
        
        return highest_VoG_stack

    def get_stack_height(self, stack_name):
        stack_height_dicts = self.terminal.stack_height_available_spot_stacks
        stack_height_found = ""

        if self.debug:
            print(f"finding stack heights, stack_height dicts: {stack_height_dicts}")
            print(f"looking for {stack_name}")
            print(f"checking {stack_name[0]}")

        for stack in stack_height_dicts:
            if self.debug:
                print(f"looking at stack: {stack}")
                print(f"stack_block = {list(stack.keys())[0]}")
            if list(stack.keys())[0] == stack_name:
                stack_height_found = list(stack.values())[0]
                if self.debug:
                    print(f"stack block matches stack name block \n new_height found: {list(stack.values())[0]}")
                break
        return stack_height_found
    
    def get_empty_stacks_in_block(self,block_name):
        if self.debug:
            print(f"looking for empty stacks in block: {block_name}")
        empty_stacks_in_terminal = self.terminal.get_empty_stacks()
        empty_stacks_in_block = [i for i in empty_stacks_in_terminal if i[0]==block_name]
        if self.debug:
            print(f"empty stacks in terminal: {empty_stacks_in_terminal}|\n empty stacks in block: {empty_stacks_in_block}")
        return empty_stacks_in_block

    def get_normalized_ETD(self, etd_incoming,etd_stack):
        # normalized_ETD = abs((etd1-etd2)/self.max_synthetic_etd)
        etd_difference = etd_incoming -etd_stack
        
        # print(normalized_ETD)
        return self.linear_etd_function(etd_difference)
    
    def linear_etd_function(self,etd_difference):
        #y = mx+b
        #b always 0.5 (difference of zero = 0.5)
        # 0 at - (max synthetic etd)
        # 1 at max synthetic_etd
        # slope is therefore 0.5/max_synthetic etd

        return ((0.5/self.max_synthetic_etd)*etd_difference)+0.5
    

    def get_stack_VoG(self,stack_h,normalized_ETD):
        stack_height = FuzzyInputVariable('stack_height', 0, 6, 100)
        stack_height.add_triangular('Low', 0, 0, 2)
        stack_height.add_triangular('Medium', 0, 3, 4)
        stack_height.add_triangular('High', 3, 6, 6)

        etd = FuzzyInputVariable('ETD', 0, 1, 100)
        etd.add_triangular('Earlier', 0, 0, 0.6)
        etd.add_triangular('Later', 0.4, 1, 1)

        stack_VoG = FuzzyOutputVariable('stack_VoG', 0, 1, 100)
        stack_VoG.add_triangular('Small', 0, 0, 0.4)
        stack_VoG.add_triangular('Medium', 0.1, 0.5, 0.9)
        stack_VoG.add_triangular('High', 0.6, 1, 1)

        system = FuzzySystem()
        system.add_input_variable(stack_height)
        system.add_input_variable(etd)
        system.add_output_variable(stack_VoG)

        system.add_rule(
                { 'stack_height':'Low',
                    'ETD':'Later' },
                { 'stack_VoG':'Small'})

        system.add_rule(
                { 'stack_height':'Medium',
                    'ETD':'Later' },
                { 'stack_VoG':'Small'})

        system.add_rule(
                { 'stack_height':'Medium',
                    'ETD':'Earlier' },
                { 'stack_VoG':'High'})

        system.add_rule(
                { 'stack_height':'High',
                    'ETD':'Earlier' },
                { 'stack_VoG':'Medium'})


        output = system.evaluate_output({
                        'stack_height':stack_h,
                        'ETD':normalized_ETD
                })
        
        if math.isnan(output['stack_VoG']):
            return 0
        else:
            return output['stack_VoG']

    
    def get_block_VoG(self,block_u):
        
        block_utilization = FuzzyInputVariable('block_utilization', 0, 1, 100)
        block_utilization.add_triangular('Low', 0, 0, 0.4)
        block_utilization.add_triangular('Medium', 0.1, 0.5, 0.9)
        block_utilization.add_triangular('High', 0.6, 1, 1)

        block_VoG = FuzzyOutputVariable('block_VoG', 0, 1, 100)
        block_VoG.add_triangular('Low', 0, 0, 0.4)
        block_VoG.add_triangular('Medium', 0, 0.5, 1)
        block_VoG.add_triangular('High', 0.6, 1, 1)

        system = FuzzySystem()
        system.add_input_variable(block_utilization)
        system.add_output_variable(block_VoG)

        system.add_rule(
                { 'block_utilization':'Low'},
                { 'block_VoG':'High'})

        system.add_rule(
                { 'block_utilization':'Medium'},
                { 'block_VoG':'Medium'})

        system.add_rule(
                { 'block_utilization':'High'},
                { 'block_VoG':'Low'})

        output = system.evaluate_output({
                        'block_utilization': block_u
                })

        return output['block_VoG']
    
    def get_results(self):
        results = {}
        results['max_block_utilization'] = self.terminal.peak_block_utilization
        results['relocation_ratio'] = self.terminal.container_reshuffles/(self.terminal.n_moves +self.terminal.container_reshuffles)

        return results