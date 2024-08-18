from barfi import Block
import ast
import inspect
import json
import os
import time
from typing import Dict, Any
import numpy as np
import streamlit as st
from joblib import Memory
import itertools


def generate_block(
    compute_func,
    options_config_param: Dict[str, Any] = None,
    func_modificator=None,
    func_modificator_config_params: Dict[str, Any] = {},
    func_modificator_params_visible: list = [],
    add_display_option: bool = True,
    category_name: str = "Uncategorized",
    cache: bool = True,
    cache_visible: bool = True,
):
    """
    Generates a Block object configured with inputs, outputs, and options based on a compute function and additional parameters.

    This function dynamically creates a Block object for a given compute function. It configures the Block with input and output interfaces
    based on the function's signature, adds configurable options, and optionally enables caching for the compute function's results.
    Additional configuration can be provided through a JSON file named after the compute function or directly via the `options_config_param` parameter.

    Parameters:
    ----------
    
    - compute_func (Callable): The compute function that the Block will execute. This function's signature is analyzed to configure inputs and outputs.
    - options_config_param (Dict[str, Any], optional): A dictionary containing additional configuration for the Block, such as custom input names, output names, and options. Defaults to None.
    - func_modificator (Callable, optional): A function that can be applied to the compute function to modify its behavior. Defaults to None.
    - func_modificator_config_params (Dict[str, Any], optional): A dictionary containing configuration parameters for the function modifier. Defaults to an empty dictionary.
    - func_modificator_params_visible (list, optional): A list of parameter names that should be visible in the function modifier's interface. Defaults to an empty list.
    - add_display_option (bool, optional): If True, adds a display option to the Block showing the compute function's docstring. Defaults to False.
    - category_name (str, optional): The category name under which the Block will be grouped. Defaults to "Uncategorized".
    - cache (bool, optional): Enables caching of the compute function's results if True. Defaults to False.
    - cache_visible (bool, optional): If True, enables a cache visibility option in the Block's interface. Defaults to True.

    Returns:
    - Block: A configured Block object ready for use within a larger application or framework.
    """

    if func_modificator is not None:
        compute_function = func_modificator(**func_modificator_config_params)(
            compute_func
        )
    else:
        compute_function = compute_func

    def load_options_config(config_file):
        """
        Loads a JSON configuration file for block options.

        This function attempts to load a JSON file located in the same directory as this script.
        It constructs the file path using the script's directory and the provided filename. If the file
        exists, it reads and parses the JSON content into a dictionary. If the file does not exist,
        it returns an empty dictionary.

        Parameters:
        - config_file (str): The name of the configuration file to load.

        Returns:
        - dict: A dictionary containing the loaded configuration. Returns an empty dictionary if the file does not exist or an error occurs during file reading or JSON parsing.
        """
        path = os.path.join(
            os.path.dirname(os.path.abspath(inspect.getfile(compute_func))), config_file
        )
        if os.path.exists(path):
            with open(path, "r", encoding="UTF-8") as f:
                return json.load(f)
        return {}

    # Get the function signature
    signature = inspect.signature(compute_function)

    # Load options config
    try:
        options_config = load_options_config(f"{compute_func.__name__}.json")
    except FileNotFoundError:
        options_config = {}
    if isinstance(options_config_param, dict):
        options_config.update(
            (k, options_config_param[k]) for k in options_config_param.keys()
        )

    category_name_ = options_config.get("category", category_name)
    if not isinstance(category_name_, str):
        category_name_ = "Uncategorized"

    cache_ = options_config.get("cache", cache)

    # Create a Block
    block_name = compute_func.__name__ + "_block"
    block_name = options_config.get("block_name", block_name)

    block = Block(name=block_name)
    block.set_state("category", category_name_)

    # Add input interfaces
    input_names_all = {}

    op_conf_in_n = options_config.get("input_names", {})
    for param_name, param in signature.parameters.items():
        if param.kind == param.VAR_POSITIONAL:
            var_pos_params = [k for k, v in op_conf_in_n.items() if param_name in k]
            if len(var_pos_params) > 0:
                input_names_all[param_name] = []
                for i, var_pos_param in enumerate(var_pos_params):
                    input_names_all[param_name].append(
                        op_conf_in_n.get(var_pos_param, var_pos_param)
                    )
            else:
                input_names_all[param_name] = op_conf_in_n.get(param_name, param_name)
        else:
            input_name = op_conf_in_n.get(param_name, param_name)
            input_names_all[param_name] = input_name

    options_names = options_config.get("options", {})
    input_names_current = {
        k: v for k, v in input_names_all.items() if k not in options_names
    }
    for input_name in input_names_current.values():
        if isinstance(input_name, str):
            block.add_input(name=input_name)
        elif isinstance(input_name, list):
            for i, name in enumerate(input_name):
                block.add_input(name=name)

    # Add output interfaces
    num_outputs = find_return_value_count(compute_function)
    output_names_default = [f"output_{i+1}" for i in range(num_outputs)]
    output_names = options_config.get("output_names", output_names_default)
    if len(output_names) > len(output_names_default):
        output_names = output_names[: len(output_names_default)]
    elif len(output_names) < len(output_names_default):
        output_names = output_names + output_names_default[len(output_names) :]

    for output_name in output_names:
        block.add_output(name=output_name)
    if cache_visible:
        block.add_option(name="Cache Block", type="checkbox", value=cache_)
    if add_display_option:
        docstring = inspect.getdoc(compute_func)
        if docstring is None:
            docstring = ""
        docstring = options_config.get("docstring", docstring)
        if len(docstring) > 0:
            block.add_option(
                name="display_line_1",
                type="display",
                value="-" * 9 + " Documentation " + "-" * 9,
            )
            block.add_option(name="display_option", type="display", value=docstring)
            block.add_option(name="display_line_2", type="display", value="-" * 38)

    # Add options to the Block
    add_options(block, compute_function, options_names)

    if len(func_modificator_params_visible) > 0:
        block.add_option(
            name="display_line_3", type="display", value="== Modificator parameters =="
        )
        func_modificator_options_names = options_config.get(
            "func_modificator_options",
            {k: {"name": k} for k in func_modificator_params_visible},
        )
        add_options(
            block,
            func_modificator,
            func_modificator_options_names,
        )
        block.add_option(name="display_line_4", type="display", value="=" * 19)

    # Define the compute function
    def compute_func_wrapper(self):
        """
        Wraps the compute function to integrate with the Block's input and output interfaces, including caching.

        This method retrieves input values from the Block's input interfaces and option values from the Block's options.
        It then executes the compute function with these values. If caching is enabled, the compute function's output
        is cached for future use. Finally, it sets the output values to the Block's output interfaces.

        Parameters:
        - self: An instance of the Block class.

        Returns:
        None. However, it updates the Block's state with the execution time and sets the output interface values.
        """
        # Get the value of the input interfaces
        list_var_args = list(
            itertools.chain(
                *[
                    param_name[1]
                    for param_name in input_names_current.items()
                    if isinstance(param_name[1], list)
                ]
            )
        )

        input_valuse_var_arg = [
            self.get_interface(param_var_arg) for param_var_arg in list_var_args
        ]

        input_values = {
            param_name[0]: self.get_interface(name=param_name[1])
            for param_name in input_names_current.items()
            if isinstance(param_name[1], str)
        }
        option_values = {
            opt_name[0]: self.get_option(name=opt_name[1].get("name", opt_name[0]))
            for opt_name in options_names.items()
        }

        if cache_visible:
            cache_ = self.get_option(name="Cache Block")
        else:
            cache_ = options_config.get("cache", cache)

        if len(func_modificator_params_visible) > 0 and func_modificator is not None:
            func_modificator_config_params_new = dict(func_modificator_config_params)
            func_modificator_option_values = {
                opt_name[0]: self.get_option(name=opt_name[1].get("name", opt_name[0]))
                for opt_name in func_modificator_options_names.items()
            }
            func_modificator_config_params_new.update(func_modificator_option_values)
            new_func_modificator_inst = func_modificator(
                **func_modificator_config_params_new
            )
            compute_function = new_func_modificator_inst(compute_func)
        elif len(func_modificator_params_visible) == 0 and func_modificator is not None:
            compute_function = func_modificator(**func_modificator_config_params)(
                compute_func
            )
        else:
            compute_function = compute_func

        memory = Memory(".cache", verbose=0)
        with st.spinner(f"Running {block_name}"):
            start_time = time.time_ns()
            # Call the provided compute function with input values
            compute_func_wrapper_ = (
                memory.cache(compute_function) if cache_ else compute_function
            )
            outputs = compute_func_wrapper_(
                *input_valuse_var_arg, **input_values, **option_values
            )
            exec_time = time.time_ns() - start_time
        self.set_state("exec_time", exec_time)

        # Set the values of the output interfaces
        if not isinstance(outputs, tuple):
            outputs = (outputs,)
        for output_value, output_name in zip(outputs, output_names):
            self.set_interface(name=output_name, value=output_value)

    # Add the compute function to the Block
    block.add_compute(compute_func_wrapper)
    return block


