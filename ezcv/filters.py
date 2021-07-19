"""This is a module that provides additional jinja filters to help with theme development"""

from typing import List

import jinja2



def inject_filters(env:jinja2.Environment) -> jinja2.Environment:
    filters = [split_to_sublists]

    for filter in filters:
        env.filters[filter.__name__] = filter

    return env

def split_to_sublists(initial_list:list, n:int) -> List[list]:
    """Takes a list and splits it into sublists of size n

    Parameters
    ----------
    initial_list : list
        The initial list to split into sublists

    n : int
        The size of each sublist

    Returns
    -------
    List[list]
        A list of lists of size n
    """

    if not len(initial_list) % n == 0:
        raise ValueError(f"Provided list was not of correct size: \n\tList: {initial_list}\n\tSegment size {n}")

    result = []
    for i in range(0, len(initial_list), n):
        result.append( initial_list[i:i + n])

    return result