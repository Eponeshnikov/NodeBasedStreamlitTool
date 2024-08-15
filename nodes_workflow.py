import streamlit as st
import numpy as np
import json
import os
from barfi import st_barfi, barfi_schemas
from collections import ChainMap
from blocks import blocks
import inspect
from typing import Any
import pickle
from st_pages import show_pages_from_config
from utils import format_nanoseconds, get_configs, between


# ─────────────────────────────────────
# ───── Block 1: Helper Functions ────
# ─────────────────────────────────────


def display_value(value: Any) -> None:
    """
    Display the value and its type using Streamlit's write method.

    This function is used to output a given value and the type of that value
    to the Streamlit app interface. It is useful for debugging or for providing
    users with information about the data being processed.

    Parameters
    ----------
    value : any
        The value to be displayed. This can be of any type.

    Returns
    -------
    None
        This function does not return any value. It outputs directly to the
        Streamlit interface.
    """
    st.write("Value:", value)  # Display the actual value
    # Display the type of the value
    st.write("Type of value:", str(type(value)))


def display_block_results(block_result: dict, expanded: bool = False) -> None:
    """
    Display the results of a block computation in the Streamlit app.

    This function takes the result of a block computation and displays various
    details about the block, including its name, status (e.g., computed or errored),
    execution time, inputs, outputs, options, and state. It uses Streamlit components
    to render the information in a user-friendly manner, with sections for inputs,
    outputs, options, and state information expandable by the user.

    Parameters
    ----------
    block_result : dict
        A dictionary containing the result of a block computation. It is expected
        to have a 'block' key with an object that has '_name', '_state', '_inputs',
        '_outputs', and '_options' attributes.
    expanded : bool, optional
        A boolean flag indicating whether the expandable sections (inputs, outputs,
        options, state) should be initially expanded or collapsed. Default is False,
        meaning sections will be initially collapsed.

    Returns
    -------
    None
        This function does not return any value. It directly renders content to the
        Streamlit interface.
    """
    block_dict = block_result["block"].__dict__

    st.header(f"Block: {block_dict['_name']}")

    state_info = block_dict["_state"]["info"]
    if state_info["status"] == "Errored":
        st.error(f"Error: {state_info['exception'][0]}")
        if "traceback" in state_info:
            st.code(state_info["traceback"])
    elif state_info["status"] == "Computed":
        exec_time = block_dict["_state"].get("exec_time", None)
        exec_time = format_nanoseconds(exec_time) if exec_time is not None else None
        st.success(f"Successfully computed in {exec_time}")

    with st.expander("**Inputs**", expanded=expanded):
        for input_name, input_data in block_dict["_inputs"].items():
            st.write(f"- {input_name}:")
            display_value(input_data["value"])
            st.divider()

    with st.expander("**Outputs**", expanded=expanded):
        for output_name, output_data in block_dict["_outputs"].items():
            st.write(f"- {output_name}:")
            display_value(output_data["value"])
            st.divider()

    with st.expander("**Options**", expanded=expanded):
        for option_name, option_data in block_dict["_options"].items():
            if option_name not in ["display_line1", "display_line2"]:
                st.write(f"- **{option_name}**")
                st.write(f"Type of option: {option_data['type']}")
                display_value(option_data["value"])
                st.divider()

    with st.expander("**State**", expanded=expanded):
        st.write(f"Status: {state_info['status']}")

    with st.expander("**Raw data**"):
        st.json(block_dict)


# ─────────────────────────────────────
# ── Block 2: Setup Parameters Widget ─
# ─────────────────────────────────────


