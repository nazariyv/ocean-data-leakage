import pytest
import os
import json
import tempfile
from typing import Optional, Dict

from filter.conditions.no_keywords import NoKeywords

DEFAULT_FAKE_META = {
    "service": [
        {
            "type": "metadata",
            "attributes": {
                "additionalInformation": {
                    "categories": ["Agriculture & Bio Engineering"]
                }
            },
        }
    ]
}


class MockDDO:
    def __init__(self, out: Optional[Dict] = None) -> None:
        self.out = out

    def find_one(self, *args, **kwargs) -> Dict:
        if self.out:
            return self.out
        return DEFAULT_FAKE_META


class Aquarius:
    def __init__(self, out: MockDDO) -> None:
        self.ddo = out


class MockClient:
    def __init__(self, out: Optional[Dict] = None) -> None:
        mock_ddo = MockDDO(out)
        self.aquarius = Aquarius(mock_ddo)


def monkey_patch_client(nk: NoKeywords, out: Optional[Dict] = None) -> NoKeywords:
    mock_client = MockClient(out)
    nk.client = mock_client
    return nk


@pytest.fixture(autouse=True)
def clean_env_vars_before_tests():
    os.environ["OUTPUTS"] = ""
    os.environ["INPUTS"] = ""
    os.environ["DIDS"] = "[]"
    yield


def test_all_keywords():
    nk = NoKeywords()
    nk = monkey_patch_client(nk)

    outputs = tempfile.mkdtemp()

    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    has_keyword = "0,1,2,3\nagri1,0,0,0"

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, f"{output_f}.csv"), "w") as f:
        f.write(has_keyword)

    r = nk()

    assert r == False


def test_not_supported_file():
    nk = NoKeywords()
    nk = monkey_patch_client(nk)

    outputs = tempfile.mkdtemp()

    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    has_keyword = "0,1,2,3\nagri1,0,0,0"

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, f"{output_f}.huh"), "w") as f:
        f.write(has_keyword)

    r = nk()

    assert r == False


def test_l33t_sp33k():
    """Currently l33t sp33k would pass
    """
    nk = NoKeywords()
    nk = monkey_patch_client(nk)

    outputs = tempfile.mkdtemp()

    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    #  * here we use 1 in place of i
    has_keyword = "0,1,2,3\nagr11,0,0,0"

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, f"{output_f}.csv"), "w") as f:
        f.write(has_keyword)

    r = nk()

    # TODO: * ideally this should be false
    assert r == True


def test_multiple_files():
    nk = NoKeywords()
    nk = monkey_patch_client(nk)

    outputs = tempfile.mkdtemp()

    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    # this file is OK
    does_not_have_keyword = "0,1,2,3\n0,0,0,0"

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, f"{output_f}.csv"), "w") as f:
        f.write(does_not_have_keyword)

    has_keyword = "0,1,2,3\n0,agri3,2,3"

    # this file is not OK
    with open(os.path.join(outputs, f"{output_f}_2.csv"), "w") as f:
        f.write(has_keyword)

    r = nk()

    assert r == False


def test_multiple_categories():
    nk = NoKeywords()

    r = {
        "service": [
            {
                "type": "metadata",
                "attributes": {
                    "additionalInformation": {
                        "categories": [
                            "Agriculture & Bio Engineering",
                            "Computer Technology",
                        ]
                    }
                },
            }
        ]
    }

    nk = monkey_patch_client(nk, out=r)

    outputs = tempfile.mkdtemp()

    os.environ["OUTPUTS"] = outputs
    os.environ["DIDS"] = '["a12345678"]'

    did = json.loads(os.getenv("DIDS"))

    has_keyword = "0,1,2,3\ncomp1,0,0,0"

    output_f = tempfile.gettempprefix()
    with open(os.path.join(outputs, f"{output_f}.csv"), "w") as f:
        f.write(has_keyword)

    r = nk()

    assert r == False
