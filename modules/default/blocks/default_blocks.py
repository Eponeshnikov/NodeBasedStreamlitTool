from gen_block import generate_block
import streamlit as st
import itertools
import numpy as np
import copy
from typing import Iterable, Any, List, Dict, Union
from flatten_json import flatten

##############################
########Functions#############
##############################


def slider_params(config_str=None, params_str=None, param=None, expand_dim=False):
    """
    This function retrieves slider parameters from the session state based on the provided configuration and parameter strings.

    Parameters
    ----------
    config_str (str, optional) :
        The name of the configuration for which to retrieve parameters. If not provided or empty, the function returns all slider parameters.
    params_str (str, optional) :
        The name of the specific parameter within the configuration to retrieve. If not provided or empty, the function returns all parameters for the specified configuration.
    param (str, optional) :
        The name of the specific parameter within the configuration to retrieve. If not provided or empty, the function returns all parameters for the specified configuration.
    expand_dim (bool, optional) :
        If True, the function returns the output as a list containing the original output. If False (or not provided), the function returns the output as is.

    Returns
    ----------
    dict or any:
        If both `config_str` and `params_str` are provided, the function returns the value of the specified parameter. If only `config_str` is provided, the function returns a dictionary of all parameters for the specified configuration. If neither `config_str` nor `params_str` are provided, the function returns a dictionary of all slider parameters.
    """
    if config_str is None or len(config_str) == 0:
        output = st.session_state["slider_params"]
    else:
        if params_str is None or len(params_str) == 0:
            output = st.session_state["slider_params"][config_str]
        else:
            if param is None or len(param) == 0:
                output = st.session_state["slider_params"][config_str][params_str]
            else:
                output = st.session_state["slider_params"][config_str][params_str][
                    param
                ]
    if expand_dim:
        output = [output]
    return output


def storage(data, id_str, overwrite, unique):
    """
    This function stores the provided data in the session state under a unique identifier.
    If no identifier is provided, the function generates a unique identifier based on the data's class name and object id.
    If an identifier is provided, the function checks for existing data with the same identifier and either overwrites it or generates a new identifier.

    Parameters
    ----------
    - data (any): The data to be stored.
    - id_str (str): The identifier for the data. If not provided, the function generates a unique identifier.
    - overwrite (bool): A flag indicating whether to overwrite existing data with the same identifier.
    - unique (bool): A flag indicating whether to generate a unique identifier if no identifier is provided.

    Returns
    ----------
    None
    """
    if "storage" not in st.session_state:
        st.session_state["storage"] = dict()
    if data.__class__.__name__ not in st.session_state["storage"]:
        st.session_state["storage"][data.__class__.__name__] = dict()
    if len(id_str) > 0:
        init_name = id_str
    else:
        if unique:
            init_name = f"{data.__class__.__name__}_{id(data)}"
        else:
            init_name = f"{data.__class__.__name__}"
    keys_ids_str = [
        i
        for i in st.session_state["storage"][data.__class__.__name__].keys()
        if i.startswith(init_name)
    ]
    if len(keys_ids_str) > 0 and not overwrite:
        num = max([int(i.split("-")[-1]) for i in keys_ids_str]) + 1
        data_name = f"{init_name}-{num}"
    else:
        data_name = f"{init_name}-1"

    st.session_state["storage"][data.__class__.__name__][data_name] = data


