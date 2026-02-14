import sys
from typing import Optional

# ِdefine logical symbols used in formula
NOT = '¬'
AND = '∧'
OR = '∨'
IMP = '→'

# operator precedence
OPERATOR_PRECEDENCE = {
    IMP : 1, OR : 2 ,AND : 3, NOT : 4 
}

# get formula from user file input and remove spaces
def get_input():
    print("Please enter a file name :")
    file_name = input()
    with open(file_name, 'r', encoding='utf-8') as file:
        formula = file.read().strip()
        formula = formula.replace(" ", "")
        return formula

#define the class for the nodes
class Node :
    def __init__(self , key) :
        self.data = key
        self.left : Node | None = None 
        self.right : Node | None = None 

# check balanced parentheses using a stack
def check_parentheses(formula) :
    stack = []
    for char in formula :
        if char == '(' :
            stack.append(char)
        elif char == ')' :
            if not stack :
                return False
            stack.pop()
    return not stack

# remove the outer parenteses 
def remove_outer_parentheses(formula , begin , end):
    
    if begin < 0 or end >= len(formula) or begin > end:
        return False
    if formula[begin] == '(' and formula[end] == ')'  :
        count = 0
        for i in range (begin , end +1):
            if formula[i] == '(':
                count += 1
            elif formula[i] == ')':
                count-=1
            if count == 0 and i<end:
                return False
        return count ==0
    return False


#build binary tree
def binary_tree(formula  , begin , end) :
    if begin > end :
        return None 
    
    if begin == end and formula[begin].isalpha() and formula[begin].islower() :
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
                    if formula[i] == IMP:
                        main_operator = i
    
    if main_operator != -1 :
        char_main_operator = formula[main_operator]
        node = Node(char_main_operator)

        node.right = binary_tree(formula , main_operator+1 , end)
        node.left = binary_tree(formula , begin , main_operator-1)

        return node 
    
    if formula[begin] == NOT:
        node = Node (NOT)
        node.right = binary_tree(formula , begin+1 , end)
        return node
    
    return None 

# step 1 : elimenation IMP 

def elimination_IMP (node :Optional [Node]) ->Optional[ Node] :
    if node is None :
        return None

       
    node.left = elimination_IMP(node.left)
    node.right = elimination_IMP(node.right)

    if node.data == IMP :
        new_node = Node(OR)
        new_node.right = node.right
        new_node.left = Node(NOT)
        new_node.left.right  = node.left
        return new_node
    return node

# step 2 : remove double negation and 

def remove_double_negation ( node : Optional[Node] )->Optional [Node]:
    
    if node is None :
        return None 
    
    node.right= remove_double_negation(node.right)
    
    node.left = remove_double_negation(node.left)

    if node.data == NOT and node.right is not None and node.right.data == NOT:
        return node.right.right
    
    return node
    
# step 3 : applying demorgan's law

def apply_demorgan(node : Optional[Node])-> Optional[Node]:

    if node is None :
        return None
    
    node.right = apply_demorgan(node.right)
    node.left = apply_demorgan(node.left)
    

    if node.data == NOT and node.right is not None and node.right.data in {OR , AND}:
        
        if node.right.data == AND:
            new_node = Node(OR)
            new_node.left =Node (NOT)
            new_node.right = Node (NOT)
            new_node.left.right = node.right.left
            new_node.right.right = node.right.right
            return new_node
        
        elif node.right.data == OR:
            new_node = Node(AND)
            new_node.left =Node (NOT)
            new_node.right = Node (NOT)
            new_node.left.right = node.right.left
            new_node.right.right = node.right.right
            return new_node

    return node

# step 4 : distribute or over and 

def OR_over_AND (node : Optional[Node]) -> Optional[Node]:

    if node is None:
        return None
    
    node.left = OR_over_AND(node.left)
    node.right = OR_over_AND(node.right)

    if node.data == OR:

        if node.left and node.left.data == AND:

            temp1 = node.left.left
            temp2 = node.left.right
            temp3 = node.right 

            new_node = Node(AND)
            new_node.right = Node(OR)
            new_node.left = Node(OR)

            new_node.left.left  = temp1
            new_node.left.right = temp3 

            new_node.right.left = temp2
            new_node.right.right = temp3

            return OR_over_AND(new_node)
        
    
        elif node.right is not None and node.right.data == AND:

            temp1 = node.left
            temp2 = node.right.left
            temp3 = node.right.right

            new_node = Node(AND)
            new_node.right = Node(OR)
            new_node.left = Node(OR)

            new_node.left.right = temp2
            new_node.left.left  = temp1

            new_node.right.right = temp3
            new_node.right.left = temp1

            return OR_over_AND(new_node)
        
    return node

#print the parse tree
def print_tree(node , level = 0):

    if node is None:
        return 
    
    print("  "*level + str(node.data))
    print_tree(node.left , level+1)
    print_tree(node.right , level+1)

#print fourmula to another way 

def CNF_formula(node: Optional[Node]) -> str:
    
    if node is None:
        return ""
    
    if node.left is None and node.right is None:
        return node.data
    
    if node.data == NOT:
        if node.right and node.right.data in {OR, AND, IMP}:
            return f"{NOT}({CNF_formula(node.right)})"
        return NOT + CNF_formula(node.right)
    
    left_str = CNF_formula(node.left)
    right_str = CNF_formula(node.right)

    if node.data == OR:
        if node.left and node.left.data == AND:
            left_str = f"({left_str})"
        if node.right and node.right.data == AND:
            right_str = f"({right_str})"
        return f"{left_str}{OR}{right_str}"

    if node.data == AND:
        if node.left and node.left.data == OR:
            left_str = f"({left_str})"
        if node.right and node.right.data == OR:
            right_str = f"({right_str})"
        return f"{left_str}{AND}{right_str}"
    
    return f"({left_str}{node.data}{right_str})"

    
# main function 

def main():

    formula = get_input()

    if not check_parentheses(formula):
        print ("Invalid input !")
        sys.exit(1)

    tree = binary_tree(formula, 0 , len(formula)-1)
    tree = elimination_IMP(tree)


    for _ in range(5):
        old_tree_str = CNF_formula(tree)
        tree = remove_double_negation(tree)
        tree = apply_demorgan(tree)
        tree = remove_double_negation(tree)
        if old_tree_str == CNF_formula(tree):
            break
    
    while True:
        old_tree_str = CNF_formula(tree)
        tree = OR_over_AND(tree)
        if old_tree_str == CNF_formula(tree):
            break
    
    print ("===================")
    print(CNF_formula(tree))
    print("====================")
    print ("")
    #print_tree(tree)

# run main() only when script is executed directly , not when imported
if __name__ == "__main__":
    main()


# LAST VERSION 