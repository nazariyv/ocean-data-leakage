from typing import Optional, ClassVar, List
from collections import namedtuple
from math import log, e, ceil
from enum import Enum
import logging
import json
import os

from .utils import EntropyAlgos

shannon = EntropyAlgos.shannon

l = logging.getLogger("[encrypted]")

EntropyOfBlock = namedtuple(
    "EntropyOfBlock", ["offset", "file", "entropy", "description"]
)


# taken from: https://github.com/ReFirmLabs/binwalk/blob/c0365350af70ac537286fabcb08a793078e60241/src/binwalk/modules/entropy.py
# with some modifications
class NotEncrypted:
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
        self.name = "NotEncrypted"
        self.algorithm = shannon
        self.results: List[EntropyOfBlock] = []
        self.block_size = None

    def __call__(self) -> bool:
        """The intended usage of the class is to instantiate it,
        and then call it with a file location string.

        Args:
            file_loc (str): File for which to compute the entropy.

        Returns:
            List[EntropyOfBlock]: Returned is list of entropy block
            namedtuples.
        """
        outputs = os.getenv("OUTPUTS")

        if not outputs:
            l.error(f"could not find output files")

        for file in os.listdir(outputs):
            self._calculate_file_entropy(
                os.path.join(outputs, file)  # type: ignore
            )

            r = [e.entropy for e in self.results]

            entropy = sum(r) / len(r)
            if entropy > self._get_threshold():
                l.error(
                    "file exceeds the encryption threshold, therefore condition is not met. {}"
                )
                return False

        return True

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

        file_size = os.path.getsize(file_loc)  # in bytes

        l.debug(f"{file_size=}")

        block_size = file_size / self.DEFAULT_DATA_POINTS
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
                entropy = self.algorithm(data)
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

    def _get_threshold(self):
        return float(os.getenv("ENCRYPTION_ENTROPY_THRESH", 0.85))
