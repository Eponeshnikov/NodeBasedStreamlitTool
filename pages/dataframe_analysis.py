import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer
from ydata_profiling import ProfileReport
import streamlit.components.v1 as components
import hashlib
import os
import json
import glob
from st_pages import show_pages_from_config

# Configure the Streamlit page
st.set_page_config(
    page_title="Dataframe Analysis",
    page_icon=":test_tube:",
    layout="wide",
    initial_sidebar_state="expanded",
)

show_pages_from_config()

advanced_sidebar = st.sidebar.expander("Advanced")
with advanced_sidebar:
    with open(
        st.text_input("Main Configuration", value="configs/main.json"),
        "r",
        encoding="UTF-8",
    ) as f:
        file_content = f.read()
        main_config = json.loads(file_content)

    root_dir_dataframe_hash = main_config.get("root_dir_dataframe_hash")
    root_dir_dataframe_custom = main_config.get("root_dir_dataframe_custom")
    configs = glob.glob("*.json", root_dir=root_dir_dataframe_custom)

# Sidebar for DataFrame selection
st.sidebar.title("DataFrame Selector")

# Get DataFrames from session state
if "storage" not in st.session_state:
    st.session_state["storage"] = dict()

dataframes = {
    key: value
    for key, value in st.session_state["storage"].get(pd.DataFrame.__name__, {}).items()
    if isinstance(value, pd.DataFrame)
}

# Dropdown to select DataFrame
selected_df_key = st.sidebar.selectbox(
    "Select DataFrame", options=list(dataframes.keys())
)

# Option to upload a new DataFrame
uploaded_file = st.sidebar.file_uploader("Or upload a new CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    if selected_df_key:
        df = dataframes[selected_df_key]
    else:
        st.sidebar.warning("No DataFrame selected or uploaded")
        st.stop()

# Sidebar for customizing StreamlitRenderer
st.sidebar.title("Renderer Customization")
use_custom_config = st.sidebar.checkbox("Use Custom Config", False)
custom_config = st.sidebar.selectbox(
    "Use custom configuration", configs, disabled=not use_custom_config
)
# spec_io_mode = st.sidebar.selectbox("Spec IO Mode", options=["rw", "r"], index=0)


# Function to generate hash from DataFrame
def generate_hash(data):
    data_string = data.__str__()
    hasher = hashlib.md5()
    hasher.update(data_string.encode("utf-8"))  # Encode the string to bytes
    return hasher.hexdigest()


# Function to load or create configuration
def load_or_create_config(data, use_custom_config_):
    if use_custom_config_:
        try:
            config_dir = root_dir_dataframe_custom
            config_path = os.path.join(config_dir, f"{custom_config}")
        except Exception as e:
            st.sidebar.warning("Could not load configuration, use default")
            config_dir = root_dir_dataframe_hash  # Directory to store config files
            os.makedirs(config_dir, exist_ok=True)
            hash_name = generate_hash(data)
            config_path = os.path.join(config_dir, f"{hash_name}.json")
    else:
        config_dir = root_dir_dataframe_hash  # Directory to store config files
        os.makedirs(config_dir, exist_ok=True)
        hash_name = generate_hash(data)
        config_path = os.path.join(config_dir, f"{hash_name}.json")

    if not os.path.exists(config_path):
        spec = []
        with open(config_path, "w") as f:
            json.dump(spec, f)
    return config_path


@st.cache_resource
def get_renderer(data, use_custom_config_):
    spec_config = load_or_create_config(data, use_custom_config_)
    return StreamlitRenderer(data, spec=spec_config, spec_io_mode="rw")


st.header("DataFrame")
with st.expander("DataFrame"):
    df = st.data_editor(df, use_container_width=True)

st.header("Profiling Report")
profile_columns = st.columns([0.3, 0.7])

profile_button = profile_columns[0].button(
    "Generate Profiling Report", use_container_width=True
)
with profile_columns[1].popover(
    "Profiling Report Parameters", use_container_width=True
):
    columns = st.columns(5)
    dark_mode = columns[0].checkbox(
        "Dark Mode", value=True, help="Enable dark mode for profiling report"
    )
    explorative = columns[1].checkbox(
        "Explorative", value=True, help="Explorative mode"
    )
    orange_mode = columns[2].checkbox(
        "Orange Mode", value=True, help="Enable Orange mode for profiling report"
    )
    sensitive = columns[3].checkbox(
        "Sensitive",
        value=False,
        help="Hides the values for categorical and text variables for report privacy",
    )
    tsmode = columns[4].checkbox(
        "Time-series analysis",
        value=False,
        help="Activates time-series analysis for all the numerical variables from the dataset",
    )

if profile_button:
    with st.expander("Profiling Report"):
        with st.spinner("Generating Profile Report..."):
            profile = ProfileReport(
                df,
                title="Profiling Report",
                dark_mode=dark_mode,
                explorative=explorative,
                orange_mode=orange_mode,
                sensitive=sensitive,
                tsmode=tsmode,
            ).to_html()
        components.html(profile, height=800, scrolling=True)

st.divider()
renderer = get_renderer(df, use_custom_config_=use_custom_config)


st.header("Graphic Walker")
renderer.explorer()
