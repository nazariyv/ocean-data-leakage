from typing import Optional
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


__all__ = ["EntropyAlgos", "validate_inputs_outputs"]
