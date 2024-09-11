# Node-Based Workflow Application (Beta)

## Introduction

This is a Streamlit-based application that provides a node-based workflow for data processing and analysis. The application allows users to create, configure, and execute a series of interconnected nodes, where each node represents a specific data processing or analysis task. The application is designed to be flexible, extensible, and easy to use, making it suitable for a wide range of data-driven projects.

The key features of the application include:

1. **Node-Based Interface**: The application provides a visual interface where users can easily create, connect, and configure nodes to build their desired workflow.
2. **Configurable Nodes**: Each node can be customized with input parameters, output options, and various processing options, allowing users to fine-tune the behavior of their workflow.
3. **Caching and Reproducibility**: The application leverages caching mechanisms to improve performance and ensure reproducibility of results, allowing users to quickly iterate on their workflows.
4. **Extensible Functionality**: The application is designed to be extensible, allowing users to easily add new node types and expand the available functionality.
5. **Integrated Plotting and Visualization**: The application includes integrated support for creating and managing plots and visualizations, which can be easily incorporated into the node-based workflow.
6. **Python Scripting Integration**: The application provides a Python scripting interface, allowing users to seamlessly integrate custom Python code into their workflows.

## Pages

The application consists of the following pages:

### Node-Based Workflow

The main page of the application, where users can interact with the node-based workflow. This page includes the following key components:

1. **Node Configuration Panel**: This panel allows users to configure the various input parameters, output options, and processing options for each node in the workflow.
2. **Node Execution Viewer**: This section displays the results of the executed nodes, including input and output data, execution time, and any error messages.
3. **Node Palette**: A collection of predefined node types that users can drag and drop onto the workflow canvas to build their custom workflow.
4. **Workflow Canvas**: The main area where users can create, connect, and arrange the nodes to build their desired data processing and analysis pipeline.

### Dataframe Analysis

This page provides functionality for analyzing and exploring DataFrames within the application. Users can:

1. **Load and View DataFrames**: Upload new DataFrames or select from previously stored DataFrames in the application.
2. **Generate Profiling Reports**: Automatically generate comprehensive profiling reports for the loaded DataFrames, including statistical summaries, data quality assessments, and visualizations.
3. **Interact with DataFrames**: Use the built-in Streamlit data editor to interactively explore and manipulate the DataFrames.
4. **Visualize DataFrames**: Leverage the Graphical Walker library to create interactive visualizations and explorations of the DataFrame data.

### Plots

This page allows users to manage and display various plots and visualizations within the application. Key features include:

1. **Plot Storage and Retrieval**: Users can upload, save, and load plots and visualizations to/from the application's storage.
2. **Plot Display Options**: Users can choose between different display modes (Matplotlib, Plotly, Interactive Matplotlib) to view the stored plots.
3. **Dynamic Grid Layout**: The page dynamically scales and arranges the displayed plots in a grid layout based on the user's preferences.
4. **Folder-based Plot Loading**: Users can load a folder of image files and automatically convert them to Matplotlib figures for display.

### Python Editor

This page provides a fully-featured Python code editor, which allows users to write, save, and execute custom Python scripts within the application. Key features include:

1. **Code Editor**: A powerful code editor with syntax highlighting, code folding, and other advanced features, powered by the Streamlit Ace library.
2. **Script Management**: Users can upload new scripts or select from a predefined set of scripts stored in the application's script directory.
3. **Execution and Storage**: Executed scripts can access and modify the application's storage, allowing for seamless integration between the Python code and the rest of the application.
4. **Editor Customization**: Users can customize various aspects of the code editor, such as the theme, keybinding mode, font size, and more.

These pages collectively provide a comprehensive set of tools and functionalities for users to build, configure, and execute their data processing and analysis workflows within a unified, node-based application.


## Configuring the Sidepanel

The Node-Based Workflow Application allows users to configure the behavior and appearance of the sidepanel through a set of JSON configuration files. These configuration files specify the input parameters, options, and other settings that are displayed in the sidepanel for each workflow.

### Defining Configuration Files

The configuration files are stored in the `configs/sidepanel/` directory. Each configuration file represents a specific workflow or set of parameters, and the filename (without the `.json` extension) is used as the name of the configuration in the application.

Here's an example of a configuration file, `Normal.json`:

