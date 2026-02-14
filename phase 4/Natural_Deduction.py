import sys

# define logical symbols used in formula
NOT = '¬'
AND = '∧'
OR = '∨'
IMP = '→'
FALSE = '⊥' 

# operator precedence
OPERATOR_PRECEDENCE = {
    IMP : 1, OR : 2 ,AND : 3, NOT : 4 
}

# remove the outer parenteses 
def remove_outer_parentheses(formula , begin , end):
    if formula[begin] == '(' and formula[end] == ')' :
        count = 0
        for i in range (begin , end +1):
            if formula[i] == '(':
                count += 1
            elif formula[i] == ')':
                count-=1
            if count == 0 and i<end:
                return False
        return True 
    return False

#define the class for the nodes
class Node :
    def __init__(self , key, left=None, right=None) :
        self.data = key
        self.left : Node | None = left
        self.right : Node | None = right

# read the input file and extracts the fomula and rules 
def read_input_file():
    print("please enter a file name :")
    file_name = input()

    with open (file_name , 'r', encoding = 'utf-8')as file:
        lines = [line.strip() for line in file if line.strip()]

    formula_line = []
    rule_line = None

    for line in lines :
        # formula
        if line and line[0].isdigit():
            formula_line.append(line)
        # rules
        else:
            rule_line = line
    
    formulas = parse_formulas_from_lines(formula_line)
    ruel = read_rule(rule_line) if rule_line else None

    return formulas , ruel

# parse lines containing a line number and a logical formula 
#builds aa binary tree for each formula and stores it in a dictionalry by line number
# ignores invalid lines
def parse_formulas_from_lines (lines):
    line_formula = {}
    for line in lines:
        if '    ' not in line :
            continue 

        line_number_str , formula_str = line.split('    ' , maxsplit=1)
        # Remove all spaces from the formula string before parsing
        formula_str = formula_str.replace(" ", "") 
        
        line_number = int ( line_number_str)
        formula_tree = binary_tree(formula_str , 0 , len(formula_str)-1)
        if formula_tree is None:
            continue
        line_formula[line_number] = formula_tree
    return line_formula

# extract rule name and line numbers from a rule line 
def read_rule(line):
    if not line:
        return None
    parts = line.split(',')
    rule_name = parts[0].strip()
    rule_lines = [int(p.strip()) for p in parts[1:]]
    return rule_name , rule_lines


# recursively builds a binary parse tree from a propositional logic fromula 

# steps :
# 1 ) lase case : if it's a single variable , retrun a leaf node 
# 2 ) if fully parenthesezed , remove the outer parentheses and process inner part 
# 3 ) ptaverse the formula to find the main logical operator whti the lowest precedence 
# (outside of any parentheses) , respecting porerator precedence rules 
# 4 ) recursively build left and right subtrees based on the main operator's position 
# 5 ) handle negation as a unary operator applied to the right subtree only  

def binary_tree(formula , begin , end) :
    if begin > end :
        return None 
    
    if begin == end and (formula[begin].isalpha() and formula[begin].islower() or formula[begin] == FALSE) :
        node = Node(formula[begin])
        return node
    
    if remove_outer_parentheses(formula , begin , end ):
        return binary_tree(formula, begin +1 , end-1)
    
    main_operator = -1
    min_value = 5 
    parantesses_check = 0

    for i in range (begin , end + 1):
        if formula[i] == '(':
            parantesses_check += 1
        elif formula[i] ==')':
            parantesses_check -= 1
        elif parantesses_check == 0 :
            if formula[i] in [IMP , OR , AND]:
                flag = OPERATOR_PRECEDENCE[formula[i]]
                if flag < min_value:
                    min_value = flag 
                    main_operator = i
                elif flag == min_value:
                    if formula[i] in [AND , OR]:
                        main_operator = i
    
    if main_operator != -1 :
        char_main_operator = formula[main_operator]
        node = Node(char_main_operator)

        node.left = binary_tree(formula , begin , main_operator-1)
        node.right = binary_tree(formula , main_operator+1 , end)

        return node 
    
    if formula[begin] == NOT:
        node = Node (NOT)
        node.right = binary_tree(formula , begin+1 , end)
        return node
    
    return None
    
################### RULES ##################### 

# each function implements a specific natrual deduction rule 
# it take line numbers and a dictionary of parsed formulas as input 
# the function checks if the rule can be applied based on the structure of the formulas
# if valid , it returns a new fomula node 
# if not , it print "rule can not be applied " and returns None 
def AND_introduction (line1 , line2 , formulas):
    formula1 = formulas.get(line1)
    formula2 = formulas.get(line2)

    if formula1 is None or formula2 is None:
        print("Rule Cannot Be Applied")
        return None
    return Node(AND , formula1 , formula2)


def AND_elimination_1 (line , formulas):
    formula1 = formulas.get(line)

    if formula1 is None:
        print("Rule Cannot Be Applied")
        return None
    
    if formula1.data == AND and formula1.left and formula1.right :
        return formula1.left
    else:
        print("Rule Cannot Be Applied")
        return None
    

def AND_elimination_2(line , formulas):
    formula1 = formulas.get(line)

    if formula1 is None :
        print("Rule Cannot Be Applied")
        return None
    
    if formula1.data == AND and formula1.left and formula1.right:
        return formula1.right
    else :
        print("Rule Cannot Be Applied")
        return None
    

def IMP_elimination(line_imp , line_pre , formulas):
    implication = formulas.get(line_imp)
    permise = formulas.get(line_pre)

    if implication is None or permise is None :
        print("Rule Cannot Be Applied")
        return None
    
    if implication.data == IMP :
        if trees_equal(implication.left , permise):
            return implication.right
        else:
            print("Rule Cannot Be Applied")
            return None
    else:
        print("Rule Cannot Be Applied")
        return None
    

