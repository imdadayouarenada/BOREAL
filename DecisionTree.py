import numpy as np
import scipy.io 
from graphviz import Digraph
import matplotlib.pyplot as plt

# DEVIATION SCORES - LOADING DATA 
parameters_data = scipy.io.loadmat('/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Database/12thApril2024params.mat')
dev_scores_data = scipy.io.loadmat('/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Database/12thApril2024DeviationScores2.mat')
file_name = '12th April 2024'

# DATA EXTRACTION
X = parameters_data['params']
Y = dev_scores_data ['deviationScores2']

# FUNCTION DEFINITIONS
def find_importance(s1,s2,Y):
    MSE_s1 = mse_calculation(s1,Y)
    MSE_s2 = mse_calculation(s2,Y)
    MSE_node = mse_calculation(s1+s2,Y)
    node_importance = ((len(s1)+len(s2))/len(Y))*MSE_node - (len(s1)/len(Y))*MSE_s1 - (len(s2)/len(Y))*MSE_s2
    return node_importance
    

def find_mean_value(subset, Y):
    target_values = [Y[i] for i in subset]
    if target_values:
        mean_value = sum(target_values)/len(target_values)
    else:
        mean_value = 0
    return mean_value 

def mse_calculation(subset, Y):
    mean_y = find_mean_value(subset,Y)
    mse = sum((Y[i] - mean_y) ** 2 for i in subset) / len(subset) if subset else 0
    return mse

def IG(s1, s2, Y):
    MSE_before = mse_calculation(s1+s2,Y)
    MSE_s1 = mse_calculation(s1,Y)
    MSE_s2 = mse_calculation(s2,Y)
    tot_samples = len(s1)+len(s2)
    MSE_after = (len(s1)/tot_samples)*MSE_s1 + (len(s2)/tot_samples)*MSE_s2
    Delta = MSE_before - MSE_after
    return Delta

def DecisionTree(X, Y):
    D = {}
    D_importances = {}
    n, m = X.shape
    samples = list(range(n))
    var_set = list(range(m))

    def split(var_set, samples, actual_depth):
        Information_Gain = 0
        var = None
        sub_set1, sub_set2 = [], []

        for v in var_set: # Iterate over all variables and try to split 
            sub1 = [i for i in samples if X[i, v] == 0] # subset which does not contain the feature. Subset 1 is the left child
            sub2 = [i for i in samples if X[i, v] != 0] # subset which contains the feature. Subset 2 is the right child

            current_gain = IG(sub1, sub2, Y) # calculate IG for the current split 
            # If the current split is better than the previous best split, update the best split 
            if current_gain > Information_Gain:
                Information_Gain = current_gain
                var = v
                sub_set1, sub_set2 = sub1, sub2
                node_importance = find_importance(sub1,sub2,Y)
    
        if var is not None: 
            node_importance = node_importance.item() if isinstance(node_importance, np.ndarray) and node_importance.size == 1 else node_importance # Convert node_importance to a scalar value
            Information_Gain = Information_Gain.item() if isinstance(Information_Gain, np.ndarray) and Information_Gain.size == 1 else Information_Gain # Convert IG to a scalar value
            D[tuple(samples)] = [var, sub_set1, sub_set2, Information_Gain, actual_depth] # Save the best split in the dictionary 
            # print(f'Splitting on variable {var} with IG = {Information_Gain} for samples {tuple(samples)} and depth {actual_depth}')

            if var in D_importances:
                D_importances[var] += node_importance/actual_depth # Update the importance of the feature if it already exists in the dictionary
            else:
                D_importances[var] = node_importance/actual_depth # Add the feature and its importance to the dictionary if it does not exist

            if len(sub_set2) > 1:
                split(var_set, sub_set2, actual_depth+1) # Recursively split the right child if contains more than one sample
            new_var_set = var_set[:]  # Create a copy of var_set before modifying it
            new_var_set.remove(var) # Remove the variable used for the current split 
            
            if len(sub_set1) > 1:
                split(new_var_set, sub_set1, actual_depth+1) # Recursively split the left child if contains more than one sample 

    split(var_set, samples, 1) # Start the recursive splitting process and ensure the tree is built 

    total_importance = sum(D_importances.values())
    for feature in D_importances:
        D_importances[feature] /= total_importance # Normalize the importance of each feature
    return D, D_importances

def print_leaf(samples, case_labels, space, depth, direction=''):
    if samples:  
        sample_cases = ", ".join(case_labels[idx] for idx in samples) 
        print(f"{space}{direction} Leaf node at depth {depth} containing cases: {sample_cases}")
    else:
        print(f"{space}{direction} Leaf node at depth {depth} with no cases.")

