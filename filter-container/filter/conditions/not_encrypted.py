from typing import Optional, ClassVar, List
from collections import namedtuple
from math import log, e, ceil
from enum import Enum
import logging
import json
import os

l = logging.getLogger("encrypted")

EntropyOfBlock = namedtuple(
    "EntropyOfBlock", ["offset", "file", "entropy", "description"]
)


# taken from: https://github.com/ReFirmLabs/binwalk/blob/c0365350af70ac537286fabcb08a793078e60241/src/binwalk/modules/entropy.py
# with some modifications
class Entropy:
    """Entropy class is responsible for computing entropy of any file.
    It does so by chunking the fily into byte blocks and computing the
    entropy on each block. It is foreseeable that the file may contain
    headers, and that the last byte block may be smaller than the
    others. This is a small limitation of the solution. Although,
    it can be aleviated to some extent by scaling each block by
    the number of bytes in a block, for example.
    """

    DEFAULT_BLOCK_SIZE: ClassVar[int] = 1024
    DEFAULT_DATA_POINTS: ClassVar[int] = 2048

    def __init__(self) -> None:
        self.algorithm = self.shannon
        self.results: List[EntropyOfBlock] = []
        self.block_size = None

    def __call__(self, file_loc: str) -> List[EntropyOfBlock]:
        """The intended usage of the class is to instantiate it,
        and then call it with a file location string.

        Args:
            file_loc (str): File for which to compute the entropy.

        Returns:
            List[EntropyOfBlock]: Returned is list of entropy block
            namedtuples.
        """
        self._calculate_file_entropy(file_loc)
        return self.results

    def _calculate_file_entropy(self, file_loc: str) -> None:
        """Internal function that will calculate the entropy for file
        specified in file_loc

        Args:
            file_loc (str): absolute string path to the location of the file
        """
        if not os.path.exists(file_loc):
            l.error(f"file does not exist: {file_loc}")
            return

        # clear results from any previously analyzed files
        self.results = []

        file_length = os.path.getsize(file_loc)  # in bytes

        block_size = file_length / self.DEFAULT_DATA_POINTS
        # round up to the nearest DEFAULT_BLOCK_SIZE (1024)
        block_size = int(
            block_size
            + ((self.DEFAULT_BLOCK_SIZE - block_size) % self.DEFAULT_BLOCK_SIZE)
        )

        # ensure block size is greater than 0
        if block_size <= 0:
            block_size = self.DEFAULT_BLOCK_SIZE

        l.info(
            "entropy block size (%d data points): %d"
            % (self.DEFAULT_DATA_POINTS, block_size)
        )

        i = 0

        with open(file_loc, "rb") as f:
            data = f.read(block_size)
            while data:
                entropy = self.algorithm(data, block_size)
                self.results.append(
                    EntropyOfBlock(
                        offset=(i * block_size),
                        file=file_loc,
                        entropy=entropy,
                        description="%f" % entropy,
                    )
                )
                i += 1
                l.debug(f"{i=}, last block entropy: {self.results[-1]=}")
                data = f.read(block_size)

    # ! if performance is slow we can multiprocess this in the future
    @staticmethod
    def shannon(data: bytes, block_size: Optional[int] = None) -> float:
        """Shannon's entropy

        Args:
            data (bytes): data bytes
            block_size (Optional[int], optional): block_size, used for logging if passed
            Can be used for scaling blocks with fewer bytes in the future. Defaults to None.

        Returns:
            float: shannon's entropy of the byte block
        """
        entropy = 0.0

        if data:
            length = len(data)

            # a byte is represented by 8 bits. 2 ^ 8 = 256
            seen = dict(((chr(x), 0.0) for x in range(0, 256)))

            for byte in data:
                seen[chr(byte)] += 1.0

            for v in seen.values():
                p_x = v / length

                if p_x > 0:
                    entropy -= p_x * log(p_x, 2)

        if block_size:
            l.debug(f"{block_size=},{length=}")

        # normalize the entropy 1 byte = 8 bits. Our entropy is per byte before normalization
        return entropy / 8.0