def MT (line1 , line2 , formulas):
    formula1 = formulas.get(line1)
    formula2 = formulas.get(line2)

    if formula1 is None or formula2 is None :
        print ("Rule Cannot Be Applied")
        return None
    
    implication = None
    neg = None
            
    if formula1.data == IMP and formula2.data == NOT:
        if trees_equal(formula1.right, formula2.right):
            implication = formula1 
            neg = formula2.right 
    elif formula2.data == IMP and formula1.data == NOT :
        if trees_equal(formula2.right, formula1.right):
            implication = formula2
            neg = formula1.right
    
    if implication and neg:
        return Node(NOT , implication.left)
    else:
        print("Rule Cannot Be Applied")
        return None
        

def NOT_elimination(line1 , line2 , formulas):
    formula1 = formulas.get(line1)
    formula2 = formulas.get(line2)

    if formula1 is None or formula2 is None:
        print("Rule Cannot Be Applied")
        return None
    
    if (formula2.data == NOT and trees_equal(formula1, formula2.right)) or \
       (formula1.data == NOT and trees_equal(formula2, formula1.right)):
        return Node(FALSE)
    else:
        print("Rule Cannot Be Applied")
        return None
            

def double_NOT_elimination(line , formulas):
    formula1 = formulas.get(line)

    if formula1 is None:
        print("Rule Cannot Be Applied")
        return None
    if formula1.data == NOT and formula1.right and \
       formula1.right.data == NOT and formula1.right.right:
        return formula1.right.right
    else:
        print("Rule Cannot Be Applied")
        return None


def double_NOT_introduction (line , formulas):
    formula1 = formulas.get(line)

    if formula1 is None:
        print("Rule Cannot Be Applied")
        return None
            
    return Node(NOT , Node(NOT , formula1))

############################################


# recursivly checks if if two bunary trees are equls 
def trees_equal(node1 , node2):
    if node1 is None and node2 is None:
        return True
    if node1 is None or node2 is None:
        return False
    if node1.data != node2.data:
        return False
    return trees_equal(node1.left, node2.left) and trees_equal(node1.right , node2.right)



# converts a binary tree back into its string form
# this function essentially revereses the parsing done by binary_tree
# it adds parentheses based on poerator precedence to ensure correnct logical grouping
def tree_to_formula_string(node):
    if node is None:
        return ""

    if node.data.isalpha() and node.data.islower() or node.data == FALSE:
        return node.data

    if node.data == NOT:
        right_str = tree_to_formula_string(node.right)
        if node.right and (node.right.data in [AND, OR, IMP] or node.right.data == NOT):
            return f"{NOT}({right_str})"
        return f"{NOT}{right_str}"

    left_str = tree_to_formula_string(node.left)
    right_str = tree_to_formula_string(node.right)

    current_op = node.data
    current_op_precedence = OPERATOR_PRECEDENCE[current_op]

    if node.left and node.left.data in OPERATOR_PRECEDENCE: 
        left_child_op = node.left.data
        left_child_op_precedence = OPERATOR_PRECEDENCE[left_child_op]
        
        
        if left_child_op_precedence < current_op_precedence:
            left_str = f"({left_str})"
        
        elif left_child_op_precedence == current_op_precedence and current_op == IMP:
            left_str = f"({left_str})"
       
        elif left_child_op == NOT:
            left_str = f"({left_str})"



    if node.right and node.right.data in OPERATOR_PRECEDENCE: 
        right_child_op = node.right.data
        right_child_op_precedence = OPERATOR_PRECEDENCE[right_child_op]
        
        if right_child_op_precedence < current_op_precedence:
            right_str = f"({right_str})"

        elif right_child_op_precedence == current_op_precedence and current_op in [AND, OR]:
            right_str = f"({right_str})"
        
        elif right_child_op == NOT:
            right_str = f"({right_str})"

    return f"{left_str} {current_op} {right_str}" 


# maps rule names to fuctoin 
RULES ={
    '∧i': AND_introduction,
    '∧e1': AND_elimination_1,
    '∧e2': AND_elimination_2,
    '→e': IMP_elimination,
    '¬e': NOT_elimination,
    '¬¬e': double_NOT_elimination,
    'MT': MT,
    '¬¬i': double_NOT_introduction,
}


# applies a rule to given lines and prints the rusult if valid 
def apply_rule(rule_name , lines_to_use , formulas):
    rule_function = RULES.get(rule_name)

    if rule_function is None:
        print("Rule Cannot Be Applied")
        return

    result_node = None
    if rule_name in ['∧i', '¬e', 'MT', '→e']:
        if len(lines_to_use) != 2:
            print("Rule Cannot Be Applied")
            return
        result_node = rule_function(lines_to_use[0], lines_to_use[1], formulas)
    elif rule_name in ['∧e1', '∧e2', '¬¬e', '¬¬i']:
        if len(lines_to_use) != 1:
            print("Rule Cannot Be Applied")
            return
        result_node = rule_function(lines_to_use[0], formulas)
    else:
        print("Rule Cannot Be Applied")
        return
            
    if result_node:
        print(tree_to_formula_string(result_node))


# main function 
def main():
    formulas_map, rule_data = read_input_file()
    
    if rule_data:
        rule_name, lines_to_use = rule_data
        apply_rule(rule_name, lines_to_use, formulas_map)
    else:
        print("Error: Rule information not found in input file.")

# run main() only when script is executed directly , not when imported
if __name__ == "__main__":
    main()
