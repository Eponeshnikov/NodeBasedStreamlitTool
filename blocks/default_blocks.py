from gen_block import generate_block
import streamlit as st


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
