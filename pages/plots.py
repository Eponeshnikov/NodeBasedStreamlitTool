import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from plotly.graph_objects import Figure as Figure_plotly
from PIL import Image
import os
import plotly.tools as tls
import mpld3
import streamlit.components.v1 as components
from st_pages import show_pages_from_config


def save_fig(fig, name, category):
    if category not in st.session_state["storage"][Figure.__name__]:
        st.session_state["storage"][Figure.__name__][category] = dict()
    st.session_state["storage"][Figure.__name__][category][name] = fig


# Function to load images and convert them to matplotlib figures
def image_to_figure(image_file):
    image = Image.open(image_file)
    fig, ax = plt.subplots()
    ax.imshow(image)
    ax.axis("off")
    return fig


def mpl2plotly(fig_):
    plotly_fig = tls.mpl_to_plotly(fig_)
    return plotly_fig


# Function to load plots from a folder with progress bar
def load_plots_from_folder(folder_path):
    files = os.listdir(folder_path)
    total_files = len(files)
    progress_bar = st.progress(0)

    for index, filename in enumerate(files):
        if filename not in st.session_state["storage"]["folder"][Figure.__name__]:
            file_path = os.path.join(folder_path, filename)
            try:
                fig = image_to_figure(file_path)
                save_fig(fig, filename, "folder")
            except Exception as e:
                st.warning(f"Could not load file {filename}: {e}")
            progress_bar.progress((index + 1) / total_files, text=filename)
    progress_bar.progress((index + 1) / total_files, text="Completed")
    st.success("Loading complete!")


# Function to display figures in a dynamically scaled grid
def display_figures_in_grid(figures, columns=3):
    keys = list(figures.keys())
    cols = st.columns(columns)

    for idx, key in enumerate(keys):
        col = cols[idx % columns]
        with col:
            st.subheader(key)
            if isinstance(figures[key], Figure):
                matplotlib_plot = figures[key]
                try:
                    plotly_plot = mpl2plotly(figures[key])
                except Exception as e:
                    plotly_plot = None
            elif isinstance(figures[key], Figure_plotly):
                plotly_plot = figures[key]
                matplotlib_plot = None
            if st.session_state["display_mode"] == "matplotlib":
                if matplotlib_plot is not None:
                    st.pyplot(matplotlib_plot)
                else:
                    st.plotly_chart(plotly_plot, use_container_width=True)

            elif (
                st.session_state["display_mode"] == "plotly"
                and key in selected_storage_figs_key
            ):
                if plotly_plot is not None:
                    st.plotly_chart(plotly_plot, use_container_width=True)
                else:
                    st.pyplot(matplotlib_plot)

            elif st.session_state["display_mode"] == "interactive_matplotlib":
                if matplotlib_plot is not None:
                    fig_html = mpld3.fig_to_html(matplotlib_plot)
                    components.html(fig_html, height=500)
                else:
                    st.plotly_chart(plotly_plot, use_container_width=True)


# Initialize session state for storage and display mode
if "storage" not in st.session_state:
    st.session_state["storage"] = dict()

if "display_mode" not in st.session_state:
    st.session_state["display_mode"] = "matplotlib"

if Figure.__name__ not in st.session_state["storage"]:
    st.session_state["storage"][Figure.__name__] = dict()

st.set_page_config(
    page_title="Plots",
    page_icon=":test_tube:",
    layout="wide",
    initial_sidebar_state="expanded",
)

show_pages_from_config()

# Load plots from a specified folder
folder_path = st.sidebar.text_input("Enter folder path to load plots")
if folder_path:
    load_plots_from_folder(folder_path)

# Drag and drop file uploader
uploaded_files = st.sidebar.file_uploader("Upload Plots", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            fig = image_to_figure(uploaded_file)
            save_fig(fig, uploaded_file.name, "uploaded")
        except Exception as e:
            st.warning(f"Could not load file {uploaded_file.name}: {e}")

# Retrieve saved figures
storage_figs = st.session_state["storage"].get(Figure.__name__)
storage_figs = {
    k: v
    for k, v in storage_figs.items()
    if any([isinstance(v, Figure), isinstance(v, Figure_plotly)])
}
uploaded_figs = st.session_state["storage"].get(Figure.__name__, {}).get("uploaded", {})
folder_figs = st.session_state["storage"].get(Figure.__name__, {}).get("folder", {})

# Dropdown to select and display figures
st.sidebar.header("Select Figures to Display")

selected_storage_figs_key = st.sidebar.multiselect(
    "Directly from Storage", options=list(storage_figs.keys())
)
selected_uploaded_figs_key = st.sidebar.multiselect(
    "Uploaded Figures", options=list(uploaded_figs.keys())
)
selected_folder_figs_key = st.sidebar.multiselect(
    "Figures from Folder", options=list(folder_figs.keys())
)

selected_figs = {
    **{key: storage_figs[key] for key in selected_storage_figs_key},
    **{key: uploaded_figs[key] for key in selected_uploaded_figs_key},
    **{key: folder_figs[key] for key in selected_folder_figs_key},
}


# Add a sidebar radio button to allow the user to select the display mode.
display_mode = st.sidebar.radio(
    "Display Mode for Figures from Storage",
    ["Matplotlib", "Plotly", "Interactive Matplotlib"],
)
st.session_state["display_mode"] = display_mode.lower().replace(" ", "_")

columns = st.slider("Number of columns", min_value=1, max_value=8, value=2, step=1)
# Display the selected figures in a dynamically scaled grid
display_figures_in_grid(selected_figs, columns)
