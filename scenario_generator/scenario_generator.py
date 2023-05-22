from terminal.containerClass import Container
from terminal.terminalClass import Terminal
import terminal.terminalClass
from terminal.containerClass import serialize
import random
import datetime
import os

import json
from scipy.stats import randint
import numpy as np
import random
import matplotlib.pyplot as plt
import math

class ScenarioGenerator:

    def __init__(self,n_blocks,n_rows,n_stacks,stack_height,n_containers, time_scale,n_tests, target_percentages, initial_congestions):

        self.n_blocks = n_blocks
        self.n_rows = n_rows
        self.n_stacks = n_stacks
        self.stack_height = stack_height
        self.max_capacity= n_blocks*n_rows*n_stacks*stack_height
        self.n_containers = n_containers
        self.time_scale = time_scale
        self.n_tests = n_tests
        self.target_percentages = target_percentages
        self.initial_congestions = initial_congestions
        self.print_histograms = True


    def generate_scenarios_one_per_hour(self):

        #initialize dictionaries
        moves = {}
        terminals = {}
        for i in range(self.n_tests):
            moves[i] = {}
            terminals[i] = {}
            for congestion in self.initial_congestions:
                moves[i][congestion] = {}
                terminals[i][congestion] = {}
                for accuracy in self.target_percentages:
                    moves[i][congestion][accuracy] = {}
                    moves[i][congestion][accuracy]['max_synthetic_etd'] = 0
                    terminals[i][congestion][accuracy] = Terminal([],self.n_blocks,self.n_rows,self.n_stacks,self.stack_height)
                    for time_step in range(0,self.time_scale+1):
                        moves[i][congestion][accuracy][time_step] = {"enter":[],"exit":[]}

        for i in range(self.n_tests):
            for initial_congestion in self.initial_congestions:
                #empty congestion
                if initial_congestion == '0':
                    number_of_containers_to_fill = math.floor(self.max_capacity*(337/472))
                    time_scale = number_of_containers_to_fill+1

                    for container_number in range(0,number_of_containers_to_fill):
                        dwell_time = 0

                        while dwell_time < 1:
                            container_entry_time = container_number
                            container_exit_time = random.randint(container_entry_time,time_scale-1)
                            dwell_time = container_exit_time - container_entry_time

                        container_name = "ISO_"+str(container_number)

                        for accuracy in self.target_percentages:
                        
                            if accuracy == "110":
                                synthetic_etd = container_entry_time+dwell_time
                            else:
                                synthetic_etd = container_entry_time+random_choice_histogram_5_day_range(dwell_time,(int(accuracy)/100))

                            if synthetic_etd>moves[i][initial_congestion][accuracy]['max_synthetic_etd']:
                                moves[i][initial_congestion][accuracy]['max_synthetic_etd'] = synthetic_etd

                            container = Container(container_name, container_exit_time,synthetic_etd)
                            

                            moves[i][initial_congestion][accuracy][container_entry_time]["enter"].append(json.loads(serialize(container)))
                            moves[i][initial_congestion][accuracy][container_exit_time]["exit"].append(json.loads(serialize(container)))
                
                #more congestion
                else:
                    number_of_containers_to_add = math.floor((int(initial_congestion)/100)*self.max_capacity)
                    remaining_amount_of_containers = math.floor((100/472)*self.max_capacity)
                    time_scale = (remaining_amount_of_containers*5)+1
                    arrival_rate = 5

                    for container_number in range(0,number_of_containers_to_add):
                        dwell_time = 0

                        while dwell_time < 1:
                            container_entry_time = 0
                            container_exit_time = random.randint(container_entry_time,time_scale-1)
                            dwell_time = container_exit_time - container_entry_time

                        container_name = "ISO_"+str(container_number)
                        random_location = random.choice(terminals[i][initial_congestion][self.target_percentages[0]].get_available_stacks())

                        for accuracy in self.target_percentages:
                            if accuracy == "110":
                                synthetic_etd = dwell_time
                            else:
                                synthetic_etd = random_choice_histogram_5_day_range(dwell_time,(int(accuracy)/100))

                            if synthetic_etd>moves[i][initial_congestion][accuracy]['max_synthetic_etd']:
                                moves[i][initial_congestion][accuracy]['max_synthetic_etd'] = synthetic_etd
                                
                            container = Container(container_name, container_exit_time,synthetic_etd)
                            terminals[i][initial_congestion][accuracy].add_container(container,random_location)

                            moves[i][initial_congestion][accuracy][container_exit_time]["exit"].append(json.loads(serialize(container)))

                    for container_number in range(0,remaining_amount_of_containers):
                        dwell_time = 0

                        while dwell_time < 1:
                            container_entry_time = math.floor(container_number*arrival_rate)
                            container_exit_time = random.randint(container_entry_time,time_scale-1)
                            dwell_time = container_exit_time - container_entry_time

                        container_name = "ISO_"+str(number_of_containers_to_add+container_number)

                        for accuracy in self.target_percentages:
                            if accuracy == "110":
                                synthetic_etd = container_entry_time +dwell_time
                            else:
                                synthetic_etd = container_entry_time+random_choice_histogram_5_day_range(dwell_time,(int(accuracy)/100))
                                
                            if synthetic_etd>moves[i][initial_congestion][accuracy]['max_synthetic_etd']:
                                moves[i][initial_congestion][accuracy]['max_synthetic_etd'] = synthetic_etd

                            container = Container(container_name, container_exit_time,synthetic_etd)
                            
                            moves[i][initial_congestion][accuracy][container_entry_time]["enter"].append(json.loads(serialize(container)))
                            moves[i][initial_congestion][accuracy][container_exit_time]["exit"].append(json.loads(serialize(container)))

        self.serialize_scenarios(moves,terminals)


    def generate_scenario_waves(self):
        n_waves = 5
        wave_duration = 288
        n_containers_per_wave = 100
        wave_overlap = 4*24 #4 days overlap (+- of accuracy)
        wave_rate = wave_duration-wave_overlap
        total_timescale = wave_duration*(n_waves-1)+1

        self.initial_congestions = ['0']

        #initialize dictionaries
        moves = {}
        terminals = {}
        for i in range(self.n_tests):
            moves[i] = {}
            terminals[i] = {}
            for congestion in self.initial_congestions:
                moves[i][congestion] = {}
                terminals[i][congestion] = {}
                for accuracy in self.target_percentages:
                    moves[i][congestion][accuracy] = {}
                    moves[i][congestion][accuracy]['max_synthetic_etd'] = 0
                    terminals[i][congestion][accuracy] = Terminal([],self.n_blocks,self.n_rows,self.n_stacks,self.stack_height)
                    for time_step in range(0,total_timescale+1):
                        moves[i][congestion][accuracy][time_step] = {"enter":[],"exit":[]}
              
        for i in range(self.n_tests):
            for initial_congestion in self.initial_congestions:  
                for wave_number in range(n_waves):

                    for container_number in range(0,n_containers_per_wave):
                        dwell_time = 0

                        while dwell_time < 1:
                            container_entry_time = wave_number*wave_rate
                            container_exit_time = random.randint(container_entry_time,(container_entry_time+wave_duration)-1)
                            dwell_time = container_exit_time - container_entry_time

                        container_name = "ISO_"+str((wave_number*n_containers_per_wave)+container_number)

                        for accuracy in self.target_percentages:
                        
                            if accuracy == "110":
                                synthetic_etd = container_entry_time+dwell_time
                            else:
                                synthetic_etd = container_entry_time+random_choice_histogram_5_day_range(dwell_time,(int(accuracy)/100))

                            if synthetic_etd>moves[i][initial_congestion][accuracy]['max_synthetic_etd']:
                                moves[i][initial_congestion][accuracy]['max_synthetic_etd'] = synthetic_etd

                            container = Container(container_name, container_exit_time,synthetic_etd)
                            

                            moves[i][initial_congestion][accuracy][container_entry_time]["enter"].append(json.loads(serialize(container)))
                            moves[i][initial_congestion][accuracy][container_exit_time]["exit"].append(json.loads(serialize(container)))

        self.serialize_scenarios(moves,terminals)


    def serialize_scenarios(self,moves,terminals):
        #merge movesets with terminals
        cwd = os.getcwd()
        folder = os.path.join(cwd,'scenarios')
        for i in range(self.n_tests):
            for congestion in self.initial_congestions:
                for accuracy in self.target_percentages:
                    final_moveset = {}  
                    final_moveset['moves'] = moves[i][congestion][accuracy]
                    final_moveset['initial_terminal'] = terminals[i][congestion][accuracy].serialize_in_class()
                    test_name = f"{congestion}_congestion_{accuracy}_accuracy_{i}.json"
                    filename = os.path.join(folder,test_name)
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(final_moveset, f, ensure_ascii=False, indent=4)