def generate_combinations(params):
    """
    This function generates combinations of input parameters for further analysis or processing.

    Parameters
    ----------
    - params (dict): A dictionary containing the parameters to be combined. The dictionary can have nested dictionaries as values.
        Each parameter can be either a single value or a dictionary with 'from', 'to', and 'step' keys to define a range of values.
        If a parameter is a dictionary, its values will be used as the possible combinations.

    Returns
    ----------
    - list: A list of dictionaries, where each dictionary represents a combination of the input parameters.
        If the input parameters have nested dictionaries, the generated combinations will also have nested dictionaries.
    """

    def replace_item(obj, key, replace_value):
        # Recursively replace the value of a key in a nested dictionary
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = replace_item(v, key, replace_value)
        if key in obj:
            obj[key] = replace_value
        return obj

    def get_values(param):
        # Get the values for a parameter, either from a range or a dictionary
        if "from" in param and "to" in param and "step" in param:
            return np.arange(
                param["from"], param["to"] + param["step"] / 2, param["step"]
            ).tolist()
        elif isinstance(param, dict):
            return list(set(param.values()))
        else:
            return [param]

    def extract_param_combinations(d):
        # Extract combinations of parameters from a dictionary
        keys, values = zip(*[(k, get_values(v)) for k, v in d.items()])
        return [dict(zip(keys, combo)) for combo in itertools.product(*values)]

    def depth(x):
        # Calculate the depth of a nested dictionary
        if type(x) is dict and x:
            return 1 + max(depth(x[a]) for a in x)
        if type(x) is list and x:
            return 1 + max(depth(a) for a in x)
        return 0

    # print('Depth', depth(params), params)
    params_ = params if depth(params) == 3 else {"tmp": params}
    # Generate combinations for each section
    section_combinations = {
        category: extract_param_combinations(category_params)
        for category, category_params in params_.items()
    }

    # Generate the cross product of all section combinations
    all_combinations_ = [
        copy.deepcopy(dict(zip(section_combinations.keys(), p)))
        for p in itertools.product(*section_combinations.values())
    ]
    all_combinations = copy.deepcopy(all_combinations_)
    if st.session_state["random_seed"]:
        seeds = np.random.randint(2**32 - 2, size=len(all_combinations), dtype=np.int64)
        for i, comb in enumerate(all_combinations):
            replace_item(comb, "seed", seeds[i])
    all_combinations = (
        all_combinations
        if depth(params) == 3
        else [all_combination["tmp"] for all_combination in all_combinations]
    )
    return all_combinations


def flatten_params_multi(data: List[tuple[Dict, Any]]) -> List[tuple[Dict, Any]]:
    """
    This function takes a list of tuples, where each tuple contains a dictionary and an additional value.
    It uses the flatten_json library to flatten the dictionaries in each tuple.

    Parameters
    ----------
    - data (List[tuple[Dict, Any]]): A list of tuples. Each tuple contains a dictionary (first element) and an additional value (second element).

    Returns
    ----------
    - List[tuple[Dict, Any]]: A list of tuples. Each tuple contains a flattened dictionary (first element) and the corresponding additional value (second element).
    """

    def flat_dict_in_tuple(t):
        return (flatten(t[0]), t[1])

    result = [flat_dict_in_tuple(i) for i in data]
    return result


def filter_dict(
    data: Union[Dict, Any],
    value: Any,
    filter_type: str = "contains",
    where: str = "key",
) -> Union[Dict, Any]:
    """
    This function filters dictionaries based on a specified value and filter type.

    Parameters
    ----------
    - data (Union[Dict, Any]): The input data, which can be a dictionary or a list of dictionaries.
    - value (Any): The value to filter by.
    - filter_type (str): The type of filter to apply. It can be one of the following:
        - "contains": Filters dictionaries where the value contains the specified value.
        - "not_contains": Filters dictionaries where the value does not contain the specified value.
        - "exact": Filters dictionaries where the value is exactly the specified value.
    - where (str): The location to filter. It can be one of the following:
        - "key": Filters dictionaries based on the keys.
        - "value": Filters dictionaries based on the values.
        - "both": Filters dictionaries based on both keys and values.

    Returns:
    - Union[Dict, Any]: The filtered data. If the original data was a dictionary, the function returns a dictionary.
        If the original data was a list, the function returns a list of dictionaries.
    """
    
    def filter_value(item: str) -> bool:
        item_str = str(item).lower()
        value_str = str(value).lower()
        if filter_type == "contains":
            return value_str in item_str
        elif filter_type == "not_contains":
            return value_str not in item_str
        elif filter_type == "exact":
            return value_str == item_str
        return False

    def reconstruct(flat_dict: Dict[str, Any]) -> Any:
        result: Dict[str, Any] = {}
        for key, value in flat_dict.items():
            parts = key.split("___")
            d = result
            for part in parts[:-1]:
                if part.isdigit() and isinstance(d, list):
                    idx = int(part)
                    while len(d) <= idx:
                        d.append({})
                    d = d[idx]
                elif isinstance(d, dict):
                    if part not in d:
                        d[part] = {}
                    d = d[part]
                else:
                    # If we encounter an unexpected structure, we create a new dict
                    new_d = {}
                    d.append(new_d)
                    d = new_d
            if parts[-1].isdigit() and isinstance(d, list):
                idx = int(parts[-1])
                while len(d) <= idx:
                    d.append(None)
                d[idx] = value
            else:
                d[parts[-1]] = value
        return result

    if isinstance(data, dict):
        data_ = [data]
    elif isinstance(data, list):
        data_ = data
    else:
        raise ValueError("Input data must be a dictionary or a list")
    return_value = []
    filter_func = all if filter_type == 'not_contains' else any
    for _data_ in data_:
        flattened = flatten(_data_, separator="___")
        filtered = {}
        for k, v in flattened.items():
            key_parts = k.split("___")
            if (
                where in ["key", "both"]
                and filter_func(list(filter_value(part) for part in key_parts))
            ) or (where in ["value", "both"] and filter_value(v)):
                filtered[k] = v
        reconstructed = reconstruct(filtered)
        return_value.append(reconstructed)

    # If the original data was not a dict, we return the first (and only) value
    return_value = return_value[0] if isinstance(data, dict) else return_value
    return return_value