def find_return_value_count(func):
    """
    Analyzes a function to determine the number of values it returns.

    This function inspects the source code of the given function to count how many values are returned.
    It specifically looks for return statements and evaluates whether the return value is a tuple (multiple values),
    a single value, or None (no value).

    Parameters:
    - func (function): The function to analyze.

    Returns:
    - int: The number of values the function returns. Returns 0 if the function does not return anything or returns None.

    """

    import textwrap

    source_lines, _ = inspect.getsourcelines(
        func
    )  # Retrieve the source lines of the function.
    source_code = "".join(source_lines)  # Combine the lines into a single string.
    source_code = textwrap.dedent(source_code)
    tree = ast.parse(
        source_code
    )  # Parse the source code into an abstract syntax tree (AST).
    return_value_count = 0  # Initialize the return value count.
    for node_ in ast.walk(tree):  # Walk through the AST nodes.
        if (
            isinstance(node_, ast.FunctionDef) and func.__name__ == node_.name
        ):  # Find the function definition node.
            for node in ast.walk(
                node_
            ):  # Walk through the nodes within the function definition.
                if (
                    isinstance(node, ast.Return) and node in node_.body
                ):  # Identify return statements within the function body.
                    if isinstance(
                        node.value, ast.Tuple
                    ):  # If the return value is a tuple, count its elements.
                        return_value_count = len(node.value.elts)
                    elif isinstance(
                        node.value, ast.Constant
                    ):  # If the return value is a constant, determine if it's None or a single value.
                        if node.value.value is None:
                            return_value_count = 0
                        else:
                            return_value_count = 1
                    else:  # For other cases, consider it as a single return value.
                        return_value_count = 1
    return return_value_count  # Return the count of return values.