def print_tree(samples, D, case_labels, variable_names, depth=0):
    samples_tuple = tuple(samples)
    
    if samples_tuple in D:
        var, sub_set1, sub_set2, information_gain, depth = D[samples_tuple]
        if isinstance(information_gain, np.ndarray):
            if information_gain.size == 1:
                information_gain = information_gain.item()  
        var_name = variable_names.get(var, f"Unknown variable {var}")  # Get the variable name or use a default name
        
        space = "    " * depth  # Initial space for readability
        print(f"{space}Split on {var_name} at depth {depth} with IG {information_gain:.4f}")
        
        # Process left child
        if sub_set1 and len(sub_set1) > 1:
            print(f"{space}Left:")
            print(f"{space}    Cases: " + ", ".join(case_labels[i] for i in sub_set1))
            print_tree(sub_set1, D, case_labels, variable_names)
        else:
            print_leaf(sub_set1, case_labels, space, depth, 'Left') 
        
        # Process right child
        if sub_set2 and len(sub_set2) > 1:
            print(f"{space}Right:")
            print(f"{space}    Cases: " + ", ".join(case_labels[i] for i in sub_set2))
            print_tree(sub_set2, D, case_labels, variable_names)
        else:
            print_leaf(sub_set2, case_labels, space, depth, 'Right')
    else:
        depth = 0
        print_leaf(samples, case_labels, "    " * depth, depth)

def create_dot(D, case_labels, variable_names):
    dot = Digraph(comment='Decision Tree', format='png')

    def add_nodes_and_edges(samples, parent=None, edge_label=''):
        samples_tuple = tuple(samples)
        
        if samples_tuple in D:
            var, sub_set1, sub_set2, information_gain, depth = D[samples_tuple]
            if isinstance(information_gain, np.ndarray):
                if information_gain.size == 1:
                    information_gain = information_gain.item() 
            var_name = variable_names.get(var, f"Unknown variable {var}")
            
            node_label = f"{var_name}\nIG={information_gain:.4f}\nSamples={len(samples)}\nDepth={depth}"
            node_name = f"node{samples_tuple}"  # Unique node name based on samples
            dot.node(node_name, label=node_label, shape='box', style='rounded,filled', color='lightblue')

            if parent:
                dot.edge(parent, node_name, label=edge_label)
            
            if sub_set1 and len(sub_set1) > 1:
                add_nodes_and_edges(sub_set1, node_name, 'True')
            else:
                add_leaf_node(sub_set1, node_name, 'True')
            if sub_set2 and len(sub_set2) > 1:
                add_nodes_and_edges(sub_set2, node_name, 'False')
            else: 
                add_leaf_node(sub_set2, node_name, 'False')
        else:
            add_leaf_node(samples, parent, edge_label)
    
    def add_leaf_node(samples, parent, edge_label):
        if samples:
            leaf_label = f"Leaf: {', '.join(case_labels[i] for i in samples)}\nSamples={len(samples)}"
            leaf_name = f"leaf{tuple(samples)}"
            dot.node(leaf_name, label=leaf_label, shape='ellipse', style='filled', color='lightgray')
            if parent:
                dot.edge(parent, leaf_name, label=edge_label)

    # Initialize recursion from the root node
    root_samples = list(range(len(case_labels)))  
    add_nodes_and_edges(root_samples)

    return dot

# MAIN 
D, D_importances = DecisionTree(X,Y)
num_samples = 78  # total number of cases 
case_labels = {i: f"Case{str(i+1).zfill(2)}" for i in range(num_samples)}
variable_names = {
    0: "ext355",
    1: "ext532",
    2: "ext1064",
    3: "back355",
    4: "back532",
    5: "back1064",
    6: "pd355",
    7: "pd532",
    8: "pd1064"
}
samples = list(range(len(Y)))  

# Convert the feature indices to names
new_importances = {variable_names[key]: value for key, value in D_importances.items()}  
# Sort the importances in descending order
sorted_importances = dict(sorted(new_importances.items(), key=lambda item: item[1], reverse=True)) 

plt.figure(figsize=(10, 6))  
plt.bar(sorted_importances.keys(), sorted_importances.values()) 
plt.xlabel('Features')  
plt.ylabel('Importance')  
plt.title(f'Input Parameters Importances - {file_name}')  
plt.xticks(rotation=45, ha='right')  
plt.tight_layout()
plt.grid(True) 
plt.show() 

dot_graph = create_dot(D, case_labels, variable_names)
dot_graph.render(f'output_tree_{file_name}') # Save the decision tree as a PNG file
