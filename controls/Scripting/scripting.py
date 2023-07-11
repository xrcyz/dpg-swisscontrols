import ast
import operator as op
from typing import List, Union, Tuple, Callable

"""
TODO
- return error messages instead of raising exceptions
"""

def create_combined_lambdas(lambdas: List[Callable]) -> Callable:
    """
    Takes a list of lambda functions and returns a new function that,
    when called with a row of a DataFrame, returns True only if all of the
    lambda functions in the list return True for that row.

    Parameters
    ----------
    lambdas : List[Callable]
        A list of lambda functions that take a DataFrame row and return a bool.

    Returns
    -------
    Callable
        A function that takes a DataFrame row and returns a bool.
    """

    def filter_func(row):
        # apply each lambda to the row and check if all return True
        return all(f(row) for f in lambdas)

    return filter_func

def create_lambda_from_checklist(column: str, include_items: List[Union[str, int]]):
    """
    Create a lambda function to filter a DataFrame based on multiple conditions.

    Args:
        column: A column name in a dataframe.
        include_items: A list of items to include from that column.

    Returns:
        callable: A lambda function which when applied to a DataFrame, filters the DataFrame based 
        on the conditions provided.

    Usage:
    >>> lambda = construct_filter_lambda('Fruit',  ['Pear'])
    >>> filtered_df = df[df.apply(lambda, axis=1)]
    """
    def filter_func(row):
        return row[column] in include_items
    return filter_func

def create_lambda_from_expression(expr: str, allowed_vars: List[str]):
    """
    Create a lambda function from a given string expression. 

    This function converts a user provided string expression into a valid 
    lambda function, ensuring that the expression only contains allowed variables.

    Parameters:
    expr (str): The string expression to be converted into a lambda function.
    allowed_vars (List[str]): A list of variable names that are allowed in the expression.

    Returns:
    function: A lambda function equivalent to the provided string expression.

    Raises:
    ValueError: If the provided string expression contains disallowed variables or operations,
                a ValueError is raised with the message: "Disallowed expression: {expr}".

    Example:
    Given a DataFrame df with columns ['Fruit', 'Year', 'Quarter']:

    >>> expr = '((Fruit == "Apple") and (Year == 2023)) or (Quarter == 4)'
    >>> lambda_func = create_lambda_from_expression(expr, allowed_vars=['Fruit', 'Year', 'Quarter'])
    >>> filtered_df = df[df.apply(lambda_func, axis=1)]

    The filtered_df will contain only the rows where Fruit is "Apple" and Year is 2023,
    or where Quarter is 4.

    Note: The lambda function operates on a row-wise basis (i.e., axis=1 in df.apply()).
    Each identifier in expr corresponds to a column in the DataFrame.
    """
    node = ast.parse(expr, mode='eval')
    if not is_allowed(node, allowed_vars):
        raise ValueError(f"Disallowed expression: {expr}")

    return ast_to_lambda(node)

def is_allowed(node, allowed_vars):
    """
    Recursively check if a parsed AST node is allowed.

    Parameters:
    node (ast.AST): The AST node to check.
    allowed_vars (List[str]): A list of variable names that are allowed in the expression.

    Returns:
    bool: True if the node is allowed, False otherwise.
    """
    if isinstance(node, (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)):
        return True
    elif isinstance(node, ast.BoolOp):
        return all(is_allowed(value, allowed_vars) for value in node.values)
    elif isinstance(node, ast.Compare):
        return is_allowed(node.left, allowed_vars) and all(is_allowed(comp, allowed_vars) for comp in node.ops) and all(is_allowed(c, allowed_vars) for c in node.comparators)
    elif isinstance(node, ast.Name):
        return node.id in allowed_vars
    elif isinstance(node, ast.Constant):
        return True
    elif isinstance(node, ast.Expression):
        return is_allowed(node.body, allowed_vars)
    else:
        return False
    
def ast_to_lambda(node):
    """
    Convert an AST to a lambda function.

    Parameters:
    node (ast.AST): The AST node to convert.

    Returns:
    function: A lambda function equivalent to the provided AST node.
    """
    if isinstance(node, ast.Expression):
        return ast_to_lambda(node.body)
    elif isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return lambda row: all(ast_to_lambda(value)(row) for value in node.values)
        elif isinstance(node.op, ast.Or):
            return lambda row: any(ast_to_lambda(value)(row) for value in node.values)
        else:
            raise ValueError(f"Unsupported boolean operator: {type(node.op)}")
    elif isinstance(node, ast.Compare):
        if len(node.ops) == 1:
            return make_compare_lambda(node.left, node.ops[0], node.comparators[0])
        elif len(node.ops) == 2:
            # print(ast.dump(node, indent=4))
            # Compare(
            #     left=Constant(value=2022),
            #     ops=[
            #         Lt(),
            #         Lt()],
            #     comparators=[
            #         Name(id='Year', ctx=Load()),
            #         Constant(value=2024)])
            my_ast = ast.BoolOp(op=ast.And(),
                values=[ast.Compare(left=node.left,
                                    ops=[node.ops[0]],
                                    comparators=[node.comparators[0]]),
                        ast.Compare(left=node.comparators[0],
                                    ops=[node.ops[1]],
                                    comparators=[node.comparators[1]])])

            return lambda row: ast_to_lambda(my_ast)(row)
        else:
            raise ValueError("More than two comparisons are not supported.")
    else:
        raise ValueError(f"Unsupported node type: {type(node)}")
    
def make_compare_lambda(left, op, right):
    """
    Create a lambda function from a comparison AST node.

    Parameters:
    node (ast.Compare): The comparison AST node to convert.

    Returns:
    function: A lambda function equivalent to the provided comparison AST node.
    """
    if isinstance(left, ast.Name):
        name = left.id
        value = ast.literal_eval(right)
    elif isinstance(right, ast.Name):
        name = right.id
        value = ast.literal_eval(left)
        # Swap comparison operator for reversed operands
        if isinstance(op, ast.Lt):
            op = ast.Gt()
        elif isinstance(op, ast.LtE):
            op = ast.GtE()
        elif isinstance(op, ast.Gt):
            op = ast.Lt()
        elif isinstance(op, ast.GtE):
            op = ast.LtE()
    else:
        raise ValueError("Either left or right operand must be a column name.")

    if isinstance(op, ast.Lt):
        return lambda row: row[name] < value
    elif isinstance(op, ast.LtE):
        return lambda row: row[name] <= value
    elif isinstance(op, ast.Gt):
        return lambda row: row[name] > value
    elif isinstance(op, ast.GtE):
        return lambda row: row[name] >= value
    elif isinstance(op, ast.Eq):
        return lambda row: row[name] == value
    elif isinstance(op, ast.NotEq):
        return lambda row: row[name] != value
    else:
        raise ValueError(f"Unsupported operator type: {type(op)}")
    