def setup_params() -> dict:
    """
    Set up and display Streamlit widgets for parameter input based on the current configuration.

    This function initializes widgets for each parameter. It uses the configuration stored in the Streamlit session state
    to dynamically generate widgets. The function supports customizing widget labels and help texts
    through the "text_params" section of the configuration. It also handles special cases, such as
    setting a specific value for the "seed" parameter when the "random_seed" flag is enabled.

    The widgets are organized by parameter groups, with each group's widgets stored in a dictionary.
    The function returns a dictionary containing these groups, allowing for further manipulation or
    access to the widget values elsewhere in the application.

    Returns:
        dict: A dictionary where keys are parameter group names and values are dictionaries of
              Streamlit widgets created for each parameter in the group. Each widget dictionary
              contains keys corresponding to parameter names and values that are the actual
              Streamlit widgets.
    """
    # Initialize an empty dictionary to store the widgets
    widgets = {}

    # Get the current configuration from the session state
    config = st.session_state["all_params"][config_name]
    default_text = {
        k: ChainMap(
            {v: v for v in config["numerical_params"][k]},
            {"title": k},
        )
        for k in config["numerical_params"]
    }
    # Get the "pretty" text (user-friendly labels) for the numerical parameters
    pretty_text = config.get(  # Access the all_params dictionary for the current config
        "text_params", {}
    ).get(  # Get the "text_params" dictionary, or an empty dict if it doesn't exist
        "pretty_text",  # Get the "pretty_text" dictionary, or construct it from the numerical_params if it doesn't exist
        default_text,
    )

    # Get the help text for the numerical parameters
    help_text = config.get(  # Access the all_params dictionary for the current config
        "text_params", {}
    ).get(  # Get the "text_params" dictionary, or an empty dict if it doesn't exist
        "help_text", pretty_text
    )  # Get the "help_text" dictionary, or use pretty_text if it doesn't exist
    with tab:
        # Iterate over the numerical parameters
        for name, values in config["numerical_params"].items():
            # Display the title for the current parameter group
            st.title(
                pretty_text.get(name, default_text[name]).get(
                    "title", default_text[name]["title"]
                ),
                help=help_text.get(name, pretty_text.get(name, default_text[name])).get(
                    "title",
                    pretty_text.get(name, default_text[name]).get(
                        "title", default_text[name]["title"]
                    ),
                ),
            )

            # Initialize an empty dictionary to store the widgets for the current parameter group
            params_widgets = {}

            # Iterate over the individual parameters in the current group
            for key, value in values.items():
                # Check if the parameter is the "seed" parameter and if it needs to be set to a specific value
                if (
                    name == "generate_params"
                    and key == "seed"
                    and st.session_state["random_seed"][config_name]
                ):
                    value_ = st.session_state["all_params"][config_name][
                        "numerical_params"
                    ]["generate_params"]["seed"]
                else:
                    # Otherwise, get the default value from the initial parameters
                    value_ = st.session_state["all_params_init"][config_name][
                        "numerical_params"
                    ][name][key]
                # Extract the widget type
                widget_type = value_.get("type", "text_input")
                # Extract additional widget parameters
                widget_params = {k: v for k, v in value_.items() if k != "type"}

                # Get the widget function for the parameter type
                widget_func = getattr(st, widget_type, st.text_input)

                # Filter out any incompatible parameters
                signature = inspect.signature(widget_func)
                param_names = list(signature.parameters.keys())
                widget_params = {
                    k: v for k, v in widget_params.items() if k in param_names
                }
                # Enhanced widget setup based on parameter type
                if (
                    "step" in param_names
                    and st.session_state["multi_params"][config_name]
                ):
                    # Setup range widgets (from, to, step)
                    from_key = f"{config_name}.{name}.{key}.from"
                    to_key = f"{config_name}.{name}.{key}.to"
                    step_key = f"{config_name}.{name}.{key}.step"

                    from_value = widget_params.get("value", {})
                    if isinstance(from_value, dict):
                        from_value = from_value.get("from", "min")
                    widget_params_from = dict(widget_params)
                    widget_params_from.update({"value": from_value})

                    to_value = widget_params.get("value", {})
                    if isinstance(to_value, dict):
                        to_value = to_value.get("to", "min")
                    widget_params_to = dict(widget_params)
                    widget_params_to.update({"value": to_value})

                    step_value = widget_params.get("step", 0.0)
                    if isinstance(widget_params.get("value", {}), dict):
                        step_value = widget_params.get("value", {}).get(
                            "step", step_value
                        )

                    widget_params_step = dict(widget_params)
                    widget_params_step.update({"value": step_value})

                    caption_columms = st.columns(1)
                    multi_columms = st.columns(3)
                    with caption_columms[0]:
                        st.markdown(
                            pretty_text.get(name, default_text[name]).get(
                                key, default_text[name][key]
                            ),
                            help=help_text.get(
                                name, pretty_text.get(name, default_text[name])
                            ).get(
                                key,
                                pretty_text.get(name, default_text[name]).get(
                                    key, default_text[name][key]
                                ),
                            ),
                        )
                    with multi_columms[0]:
                        from_w = widget_func(
                            f"From:",
                            key=from_key,
                            **widget_params_from,
                        )
                    with multi_columms[1]:
                        to_w = widget_func(f"To:", key=to_key, **widget_params_to)
                    with multi_columms[2]:
                        step_w = widget_func(
                            f"Step:", key=step_key, **widget_params_step
                        )

                    params_widgets[key] = {"from": from_w, "to": to_w, "step": step_w}
                elif (
                    widget_type == "checkbox"
                    and st.session_state["multi_params"][config_name]
                ):
                    config1_key = f"{config_name}.{name}.{key}.config1"
                    config2_key = f"{config_name}.{name}.{key}.config2"

                    config1_value = widget_params.get("value", {})

                    if isinstance(config1_value, dict):
                        config1_value = config1_value.get("config1", True)
                    widget_params_config1 = dict(widget_params)
                    widget_params_config1.update({"value": config1_value})

                    config2_value = widget_params.get("value", {})
                    if isinstance(config2_value, dict):
                        config2_value = config2_value.get("config2", False)
                    widget_params_config2 = dict(widget_params)
                    widget_params_config2.update({"value": config2_value})

                    checkbox_columms = st.columns(2)
                    with checkbox_columms[0]:
                        st.markdown("Config 1:")
                        config1 = widget_func(
                            f"{pretty_text.get(name, default_text[name]).get(key, default_text[name][key])}:",
                            key=config1_key,
                            help=help_text.get(
                                name, pretty_text.get(name, default_text[name])
                            ).get(
                                key,
                                pretty_text.get(name, default_text[name]).get(
                                    key, default_text[name][key]
                                ),
                            ),
                            **widget_params_config1,
                        )
                    with checkbox_columms[1]:
                        st.markdown("Config 2:")
                        config2 = widget_func(
                            f"{pretty_text.get(name, default_text[name]).get(key, default_text[name][key])}:",
                            key=config2_key,
                            help=help_text.get(
                                name, pretty_text.get(name, default_text[name])
                            ).get(
                                key,
                                pretty_text.get(name, default_text[name]).get(
                                    key, default_text[name][key]
                                ),
                            ),
                            **widget_params_config2,
                        )
                    params_widgets[key] = {
                        "config1": config1,
                        "config2": config2,
                    }
                else:
                    # Default widget setup
                    widget_value = widget_params.get("value", "min")
                    if isinstance(widget_value, dict):
                        widget_value = widget_value.get("from", "min")
                    widget_params_default = dict(widget_params)
                    widget_params_default.update({"value": widget_value})
                    params_widgets[key] = widget_func(
                        f"{pretty_text.get(name, default_text[name]).get(key, default_text[name][key])}:",
                        key=f"{config_name}.{name}.{key}",
                        help=help_text.get(
                            name, pretty_text.get(name, default_text[name])
                        ).get(
                            key,
                            pretty_text.get(name, default_text[name]).get(
                                key, default_text[name][key]
                            ),
                        ),
                        **widget_params_default,
                    )

            # Store the widgets for the current parameter group in the main widgets dictionary
            widgets[name] = params_widgets

    # Return the dictionary containing all the widgets
    return widgets


