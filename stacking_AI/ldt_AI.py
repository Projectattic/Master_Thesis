import random
from terminal.terminalClass import Terminal
from terminal.containerClass import deserialize

class LDTAI:

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
            returned_container = self.terminal.remove_container(container.get_number(),False)
            if self.debug:
                print(f"LDTgAI returned_container: {returned_container}")
                print("LDTAI terminal layout")
                print(self.terminal.pretty_str())
        

        for container in moves_in:
            stack_etds = self.terminal.get_top_spot_container_stacks()

            synthetic_etd = container.get_synthetic_etd()

            #find the location with lowest ETD difference, if ETD difference>0, look for empty stack, if none exist, add to highest stack

            if stack_etds:
                min_ETD_difference_found = 100000
                min_ETD_difference_location = ""

                for spot_and_etd in stack_etds:

                    ETD_difference = synthetic_etd - list(spot_and_etd.values())[0]

                    if ETD_difference < min_ETD_difference_found:
                        min_ETD_difference_found = ETD_difference
                        min_ETD_difference_location = list(spot_and_etd.keys())[0]

                if min_ETD_difference_found>0:
                    if len(self.terminal.get_empty_stacks())>0:

                        random_spot = random.choice(self.terminal.get_empty_stacks())

                        self.terminal.add_container(container,random_spot)
                    else:
                        highest_stacks = self.terminal.get_highest_stacks()

                        random_spot = random.choice(highest_stacks)
  
                        self.terminal.add_container(container,random_spot)
                   
                else:

                    self.terminal.add_container(container,min_ETD_difference_location)

            elif len(self.terminal.get_empty_stacks())>0:
                random_spot = random.choice(self.terminal.get_empty_stacks())

                self.terminal.add_container(container,random_spot)
            
            else:
                highest_stacks = self.terminal.get_highest_stacks()

                random_spot = random.choice(highest_stacks)

                self.terminal.add_container(container,random_spot)
    
    def get_results(self):
        results = {}
        results['max_block_utilization'] = self.terminal.peak_block_utilization
        results['relocation_ratio'] = self.terminal.container_reshuffles/(self.terminal.n_moves +self.terminal.container_reshuffles)

        return results
