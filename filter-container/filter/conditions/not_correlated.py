from typing import List
import logging
import json
import os

from . import DEFAULT_FILENAME
from .utils import EntropyAlgos, validate_inputs_outputs

shannon = EntropyAlgos.shannon

l = logging.getLogger("[correlation]")

# reasoning for the choice: 0.1 is quite stringent, 0.05 is probably too lax
# so take something in the middle
DEFAULT_CORRELATION_ENTROPY_THRESH = 0.075

DEFAULT_BLOCK_SIZE = 1024

# ! There are a number of challenges with computing the correlation of
# ! the output to the original dataset:
# ! 1. output must be smaller, so correlation measure is not effective
# ! 2. since output is smaller, we would have to compare output to different
# !   blocks of the input. Adding to the time complexity of the algorithm
# ! 3. output may be the shifted copy of the input
# ! 4. output may be sliced and shuffled copy of the input
# ! The solution that I propose is to use compression distance metric
# ! like entropy. Since we are already using it to identify if the output
# ! is encrypted, we do not have to reinvent the wheel. For more algorithms
# ! that you may consider implementing in the future, in place of this
# ! consult: https://pypi.org/project/textdistance/. You will see that they
# ! are also using entropy in one of the methods, they place it in the
# ! "compression" group of document distance metrics.

# ! Assumption I am making is that there is only one input file
# ! that lives in the folder defined by INPUTS env var
# ! You will need to edit this algo, if this fails to be the
# ! the case in the future. i.e. input file directory contains
# ! a number of input files
# ! I would highly recommend imposing restrictions on how the inputs
# ! and outputs look like. This would make it much easier to protect
# ! against the data leaks. Also, it makes a lot of sense to create
# ! the condition sets per file type


class NotCorrelated:
    """The approach here is to compute the entropy of the source file
    in blocks of size of the output and then determine the average of
    these blocks. If the entropy of the output is within some epsilon
    of the average of the block entropies of the input, then condition
    is not met. Let's explain this on a higher level again. There is
    an input file, denote it I and output file, O. Consider them as
    sources of randomness. We can compute how much randomness there is
    in each by computing their Shannon Entropy. The problem we have to
    overcome is that they are of different sizes. More precisely, we know
    that the output has to be less than some fixed precentage of the
    input, by default, we set it to 10%. So, to overcome our problem of
    different sizes, we chunk up the input file into pieces of the size of
    the output. We then determine the average of these blocks. This algorithm
    can be improved by avoiding header row in .csv if it exists, or any other
    meta information (in different file types).
    This would be the next step. We then compare this
    entropy with the entropy of the output file, which we compute in a
    single block of size of the file. Both entropies are normalized such
    that their upper bound is 1.0 and lower bound 0.0. We define the env var
    CORRELATION_ENTROPY_THRESH that governs by how much the entropy of
    the output file can deviate from the input file, i.e. if

    I_entropy \in [O_entropy - CORRELATION_ENTROPY_THRESH, O_entropy + CORRELATION_ENTROPY_THRESH]

    then this condition is violated and so this signals potential data leak.

    Therefore, there is a balance to be struck here. You don't want false
    positives (you get them by setting that env var very high). But, at
    the same time, you don't want to miss true positives. Only practice
    will tell what a good value for this is.
    """

    def __call__(self) -> bool:
        """Calls internal method to compute correlation between the files that
        uses compression bases algorithm. Uses Shannon entropy on the blocks
        of sizes of the output file. Assumption is that there is a single output
        file and a single input file. It is recommended that this condition is
        not hard. But should set off warning if is violated. It is anticipated
        that this condition will yield the greatest number of false positives.
        This can be reduced, by decreasing the epsilon, i.e. CORRELATION_ENTROPY_THRESH
        env variable.

        We use __call__ as a wrapper for the calc correlation for at least two reasons.
        1. this allows us to add more logic in the future in this method.
        2. we conform to the standard we have defined in other condition checking algos,
           they are all too, invoked / evaluated by calling the instances of themselves.
           This creates consistent use standard. And so the library code writers know what
           to expect from our code.

        Returns:
            bool: boolean, if True then there are no problems. If False, then the
            entropy in in the input and output is too similar and indicated a potential
            data leak
        """
        is_valid = self._calc_correlation()
        return is_valid

    def _validate_env_vars(self) -> bool:
        """Validates if there CORRELATION_ENTROPY_THRESH, if set
        is in the range [0, 1]. 0 meaning that the epsilon is zero and so the input
        and output entropies have to match EXACTLY for this condition to be violated,
        this is equivalent to a 1-1 copy condition. 1 on the other hand would siwtch
        off this condition. So you have this spectrum to play around with and determine
        in practice what value works best to avoid having too many false positives, but
        also catch the leaks at the same time.

        Returns:
            bool: is the correlation in the correct range
        """
        epsilon = self._get_epsilon()

        if epsilon > 1 or epsilon < 0:
            l.error(
                "invalid  CORRELATION_ENTROPY_THRESH. pick something in the range [0, 1]."
            )
            return False

        return True

    def _calc_correlation(self) -> bool:
        """Method that actually computes the entropies of input and output and compares
        them

        Returns:
            bool: is condition met?
        """
        is_valid = validate_inputs_outputs()

        if not is_valid:
            return False

        thresh_valid = self._validate_env_vars()

        if not thresh_valid:
            return False

        self.epsilon = self._get_epsilon()
        self.inputs = os.getenv("INPUTS")
        self.outputs = os.getenv("OUTPUTS")

        did = json.loads(os.getenv("DIDS", "[]"))

        if len(did) < 1:
            l.error("no dids")
            return False

        output_files = os.listdir(self.outputs)

        # ! we absolutely need to restrict the form of the output file(s)
        # ! otherwise, it becomes incredibly hard to protect against the
        # ! data leaks
        if len(output_files) > 1:
            l.warning(
                "noticed more than one file in outputs: "
                f"{self.outputs}, but will only use the first one: "
                f"{output_files[0]}"
            )

        # ! if name changes from "0" to something else, this will fail
        # * ignoring type because mypy linter is bad in this case
        input_file = os.path.join(self.inputs, did[0], DEFAULT_FILENAME)  # type: ignore
        output_file = os.path.join(self.outputs, output_files[0])  # type: ignore

        output_file_size = os.path.getsize(output_file)

        input_file_entropy: List[float] = []
        output_file_entropy: List[float] = []

        # * to avoid having very small blocks
        if output_file_size < DEFAULT_BLOCK_SIZE:
            output_file_size = DEFAULT_BLOCK_SIZE

        with open(input_file, "rb") as f:
            input_data = f.read(output_file_size)

            while input_data:
                input_block_entropy = shannon(input_data)
                input_file_entropy.append(input_block_entropy)
                input_data = f.read(output_file_size)

        with open(output_file, "rb") as f:
            output_data = f.read(output_file_size)

            while output_data:
                output_block_entropy = shannon(output_data)
                output_file_entropy.append(output_block_entropy)
                output_data = f.read(output_file_size)

        input_entropy = sum(input_file_entropy) / len(input_file_entropy)
        output_entropy = sum(output_file_entropy) / len(output_file_entropy)

        if (
            output_entropy - self.epsilon
            < input_entropy
            < output_entropy + self.epsilon
        ):
            l.error(
                "the output is very similar to the input. this may be a false positive"
            )
            return False

        return True

    def _get_epsilon(self) -> float:
        return float(
            os.getenv("CORRELATION_ENTROPY_THRESH", DEFAULT_CORRELATION_ENTROPY_THRESH)
        )