# ─────────────────────────────────────
# ────── Block 3: Page Configuration ─
# ─────────────────────────────────────

st.set_page_config(
    page_title="Node-Based Workflow Application",
    page_icon=":test_tube:",
    layout="wide",
    initial_sidebar_state="expanded",
)

show_pages_from_config()

# ─────────────────────────────────────
# ── Block 4: Advanced Configuration ─
# ─────────────────────────────────────
advanced_sidebar = st.sidebar.expander("Advanced")
with advanced_sidebar:
    with open(
        st.text_input("Main Configuration", value="configs/main.json"),
        "r",
        encoding="UTF-8",
    ) as f:
        file_content = f.read()
        main_config = json.loads(file_content)

    root_dir_sidepanel = main_config.get("root_dir_sidepanel")
    show_example_block = st.checkbox(
        "Show Example Blocks", value=main_config.get("show_example_blocks", True)
    )

    # ─────────────────────────────────────
    # ─ Block 5: Check and Load Configs ──
    # ─────────────────────────────────────
    # Get all JSON files in the root_dir directory
    configs, modules_names = get_configs(root_dir_sidepanel)
    config_names = {
        modules_names[i] + os.path.basename(i).split(".")[0]: i for i in configs
    }


if len(configs) == 0:
    modules_warnings = ", ".join(
        [f'"{i.strip("/")}"' for i in modules_names.values() if len(i) > 0]
    )
    st.warning(f"No configurations found in {root_dir_sidepanel}")
    st.warning(f"No configurations found in modules {modules_warnings}")
