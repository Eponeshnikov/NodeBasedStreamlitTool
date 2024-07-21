from gen_block import generate_block
import streamlit as st
import itertools
import numpy as np


def slider_params(config_str=None, params_str=None):
    if config_str is None or len(config_str) == 0:
        output = st.session_state["slider_params"]
    else:
        if params_str is None or len(params_str) == 0:
            output = st.session_state["slider_params"][config_str]
        else:
            output = st.session_state["slider_params"][config_str][params_str]
    return output


def storage(data, id_str, overwrite, unique):
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
    def get_values(param):
        if "from" in param and "to" in param and "step" in param:
            return np.arange(
                param["from"], param["to"] + param["step"] / 2, param["step"]
            ).tolist()
        elif isinstance(param, dict):
            return list(set(param.values()))
        else:
            return [param]

    def extract_param_combinations(d):
        keys, values = zip(*[(k, get_values(v)) for k, v in d.items()])
        return [dict(zip(keys, combo)) for combo in itertools.product(*values)]

    # Generate combinations for each section
    section_combinations = {
        category: extract_param_combinations(category_params)
        for category, category_params in params.items()
    }

    # Generate the cross product of all section combinations
    all_combinations = [
        dict(zip(section_combinations.keys(), p))
        for p in itertools.product(*section_combinations.values())
    ]

    return all_combinations


option_config_slider_params = {
    "block_name": "Slider Panel Parameters",
    "docstring": "This block allows you to use the parameters of the slider panel as an output in dictionary format. Put in 'Config' field the name of the configuration you want to use.",
    "output_names": ["Slider Parameters Dictionary"],
    "options": {
        "config_str": {
            "type": "input",
            "name": "Config",
        },
        "params_str": {"type": "input", "name": "Config's parameter"},
    },
}

option_config_stored_params = {
    "options": {
        "id_str": {
            "type": "input",
        },
        "overwrite": {
            "type": "checkbox",
            "value": False,
        },
        "unique": {
            "type": "checkbox",
            "value": False,
        },
    }
}

option_config_generate_combinations = {
    "block_name": "Generate Combinations Panel",
    "docstring": "This block generates combinations of input parameters for further analysis or processing.",
    "output_names": ["Combinations list of dicts"],
    "input_names": {
      "params": "Input Dictionary",
    },
}

slider_block = generate_block(
    slider_params,
    option_config_slider_params,
    category_name="Input",
    cache=False,
    add_display_option=False,
)

storage_block = generate_block(
    storage, option_config_stored_params, category_name="Output", cache=False
)

generate_combinations_block = generate_block(
    generate_combinations,
    option_config_generate_combinations,
    add_display_option=True,
    cache=False,
)
