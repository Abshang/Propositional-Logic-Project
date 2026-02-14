# Define logical operators
NOT = '¬'
AND = '∧'
OR = '∨'
IMP = '→'
FALSE = '⊥'


############### Input and Parsing ###############

# finds and returns the entry with the specified line number from list 
def get_line_by_num(lines, number):
    for entry in lines:
        if entry['line'] == number:
            return entry
    return None


# parses a rule reference string into a list of line numbers and ranges 
def parse_rule_references(rule_string):
    refs = []
    parts = [p.strip() for p in rule_string.split(',') if p.strip()]
    for part in parts:
        if '-' in part:
            try:
                start_str, end_str = part.split('-')
                start = int(start_str.strip())
                end = int(end_str.strip())
                if start <= 0 or end <= 0: 
                    return None
                refs.append((start, end))
            except ValueError:
                return None 
        else:
            try:
                line_num = int(part)
                if line_num <= 0:
                    return None
                refs.append(line_num)
            except ValueError:
                return None 
    return refs


# reads a natural deduction proof file from user input and parses its structure 
def read_input_file():
    print("Please enter a file name:")
    file_name = input()

    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines_from_file = [line.rstrip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return [], {}

    parsed_deduction_lines = []
    scope_stack = [(0, 0)]
    scope_metadata = {0: {'start_file_line': 0, 'end_file_line': None, 'parent_scope_id': None}} 

    current_file_line_number = 0

    for line_str in lines_from_file:
        current_file_line_number += 1
        current_scope_id = scope_stack[-1][0]

        stripped_line = line_str.strip()

        if stripped_line == 'BeginScope':
            new_scope_id = current_file_line_number 
            parent_scope_id_for_new_scope = scope_stack[-1][0]
            scope_stack.append((new_scope_id, parent_scope_id_for_new_scope)) 
            scope_metadata[new_scope_id] = {
                'start_file_line': current_file_line_number,
                'end_file_line': None,
                'parent_scope_id': parent_scope_id_for_new_scope
            }
            continue
        elif stripped_line == 'EndScope':
            if len(scope_stack) > 1:
                closed_scope_id, _ = scope_stack.pop()
                scope_metadata[closed_scope_id]['end_file_line'] = current_file_line_number
            else:
                print(f"Error: Mismatched EndScope at file line {current_file_line_number}. No active scope to close.")
            continue
        
        # Find first digit
        first_digit_idx = -1
        for i, char in enumerate(line_str):
            if char.isdigit():
                first_digit_idx = i
                break
        
        if first_digit_idx == -1:
            print(f"Error: Invalid line format (no line number found) at file line {current_file_line_number}: '{line_str}'")
            continue

        # Extract line number
        line_number_str = ""
        after_line_num_idx = -1
        for i in range(first_digit_idx, len(line_str)):
            if line_str[i].isdigit():
                line_number_str += line_str[i]
            else:
                after_line_num_idx = i
                break
        
        if after_line_num_idx == -1:
            after_line_num_idx = len(line_str)
        
        try:
            line_number = int(line_number_str)
        except ValueError:
            print(f"Error: Invalid line number format at file line {current_file_line_number}: '{line_str}'")
            continue
        
        # Get remaining part after line number
        remaining_part = line_str[after_line_num_idx:].strip()
        
        if not remaining_part:
            print(f"Error: Invalid line format (missing formula or rule) at file line {current_file_line_number}: '{line_str}'")
            continue
        
        # Find where rule starts (4+ consecutive spaces)
        rule_start_idx = -1
        consecutive_spaces = 0
        
        for i in range(len(remaining_part)):
            if remaining_part[i] == ' ':
                consecutive_spaces += 1
                if consecutive_spaces >= 4 and rule_start_idx == -1:
                    rule_start_idx = i - 3  # Start of the 4 spaces
            else:
                consecutive_spaces = 0
        
        if rule_start_idx != -1:
            formula = remaining_part[:rule_start_idx].strip()
            rule_part = remaining_part[rule_start_idx:].strip()
        else:
            # No rule found, entire remaining part is formula
            formula = remaining_part.strip()
            rule_part = ""
        
        if not formula:
            print(f"Error: Invalid line format (empty formula) at file line {current_file_line_number}: '{line_str}'")
            continue

        parsed_deduction_lines.append({
            'line': line_number,
            'formula': formula,
            'rule_string': rule_part,
            'scope_id': current_scope_id,
            'file_line_number': current_file_line_number
        })

    for scope_id, s_info in scope_metadata.items():
        if s_info['end_file_line'] is None:
            s_info['end_file_line'] = current_file_line_number 

    return parsed_deduction_lines, scope_metadata


############### Scope Management ###############

# returns the list of ancestor scope id from root to the given scope 
def get_ancestors(scope_id, scope_metadata):
    path = []
    current_id = scope_id
    visited = set()
    
    while current_id is not None:
        if current_id in visited:
            break
        visited.add(current_id)
        path.insert(0, current_id)
        if current_id == 0: 
            break
        parent_id = scope_metadata.get(current_id, {}).get('parent_scope_id')
        if parent_id is None: 
            break
        if parent_id == current_id:
            break
        current_id = parent_id
    return path


# returns true if the target scope is an ancestor of the current scope 
def is_accessible(current_line_scope_id, target_line_scope_id, scope_metadata):
    current_scope_path = get_ancestors(current_line_scope_id, scope_metadata)
    return target_line_scope_id in current_scope_path


# finds the smallest common scope that encloses both start and end lines 
def find_enclosing_scope_by_logical_lines(all_parsed_lines, all_scope_metadata, logical_start_line, logical_end_line):
    start_line_entry = get_line_by_num(all_parsed_lines, logical_start_line)
    end_line_entry = get_line_by_num(all_parsed_lines, logical_end_line)

    if not start_line_entry or not end_line_entry:
        return None
    expected_begin_file_line = start_line_entry['file_line_number'] - 1
    expected_end_file_line = end_line_entry['file_line_number'] + 1

    for scope_id, s_info in all_scope_metadata.items():
        if s_info.get('start_file_line') == expected_begin_file_line and \
           s_info.get('end_file_line') == expected_end_file_line:
            return scope_id
    return None


############### Normalization and Processing Formula ###############

# remove the outer parentheses properly
def norm_frm(formula_str):
    s = formula_str.strip()
    
    while len(s) >= 2 and s.startswith('(') and s.endswith(')'):
        # Check if parentheses actually enclose the entire formula
        depth = 0
        can_remove = True
        
        for i in range(len(s)):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
            
            # If depth reaches 0 before the end, we can't remove outer parens
            if depth == 0 and i < len(s) - 1:
                can_remove = False
                break
        
        if can_remove and depth == 0:
            s = s[1:-1].strip()
        else:
            break
    
    return s


# Find the main operator at the top level (outside parentheses)
def find_main_operator(formula, operator):
    """Find the first occurrence of operator at depth 0 (outside all parentheses)"""
    depth = 0
    i = 0
    while i < len(formula):
        if formula[i] == '(':
            depth += 1
            i += 1
        elif formula[i] == ')':
            depth -= 1
            i += 1
        elif depth == 0 and formula[i:i+len(operator)] == operator:
            return i
        else:
            i += 1
    return -1


# Split formula by the main operator
def split_by_operator(formula, operator):
    """Split formula by the main operator at depth 0"""
    idx = find_main_operator(formula, operator)
    if idx == -1:
        return None
    left = formula[:idx].strip()
    right = formula[idx+len(operator):].strip()
    return (left, right)


############### Validation and Deduction Logic ###############

# validates a single proof line based on its inference rule and references
def check_line_validity(line_entry, all_lines, scope_metadata):
    
    rule_string = line_entry['rule_string']
    formula = line_entry['formula']
    current_line_scope_id = line_entry['scope_id']

    # premise and assumption 
    if rule_string == 'Premise' or rule_string == 'Assumption':
        return True

    # Split rule name and references
    rule_parts = rule_string.split(',', 1) 
    rule_name = rule_parts[0].strip()
    rule_refs_part = rule_parts[1].strip() if len(rule_parts) > 1 else ""
    
    par_ref = parse_rule_references(rule_refs_part)
    if par_ref is None: 
        return False

    # AND introduction 
    if rule_name == '∧i':
        if len(par_ref) != 2 or any(isinstance(ref, tuple) for ref in par_ref):
            return False 
        l1_num, l2_num = par_ref[0], par_ref[1]
        l1 = get_line_by_num(all_lines, l1_num)
        l2 = get_line_by_num(all_lines, l2_num)

        if not l1 or not l2:
            return False 
        if not is_accessible(current_line_scope_id, l1['scope_id'], scope_metadata) or \
           not is_accessible(current_line_scope_id, l2['scope_id'], scope_metadata):
            return False 
      
        expected_formula_str = f"{norm_frm(l1['formula'])} {AND} {norm_frm(l2['formula'])}"
        return norm_frm(formula) == norm_frm(expected_formula_str)

    # AND elimination 1 
    if rule_name == '∧e1':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        conj_line = get_line_by_num(all_lines, ref_num) 

        if not conj_line or not is_accessible(current_line_scope_id, conj_line['scope_id'], scope_metadata):
            return False 
        
        conj_formula_norm = norm_frm(conj_line['formula'])
        parts = split_by_operator(conj_formula_norm, AND)
        if parts is None:
            return False
        
        left_part, right_part = parts
        return norm_frm(formula) == norm_frm(left_part)

    # AND elimination 2 
    if rule_name == '∧e2':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        conj_line = get_line_by_num(all_lines, ref_num) 

        if not conj_line or not is_accessible(current_line_scope_id, conj_line['scope_id'], scope_metadata):
            return False 
        
        conj_formula_norm = norm_frm(conj_line['formula'])
        parts = split_by_operator(conj_formula_norm, AND)
        if parts is None:
            return False
        
        left_part, right_part = parts
        return norm_frm(formula) == norm_frm(right_part)

    # IMP elimination 
    if rule_name == '→e':
        if len(par_ref) != 2 or any(isinstance(ref, tuple) for ref in par_ref):
            return False 
        imp_line_num, ant_line_num = par_ref[0], par_ref[1]
        imp_line = get_line_by_num(all_lines, imp_line_num)
        ant_line = get_line_by_num(all_lines, ant_line_num) 

        if not imp_line or not ant_line:
            return False 
        if not is_accessible(current_line_scope_id, imp_line['scope_id'], scope_metadata) or \
           not is_accessible(current_line_scope_id, ant_line['scope_id'], scope_metadata):
            return False 

        imp_formula_norm = norm_frm(imp_line['formula'])
        parts = split_by_operator(imp_formula_norm, IMP)
        if parts is None:
            return False
        
        antecedent_in_imp, consequent_in_imp = parts
        
        if norm_frm(ant_line['formula']) != norm_frm(antecedent_in_imp):
            return False 
        return norm_frm(formula) == norm_frm(consequent_in_imp)
    
    # copy 
    if rule_name == 'Copy':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        source_line = get_line_by_num(all_lines, ref_num)

        if not source_line:
            return False 
        if not is_accessible(current_line_scope_id, source_line['scope_id'], scope_metadata):
            return False 
        return norm_frm(formula) == norm_frm(source_line['formula'])

    # Negation elimination 
    if rule_name == '¬e':
        if len(par_ref) != 2 or any(isinstance(ref, tuple) for ref in par_ref):
            return False 
        
        l1_num, l2_num = par_ref[0], par_ref[1]
        l1 = get_line_by_num(all_lines, l1_num)
        l2 = get_line_by_num(all_lines, l2_num)

        if not l1 or not l2:
            return False 
        if not is_accessible(current_line_scope_id, l1['scope_id'], scope_metadata) or \
           not is_accessible(current_line_scope_id, l2['scope_id'], scope_metadata):
            return False 
        
        l1_norm = norm_frm(l1['formula'])
        l2_norm = norm_frm(l2['formula'])

        if l1_norm.startswith(NOT) and norm_frm(l1_norm[len(NOT):]) == l2_norm:
            return norm_frm(formula) == FALSE
 
        if l2_norm.startswith(NOT) and norm_frm(l2_norm[len(NOT):]) == l1_norm:
            return norm_frm(formula) == FALSE
        
        return False 
    
    # FALSE elimination 
    if rule_name == '⊥e':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        
        ref_num = par_ref[0]
        false_line = get_line_by_num(all_lines, ref_num)
        
        if not false_line:
            return False 
        if not is_accessible(current_line_scope_id, false_line['scope_id'], scope_metadata):
            return False
        
        return norm_frm(false_line['formula']) == FALSE
    
    # IMP introduction 
    if rule_name == '→i':
        if len(par_ref) != 1 or not isinstance(par_ref[0], tuple):
            return False 
        
        start_logical_line, end_logical_line = par_ref[0]
        
        ass_line = get_line_by_num(all_lines, start_logical_line)
        con_line = get_line_by_num(all_lines, end_logical_line)

        if not ass_line or not con_line:
            return False
    
        if ass_line['rule_string'] != 'Assumption':
            return False

        target_scp_id = find_enclosing_scope_by_logical_lines(all_lines, scope_metadata, start_logical_line, end_logical_line)
        
        if target_scp_id is None: 
            return False

        if scope_metadata[target_scp_id]['parent_scope_id'] != current_line_scope_id:
            return False

        expected_formula_str = f"{norm_frm(ass_line['formula'])} {IMP} {norm_frm(con_line['formula'])}"
        return norm_frm(formula) == norm_frm(expected_formula_str)

    # OR elimination 
    if rule_name == '∨e':
        if len(par_ref) != 3: 
            return False 
        main_formula_ref = par_ref[0]
        scope1_range = par_ref[1] 
        scope2_range = par_ref[2] 

        if not isinstance(main_formula_ref, int) or \
           not isinstance(scope1_range, tuple) or \
           not isinstance(scope2_range, tuple):
            return False 

        main_line = get_line_by_num(all_lines, main_formula_ref)
        if not main_line or not is_accessible(current_line_scope_id, main_line['scope_id'], scope_metadata):
            return False 
        
        main_formula_norm = norm_frm(main_line['formula'])
        parts = split_by_operator(main_formula_norm, OR)
        if parts is None:
            return False
        
        disjunct1, disjunct2 = parts
        disjunct1 = norm_frm(disjunct1)
        disjunct2 = norm_frm(disjunct2)

        scope1_assume_logical_line = scope1_range[0]
        scope1_conclude_logical_line = scope1_range[1]

        scope1_assume_line = get_line_by_num(all_lines, scope1_assume_logical_line)
        scope1_conclude_line = get_line_by_num(all_lines, scope1_conclude_logical_line)
        
        if not scope1_assume_line or not scope1_conclude_line:
            return False 
        
        if scope1_assume_line['rule_string'] != 'Assumption' or norm_frm(scope1_assume_line['formula']) != disjunct1:
            return False
        
        scope1_id = find_enclosing_scope_by_logical_lines(all_lines, scope_metadata, scope1_assume_logical_line, scope1_conclude_logical_line)
        if scope1_id is None:
            return False 
        
        if scope_metadata[scope1_id]['parent_scope_id'] != current_line_scope_id:
            return False 
        
        if norm_frm(scope1_conclude_line['formula']) != norm_frm(formula):
            return False

        scp2_assume_logical_line = scope2_range[0]
        scp2_conclude_logical_line = scope2_range[1]

        scp2_ass_line = get_line_by_num(all_lines, scp2_assume_logical_line)
        scp2_conclude_line = get_line_by_num(all_lines, scp2_conclude_logical_line)

        if not scp2_ass_line or not scp2_conclude_line:
            return False 
        if scp2_ass_line['rule_string'] != 'Assumption' or norm_frm(scp2_ass_line['formula']) != disjunct2:
            return False

        scope2_id = find_enclosing_scope_by_logical_lines(all_lines, scope_metadata, scp2_assume_logical_line, scp2_conclude_logical_line)
        if scope2_id is None:
            return False 
        if scope_metadata[scope2_id]['parent_scope_id'] != current_line_scope_id:
            return False
        
        if norm_frm(scp2_conclude_line['formula']) != norm_frm(formula):
            return False

        return True 
    
    # OR introduction 1 
    if rule_name == '∨i1':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        ref_line = get_line_by_num(all_lines, ref_num)

        if not ref_line or not is_accessible(current_line_scope_id, ref_line['scope_id'], scope_metadata):
            return False 
        
        formula_norm = norm_frm(formula)
        parts = split_by_operator(formula_norm, OR)
        if parts is None:
            return False
        
        left_disjunct, right_disjunct = parts
        
        return norm_frm(left_disjunct) == norm_frm(ref_line['formula'])

    # OR introduction 2 
    if rule_name == '∨i2':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        ref_line = get_line_by_num(all_lines, ref_num)

        if not ref_line or not is_accessible(current_line_scope_id, ref_line['scope_id'], scope_metadata):
            return False 
        
        formula_norm = norm_frm(formula)
        parts = split_by_operator(formula_norm, OR)
        if parts is None:
            return False
        
        left_disjunct, right_disjunct = parts
        
        return norm_frm(right_disjunct) == norm_frm(ref_line['formula'])

    # Negation Introduction 
    if rule_name == '¬i':
        if len(par_ref) != 1 or not isinstance(par_ref[0], tuple):
            return False
        
        start_logical_line, end_logical_line = par_ref[0]
        
        ass_line = get_line_by_num(all_lines, start_logical_line)
        con_line = get_line_by_num(all_lines, end_logical_line)

        if not ass_line or not con_line:
            return False
        
        if ass_line['rule_string'] != 'Assumption':
            return False
            
        if norm_frm(con_line['formula']) != FALSE:
            return False 

        target_scp_id = find_enclosing_scope_by_logical_lines(all_lines, scope_metadata, start_logical_line, end_logical_line)
        
        if target_scp_id is None: 
            return False
        
        if scope_metadata[target_scp_id]['parent_scope_id'] != current_line_scope_id:
            return False
        
        expected_formula_str = f"{NOT}{norm_frm(ass_line['formula'])}"
        return norm_frm(formula) == norm_frm(expected_formula_str)

    # Double Negation Elimination 
    if rule_name == '¬¬e':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        ref_line = get_line_by_num(all_lines, ref_num)

        if not ref_line or not is_accessible(current_line_scope_id, ref_line['scope_id'], scope_metadata):
            return False 
        
        ref_formula_norm = norm_frm(ref_line['formula'])
        
        if not (ref_formula_norm.startswith(f"{NOT}{NOT}")):
            return False
            
        expected_formula = ref_formula_norm[len(NOT)*2:].strip()
        return norm_frm(formula) == norm_frm(expected_formula)

    # Modus Tollens 
    if rule_name == 'MT':
        if len(par_ref) != 2 or any(isinstance(ref, tuple) for ref in par_ref):
            return False 
        
        imp_line_num, neg_consequent_line_num = par_ref[0], par_ref[1]
        imp_line = get_line_by_num(all_lines, imp_line_num)
        neg_consequent_line = get_line_by_num(all_lines, neg_consequent_line_num)

        if not imp_line or not neg_consequent_line:
            return False 
        if not is_accessible(current_line_scope_id, imp_line['scope_id'], scope_metadata) or \
           not is_accessible(current_line_scope_id, neg_consequent_line['scope_id'], scope_metadata):
            return False 

        imp_formula_norm = norm_frm(imp_line['formula'])
        neg_con_formula_norm = norm_frm(neg_consequent_line['formula'])

        parts = split_by_operator(imp_formula_norm, IMP)
        if parts is None:
            return False
        
        ant, con = parts
        ant = norm_frm(ant)
        con = norm_frm(con)

        if not neg_con_formula_norm.startswith(NOT) or \
           norm_frm(neg_con_formula_norm[len(NOT):]) != con:
            return False
            
        expected_formula = f"{NOT}{ant}"
        return norm_frm(formula) == norm_frm(expected_formula)

    # Double Negation Introduction 
    if rule_name == '¬¬i':
        if len(par_ref) != 1 or isinstance(par_ref[0], tuple):
            return False 
        ref_num = par_ref[0]
        ref_line = get_line_by_num(all_lines, ref_num)

        if not ref_line or not is_accessible(current_line_scope_id, ref_line['scope_id'], scope_metadata):
            return False 
        
        expected_formula = f"{NOT}{NOT}{norm_frm(ref_line['formula'])}"
        return norm_frm(formula) == norm_frm(expected_formula)

    # Proof by Contradiction 
    if rule_name == 'PBC':
        if len(par_ref) != 1 or not isinstance(par_ref[0], tuple):
            return False
        
        start_logical_line, end_logical_line = par_ref[0]
        
        ass_line = get_line_by_num(all_lines, start_logical_line)
        con_line = get_line_by_num(all_lines, end_logical_line)

        if not ass_line or not con_line:
            return False
        
        if ass_line['rule_string'] != 'Assumption':
            return False
        
        assumption_formula_norm = norm_frm(ass_line['formula'])
        if not assumption_formula_norm.startswith(NOT):
            return False 

        if norm_frm(con_line['formula']) != FALSE:
            return False 

        target_scp_id = find_enclosing_scope_by_logical_lines(all_lines, scope_metadata, start_logical_line, end_logical_line)
        
        if target_scp_id is None: 
            return False
        
        if scope_metadata[target_scp_id]['parent_scope_id'] != current_line_scope_id:
            return False
        
        expected_formula_str = assumption_formula_norm[len(NOT):].strip()
        return norm_frm(formula) == norm_frm(expected_formula_str)

    # Law of Excluded Middle 
    if rule_name == 'LEM':
        if len(par_ref) != 0: 
            return False 
        
        formula_norm = norm_frm(formula)
        parts = split_by_operator(formula_norm, OR)
        if parts is None:
            return False
        
        left_part, right_part = parts
        left_part = norm_frm(left_part)
        right_part = norm_frm(right_part)
        
        # Check if right part is NOT left part
        if right_part.startswith(NOT):
            return norm_frm(right_part[len(NOT):]) == left_part
        
        return False

    return False 


# checks validity of all deduction lines and prints result and returns true if all valid 
def check_deduction(lines, scope_metadata):
    all_valid = True
    for line_entry in lines:
        if not check_line_validity(line_entry, lines, scope_metadata):
            print(f"Invalid deduction at Line {line_entry['line']}")
            all_valid = False
    
    if all_valid:
        print("\nValid Deduction")
    
    return all_valid


####################################

# main function 
def main():
    deduction_lines, scope_metadata = read_input_file()
    if deduction_lines: 
        check_deduction(deduction_lines, scope_metadata)

# run main() only when script is executed directly, not when imported
if __name__ == '__main__':
    main()