else:

    # ─────────────────────────────────────
    # ──────── Select Configuration ──────
    # ─────────────────────────────────────

    if "keys" not in st.session_state:
        st.session_state["keys"] = {}

    # Allow user to select a configuration.

    # Create a list of configuration names (without .json extension) in st.session_state["configs"]
    if "configs_n" not in st.session_state:
        st.session_state["configs_n"] = {
            modules_names[i] + os.path.basename(i).split(".")[0]: 1 for i in configs
        }

    default_config_multiselect = None

    if len(list(st.session_state["configs_n"].keys())) != len(configs):
        try:
            default_config_multiselect = list(st.session_state["configs_in_run"])
        except Exception as e:
            default_config_multiselect = None

        for i in configs:
            if (
                modules_names[i] + os.path.basename(i).split(".")[0]
                not in st.session_state["configs_n"]
            ):
                st.session_state["configs_n"][
                    modules_names[i] + os.path.basename(i).split(".")[0]
                ] = 1

    with advanced_sidebar:
        add_child_config = st.selectbox(
            "Add configuration",
            [modules_names[i] + os.path.basename(i).split(".")[0] for i in configs],
        )
        add_child_config_button = st.button("Add configuration")

    if add_child_config_button:
        st.session_state["configs_n"][add_child_config] += 1

    configs_dict = dict()
    for config_ in configs:
        for i in range(
            st.session_state["configs_n"][
                modules_names[config_] + os.path.basename(config_).split(".")[0]
            ]
        ):
            configs_dict[
                f'{modules_names[config_] + os.path.basename(config_).split(".")[0]}-{i+1}'
            ] = config_
    st.session_state["configs"] = configs_dict

    # Display a selectbox in the sidebar to choose a configuration from st.session_state["configs"]
    configs_in_run = st.sidebar.multiselect(
        "Choose configurations",
        st.session_state["configs"].keys(),
        default=default_config_multiselect,
    )
    st.session_state["configs_in_run"] = configs_in_run
    if len(st.session_state["configs_in_run"]) > 0:

        # ─────────────────────────────────────
        # ──── Load Configuration Parameters ──
        # ─────────────────────────────────────
        # Load parameters for the selected configuration.

        # If "all_params" doesn't exist in st.session_state or the selected config is different from the previous one
        if "all_params" not in st.session_state:
            st.session_state["all_params"] = {}
            st.session_state["all_params_init"] = {}
        tabs = st.sidebar.tabs(st.session_state["configs_in_run"])
        for config_name, tab in zip(st.session_state["configs_in_run"], tabs):
            if config_name not in st.session_state["all_params"]:
                with open(
                    f'{st.session_state["configs"][config_name]}',
                    "r",
                    encoding="UTF-8",
                ) as f:
                    file_content = f.read()
                    st.session_state["all_params"][config_name] = json.loads(
                        file_content
                    )
                    st.session_state["all_params_init"][config_name] = json.loads(
                        file_content
                    )

            # ─────────────────────────────────────
            # ────── Initialize Random Seed ───────
            # ─────────────────────────────────────
            # Initialize or update random seed.

            # Initialize st.session_state["random_seed"] to True if it doesn't exist
            if "random_seed" not in st.session_state:
                st.session_state["random_seed"] = dict()
            if config_name not in st.session_state["random_seed"]:
                st.session_state["random_seed"][config_name] = True

            if "multi_params" not in st.session_state:
                st.session_state["multi_params"] = dict()
            if config_name not in st.session_state["multi_params"]:
                st.session_state["multi_params"][config_name] = False

            with tab:
                st.session_state["multi_params"][config_name] = st.checkbox(
                    "Multi Parameters",
                    value=False,
                    key=f"{config_name}.generate_params.multi_params",
                )

            # If st.session_state["random_seed"] is True
            if st.session_state["random_seed"][config_name]:
                # Set a random seed for the "generate_params" in the "numerical_params"
                st.session_state["all_params"][config_name]["numerical_params"][
                    "generate_params"
                ]["seed"]["value"] = np.random.randint(2**32 - 2, dtype=np.int64)

            # ─────────────────────────────────────
            # ───────── Setup Parameters ──────────
            # ─────────────────────────────────────
            # Setup parameters based on user inputs.

            # Call the setup_params function with st.session_state["all_params"] and update the "numerical_params"
            widgets_vals = setup_params()
            for key, val_n in widgets_vals.items():
                for val in val_n:
                    st.session_state["all_params"][config_name]["numerical_params"][
                        key
                    ][val]["value"] = val_n[val]

            # ─────────────────────────────────────
            # ──────── Toggle Random Seed ────────
            # ─────────────────────────────────────
            # Toggle the random seed option.

            # Display a checkbox in the sidebar to toggle "Random seed" with the initial value set to True
            with tab:
                st.session_state["random_seed"][config_name] = st.checkbox(
                    "Random seed",
                    value=True,
                    key=f"{config_name}.generate_params.random_seed",
                )
                # ─────────────────────────────────────
                # ────── Block for Saving Config ──────
                # ─────────────────────────────────────
                st.divider()
                st.write("## Save Configuration")
                # Input for specifying the file path where the configuration should be saved
                save_path = st.text_input(
                    "Save Config Path",
                    value=f"configs/sidepanel/{config_name}.json",
                    key=f"{config_name}.save_config.save_path",
                )
                slider_params_save = dict()
                slider_params_save[config_name] = {
                    "numerical_params": {},
                    "text_params": {},
                }
                for key, val_n in st.session_state["all_params"][config_name][
                    "numerical_params"
                ].items():
                    slider_params_save[config_name]["numerical_params"][key] = dict()
                    for val in val_n:
                        slider_params_save[config_name]["numerical_params"][key][
                            val
                        ] = val_n[val]
                slider_params_save[config_name]["text_params"] = st.session_state[
                    "all_params"
                ][config_name]["text_params"]
                # Button to save the configuration
                if st.button("Save Config", key=f"{config_name}.save_config.button"):
                    try:
                        # Convert the configuration dictionary to a JSON string
                        config_json = json.dumps(
                            slider_params_save[config_name], indent=4
                        )
                        # Write the JSON string to the specified file path
                        with open(save_path, "w", encoding="UTF-8") as f:
                            f.write(config_json)
                        st.success(f"Configuration saved to {save_path}")
                    except Exception as e:
                        st.error(f"Failed to save configuration: {e}")

        # ─────────────────────────────────────
        # ──────── Display Parameters ────────
        # ─────────────────────────────────────
        # Display the parameters for the selected configuration.

        # Output the parameters
        with st.expander("Slider Panel Parameters"):
            slider_params = dict()
            for config_name in st.session_state["configs_in_run"]:
                slider_params[config_name] = dict()
                for key, val_n in st.session_state["all_params"][config_name][
                    "numerical_params"
                ].items():
                    slider_params[config_name][key] = dict()
                    for val in val_n:
                        slider_params[config_name][key][val] = val_n[val]["value"]
                st.session_state["slider_params"] = slider_params
            st.json(slider_params)
    else:
        st.sidebar.warning("No configurations chosen")

