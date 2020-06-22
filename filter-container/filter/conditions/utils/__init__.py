from typing import Optional
from enum import Enum, auto
from math import log2
import logging
import os

l = logging.getLogger("utils")


class EntropyAlgos:
    # * if performance is slow, we can multiprocess in the future
    @staticmethod
    def shannon(data: bytes) -> float:
        """Shannon's entropy

        Args:
            data (bytes): data bytes

        Returns:
            float: shannon's entropy of the byte block
        """
        entropy = 0.0

        if data:
            tot_num_bytes = len(data)

            # a byte is represented by 8 bits. 2 ^ 8 = 256
            seen = dict(((chr(x), 0.0) for x in range(0, 256)))

            for byte in data:
                seen[chr(byte)] += 1.0

            for v in seen.values():
                p_x = v / tot_num_bytes
                # expected value of the random variable I_X (which is log2(p_x))
                if p_x > 0:
                    entropy -= p_x * log2(p_x)

        # normalize the entropy 1 byte = 8 bits. Our entropy is per byte before normalization
        return entropy / 8.0


def validate_inputs_outputs() -> bool:
    """This function validates that INPUTS and OUTPUTS exists and is a dir

    Returns:
        bool: True if validated.
    """
    inputs = os.getenv("INPUTS")
    outputs = os.getenv("OUTPUTS")

    if not inputs:
        l.error(
            "INPUTS environment variable that points to the inputs data is not defined"
        )
        return False

    if not outputs:
        l.error(
            "OUTPUTS environment variable that points to the outputs is not defined"
        )
        return False

    if not os.path.exists(inputs):
        l.error("INPUTS directory does not exist")
        return False

    if not os.path.exists(outputs):
        l.error("OUTPUTS directory does not exist")
        return False

    return True


def get_size_of_dir(start_path="."):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size


def dataCategory(category: str) -> str:
    """Converts the name of the category pulled from the meta db
    to the config yaml file compatible name. For example,
    'Agriculture & Bio Engineering' becomes
    'agricultureBioEngineering'. 'Sociology' becomes 'sociology'

    Args:
        category (str): category name pulled from the db

    Returns:
        str: yaml keywords config file category compatible name
    """
    r = category.replace("&", "").title().replace(" ", "")
    if len(r) < 1:
        raise ValueError(f"unknown category: {category}")
    r = f"{r[0].lower()}{r[1:]}"
    return r


__all__ = ["EntropyAlgos", "validate_inputs_outputs", "FileExtension", "dataCategory"]
