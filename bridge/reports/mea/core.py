# This library presents core functions for MEA, such as converting and comparison of error traces.


import operator
import re


# Conversion functions.
CONVERSION_FUNCTION_CALL_TREE = "call tree"
CONVERSION_FUNCTION_MODEL_FUNCTIONS = "model functions"
CONVERSION_FUNCTION_CONDITIONS = "conditions"
CONVERSION_FUNCTION_ASSIGNMENTS = "assignments"
CONVERSION_FUNCTION_NOTES = "error descriptions"
CONVERSION_FUNCTION_FULL = "full"
DEFAULT_CONVERSION_FUNCTION = CONVERSION_FUNCTION_MODEL_FUNCTIONS

# Comparison functions.
COMPARISON_FUNCTION_EQUAL = "equal"
COMPARISON_FUNCTION_INCLUDE = "include"
COMPARISON_FUNCTION_INCLUDE_PARTIAL = "partial include"
COMPARISON_FUNCTION_SKIP = "skip"
DEFAULT_COMPARISON_FUNCTION = COMPARISON_FUNCTION_EQUAL

# Tags for configurations.
TAG_CONVERSION_FUNCTION = "conversion_function"
TAG_COMPARISON_FUNCTION = "comparison_function"
TAG_EDITED_ERROR_TRACE = "edited_error_trace"

# Conversion fucntions arguments.
TAG_ADDITIONAL_MODEL_FUNCTIONS = "additional_model_functions"
TAG_USE_NOTES = "use_notes"
TAG_USE_WARNS = "use_warns"

# Converted error trace tags.
CET_OP = "op"
CET_OP_CALL = "CALL"
CET_OP_RETURN = "RET"
CET_OP_ASSUME = "ASSUME"
CET_OP_ASSIGN = "ASSIGN"
CET_OP_NOTE = "NOTE"
CET_OP_WARN = "WARN"
CET_THREAD = "thread"
CET_SOURCE = "source"
CET_DISPLAY_NAME = "name"
CET_ID = "id"
CET_LINE = "line"
ASSIGN_MARK = " = "

DEFAULT_SIMILARITY_THRESHOLD = 100  # in % (all threads are equal)


def convert_error_trace(error_trace: dict, conversion_function: str, args: dict = dict) -> list:
    """
    Convert json error trace into internal representation (list of selected elements).
    """
    functions = {
        CONVERSION_FUNCTION_MODEL_FUNCTIONS: __convert_model_functions,
        CONVERSION_FUNCTION_CALL_TREE: __convert_call_tree_filter,
        CONVERSION_FUNCTION_CONDITIONS: __convert_conditions,
        CONVERSION_FUNCTION_FULL: __convert_full,
        CONVERSION_FUNCTION_ASSIGNMENTS: __convert_assignments,
        CONVERSION_FUNCTION_NOTES: __convert_notes
    }
    if conversion_function not in functions.keys():
        conversion_function = DEFAULT_CONVERSION_FUNCTION
    result = functions[conversion_function](error_trace, args)

    if args.get(TAG_USE_NOTES, args.get(TAG_USE_WARNS, False)) and \
            conversion_function not in [CONVERSION_FUNCTION_FULL, CONVERSION_FUNCTION_NOTES]:
        result += __convert_notes(error_trace, args)
        result = sorted(result, key=operator.itemgetter(CET_ID))

    return result


def is_equivalent(comparison_results: float, similarity_threshold: int) -> bool:
    """
    Returns true, if compared error traces are considered to be equivalent in terms of specified threshold.
    """
    return comparison_results and (comparison_results * 100 >= similarity_threshold)


def compare_error_traces(edited_error_trace: list, compared_error_trace: list, comparison_function: str) -> float:
    """
    Compare two error traces by means of specified function and return similarity coefficient
    for their threads equivalence (in case of a single thread function returns True/False).
    """
    et1_threaded, et2_threaded = __transform_to_threads(edited_error_trace, compared_error_trace)
    if not et1_threaded and not et2_threaded:
        # Return true for empty converted error traces (so they will be applied to all reports with the same attributes)
        return 1.0
    functions = {
        COMPARISON_FUNCTION_EQUAL: __compare_equal,
        COMPARISON_FUNCTION_INCLUDE: __compare_include,
        COMPARISON_FUNCTION_INCLUDE_PARTIAL: __compare_include_partial,
        COMPARISON_FUNCTION_SKIP: __compare_skip
    }
    if comparison_function not in functions.keys():
        comparison_function = DEFAULT_COMPARISON_FUNCTION
    equal_threads = functions[comparison_function](et1_threaded, et2_threaded)
    return __get_similarity_coefficient(et1_threaded, et2_threaded, equal_threads)


