from typing import Callable, List, Dict, Union, Tuple, Sequence
import numpy as np
import itertools
import inspect


class DataCombinationDecorator:
    """
    This decorator allows you to apply data combinations to the input data sources of a function.

    Parameters:
    data_params (Union[int, str, List[Union[int, str]]]): The parameters of the data sources.
    zip_data (Union[bool, List[Union[int, str]]]): A boolean or list of booleans indicating whether to combine the data sources.
    zip_data_with_params (bool): A boolean indicating whether to combine the parameters of the data sources.
    add_new_params (bool): A boolean indicating whether to add new parameters to the results.
    return_params (bool): A boolean indicating whether to return the parameters of the results.
    custom_suffix (str): A custom suffix to be added to the function name.

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
    ):
        self.data_params = (
            data_params if isinstance(data_params, list) else [data_params]
        )
        self.zip_data = (
            zip_data if isinstance(zip_data, list) else [zip_data] * len(self.data_params)
        )
        self.zip_data_params = zip_data_with_params
        self.add_new_params = add_new_params
        self.return_params = return_params
        self.custom_suffix = custom_suffix

    def __call__(self, func: Callable):
        def wrapper(
            *data_sources: List[Union[Tuple[Dict, np.ndarray], np.ndarray]],
            list_dict_params: List[Dict],
        ):
            func_name = self.custom_suffix if self.custom_suffix else func.__name__
            # Ensure data sources contain tuples
            data_sources_ = [self._ensure_tuples(data) for data in data_sources]

            # Generate data combinations
            data_combinations = self._generate_data_combinations(data_sources_)

            # Compute results
            result = self._compute_results(
                data_combinations, list_dict_params, func, func_name
            )

            # Construct the final result
            final_result = result if self.return_params else [res[1] for res in result]
            return final_result

        return wrapper

    def _ensure_tuples(self, arr_list):
        arr_list_ = arr_list if isinstance(arr_list, Sequence) else [arr_list]
        if not all(isinstance(arr, tuple) for arr in arr_list_):
            arr_list = [({}, arr) for arr in arr_list_]
        return arr_list

    def _generate_data_combinations(self, data_sources):
        if isinstance(self.zip_data, bool):
            zip_data = [self.zip_data] * len(data_sources)
        else:
            zip_data = self.zip_data

        unique_flags = list(set(zip_data))
        dict_of_zip = {k: [] for k in unique_flags}
        for zip_flag, data_sources_ in zip(zip_data, data_sources):
            dict_of_zip[zip_flag].append(data_sources_)

        sets_of_combinations = {}
        for k, v in dict_of_zip.items():
            if k != 0:
                sets_of_combinations[k] = list(zip(*v))
            else:
                sets_of_combinations[k] = v
        if sets_of_combinations.get(0, None) is not None:
            sets_of_combinations[0] = list(itertools.product(*sets_of_combinations[0]))

        final_product = list(itertools.product(*sets_of_combinations.values()))

        result = []
        zip_data_tmp = list(zip_data)
        for combination in final_product:
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

    def _compute_results(self, data_combinations, list_dict_params, func, func_name):
        # param_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        sig = inspect.signature(func)
        param_names = {i.name: i.default for i in sig.parameters.values()}
        data_param_names = [list(param_names.keys())[i] for i in self.data_params]
        default_param_values = {
            k: None if param_names[k] == inspect._empty else param_names[k]
            for k in set(param_names.keys()).difference(set(data_param_names))
        }
        
        list_dict_params = [{}] if list_dict_params is None else list_dict_params
        
        for k, v in default_param_values.items():
            for d in list_dict_params:
                if k not in d:
                    d[k] = v

        result = []
        if self.zip_data_params:
            combinations = zip(data_combinations, list_dict_params)
        else:
            combinations = itertools.product(data_combinations, list_dict_params)
        for combination in combinations:
            data_set, params = combination
            stored_params = {}
            data_values = {}

            for i, item in enumerate(data_set):
                suffix = f"_{data_param_names[i]}"
                param_suffix = {
                    f"{key}{suffix}": value for key, value in item[0].items()
                }
                stored_params.update(param_suffix)
                data_values[data_param_names[i]] = item[1]

            updated_params = {
                f"{key}_{func_name}": value for key, value in params.items()
            }
            real_params = {
                key.split(f"_{func_name}")[0]: value
                for key, value in updated_params.items()
            }
            if self.add_new_params:
                stored_params.update(updated_params)

            result.append((stored_params, func(**data_values, **real_params)))

        return result
