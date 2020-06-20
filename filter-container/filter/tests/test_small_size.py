import tempfile
import pytest  # type: ignore
import math
import os

from filter.conditions.small_size import SmallSize, DEFAULT_SMALLER_THAN_PCT


def test_envs_do_not_exist():
    s = SmallSize()
    r = s()
    assert r == False


def test_empty_dirs():
    """testing with default size threshold
    """
    s = SmallSize()

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs

    r = s()

    assert r == False


def test_default_pct():
    s = SmallSize()

    assert s.size_threshold == DEFAULT_SMALLER_THAN_PCT


def test_end_to_end():
    s = SmallSize()

    assert s.size_threshold == DEFAULT_SMALLER_THAN_PCT

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs

    gibberish = b"2+2=5"

    input_f = tempfile.gettempprefix()
    with open(os.path.join(inputs, input_f), "wb") as f:
        f.write(100 * gibberish)

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(int(math.floor(DEFAULT_SMALLER_THAN_PCT * 100)) * gibberish)

    r = s()

    assert s.size_threshold == DEFAULT_SMALLER_THAN_PCT

    assert r == True


def test_output_too_large():
    s = SmallSize()

    assert s.size_threshold == DEFAULT_SMALLER_THAN_PCT

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs

    gibberish = b"2+2=5"

    input_f = tempfile.gettempprefix()
    with open(os.path.join(inputs, input_f), "wb") as f:
        f.write(100 * gibberish)

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(int(math.ceil(DEFAULT_SMALLER_THAN_PCT * 100) + 1) * gibberish)

    r = s()

    assert s.size_threshold == DEFAULT_SMALLER_THAN_PCT

    assert r == False


def test_custom_thresh():
    s = SmallSize()

    CUSTOM_THRESH = "0.5"
    os.environ["SMALLER_THAN_PCT"] = CUSTOM_THRESH

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs

    gibberish = b"2+2=5"

    input_f = tempfile.gettempprefix()
    with open(os.path.join(inputs, input_f), "wb") as f:
        f.write(100 * gibberish)

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(int(math.floor(float(CUSTOM_THRESH) * 100)) * gibberish)

    r = s()

    assert s.size_threshold == float(CUSTOM_THRESH)

    assert r == True
