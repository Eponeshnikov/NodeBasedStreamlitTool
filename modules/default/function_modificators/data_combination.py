from typing import Callable, List, Dict, Union, Tuple, Sequence, Any
import numpy as np
import itertools
import inspect


class DataCombinationDecorator:
    """
    This decorator allows you to apply data combinations to the input data sources of a function.

    Parameters
    ---------
    - data_params (Union[int, str, List[Union[int, str]]]): The parameters of the data sources.
    - zip_data (Union[bool, List[Union[int, str]]]): A boolean or list of booleans indicating whether to combine the data sources.
    - zip_data_with_params (bool): A boolean indicating whether to combine the parameters of the data sources.
    - add_new_params (bool): A boolean indicating whether to add new parameters to the results.
    - return_params (bool): A boolean indicating whether to return the parameters of the results.
    - custom_suffix (str): A custom suffix to be added to the function name.

    Returns:
    Callable: The decorated function with added data combination capabilities.


    Example:
    @DataCombinationDecorator(data_params=[1, 2], zip_data=True)
    def example_function(data_source1: np.ndarray, data_source2: np.ndarray):
        # Function implementation
        pass

    The above example applies the decorator to the `example_function` with `data_params` set to [1, 2] and `zip_data` set to True.
    """

    def __init__(
        self,
        data_params: Union[int, str, List[Union[int, str]]] = 0,
        zip_data: Union[bool, List[Union[int, str]]] = False,
        zip_data_with_params: bool = False,
        add_new_params: bool = True,
        return_params: bool = True,
        custom_suffix: str = None,
        result_as_params: bool = False,
        disable_data_source: bool = False
    ):
        # Convert data_params to a list if it's a single value
        self.data_params = (
            data_params if isinstance(data_params, list) else [data_params]
        )
        # Ensure zip_data is a list, replicating the boolean value if necessary
        self.zip_data = (
            zip_data
            if isinstance(zip_data, list)
            else [zip_data] * len(self.data_params)
        )
        self.zip_data_params = (
            zip_data_with_params  # Store whether to zip data with params
        )
        self.add_new_params = add_new_params  # Store whether to add new parameters
        self.return_params = return_params  # Store whether to return parameters
        self.custom_suffix = custom_suffix  # Store custom suffix
        self.result_as_params = (
            result_as_params  # Store whether to update params with result
        )

    def __call__(self, func: Callable) -> Callable:
        """
        Decorator function that applies data combinations to the input data sources of a given function.

        Parameters:
        -----------
        func : Callable
            The function to be decorated. This function should accept data sources and parameter dictionaries as input.

        Returns:
        --------
        wrapper : Callable
            The decorated function with added data combination capabilities.

        """

        def wrapper(
            *data_sources: List[Union[Tuple[Dict, np.ndarray], np.ndarray]],
            list_dict_params: Union[List[Dict], Dict] = [
                dict()
            ],  # List of parameter dictionaries
        ):
            func_name = (
                self.custom_suffix if self.custom_suffix else func.__name__
            )  # Determine function name (with suffix if provided)
            # Ensure all data sources are tuples of (dict, ndarray) – dict can be empty
            
            data_sources_ = [self._ensure_tuples(data) for data in data_sources]
            
            # Generate combinations of data sources based on zip_data settings
            data_combinations = self._generate_data_combinations(data_sources_)
            # Compute the function's results for each data combination and parameter set
            result = self._compute_results(
                data_combinations, list_dict_params, func, func_name
            )
            # prepare results, update result in params
            if self.result_as_params:
                result = [
                    (res[0].update({func_name: res[1]}), res[1]) for res in result
                ]

            # Construct and return the final result (with or without parameters)
            final_result = result if self.return_params else [res[1] for res in result]
            return final_result

        return wrapper

    @staticmethod
    def _ensure_tuples(
        arr_list: Union[List[Tuple[Dict, Any]], List[Any]]
    ) -> List[Tuple[Dict, Any]]:
        """
        Ensures that input data is a list of tuples (dict, data). If a simple list/array is given, creates tuples with empty dicts.

        Parameters
        ----------
        arr_list (Union[List[Tuple[Dict, Any]], List[Any]]): A list of data sources. Each data source can be a tuple of (dict, data) or a simple data element.

        Returns:
        List[Tuple[Dict, Any]]: A list of tuples (dict, data). If a simple data element was given, it is converted to a tuple with an empty dict.
        """
        arr_list_ = arr_list if isinstance(arr_list, Sequence) else [arr_list]
        if not all(isinstance(arr, tuple) for arr in arr_list_):
            arr_list = [({}, arr) for arr in arr_list_]
        return arr_list

    def _generate_data_combinations(
        self, data_sources: List[Tuple[Dict, np.ndarray]]
    ) -> List[Tuple[Union[Tuple[Dict, np.ndarray], np.ndarray]]]:
        """
        Generates combinations of data sources based on zip_data flags.

        Parameters
        ----------
        data_sources (List[Tuple[Dict, np.ndarray]]): A list of tuples, where each tuple contains a dictionary and a numpy array.
            The dictionary represents parameters for the data source, and the numpy array represents the actual data.

        Returns:
        List[Tuple[Union[Tuple[Dict, np.ndarray], np.ndarray]]]: A list of tuples representing combinations of data sources.
            Each tuple contains the combined data sources based on the zip_data flags.
        """
        zip_data = (
            self.zip_data
            if isinstance(self.zip_data, list)
            else [self.zip_data] * len(data_sources)
        )  # handle bool case

        unique_flags = list(set(zip_data))  # get unique values
        dict_of_zip = {
            k: [] for k in unique_flags
        }  # Initialize dictionary to group data sources by zip flag

        for zip_flag, data_sources_ in zip(zip_data, data_sources):
            dict_of_zip[zip_flag].append(data_sources_)  # group data based on flag

        sets_of_combinations = {}
        for k, v in dict_of_zip.items():
            if k != 0:  # Zip data sources if the flag is True
                sets_of_combinations[k] = list(zip(*v))  # zip groups
            else:  # Otherwise, create a cartesian product
                sets_of_combinations[k] = v

        if (
            sets_of_combinations.get(0, None) is not None
        ):  # Cartesian products of non-zipped groups
            sets_of_combinations[0] = list(itertools.product(*sets_of_combinations[0]))

        final_product = list(
            itertools.product(*sets_of_combinations.values())
        )  # combine

        result = []
        zip_data_tmp = list(zip_data)

        for combination in final_product:  # reconstruct based on original position
            temp_list = [None] * len(zip_data_tmp)
            idx = 0
            for flag, values in sets_of_combinations.items():
                for value in combination[idx]:
                    position = zip_data_tmp.index(flag)
                    temp_list[position] = value
                    zip_data_tmp[position] = None
                idx += 1
            zip_data_tmp = list(zip_data)
            result.append(tuple(temp_list))

        return result

    def process_list_of_dicts(self, list_dict_params, func):
        """
        Processes a list of dictionaries to ensure they contain all necessary parameters for a given function.

        Parameters
        -----------
        list_dict_params : Union[List[Dict], Dict]
            A list of dictionaries, where each dictionary represents a set of parameters for the function.
            If a single dictionary is provided, it will be converted to a list containing a single dictionary.
            If no dictionary is provided, an empty dictionary will be used.

        func : Callable
            The function for which the parameters are being processed.

        Returns:
        --------
        list_dict_params_ : List[Dict]
            A list of dictionaries, where each dictionary contains all necessary parameters for the function.
            If a single dictionary was provided as input, the output will also be a single-element list.
            If no dictionary was provided as input, the output will be a single-element list containing an empty dictionary.
        data_param_names : List[str]
            A list of parameter names that correspond to the data sources.

        """
        list_dict_params_ = list_dict_params

        sig = inspect.signature(
            func
        )  # Get function signature to extract parameter names and defaults
        param_names = {
            i.name: i.default for i in sig.parameters.values()
        }  # default params
        data_param_names = [
            list(param_names.keys())[i] for i in self.data_params
        ]  # data param names
        default_param_values = {  # non-data param defaults
            k: None if param_names[k] == inspect._empty else param_names[k]
            for k in set(param_names.keys()).difference(set(data_param_names))
        }
        list_dict_params_ = (
            [list_dict_params_]
            if isinstance(list_dict_params_, dict)
            else list_dict_params_
        )
        list_dict_params_ = (
            [{}] if list_dict_params_ is None else list_dict_params_
        )  # Handle empty param dictionaries
        # Update list dicts with the correct values if not provided
        for k, v in default_param_values.items():
            for d in list_dict_params_:
                if k not in d:
                    d[k] = v
        return list_dict_params_, data_param_names

    def _compute_results(
        self,
        data_combinations: List[Tuple[Union[Tuple[Dict, np.ndarray], np.ndarray]]],
        list_dict_params: Union[List[Dict], Dict],
        func: Callable,
        func_name: str,
    ) -> List[Tuple[Dict, Any]]:
        """
        Computes the function's results for each data combination.

        Parameters:
        -----------
        data_combinations : List[Tuple[Union[Tuple[Dict, np.ndarray], np.ndarray]]]
            A list of tuples representing combinations of data sources.
            Each tuple contains the combined data sources based on the zip_data flags.

        list_dict_params : Union[List[Dict], Dict]
            A list of parameter dictionaries. Each dictionary contains parameters for the function.

        func : Callable
            The function to be called with the data and parameters.

        func_name : str
            The name of the function.

        Returns:
        --------
        result : List[Tuple[Dict, Any]]
            A list of tuples. Each tuple contains a dictionary of parameters and the result of calling the function with the corresponding data and parameters.
        """
        list_dict_params_, data_param_names = self.process_list_of_dicts(
            list_dict_params, func
        )

        result = []
        # Create combinations of data and parameter sets.
        if self.zip_data_params:
            combinations = zip(data_combinations, list_dict_params_)  # zip if needed
        else:
            combinations = itertools.product(
                data_combinations, list_dict_params_
            )  # cartesian product
        for combination in combinations:
            data_set, params = combination  # Unpack data and parameters
            stored_params = {}
            data_values = {}

            for i, item in enumerate(data_set):  # Iterate through data sources
                suffix = f"_{data_param_names[i]}"  # Create suffix for parameter names
                param_suffix = (
                    {  # Update stored parameters with parameters from data source
                        f"{key}{suffix}": value for key, value in item[0].items()
                    }
                )
                stored_params.update(param_suffix)
                data_values[data_param_names[i]] = item[
                    1
                ]  # Store data values with appropriate parameter names

            updated_params = {  # Update parameters with function name suffix
                f"{key}_{func_name}": value for key, value in params.items()
            }
            real_params = {  # remove function name suffix before function application
                key.split(f"_{func_name}")[0]: value
                for key, value in updated_params.items()
            }
            if (
                self.add_new_params
            ):  # Add updated parameters to stored parameters if requested
                stored_params.update(updated_params)
            result.append(
                (stored_params, func(**data_values, **real_params))
            )  # Call function with appropriate data and parameters, store with parameters

        return result