def add_options(block, compute_func, options_config):
    """
    Adds options to a Block object based on the configuration provided.

    This function iterates through each option defined in the options configuration,
    determines the option type (automatically if necessary), and adds the option to the Block
    with appropriate default values and additional keyword arguments.

    Parameters:
    - block (Block): The Block object to which the options will be added.
    - compute_func (function): The compute function associated with the Block. Used to infer
      option types if set to 'auto'.
    - options_config (dict): A dictionary where keys are option names and values are dictionaries
      containing option configurations such as type, default value, and other keyword arguments.

    Returns:
    None. The function directly modifies the Block object by adding options to it.
    """
    signature = inspect.signature(compute_func)
    param_names = list(signature.parameters.keys())
    for option_name, option_config_ in options_config.items():
        default_values = {
            "checkbox": False,
            "input": "",
            "integer": 0,
            "number": 0.0,
            "select": option_config_.get("items", [""])[0],
            "slider": 0.0,
            "display": "",
        }
        option_type = option_config_.get("type", "auto")
        option_kwargs = {
            k: v for k, v in option_config_.items() if k not in ("type", "name")
        }

        if option_type == "auto":
            option_type = infer_option_type(compute_func, option_name)

        if option_name in param_names:
            option_kwargs["value"] = option_kwargs.get(
                "value", default_values[option_type]
            )
            block.add_option(
                name=option_config_.get("name", option_name),
                type=option_type,
                **option_kwargs,
            )


def infer_option_type(func, param_name):
    """
    Infers the type of an option based on the parameter's annotation in a function.

    This function examines the annotation of a specified parameter in the given function
    and determines the most appropriate option type for a user interface. It supports
    distinguishing between numeric types (integers and floats), boolean types, and defaults
    to a generic input type for all other cases.

    Parameters:
    - func (function): The function whose parameter's type is to be inferred.
    - param_name (str): The name of the parameter for which the option type is inferred.

    Returns:
    - str: A string representing the inferred option type. Possible return values include
      "number" for floating-point types, "integer" for integer types, "checkbox" for boolean
      types, and "input" for all other types.

    """
    ints = (
        int,
        np.int_,
        np.intc,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.uint,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
        np.uintc,
        np.intp,
        np.uintp,
        np.byte,
        np.ubyte,
        np.short,
        np.ushort,
        np.longlong,
        np.ulonglong,
    )
    floats = (
        np.float_,
        float,
        np.float16,
        np.float32,
        np.float64,
        np.longfloat,
        np.longdouble,
        np.single,
        np.double,
        np.half,
    )
    signature = inspect.signature(func)
    param = signature.parameters[param_name]
    param_type = param.annotation if param.annotation != param.empty else None
    if any([param_type == type_ for type_ in floats]):
        return "number"
    elif any([param_type == type_ for type_ in ints]):
        return "integer"
    elif any([param_type == type_ for type_ in (bool, np.bool_)]):
        return "checkbox"
    else:
        return "input"


__all__ = [generate_block]
