import pytest
import tempfile
import json
import os

from filter.conditions import DEFAULT_FILENAME
from filter.conditions.not_correlated import NotCorrelated


@pytest.fixture(autouse=True)
def clean_env_vars_before_tests():
    os.environ["OUTPUTS"] = ""
    os.environ["INPUTS"] = ""
    os.environ["DIDS"] = "[]"
    yield


# ? no output means the condition is not met. Is this what you would like to happen
def test_output_not_defined():
    """ ? no output means the condition is not met. Is this what you would like to happen
    """
    nc = NotCorrelated()

    inputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    os.makedirs(os.path.join(inputs, did[0]))

    gibberish = b"2+2=5"

    with open(os.path.join(inputs, did[0], DEFAULT_FILENAME), "wb") as f:
        f.write(100 * gibberish)

    r = nc()

    assert r == False


def test_input_not_defined():
    nc = NotCorrelated()

    outputs = tempfile.mkdtemp()

    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    gibberish = b"2+2=5"

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(100 * gibberish)

    r = nc()

    assert r == False


def test_one_to_one_copy():
    nc = NotCorrelated()

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    os.makedirs(os.path.join(inputs, did[0]))

    gibberish = b"2+2=5"

    with open(os.path.join(inputs, did[0], DEFAULT_FILENAME), "wb") as f:
        f.write(100 * gibberish)

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(100 * gibberish)

    r = nc()

    assert r == False


def test_shifted_one_to_one_copy_default_epsilon():
    """Default epsilon not catching it when half of the data is new
    """
    nc = NotCorrelated()

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    os.makedirs(os.path.join(inputs, did[0]))

    gibberish = b"2+2=5"

    with open(os.path.join(inputs, did[0], DEFAULT_FILENAME), "wb") as f:
        f.write(100 * gibberish)

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(50 * gibberish)
        f.write(50 * b"1-3?4")

    r = nc()

    assert r == True


def test_shifted_one_to_one_copy_lax_epsilon():
    """Default epsilon not catching it when half of the data is new
    """
    nc = NotCorrelated()

    inputs = tempfile.mkdtemp()
    outputs = tempfile.mkdtemp()

    os.environ["INPUTS"] = inputs
    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    os.makedirs(os.path.join(inputs, did[0]))

    gibberish = b"2+2=5"

    with open(os.path.join(inputs, did[0], DEFAULT_FILENAME), "wb") as f:
        f.write(100 * gibberish)

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, output_f), "wb") as f:
        f.write(50 * gibberish)
        f.write(50 * b"1-3?4")

    # * 0.25 on both sides => we are adding the room for 0.5 units of entropy in total
    os.environ["CORRELATION_ENTROPY_THRESH"] = "0.25"

    r = nc()

    assert r == False