```json
{
    "numerical_params": {
        "distribution_params": {
            "mu": {
                "type": "number_input",
                "step": 0.1,
                "value": 0.0
            },
            "sigma": {
                "type": "number_input",
                "step": 0.1,
                "value": 3.0
            },
            "rho": {
                "type": "number_input",
                "step": 0.1,
                "value": 0.9
            }
        },
        "generate_params": {
            "n": {
                "type": "number_input",
                "value": {
                    "from": 1,
                    "to": 10,
                    "step": 1
                }
            },
            "num_simulations": {
                "type": "number_input",
                "step": 10000,
                "value": 100000
            },
            "seed": {
                "type": "number_input",
                "step": 1,
                "value": 0
            },
            "use_feature_1": {
                "type": "checkbox",
                "value": {
                    "config1": true,
                    "config2": false
                }
            }
        }
    },
    "text_params": {
        "pretty_text": {
            "distribution_params": {
                "title": "Normal distribtion parameters",
                "mu": "$\\mu$",
                "sigma": "$\\sigma$",
                "rho": "$\\rho$"
            },
            "generate_params": {
                "title": "Generate Parameters",
                "n": "$n$",
                "num_simulations": "Number of simulations",
                "seed": "seed",
                "use_feature_1": "Use Feature 1"
            }
        },
        "help_text": {
            "distribution_params": {
                "title": "Normal distribtion parameters",
                "mu": "Mean of normal distribution",
                "sigma": "Standard deviation of the normal distribution",
                "rho": "The correlation coefficient between two normal distributions"
            },
            "generate_params": {
                "title": "Generate Parameters",
                "n": "The number of dimensions to generate.",
                "num_simulations": "The total number of simulations to run.",
                "seed": "The seed for random number generation to ensure reproducibility.",
                "use_feature_1": "Enable or disable Feature 1"
            }
        }
    }
}
```

This configuration file defines two groups of parameters: `distribution_params` and `generate_params`. Each parameter is defined with a name, a type, and a default value. The `text_params` section provides custom labels and help text for the parameters, which are displayed in the sidepanel.

### Understanding the Configuration Fields

1. **`numerical_params`**: This section defines the input parameters that are displayed in the sidepanel. Each parameter is defined with a name and a set of options:
   - `type`: The type of the input widget to be used (e.g., `number_input`, `checkbox`).
   - `step`: The step size for numeric inputs.
   - `value`: The default value for the parameter. This can be a single value or a dictionary with "from", "to", and "step" keys to define a range of values.

2. **`text_params`**: This section provides customization options for the labels and help text displayed in the sidepanel.
   - `pretty_text`: Defines the user-friendly labels for each parameter.
   - `help_text`: Provides additional help text for each parameter.

The configuration file allows users to customize the input parameters, their types, default values, and the associated labels and help text displayed in the sidepanel. This flexibility enables users to tailor the application to their specific needs and data processing requirements.

When the application is run, the sidepanel will dynamically display the input parameters and options based on the selected configuration file. Users can then interact with these inputs to configure the behavior of the node-based workflow.

### From-To-Step and Multi-Parameter Functionality

The Node-Based Workflow Application supports a special configuration for numerical parameters that allows users to define a range of values using a "from", "to", and "step" approach. This functionality is particularly useful when you need to generate a set of values within a specific range, rather than just a single value.

In the configuration file, you can specify a parameter with a dictionary value instead of a single value. This dictionary should contain the keys "from", "to", and "step", which define the range and step size for the parameter.

The application also supports a special configuration for parameters that allows users to define multiple configurations for a single parameter. This functionality is particularly useful when you need to enable or disable certain features or options based on user input.

To enable the multi-parameter functionality, the user can toggle the "Multi Parameters" checkbox in the sidebar. When this option is enabled, the application will display additional input widgets for each parameter, allowing the user to define separate configurations for the "config1" and "config2" options.

Here's an example of how this can be configured in the `numerical_params` section:

```json
"numerical_params": {
    "generate_params": {
        "n": {
            "type": "number_input",
            "value": {
                "from": 1,
                "to": 10,
                "step": 1
            }
        },
        "use_feature_1": {
            "type": "checkbox",
            "value": {
                "config1": true,
                "config2": false
            }
        }
    }
}
```

