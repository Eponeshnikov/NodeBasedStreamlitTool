import glob
import os
import itertools
import pickle
import time
import hashlib

def between(value, a, b):
    """
    Extracts a substring between two specified substrings.

    Parameters:
    value (str): The original string from which to extract the substring.
    a (str): The substring that marks the beginning of the desired substring.
    b (str): The substring that marks the end of the desired substring.

    Returns:
    str: The substring that is located between 'a' and 'b' in the original string.
         If either 'a' or 'b' is not found in the original string, an empty string is returned.
    """
    # Find and validate before-part.
    pos_a = value.find(a)
    if pos_a == -1:
        return ""
    # Find and validate after part.
    pos_b = value.rfind(b)
    if pos_b == -1:
        return ""
    # Return middle part.
    adjusted_pos_a = pos_a + len(a)
    if adjusted_pos_a >= pos_b:
        return ""
    return value[adjusted_pos_a:pos_b]


def get_configs(root_dir, ext='json', between_str=["modules/", "/configs"]):
    """
    Get a list of JSON configuration files and a list of module-specific configuration file names.

    This function takes a root directory as input and returns two lists:
    1. A list of full paths to JSON configuration files in the specified root directory and its subdirectories.
    2. A list of module-specific configuration file names, which are relative to the root directory and its subdirectories.

    The function first retrieves all JSON files in the specified root directory and its subdirectories using the `glob` module. It then retrieves all module-specific directories within the root directory and its subdirectories. For each module-specific directory, it retrieves all JSON configuration files within that directory. The function combines these lists of JSON configuration files and module-specific configuration file names and returns them as the output.

    Parameters
    ----------
    root_dir : str
        The root directory from which to retrieve JSON configuration files and module-specific configuration file names.

    Returns
    -------
    list
        A list of full paths to JSON configuration files in the specified root directory and its subdirectories.
    list
        A list of module-specific configuration file names, which are relative to the root directory and its subdirectories.
    """
    _configs_ = [
        os.path.join(root_dir, file_)
        for file_ in glob.glob(f"*.{ext}", root_dir=root_dir)
    ]

    modules_paths = [os.path.join("modules", i) for i in os.listdir("modules")]
    block_folders = [
        os.path.join(modules_path, root_dir)
        for modules_path in modules_paths
        if os.path.exists(os.path.join(modules_path, root_dir))
    ]
    full_configs_folders = [os.path.abspath(i) for i in block_folders]
    modules_configs = list(
        itertools.chain.from_iterable(
            [
                [
                    os.path.join(root_dir, file_)
                    for file_ in glob.glob(f"*.{ext}", root_dir=root_dir)
                ]
                for root_dir in full_configs_folders
            ]
        )
    )
    _configs_ = _configs_ + modules_configs
    _modules_names_ = {
        config: (
            between(config, between_str[0], between_str[1]) + "/"
            if len(between(config, between_str[0], between_str[1])) > 0
            else ""
        )
        for config in _configs_
    }

    return _configs_, _modules_names_


def format_nanoseconds(nanoseconds: int) -> str:
    """
    Convert a duration from nanoseconds to a more readable string format, breaking down
    the duration into hours, minutes, seconds, milliseconds, microseconds, and nanoseconds.

    Parameters
    ----------
    nanoseconds : int
        The duration in nanoseconds to be formatted.

    Returns
    -------
    str
        A string representing the formatted duration, including only the non-zero units
        from the highest non-zero unit down to nanoseconds. For example, "1 hr 15 min 42 s"
        or "200 ms 1 μs". Returns "0 ns" if the input is 0.
    """
    # Define the units and their conversion factors relative to the next smaller unit.
    units = {"ns": 0, "μs": 0, "ms": 0, "s": 0, "min": 0, "hr": 0}
    conversions = [1000, 1000, 1000, 60, 60, 1]  # Conversion factors for each unit.
    nanoseconds_ = nanoseconds  # Copy of the input to manipulate.

    # Convert nanoseconds to higher units iteratively.
    for key, conversion in zip(units.keys(), conversions):
        if key != "hr":  # For all units except hours, calculate quotient and remainder.
            quotient = nanoseconds_ // conversion
            remainder = nanoseconds_ % conversion
            units[key] = remainder  # Assign remainder to the unit.
            nanoseconds_ = quotient  # Update nanoseconds for the next iteration.
        else:
            units[key] = nanoseconds_  # Assign remaining nanoseconds to hours.

    # Reverse the units dictionary to start formatting from the highest unit down.
    result = list(units.items())[::-1]
    print_res = "0 ns"  # Default result if all units are zero.
    # Construct the formatted string with non-zero units.
    for i, r in enumerate(result):
        if r[1] != 0:  # If the unit is non-zero, start constructing the result string.
            print_res = " ".join(
                [f"{x[1]} {x[0]}" for x in result[i : min(len(result), i + 3)]]
            )
            break  # Stop after finding the first non-zero unit.

    return print_res


CACHE_FOLDER = '.cache'
 
def generate_cache_filename(func, *args, **kwargs):
    """
    Generate a unique cache filename based on the function name, arguments, and keyword arguments.

    This function takes a function object, positional arguments, and keyword arguments as input.
    It combines the function name, arguments, and keyword arguments into a tuple, serializes the tuple,
    and computes the SHA-256 hash of the serialized data. The hash is then used to generate a unique
    filename with a '.pickle' extension. The filename is returned as a string.

    Parameters
    ----------
    func (function): The function object for which the cache filename is being generated.
    *args (tuple): Positional arguments passed to the function.
    **kwargs (dict): Keyword arguments passed to the function.

    Returns:
    str: A unique cache filename based on the function name, arguments, and keyword arguments.
    """
    combined_data = (func.__name__, args, kwargs)
    serialized_data = pickle.dumps(combined_data)
    hash_object = hashlib.sha256(serialized_data)
    filename = hash_object.hexdigest() + '.pickle'
    return os.path.join(CACHE_FOLDER, filename)
 
def cache_result(reset=False):
    """
    A decorator function that caches the results of a function and stores them in a cache file.

    Parameters
    ----------
    reset (bool): If True, the cache file will be deleted and the function will be executed again.
                  If False (default), the function will attempt to load the result from the cache file.

    Returns:
    function: The decorated function, which will either return the cached result or execute the function
              and store the result in the cache file.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_file = generate_cache_filename(func, *args, **kwargs)
            if not reset:
                try:
                    with open(cache_file, 'rb') as file:
                        cached_data = pickle.load(file)
                    cached_result = cached_data
                    return cached_result
                except (IOError, pickle.PickleError, EOFError):
                    pass
            result = func(*args, **kwargs)
            cached_data = result
            os.makedirs(CACHE_FOLDER, exist_ok=True)
            with open(cache_file, 'wb') as file:
                pickle.dump(cached_data, file)

            return result
        return wrapper
    return decorator