columns = st.columns([25, 75])
with columns[0]:
    barfi_schema_name = st.selectbox("Select a saved schema to load:", barfi_schemas())
    if "barfi" not in st.session_state["keys"]:
        st.session_state["keys"]["barfi"] = True
    if st.button("Update Nodes", use_container_width=True):
        st.session_state["keys"]["barfi"] = not st.session_state["keys"]["barfi"]

with columns[1]:
    files = st.file_uploader("Add schemas from files", accept_multiple_files=True)
    if len(files) > 0:
        try:
            with open("schemas.barfi", "rb") as handle_read:
                schemas = pickle.load(handle_read)
        except FileNotFoundError:
            print("File not found")
            schemas = {}
        for file in files:
            new_schemas = pickle.load(file)
            schemas.update(new_schemas)
        with open("schemas.barfi", "wb") as handle_write:
            pickle.dump(schemas, handle_write, protocol=pickle.HIGHEST_PROTOCOL)


# ─────────────────────────────────────
# ───── Block 7: Categorize Blocks ────
# ─────────────────────────────────────
# Categorize blocks for display.

category_blocks = {
    block._state.get("category", "Uncategorized"): [] for block in blocks
}

if not show_example_block:
    category_blocks.pop("Examples")
for block in blocks:
    category = block._state.get("category", "Uncategorized")
    if category in category_blocks:
        category_blocks[category].append(block)

# ─────────────────────────────────────
# ───── Block 8: Display Blocks ───────
# ─────────────────────────────────────
# Display categorized blocks.

number_of_blocks = [len(category_blocks[i]) for i in category_blocks.keys()]
if np.sum(number_of_blocks) == 0:
    st.warning("No blocks found")

key_barfi = (
    None
    if st.session_state["keys"]["barfi"]
    else f"barfi_state_{st.session_state['keys']['barfi']}"
)

barfi_res = st_barfi(
    category_blocks, compute_engine=True, load_schema=barfi_schema_name, key=key_barfi
)
if st.session_state["keys"]["barfi"] == False:
    st.session_state["keys"]["barfi"] = True
    st.rerun()

with st.popover("Results", use_container_width=True):
    if len(barfi_res.keys()) > 0:
        tabs = st.tabs(barfi_res.keys())
        expand = st.button("Expand All Results")
        for tab, block in zip(tabs, barfi_res.keys()):
            with tab:
                display_block_results(barfi_res[block], expand)