In this example, the "n" parameter will be displayed as a set of three input widgets: "From", "To", and "Step". The "use_feature_1" parameter will be displayed as two checkbox widgets, with the first one being checked by default and the second one being unchecked by default.

When the application is run, the input values for the "from", "to", "step", "config1", and "config2" parameters will be stored in the session state and used to update the corresponding parameter values in the configuration.

This feature provides users with greater flexibility and control in defining the input parameters for their node-based workflows, allowing them to easily explore different ranges of values and enable or disable certain features or options based on their specific requirements.

## Creating Your Own Blocks

To create a new block, you can define a compute function and pass it to the `generate_block` function. The compute function should take the required input parameters and return the output values.

You can also provide an optional configuration dictionary to the `generate_block` function, which can include the following keys:

- `block_name`: The name of the block to be displayed in the Streamlit app.
- `input_names`: A dictionary mapping the function's parameter names to more user-friendly input names.
- `output_names`: A list of output names to be displayed in the Streamlit app.
- `options`: A dictionary of configurable options for the block, where the keys are the option names and the values are dictionaries containing the option type, default value, and other parameters.
- `docstring`: A string that will be displayed as the block's docstring in the Streamlit app.
- `category`: The category under which the block will be grouped in the Streamlit app.
- `cache`: A boolean value indicating whether the block's compute function should be cached.

## Where to Use `generate_block`

The `generate_block` function is used within the `blocks` package of the Node-Based Workflow Application. This package is responsible for managing and organizing the various computational blocks that can be used in the application.

When you want to create a new block, you should define your compute function and any associated configuration in a new Python file within the `blocks` package. The `generate_block` function is then called within this file to create the `Block` object.

For example, if you have a new compute function called `my_compute_function`, you would create a new file (e.g., `my_block.py`) in the `blocks` package and define the function and its configuration there. Inside the file, you would call `generate_block` with your compute function and configuration parameters to create the `Block` object.

```python
from gen_block import generate_block

def my_compute_function(x, y, z):
    # Compute function implementation

options_config = {
    "block_name": "My Custom Block",
    "input_names": {"x": "First Input", "y": "Second Input", "z": "Third Input"},
    "output_names": ["Result"],
    "options": {
        "z": {"type": "slider", "min": 0, "max": 100, "value": 50, "name": "Third Input"}
    },
    "docstring": "This is a custom block that performs a computation.",
    "category": "My Category",
    "cache": True,
}

my_block = generate_block(my_compute_function, options_config_param=options_config)
```

The blocks created using the `generate_block` function are then automatically discovered and included in the Node-Based Workflow Application. You don't need to manually register or import the blocks elsewhere in the application - the `blocks` package handles this automatically.

By following this convention of creating new blocks within the `blocks` package, you can ensure that your custom blocks are seamlessly integrated into the overall application, allowing users to easily discover and use them as part of their workflows.

## Parameters of Blocks

The parameters of a block are configured using the `options_config` dictionary passed to the `generate_block` function. The following keys are supported:

- `block_name`: The name of the block to be displayed in the Streamlit app.
- `input_names`: A dictionary mapping the function's parameter names to more user-friendly input names.
- `output_names`: A list of output names to be displayed in the Streamlit app.
- `options`: A dictionary of configurable options for the block, where the keys are the option names and the values are dictionaries containing the option type, default value, and other parameters.
- `docstring`: A string that will be displayed as the block's docstring in the Streamlit app.
- `category`: The category under which the block will be grouped in the Streamlit app.
- `cache`: A boolean value indicating whether the block's compute function should be cached.

The supported option types in the `options` dictionary are:

- `"input"`: A text input field.
- `"number"`: A number input field.
- `"integer"`: An integer input field.
- `"checkbox"`: A checkbox.
- `"select"`: A dropdown select field.
- `"slider"`: A slider input.
- `"display"`: A display-only field for showing information.


Each option type can have additional parameters, such as `"min"`, `"max"`, `"step"`, and `"value"`, depending on the option type.


The `options_config` parameter in the `generate_block` function can be defined as a JSON file with the same name as the compute function, and it will be automatically loaded and used to configure the block.

The `options_config` dictionary can be used to override the default configuration of the block, such as the input names, output names, options, and other settings.

By configuring the parameters of the blocks, you can customize the inputs, outputs, and options displayed in the Streamlit app, allowing users to interact with and control the behavior of the blocks.