# noinspection PyUnusedLocal
def __convert_call_tree_filter(error_trace: dict, args: dict = {}) -> list:
    converted_error_trace = list()
    counter = 0
    # TODO: check this in core (one node for call and return edges).
    double_funcs = {}
    for edge in error_trace['edges']:
        if 'enter' in edge and 'return' in edge:
            double_funcs[edge['enter']] = edge['return']
        if 'enter' in edge:
            function_call = error_trace['funcs'][edge['enter']]
            converted_error_trace.append({
                CET_OP: CET_OP_CALL,
                CET_THREAD: edge['thread'],
                CET_SOURCE: edge['source'],
                CET_LINE: edge['start line'],
                CET_DISPLAY_NAME: function_call,
                CET_ID: counter
            })
        elif 'return' in edge:
            function_return = error_trace['funcs'][edge['return']]
            converted_error_trace.append({
                CET_OP: CET_OP_RETURN,
                CET_THREAD: edge['thread'],
                CET_LINE: edge['start line'],
                CET_SOURCE: edge['source'],
                CET_DISPLAY_NAME: function_return,
                CET_ID: counter
            })
            double_return = edge['return']
            while True:
                if double_return in double_funcs.keys():
                    converted_error_trace.append({
                        CET_OP: CET_OP_RETURN,
                        CET_THREAD: edge['thread'],
                        CET_LINE: edge['start line'],
                        CET_SOURCE: edge['source'],
                        CET_DISPLAY_NAME: error_trace['funcs'][double_funcs[double_return]],
                        CET_ID: counter
                    })
                    tmp = double_return
                    double_return = double_funcs[double_return]
                    del double_funcs[tmp]
                else:
                    break
        counter += 1
    return converted_error_trace


def __convert_model_functions(error_trace: dict, args: dict = {}) -> list:
    additional_model_functions = set(args.get(TAG_ADDITIONAL_MODEL_FUNCTIONS, []))
    model_functions = __get_model_functions(error_trace, additional_model_functions)
    converted_error_trace = __convert_call_tree_filter(error_trace, args)
    while True:
        counter = 0
        is_break = False
        for item in converted_error_trace:
            op = item[CET_OP]
            thread = item[CET_THREAD]
            name = item[CET_DISPLAY_NAME]
            if op == CET_OP_CALL:
                is_save = False
                remove_items = 0
                for checking_elem in converted_error_trace[counter:]:
                    remove_items += 1
                    checking_op = checking_elem[CET_OP]
                    checking_name = checking_elem[CET_DISPLAY_NAME]
                    checking_thread = checking_elem[CET_THREAD]
                    if checking_op == CET_OP_RETURN and checking_name == name or checking_thread != thread:
                        break
                    elif checking_op == CET_OP_CALL:
                        if checking_name in model_functions:
                            is_save = True
                if not is_save:
                    del converted_error_trace[counter:(counter + remove_items)]
                    is_break = True
                    break
            counter += 1
        if not is_break:
            break
    return converted_error_trace


# noinspection PyUnusedLocal
def __convert_conditions(error_trace: dict, args: dict = {}) -> list:
    converted_error_trace = list()
    counter = 0
    for edge in error_trace['edges']:
        if 'condition' in edge:
            assume = edge['condition']
            converted_error_trace.append({
                CET_OP: CET_OP_ASSUME,
                CET_THREAD: edge['thread'],
                CET_SOURCE: edge['source'],
                CET_LINE: edge['start line'],
                CET_DISPLAY_NAME: assume,
                CET_ID: counter
            })
        counter += 1
    return converted_error_trace


# noinspection PyUnusedLocal
def __convert_assignments(error_trace: dict, args: dict = {}) -> list:
    converted_error_trace = list()
    counter = 0
    for edge in error_trace['edges']:
        if 'source' in edge:
            source = edge['source']
            if ASSIGN_MARK in source:
                converted_error_trace.append({
                    CET_OP: CET_OP_ASSIGN,
                    CET_THREAD: edge['thread'],
                    CET_SOURCE: edge['source'],
                    CET_LINE: edge['start line'],
                    CET_DISPLAY_NAME: source,
                    CET_ID: counter
                })
        counter += 1
    return converted_error_trace


def __convert_notes(error_trace: dict, args: dict = {}) -> list:
    converted_error_trace = list()
    counter = 0
    use_notes = args.get(TAG_USE_NOTES, False)
    use_warns = args.get(TAG_USE_WARNS, False)
    if not use_notes and not use_warns:
        # Ignore, since we need at least one flag as True.
        use_notes = True
        use_warns = True

    for edge in error_trace['edges']:
        if 'note' in edge:
            if use_notes:
                converted_error_trace.append({
                    CET_OP: CET_OP_NOTE,
                    CET_THREAD: edge['thread'],
                    CET_SOURCE: edge['source'],
                    CET_LINE: edge['start line'],
                    CET_DISPLAY_NAME: edge['note'],
                    CET_ID: counter
                })
        elif 'warn' in edge:
            if use_warns:
                converted_error_trace.append({
                    CET_OP: CET_OP_WARN,
                    CET_THREAD: edge['thread'],
                    CET_SOURCE: edge['source'],
                    CET_LINE: edge['start line'],
                    CET_DISPLAY_NAME: edge['warn'],
                    CET_ID: counter
                })
        counter += 1
    return converted_error_trace


