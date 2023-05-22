from stacking_AI.fuzzy_logic_AI import FuzzyLogicAI
from stacking_AI.ldt_AI import LDTAI
from stacking_AI.levelling_AI import LevellingAI
from stacking_AI.random_AI import RandomAI
from scenario_generator.scenario_generator import ScenarioGenerator
from scenario_generator.scenario_generator import deserialize_scenario
from terminal.terminalClass import Terminal, deserialize
from report_generator.latex_table_generator import latexTableGenerator
from report_generator.graph_generator import graphGenerator

import os
import statistics
import json

##################
### EDIT THESE ###
##################
# accuracies = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100','110']
# initial_congestions = ['0','50','80']
# ai_names = ['RandomAI','LevellingAI','LDTAI','FuzzyLogicAI']
# accuracies_test = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
accuracies_test = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100','110']
initial_congestions = ['0']
ai_names = ['RandomAI','LevellingAI','LDTAI','FuzzyLogicAI']
n_tests = 10

n_blocks_in_terminal = 5
n_rows_in_terminal = 5
n_stacks_in_terminal = 5
stack_height_in_terminal = 6
n_containers_to_add = 750
time_scale = 791
generate_tests = True
run_tests = True
###################


##########################
### Generate Scenarios ###
##########################

#comment out if already have scenarios in /scenarios folder
#########################
if generate_tests:
    print("Generating scenarios")
    sg = ScenarioGenerator(n_blocks_in_terminal,n_rows_in_terminal,n_stacks_in_terminal,stack_height_in_terminal,n_containers_to_add, time_scale,n_tests, accuracies_test, initial_congestions)
    # sg.generate_scenarios_one_per_hour()
    sg.generate_scenario_waves()
#########################

if run_tests:
    ### getting scenarios ###
    print("Running Tests")
    directories = {}
    cwd = os.getcwd()
    folder = os.path.join(cwd,'scenarios')
    for congestion_ratio in initial_congestions:
        directories[congestion_ratio] = {}
        for acc in accuracies_test:
            directories[congestion_ratio][acc] = {}
            for x in range(n_tests):
                file_name = f"{congestion_ratio}_congestion_{acc}_accuracy_{x}.json"
                directories[congestion_ratio][acc][str(x)] = os.path.join(folder,file_name)
    ##########################


    ### Preparing Results dictionary ###
    results = {}
    for congestion_ratio in initial_congestions:
        results[congestion_ratio] = {}
        for ai_name in ai_names:
            results[congestion_ratio][ai_name] = {}
            for acc in accuracies_test:
                results[congestion_ratio][ai_name][acc] = []

    #####################################


    ###############
    ### Run AIs ###
    ###############

    for congestion_ratio, accuracies in directories.items():
        print(f"running congestion ratio: {congestion_ratio}")
        for accuracy, sims in accuracies.items(): 
            print(f"running accuracy: {accuracy}")
            for sim_n, directory in sims.items():
                print(f"running sim_n: {sim_n}")

                moves_raw = deserialize_scenario(directory)
                moves = moves_raw['moves']
                serialized_terminal = moves_raw['initial_terminal']

                for ai_name in ai_names:
                    print(f"running {ai_name}")
                    terminal = deserialize(serialized_terminal).copy()
                    terminal.reset_moves()
                    
                    if ai_name == 'RandomAI':
                        ai = RandomAI(terminal,moves)
                    if ai_name == 'LevellingAI':
                        ai = LevellingAI(terminal,moves)
                    if ai_name == 'LDTAI':
                        ai = LDTAI(terminal,moves)
                    if ai_name == 'FuzzyLogicAI':
                        ai = FuzzyLogicAI(terminal,moves)

                    n_moves = len(moves.keys())-1

                    # try:
                    for step in range(0,n_moves):
                        ai.move(step)

                    results[congestion_ratio][ai_name][accuracy].append(ai.get_results())
                    # print(results[congestion_ratio][ai_name][acc])

    ##########################
    ### Generating Results ###
    ##########################


    ### Rearranging Results dictionary and dumping results ###
    print(f"rearranging and dumping results")

    graph_results = {}
    for congestion_ratio in initial_congestions:
        graph_results[congestion_ratio] = {}
        for ai_name in ai_names:
            graph_results[congestion_ratio][ai_name] = {}
            graph_results[congestion_ratio][ai_name]['average_relocation_ratios'] = []
            graph_results[congestion_ratio][ai_name]['stdev_relocation_ratios'] = []
            graph_results[congestion_ratio][ai_name]['average_max_block_utilizations'] = []
            graph_results[congestion_ratio][ai_name]['stdev_max_block_utilizations'] = []

            for acc in accuracies_test:
                results_dict = results[congestion_ratio][ai_name][acc]

                relocation_ratios = []
                max_block_utilizations = []
                print(f"results dict: {results_dict}")
                for result in results_dict:
                    relocation_ratios.append(result['relocation_ratio'])
                    max_block_utilizations.append(result['max_block_utilization'])

                average_relocation_ratio = sum(relocation_ratios)/len(relocation_ratios)

                if len(relocation_ratios)>1:
                    stdev_relocation_ratios = statistics.stdev(relocation_ratios)
                else: 
                    stdev_relocation_ratios = 0

                average_max_block_utilization = sum(max_block_utilizations)/len(max_block_utilizations)

                if len(max_block_utilizations)>1:
                    stdev_max_block_utilizations = statistics.stdev(max_block_utilizations)
                else:
                    stdev_max_block_utilizations = 0
                
                results[congestion_ratio][ai_name][acc] = {}

                results[congestion_ratio][ai_name][acc]["average_relocation_ratio"] = average_relocation_ratio
                results[congestion_ratio][ai_name][acc]["stdev_relocation_ratios"] = stdev_relocation_ratios
                results[congestion_ratio][ai_name][acc]["average_max_block_utilization"] = average_max_block_utilization
                results[congestion_ratio][ai_name][acc]["stdev_max_block_utilization"] = stdev_max_block_utilizations
                
                graph_results[congestion_ratio][ai_name]['average_relocation_ratios'].append(average_relocation_ratio)
                graph_results[congestion_ratio][ai_name]['stdev_relocation_ratios'].append(stdev_relocation_ratios)
                graph_results[congestion_ratio][ai_name]['average_max_block_utilizations'].append(average_max_block_utilization)
                graph_results[congestion_ratio][ai_name]['stdev_max_block_utilizations'].append(stdev_max_block_utilizations)

                #dump_results
                folder = os.path.join(cwd,'results')
                filename = os.path.join(folder,f"results_raw_{congestion_ratio}_{ai_name}.json")

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(results[congestion_ratio][ai_name], f, ensure_ascii=False, indent=4)



    print(f"generating latex tables")
    ltg = latexTableGenerator(results)

    ltg.generate_tables()

    print(f"generating graphs")
    gg = graphGenerator(graph_results,accuracies_test)

    gg.generate_graphs()

    print(f"")