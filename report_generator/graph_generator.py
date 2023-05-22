import os
import matplotlib.pyplot as plt

class graphGenerator:

    def __init__(self,results_dict,accuracies):
        self.results_dict = results_dict
        self.accuracies = accuracies

    def generate_graphs(self):
        cwd = os.getcwd()
        for congestion_ratio, ai_results in self.results_dict.items():
                self.generate_accuracy_graph_all(congestion_ratio,ai_results)
                self.generate_error_graphs(congestion_ratio,ai_results)
    

    def generate_accuracy_graph_all(self,congestion_ratio,ai_results):
        fig, ax = plt.subplots()
        ax.set_ylabel("Average relocation ratio")
        ax.set_xlabel("Dwell time accuracy (%)")
        ax.set_title(f"""{congestion_ratio}% Initial congestion, all AIs""")


        axis_values = self.accuracies

        ai_names = list(ai_results.keys())

        for ai_name in ai_names:

            if ai_name == 'RandomAI':
                average_relocation_ratios4 = list(ai_results[ai_name]["average_relocation_ratios"])
                stdev_relocation_ratios4 = list(ai_results[ai_name]["stdev_relocation_ratios"])
                ax.plot(axis_values,average_relocation_ratios4,label ='Rand',color='#009e73',marker = "H")
                # ax.errorbar(x =axis_values, y= average_relocation_ratios4,yerr=stdev_relocation_ratios4 ,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3, label = 'Rand',color='#009e73')
            if ai_name == 'LevellingAI':
                average_relocation_ratios3 = ai_results[ai_name]["average_relocation_ratios"]
                stdev_relocation_ratios3 = ai_results[ai_name]["stdev_relocation_ratios"]
                ax.plot(axis_values,average_relocation_ratios3,label ='Levelling',color='#e69f00',marker = "H")
                # ax.errorbar(x =axis_values, y= average_relocation_ratios3,yerr=stdev_relocation_ratios3 ,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3,label ='Levelling',color='#e69f00')
            if ai_name == 'LDTAI':
                average_relocation_ratios2 = ai_results[ai_name]["average_relocation_ratios"]
                stdev_relocation_ratios2 = ai_results[ai_name]["stdev_relocation_ratios"]
                ax.plot(axis_values,average_relocation_ratios2,label='LDT',color='#0072b2',marker = "H")
                # ax.errorbar(x =axis_values, y= average_relocation_ratios2,yerr=stdev_relocation_ratios2 ,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3,label='LDT',color='#0072b2')
            if ai_name == 'FuzzyLogicAI':
                average_relocation_ratios = ai_results[ai_name]["average_relocation_ratios"]
                stdev_relocation_ratios = ai_results[ai_name]["stdev_relocation_ratios"]
                ax.plot(axis_values,average_relocation_ratios,label='Fuzzy',color='#000000',marker = "H")
                # ax.errorbar(x= axis_values, y = average_relocation_ratios,yerr = stdev_relocation_ratios,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3,label='Fuzzy',color='#000000')
        
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), labelspacing=2)
        cwd = os.getcwd()
        folder_path = os.path.join(cwd,'results')
        filename = f"graph_{congestion_ratio}_all.png"
        save_location = os.path.join(folder_path,filename)
        fig.savefig(save_location,bbox_inches="tight")


    def generate_error_graphs(self,congestion_ratio,ai_results):

        ai_names = list(ai_results.keys())
        axis_values = self.accuracies
        for ai_name in ai_names:
            fig, ax = plt.subplots()
            ax.set_ylabel("Average relocation ratio")
            ax.set_xlabel("Dwell time accuracy (%)")
            ax.set_title(f"""{congestion_ratio}% Initial congestion, {ai_name}""")
            if ai_name == 'RandomAI':
                average_relocation_ratios4 = list(ai_results[ai_name]["average_relocation_ratios"])
                stdev_relocation_ratios4 = list(ai_results[ai_name]["stdev_relocation_ratios"])
                # ax.plot(x=axis_values,y = average_relocation_ratios4, label = 'Rand',color='#009e73')
                ax.errorbar(x =axis_values, y= average_relocation_ratios4,yerr=stdev_relocation_ratios4 ,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3, label = 'Rand',color='#009e73')
            if ai_name == 'LevellingAI':
                average_relocation_ratios3 = ai_results[ai_name]["average_relocation_ratios"]
                stdev_relocation_ratios3 = ai_results[ai_name]["stdev_relocation_ratios"]
                # ax.plot(x=axis_values,y = average_relocation_ratios3,label ='Levelling',color='#e69f00')
                ax.errorbar(x =axis_values, y= average_relocation_ratios3,yerr=stdev_relocation_ratios3 ,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3,label ='Levelling',color='#e69f00')
            if ai_name == 'LDTAI':
                average_relocation_ratios2 = ai_results[ai_name]["average_relocation_ratios"]
                stdev_relocation_ratios2 = ai_results[ai_name]["stdev_relocation_ratios"]
                # ax.plot(x=axis_values,y = average_relocation_ratios3,label='LDT',color='#0072b2')
                ax.errorbar(x =axis_values, y= average_relocation_ratios2,yerr=stdev_relocation_ratios2 ,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3,label='LDT',color='#0072b2')
            if ai_name == 'FuzzyLogicAI':
                average_relocation_ratios = ai_results[ai_name]["average_relocation_ratios"]
                stdev_relocation_ratios = ai_results[ai_name]["stdev_relocation_ratios"]
                # ax.plot(x=axis_values,y = average_relocation_ratios3,label='Fuzzy',color='#000000')
                ax.errorbar(x= axis_values, y = average_relocation_ratios,yerr = stdev_relocation_ratios,marker = "H",markeredgecolor = 'red',ecolor = 'red',capsize = 3,label='Fuzzy',color='#000000')
        
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), labelspacing=2)
            cwd = os.getcwd()
            folder_path = os.path.join(cwd,'results')
            filename = f"graph_{congestion_ratio}_{ai_name}.png"
            save_location = os.path.join(folder_path,filename)
            fig.savefig(save_location,bbox_inches="tight")


            # graph_results[congestion_ratio][ai_name]['average_relocation_ratios'].append(average_relocation_ratio)
            # graph_results[congestion_ratio][ai_name]['stdev_relocation_ratios'].append(stdev_relocation_ratios)
            # graph_results[congestion_ratio][ai_name]['average_max_block_utilizations'].append(average_max_block_utilization)
            # graph_results[congestion_ratio][ai_name]['stdev_max_block_utilizations'].append(stdev_max_block_utilizations)