import streamlit as st
from streamlit_ace import st_ace, THEMES, KEYBINDINGS
import json
import glob
import os
import hashlib
from st_pages import show_pages_from_config
from utils import get_configs

if "storage" not in st.session_state:
    st.session_state["storage"] = dict()

st.set_page_config(
    page_title="Python Editor",
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
        python_editor_params = main_config.get("python_editor", {})
        root_dir_py_scripts = main_config.get("root_dir_py_scripts", "scripts")
        scripts, modules_names = get_configs(root_dir_py_scripts, ext='py', between_str=["modules/", "/scripts"])
        script_names = {modules_names[i] + os.path.basename(i): i for i in scripts}
        
        


editor, app, storage_tab = st.tabs(["Editor", "App", "Storage :briefcase:"])
python_editor_params_panel = st.sidebar.expander(
    "**Python Editor Parameters**", expanded=False
)
uploaded_script = st.sidebar.file_uploader("Upload **.py** script", type="py")
folder_script = st.sidebar.selectbox(
    "Choose existing **.py** file", list(script_names.keys()), index=list(script_names.keys()).index("empty.py")
)
if uploaded_script:
    script_in_use = uploaded_script.getvalue().decode("utf-8")
else:
    with open(f"{script_names[folder_script]}", "r", encoding="UTF-8") as f:
        script_in_use = f.read()

with editor:
    code = st_ace(
        value=script_in_use,
        language="python",
        placeholder="# Write your code here \n# You can use storage variable to access objects in it",
        theme=python_editor_params_panel.selectbox(
            "Theme",
            options=THEMES,
            index=THEMES.index(python_editor_params.get("theme", "chaos")),
        ),
        keybinding=python_editor_params_panel.selectbox(
            "Keybinding mode",
            options=KEYBINDINGS,
            index=KEYBINDINGS.index(python_editor_params.get("keybinding", "vscode")),
        ),
        font_size=python_editor_params_panel.slider(
            "Font size", 5, 24, python_editor_params.get("font_size", 14)
        ),
        tab_size=python_editor_params_panel.slider(
            "Tab size", 1, 8, python_editor_params.get("tab_size", 4)
        ),
        wrap=python_editor_params_panel.checkbox(
            "Wrap lines", value=python_editor_params.get("wrap", True)
        ),
        show_gutter=python_editor_params_panel.checkbox(
            "Show Gutter", value=python_editor_params.get("show_gutter", True)
        ),
        show_print_margin=python_editor_params_panel.checkbox(
            "Show print margin",
            value=python_editor_params.get("show_print_margin", True),
        ),
        auto_update=python_editor_params_panel.checkbox(
            "Auto Update", value=python_editor_params.get("auto_update", True)
        ),
        readonly=python_editor_params_panel.checkbox(
            "Readonly", value=python_editor_params.get("readonly", False)
        ),
        key=f"ace-editor-{hashlib.sha256(script_in_use.encode('utf-8'))}",
    )
    st.write("Hit `CTRL+ENTER` to refresh")
    st.write("*Remember to save your code separately!*")

save_path = st.sidebar.text_input(
    "Save Config Path",
    value=f"scripts/",
    key=f"py_save_scripts.save_path",
)

enabled_save = save_path.endswith(".py")

if st.sidebar.button(
    "Save Script",
    key=f"py_save_config.button",
    disabled=not enabled_save,
    help="Name should be ends with **.py**",
):
    try:
        with open(save_path, "w", encoding="UTF-8") as f:
            f.write(code)
        st.sidebar.success(f"Script saved to {save_path}")
    except Exception as e:
        st.sidebar.error(f"Failed to save script: {e}")

with app:
    storage = dict(st.session_state["storage"])
    exec(code)

with storage_tab:
    st.write(st.session_state["storage"])