def deserialize_scenario(path):
    file = open(path, 'r')
    string = file.read()
    raw_dictionary = json.loads(string)
    # moves = raw_dictionary["moves"]
    # terminal_dict = raw_dictionary["initial_terminal"]
    #need to convert every container to a 
    return raw_dictionary

def random_choice_histogram(dwell_time, target_percentage):
    n = 100000

    maximum = dwell_time+48
    minimum = dwell_time-48

    standard_deviation = (maximum-minimum)/4

    randomInts = np.random.normal(loc=dwell_time, scale=standard_deviation, size=n).astype(int)
    #replace all values <= 0 with 1
    randomInts[randomInts<=minimum] = minimum
    randomInts[randomInts<=0] = 1
    #replace ll values > max with max
    randomInts[randomInts>maximum] = maximum

    total_n = n/target_percentage
    remaining_n = total_n -n
    half_remaining_n = math.floor(remaining_n/2)

    lower_bound_value = minimum if minimum>=1 else 1
    lower_bound_fill = np.full(shape=half_remaining_n,fill_value=lower_bound_value).astype(int)
    # print(f"maximum value: {maximum}")
    upper_bound_fill = np.full(shape=half_remaining_n,fill_value=maximum).astype(int)

    total_array = np.concatenate((lower_bound_fill, randomInts, upper_bound_fill))

    return random.choice(total_array).item()

