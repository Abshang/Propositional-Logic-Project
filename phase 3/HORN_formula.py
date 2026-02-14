# ِdefine logical symbols used in formula
NOT = '¬'
AND = '∧'
OR = '∨'
IMP = '→'
TRUE = '⊤'
FALSE = '⊥'

# operator precedence (currently unused in this code and kept for potential future parsing logic)
OPERATOR_PRECEDENCE = {
    IMP: 1, OR: 2, AND: 3, NOT: 4
}

# get formula from user file input and remove spaces
def get_input():
    print("Please enter a file name :")
    file_name = input()
    with open(file_name, 'r', encoding='utf-8') as file:
        formula = file.read().strip()
        formula = formula.replace(" ", "")
        return formula

# check balanced parentheses using a stack 
def check_parentheses(formula):
    stack = []
    for char in formula:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                return False
            stack.pop()
    return not stack

# separate formual clauses by AND operator considering parentheses structure 
def split_clauses(formula):

    clauses = []

    # this part of the function removes outer parentheses that do not affent the meaning or structure of thr formula 
    # note : in the previous two phases , this task was handled by the remove_outer_parentheses function 
    if formula.startswith('(') and formula.endswith(')'):
        balance = 0
        is_fully_parenthesized = True
        for i, char in enumerate(formula[1:-1]):
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            if balance < 0:
                is_fully_parenthesized = False
                break
        if is_fully_parenthesized and balance == 0:
            formula = formula[1:-1]

    # this part of the function split the formula into individual cluases
    # 
    # - split formula by top-level AND , ignoring inner parentheses
    # - track depth to aviid splitting inside nested expressions
    # - trim and clean eack clause before adding to list 
     
    current_clause_start_index = 0
    depth = 0

    for i, char in enumerate(formula):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        
        if char == AND and depth == 0:
            clause = formula[current_clause_start_index:i].strip()
            
            if clause.startswith('(') and clause.endswith(')'):
                clause = clause[1:-1]
            
            if clause:
                clauses.append(clause)
            
            current_clause_start_index = i + 1

    final_clause = formula[current_clause_start_index:].strip()
    if final_clause.startswith('(') and final_clause.endswith(')'):
        final_clause = final_clause[1:-1]

    if final_clause:
        clauses.append(final_clause)

    return clauses

# validate antecedent of a clause according to horn formula rules
def is_valid_antecedent(antecedent):
    if not antecedent:
        return False

    parts = antecedent.split(AND)

    for part in parts:
        part = part.strip()
        if part == TRUE or part == FALSE:
            continue
        if not (len(part) == 1 and part.isalpha() and part.islower()):
            return False
    return True

# validate antecedent of a clause according to horn formula rules 
def is_valid_consequent(consequent):
    if not consequent:
        return False
    if (len(consequent) == 1 and consequent.isalpha() and consequent.islower()) or \
       consequent == TRUE or consequent == FALSE:
        return True
    return False

# check if clause is a valid horn clause with proper antecedent and consequent 
def is_valid_clause(clause):
    if IMP in clause:
        parts = clause.split(IMP)
        if len(parts) != 2:
            return False
        
        ant = parts[0].strip()
        con = parts[1].strip()
        return is_valid_antecedent(ant) and is_valid_consequent(con)
    else:
        return False

# extract list of antecedent and consequent from an implication clause
def extract(clause):
    parts = clause.split(IMP)
    antecedents = parts[0].strip()
    con = parts[1].strip()
    ant = [p.strip() for p in antecedents.split(AND)]
    return ant, con

# this function is the core phase of the project that determines wheter
# the given horn formula is satisfialbe using the unit propagation algorithm

# it perfomrs :
# 1 ) validate and extraction of clauses
# 2 ) initialization of variables 
# 3 ) iterative updating of variable assignments until final result is found
 
# this function plays a critical role in the overall project solution 
def Horn_satisfiable(clauses):
    horn_clauses = []
    variables = set()

    for clause_str in clauses:
        if clause_str.startswith('(') and clause_str.endswith(')'):
            clause_str = clause_str[1:-1]

        if not is_valid_clause(clause_str):
            print("Invalid Horn Formula")
            return

        antecedents, consequent = extract(clause_str)
        horn_clauses.append((antecedents, consequent))

        for a in antecedents:
            if a != TRUE and a != FALSE:
                variables.add(a)
        if consequent != TRUE and consequent != FALSE:
            variables.add(consequent)

    assignment = {var: False for var in variables}

    changed = True
    while changed:
        changed = False
        for antecedents, consequent in horn_clauses:
            antecedent_is_true = True
            for a in antecedents:
                if a == FALSE:
                    antecedent_is_true = False
                    break
                elif a == TRUE:
                    continue
                elif not assignment.get(a, False):
                    antecedent_is_true = False
                    break

            if antecedent_is_true:
                if consequent == FALSE:
                    print("Unsatisfiable")
                    return
                if consequent == TRUE:
                    continue
                if not assignment.get(consequent, False):
                    assignment[consequent] = True
                    changed = True

    print("Satisfiable")
    true_variables = sorted([var for var, value in assignment.items() if value])
    for var in true_variables:
        print(var)

# main function : read formula , check parentheses , split clauses , validate formula and check satisfiability 
def main():
    formula = get_input()

    if not check_parentheses(formula):
        print("Invalid Horn Formula")
        return 
    
    clauses = split_clauses(formula)
    
    Horn_satisfiable(clauses)

# run main() only when script is executed directly , not when imported
if __name__ == "__main__":
    main()

# LAST VERSION 