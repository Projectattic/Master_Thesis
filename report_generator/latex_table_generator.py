import os

class latexTableGenerator:

    def __init__(self,results_dict):
        self.results_dict = results_dict

    def generate_tables(self):
        cwd = os.getcwd()
        for congestion_ratio, ais in self.results_dict.items():
            for ai_name,accuracies in ais.items():
                generated_table_string = self.generate_accuracy_table(ai_name,accuracies)
                filename = f"latex_table_{ai_name}_{congestion_ratio}.tex"
                folder = 'results'
                folder_path = os.path.join(cwd,folder)
                file_path= os.path.join(folder_path,filename)
        
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(generated_table_string)       



    def generate_accuracy_table(self,ai_name,accuracy_dict):
        first_string = """\\begin{table}[H]
\centering
\\begin{tabular}{|c|c|c|c|c|} 
\hline
                  & \multicolumn{4}{c|}{\\textbf{"""+ai_name+"""}}                                             \\\\ 
\hline
\\textbf{Accuracy} & \\textbf{avg. reloc. r.} & \\textbf{stdev} & \\textbf{avg. max block u.} & \\textbf{stdev}  \\\\ 
\hline
"""
        str_build =""

        for accuracy, results in accuracy_dict.items():
             str_build += self.generate_accuracy_string(accuracy,results)
        
        last_string = """\end{tabular}
\end{table}"""
        return first_string+str_build+last_string

    def generate_accuracy_string(self,accuracy,results_dict):
        first_string = """\\textbf{"""+accuracy+"""}\%    &""" 
        second_string = f"""      {round(results_dict['average_relocation_ratio'],3)}             &     {round(results_dict['stdev_relocation_ratios'],3)}       &           {round(results_dict['average_max_block_utilization'],3)}        &     {round(results_dict['stdev_max_block_utilization'],3)}        \\\\ 
\hline
"""
        return first_string+second_string





    def generate_congestion_latex_table(self,results_dict,accuracy):
        AI_names = ['FuzzyLogicAI','LDTAI','LevellingAI','RandomAI']
        congestion_ratios = ['0','50','80']
        
        first_string = """\\begin{table}[H]
        \\begin{tabular}{|cl|l|l|l|l|}
        \hline
        """

        header_string = """\multicolumn{1}{|l}{\\textbf{Accuracy}}               & \\textbf{"""+accuracy+"""}\\%                              & \\textbf{RAND} & \\textbf{Levelling} & \\textbf{LDT} & \\textbf{Fuzzy} \\\\ \hline
        \multicolumn{1}{|l|}{\\textbf{Congestion}}      & \\textbf{}                              &               &                    &              &                \\\\ \hline
        """

        str_build = ""

        for congestion_ratio in congestion_ratios:
            str_build += self.generate_congestion_subtable(congestion_ratio, results_dict)
        
        

        final_string = """\end{tabular}
        \end{table}
        
        """

        return first_string+header_string+str_build+final_string

    def generate_congestion_subtable(self,congestion_ratio, results_dict):
        results_types = ["average_relocation_ratio","stdev_relocation_ratios","average_max_block_utilization","stdev_max_block_utilization"]
        
        first_string = """\multicolumn{1}{|c|}{\multirow{4}{*}{\\textbf{"""+congestion_ratio+"""\%}}}  & \\textbf{Relocation Ratio}              &"""
        
        str_build = ""

        for results_type in results_types:

            if results_type == "average_relocation_ratio":
                first_line = ""
            if results_type == "stdev_relocation_ratios":
                first_line = """\multicolumn{1}{|c|}{}                               & \\textbf{Relocation Ratio (Stdev)}      &"""
            if results_type == "average_max_block_utilization":
                first_line = """\multicolumn{1}{|c|}{}                               & \\textbf{Max block utilization}         &"""
            if results_type == "stdev_max_block_utilization":
                first_line = """\multicolumn{1}{|c|}{}                               & \\textbf{Max block utilization (Stdev)} &"""

            str_build += first_line+ self.generate_congestion_results_subtable(results_type,congestion_ratio,results_dict)
        
        return first_string+str_build

    def generate_congestion_results_subtable(self,results_type, congestion_ratio, results_dict):

        string = f"""     {round(results_dict[congestion_ratio]['RandomAI'][results_type],3)}         &        {round(results_dict[congestion_ratio]['LevellingAI'][results_type],3)}           &    {round(results_dict[congestion_ratio]['LDTAI'][results_type],3)}         &        {round(results_dict[congestion_ratio]['FuzzyLogicAI'][results_type],3)}       """

        if results_type == "stdev_max_block_utilization":
            final_string = """\\\\ \hline
    """
        else:
            final_string = """\\\\ \cline{2-6}
    """

        return string+final_string