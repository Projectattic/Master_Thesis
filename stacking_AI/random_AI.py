import random
from terminal.terminalClass import Terminal
from terminal.containerClass import deserialize

class RandomAI:

    def __init__(self,terminal: Terminal,moves):
        self.terminal = terminal.copy()
        self.moves = moves

        self.debug = False

    def move(self,step):

        moves_in = self.moves[str(step)]["enter"]
        moves_out = self.moves[str(step)]["exit"]

        moves_in = list(map(deserialize,moves_in))
        moves_out = list(map(deserialize,moves_out))
        if self.debug:
            print(moves_in)
            print(moves_out)

        for container in moves_out:
            if self.debug:
                print("moving out")
                print(container)
            returned_container = self.terminal.remove_container(container.get_number(),False)

    
        for container in moves_in:

            available_stcks = self.terminal.get_available_stacks()

            random_spot = random.choice(available_stcks)
            if self.debug:
                print(f"moving in continer: {container}")
                print(f"available_stacks: {available_stcks}")
                print(f"chosen spot: {random_spot}")
            self.terminal.add_container(container,random_spot)

    def get_results(self):
        results = {}
        results['max_block_utilization'] = self.terminal.peak_block_utilization
        results['relocation_ratio'] = self.terminal.container_reshuffles/(self.terminal.n_moves +self.terminal.container_reshuffles)

        return results
