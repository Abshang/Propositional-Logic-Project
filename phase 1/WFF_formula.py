# ِdefine logical symbols used in formula
NOT = '¬'
AND = '∧'
OR = '∨'
IMP = '→'

## operator precedence
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
    
#check if the formula is a well-formed formula
def is_WFF(node) :
    if node is None :
        return False
    
    if node.right is None and node.left is None :
        return node.data.isalpha() and node.data.islower()
    
    if node.data == NOT :
        return node.left is None and is_WFF(node.right)
    
    if node.data in {AND , OR , IMP}:
        return node.left is not None and node.right is not None and is_WFF(node.left) and is_WFF(node.right)
    
    return False

# remove the outer parenteses 
def remove_outer_parentheses(formula , begin , end):
    if formula[begin] == '(' and formula[end] == ')'  :
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

# recursively builds a binary parse tree from a propositional logic fromula 
# this is the core function of the project 

# steps :
# 1 ) lase case : if it's a single variable , retrun a leaf node 
# 2 ) if fully parenthesezed , remove the outer parentheses and process inner part 
# 3 ) ptaverse the formula to find the main logical operator whti the lowest precedence 
# (outside of any parentheses) , respecting porerator precedence rules 
# 4 ) recursively build left and right subtrees based on the main operator's position 
# 5 ) handle negation as a unary operator applied to the right subtree only  

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
                    if formula[i] in [AND , OR]:
                        min_value = i
    
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


#print the parse tree
def print_tree(node , level = 0):

    if node is None:
        return 
    
    print("  "*level + str(node.data))
    print_tree(node.left , level+1)
    print_tree(node.right , level+1)
    

# main function : read formual , build binery tree , check fomula is WFF and print the result 
def main():
    formula = get_input()
    if check_parentheses(formula):
        tree  = binary_tree(formula , 0 , len(formula)-1)
        if tree is not None and is_WFF(tree):
            print(" Valid formula !")
            print_tree(tree)
        else:
            print(" Invalid formula !")

    else:
        print("Invalid formula !")

# run main() only when script is executed directly , not when imported
if __name__ == "__main__":
    main()


# LAST VERSION 