##########################
########Configs###########
##########################

option_config_filter_list_dict = {
    "block_name": "Filter (List of) Dictionaries",
    "docstring": "Filter Dictionaries by value",
    "output_names": ["Filtered"],
    "input_names": {
        "data": "Data",
    },
    "options": {
        "value": {"type": "input", "name": "Value of filter"},
        "filter_type": {
            "type": "select",
            "name": "Filter Type",
            "items": ["contains", "not_contains", "exact"],
        },
        "where": {
            "type": "select",
            "name": "Where filter",
            "items": ["key", "value", "both"],
        },
    },
}

option_config_slider_params = {
    "block_name": "Slider Panel Parameters",
    "docstring": "Retrieves slider parameters by (sub)sections",
    "output_names": ["Slider Parameters Dictionary"],
    "options": {
        "config_str": {
            "type": "input",
            "name": "Config (Tab)",
        },
        "params_str": {"type": "input", "name": "Section of Tab"},
        "param": {"type": "input", "name": "Parameter"},
        "expand_dim": {"type": "checkbox", "name": "Wrap output to list"},
    },
}

option_config_stored_params = {
    "block_name": "Data Storage",
    "docstring": "This block stores data in the session state.",
    "output_names": [],  # No output for this block
    "input_names": {
        "data": "Data",
    },
    "options": {
        "id_str": {
            "type": "input",
            "name": "Identifier",
            "default": "",  # Optional input, default value is an empty string
        },
        "overwrite": {
            "type": "checkbox",
            "name": "Overwrite existing data",
            "default": False,  # Optional checkbox, default value is False
        },
        "unique": {
            "type": "checkbox",
            "name": "Generate unique identifier",
            "default": False,  # Optional checkbox, default value is False
        },
    },
}

option_config_generate_combinations = {
    "block_name": "Generate Combinations Panel",
    "docstring": "This block generates combinations of input parameters for further analysis or processing.",
    "output_names": ["Combinations list of dicts"],
    "input_names": {
        "params": "Input Dictionary",
    },
}

option_config_flatten_params_multi = {
    "block_name": "Flatten Parameters Multi",
    "docstring": "This block flattens a list of tuples, where each tuple contains a dictionary and an additional value. It uses the flatten_json library to flatten the dictionaries.",
    "output_names": ["Flattened Parameters List"],
    "input_names": {
        "data": "Input List of Tuples",
    },
}

#########################
########Blocks###########
#########################
filter_dict_block = generate_block(
    filter_dict,
    option_config_filter_list_dict,
    add_display_option=True,
    cache=False,
    category_name="Utility",
)

slider_block = generate_block(
    slider_params,
    option_config_slider_params,
    category_name="Input",
    cache=False,
    cache_visible=False,
)

storage_block = generate_block(
    storage,
    option_config_stored_params,
    category_name="Output",
    cache=False,
    cache_visible=False,
)

generate_combinations_block = generate_block(
    generate_combinations,
    option_config_generate_combinations,
    add_display_option=True,
    cache=False,
    category_name="Utility",
)

flatten_params_multi_block = generate_block(
    flatten_params_multi,
    option_config_flatten_params_multi,
    add_display_option=True,
    cache=False,
    category_name="Utility",
)