def even_distribution(min,max,n_items):
    n_bins = (max-min)+1
    items_per_bin = int(math.floor(n_items/n_bins))

    final_array = []
    for x in range(min,max+1):
        final_array+=[x]*items_per_bin
    
    return final_array


def random_choice_histogram_even(dwell_time, target_percentage):
    n = 100000

    maximum = dwell_time+48
    minimum = dwell_time-48
    # print(f"maximum: {maximum}, minimum: {minimum}")

    if minimum<1: minimum = 1

    even_distribution_middle = even_distribution(minimum, maximum,n)

    total_n = n/target_percentage
    remaining_n = total_n -n
    half_remaining_n = math.floor(remaining_n/2)
    # print(f"total_n: {total_n}, remaining_n: {remaining_n}, half_remaining_n {half_remaining_n}")

    #lower bound even fill
    min_value_lower_fill = minimum- 48
    if min_value_lower_fill <1: min_value_lower_fill=1

    max_value_lower_fill = minimum-1
    if max_value_lower_fill<1:max_value_lower_fill = 1
    # print(f"min_value_lower_fill: {min_value_lower_fill}, max_value_lower_fill: {max_value_lower_fill}")
    lower_fill = even_distribution(min_value_lower_fill,max_value_lower_fill,half_remaining_n)

    #upper bound even fill
    min_value_upper_fill = maximum

    max_value_upper_fill = maximum+48
    # print(f"min_value_upper_fill: {min_value_upper_fill}, max_value_upper_fill: {max_value_upper_fill}")
    upper_fill = even_distribution(min_value_upper_fill,max_value_upper_fill,half_remaining_n)


    total_array = even_distribution_middle+lower_fill+upper_fill


    return random.choice(total_array)

def random_choice_histogram_5_day_range(dwell_time, target_percentage):
    n = 10000

    interval_assumption_range = 120 # 5days 

    maximum = dwell_time+48
    minimum = dwell_time-48

    absolute_minimum = minimum - interval_assumption_range
    absolute_maximum = maximum + interval_assumption_range
    if absolute_minimum<1:
            absolute_minimum = 1

    if minimum<1: minimum = 1
    # print(f"maximum: {maximum}, minimum: {minimum}")
    even_distribution_middle = list(randint.rvs(minimum, maximum+1, size=n))

    total_n = n/target_percentage
    remaining_n = math.floor(total_n -n)

    #the remaining amount should be distributed on either side of the maximum/minimum range
    
    if minimum == 1:
        #all remaining values should be above maximum
        starting_int = maximum+1
        even_distribution_right = list(randint.rvs(starting_int, absolute_maximum+1, size=remaining_n))
        total_array = even_distribution_middle + even_distribution_right
        even_distribution_left = []
    else:

        #take the ratio of left bins to right bins to assing remaining_n

        n_bins_on_left = minimum-absolute_minimum
        n_bins_on_right = absolute_maximum-maximum

        ratio_bins_left_to_right = n_bins_on_left/n_bins_on_right

        n_samples_on_left = math.floor(ratio_bins_left_to_right*remaining_n)
        n_samples_on_right = remaining_n-n_samples_on_left

        even_distribution_left = list(randint.rvs(absolute_minimum, minimum, size=n_samples_on_left))
        even_distribution_right = list(randint.rvs(maximum+1, absolute_maximum+1, size=n_samples_on_right))


        total_array = even_distribution_left + even_distribution_middle +even_distribution_right

    return random.choice(total_array).item()

def random_choice_histogram100(dwell_time, target_percentage):
    return dwell_time