# noinspection PyUnusedLocal
def __convert_full(error_trace: dict, args: dict = dict) -> list:
    converted_error_trace = __convert_call_tree_filter(error_trace, args) + \
                            __convert_conditions(error_trace, args) + \
                            __convert_assignments(error_trace, args) + \
                            __convert_notes(error_trace, args)
    converted_error_trace = sorted(converted_error_trace, key=operator.itemgetter(CET_ID))
    return converted_error_trace


def __get_model_functions(error_trace: dict, additional_model_functions: set) -> set:
    """
    Extract model functions from error trace.
    """
    stack = list()
    model_functions = additional_model_functions
    patterns = set()
    for func in model_functions:
        if not str(func).isidentifier():
            patterns.add(func)
    for edge in error_trace['edges']:
        if 'enter' in edge:
            func = error_trace['funcs'][edge['enter']]
            if patterns:
                for pattern_func in patterns:
                    if re.match(pattern_func, func):
                        model_functions.add(func)
            stack.append(func)
        if 'return' in edge:
            # func = error_trace['funcs'][edge['return']]
            stack.pop()
        if 'warn' in edge or 'note' in edge:
            if len(stack) > 0:
                model_functions.add(stack[len(stack) - 1])
    model_functions = model_functions - patterns
    return model_functions


def __prep_elem_for_cmp(elem: dict, et: dict) -> None:
    op = elem[CET_OP]
    thread = elem[CET_THREAD]
    if thread not in et:
        et[thread] = list()
    if op in [CET_OP_RETURN, CET_OP_CALL]:
        et[thread].append((op, elem[CET_DISPLAY_NAME]))
    elif op == CET_OP_ASSUME:
        thread_aux = "{}_aux".format(thread)
        if thread_aux not in et:
            et[thread_aux] = list()
        et[thread_aux].append((op, elem[CET_DISPLAY_NAME], elem[CET_SOURCE]))
    elif op in [CET_OP_WARN, CET_OP_NOTE, CET_OP_ASSIGN]:
        thread_aux = "{}_aux".format(thread)
        if thread_aux not in et:
            et[thread_aux] = list()
        et[thread_aux].append((op, elem[CET_DISPLAY_NAME]))


def __transform_to_threads(edited_error_trace: list, compared_error_trace: list) -> (dict, dict):
    et1 = dict()
    et2 = dict()
    for i in range(len(edited_error_trace)):
        __prep_elem_for_cmp(edited_error_trace[i], et1)
    for i in range(len(compared_error_trace)):
        __prep_elem_for_cmp(compared_error_trace[i], et2)
    et1_threaded = dict()
    et2_threaded = dict()
    for thread, trace in et1.items():
        if trace:
            et1_threaded[thread] = tuple(trace)
    for thread, trace in et2.items():
        if trace:
            et2_threaded[thread] = tuple(trace)
    return et1_threaded, et2_threaded


def __sublist(sublist: tuple, big_list: tuple) -> bool:
    """
    Check that list sublist is included into the list big_list.
    """
    sublist = ",".join(str(v) for v in sublist)
    big_list = ",".join(str(v) for v in big_list)
    return sublist in big_list


def __compare_skip(edited_error_trace: dict, compared_error_trace: dict) -> int:
    return min(len(edited_error_trace),  len(compared_error_trace))


def __compare_equal(edited_error_trace: dict, compared_error_trace: dict) -> int:
    equal_threads = len(set(edited_error_trace.values()) & set(compared_error_trace.values()))
    return equal_threads


def __compare_include(edited_error_trace: dict, compared_error_trace: dict) -> int:
    equal_threads = 0
    for thread_1 in edited_error_trace.values():
        result = False
        for thread_2 in compared_error_trace.values():
            if __sublist(thread_1, thread_2):
                result = True
                break
        if result:
            equal_threads += 1
    return equal_threads


def __compare_include_partial(edited_error_trace: dict, compared_error_trace: dict) -> int:
    equal_threads = 0
    for thread_1 in edited_error_trace.values():
        result = False
        for thread_2 in compared_error_trace.values():
            if all(elem in thread_2 for elem in thread_1):
                result = True
                break
        if result:
            equal_threads += 1
    return equal_threads


def __get_similarity_coefficient(l1: dict, l2: dict, common_elements: int) -> float:
    # Currently represented only as Jaccard index.
    diff_elements = len(l1) + len(l2) - common_elements
    if diff_elements:
        return round(common_elements / diff_elements, 2)
    else:
        return 0.0
