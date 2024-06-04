from gen_block import generate_block
import random
import time
import matplotlib.pyplot as plt


def compute_test_func(input1, input2):
    """
    This is a test function to demonstrate the usage of generate_block.
    """
    return input1 + input2


def compute_func(x, y, z):
    """
    This is a test function to demonstrate the usage of generate_block with differrent options configs.
    config_1 = {
        "input_names": {"x": "First", "y": "Second", "z": "Third"},
        "output_names": ["Sum"]
    }

    config_2 = {
        "input_names": {"x": "First", "y": "Second", "z": "Third"},
        "output_names": ["Sum"],
        "options": {
            "z": {"name": "Third", "type": "slider", "min": 0, "max": 100, "value": 50}
        }
    }
    """
    return x + y + z


def random_number_generator(low, high, seed):
    random.seed(seed)
    return random.uniform(low, high)


def cache_func():
    """
    Simulates a time-consuming operation by pausing execution for 2 seconds.

    This function is designed to represent a placeholder for operations that
    would typically take a significant amount of time to complete, such as
    data processing or fetching data from a remote server.

    Run this node multiple times to observe the behavior of the cache.

    Returns:
        int: A fixed integer (10) to simulate a deterministic output from a
             time-consuming operation.
    """
    time.sleep(2)  # Simulate a time-consuming operation
    return 10


options_config1 = {
    "block_name": "Compute Sum (config 1)",
    "input_names": {"x": "First", "y": "Second", "z": "Third"},
    "output_names": ["Sum"],
}

options_config2 = {
    "block_name": "Compute Sum (config 2)",
    "input_names": {"x": "First", "y": "Second", "z": "Third"},
    "output_names": ["Sum"],
    "options": {
        "z": {"name": "Third", "type": "slider", "min": 0, "max": 100, "value": 50}
    },
}

options_config3 = {"block_name": "Cache Example"}

block1 = generate_block(compute_test_func, category_name="Examples", cache=False)
block2 = generate_block(
    compute_func,
    options_config_param=options_config1,
    category_name="Examples",
    cache=False,
)
block3 = generate_block(
    compute_func,
    options_config_param=options_config2,
    category_name="Examples",
    cache=False,
)
block4 = generate_block(
    random_number_generator,
    add_display_option=True,
)
block5 = generate_block(
    cache_func,
    options_config_param=options_config3,
    category_name="Examples",
    cache=True,
)


def dataframe(param):
    import pandas as pd

    data = pd.DataFrame(
        {
            "x": range(param),
            "y": [i**2 for i in range(param)],
        }
    )
    fig, ax = plt.subplots()
    ax.plot(data["x"], data["y"])
    return data, fig

df_block = generate_block(dataframe)