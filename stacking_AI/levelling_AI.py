import random
from terminal.terminalClass import Terminal
from terminal.containerClass import deserialize

class LevellingAI:

    def __init__(self,terminal: Terminal,moves):
        self.terminal = terminal.copy()
        self.moves = moves

    def move(self,step):

        moves_in = self.moves[str(step)]["enter"]
        moves_out = self.moves[str(step)]["exit"]

        moves_in = list(map(deserialize,moves_in))
        moves_out = list(map(deserialize,moves_out))
     

        for container in moves_out:
            returned_container = self.terminal.remove_container(container.get_number(),False)

        

        for container in moves_in:
            lowest_stacks = self.terminal.get_lowest_stacks()
            chosen_spot = random.choice(lowest_stacks)
            self.terminal.add_container(container,chosen_spot)


    def get_results(self):
        results = {}
        results['max_block_utilization'] = self.terminal.peak_block_utilization
        results['relocation_ratio'] = self.terminal.container_reshuffles/(self.terminal.n_moves +self.terminal.container_reshuffles)

        return results