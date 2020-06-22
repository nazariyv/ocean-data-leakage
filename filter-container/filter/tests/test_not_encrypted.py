import pytest  # type: ignore
import os

from filter.conditions.not_encrypted import NotEncrypted


@pytest.fixture(autouse=True)
def clean_env_vars_before_tests():
    os.environ["OUTPUTS"] = ""
    os.environ["INPUTS"] = ""
    os.environ["DIDS"] = "[]"
    yield


def test_entropy_end_to_end_csv():
    folder_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "not_encrypted"
    )
    file_loc = os.path.join(folder_loc, "s1.csv")
    assert os.path.exists(file_loc)

    os.environ["OUTPUTS"] = folder_loc

    ent = NotEncrypted()
    is_valid = ent()

    assert is_valid == True

    block_entropies = ent.results

    assert len(block_entropies) > 0
    assert all(e.entropy > 0 and e.entropy <= 1 for e in block_entropies)


def test_entropy_end_to_end_zip():
    folder_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "encrypted"
    )
    file_loc = os.path.join(folder_loc, "s1.zip")
    assert os.path.exists(file_loc)

    os.environ["OUTPUTS"] = folder_loc

    ent = NotEncrypted()
    is_valid = ent()

    assert is_valid == False

    block_entropies = ent.results

    assert len(block_entropies) > 0
    assert all(e.entropy > 0 and e.entropy <= 1 for e in block_entropies)


def test_encrypted_entropy_higher():
    """A good rule of thumb is that the zipped / encrypted file should have
    higher entropy than the unzipped one.
    """
    unzipped_folder_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "not_encrypted"
    )
    unzipped_file_loc = os.path.join(unzipped_folder_loc, "s1.csv")
    zipped_folder_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "encrypted"
    )
    zipped_file_loc = os.path.join(zipped_folder_loc, "s1.zip")

    assert os.path.exists(unzipped_file_loc)
    assert os.path.exists(zipped_file_loc)

    ent = NotEncrypted()

    os.environ["OUTPUTS"] = unzipped_folder_loc
    unzipped_is_valid = ent()
    unzipped_entropies = ent.results

    os.environ["OUTPUTS"] = zipped_folder_loc
    zipped_is_valid = ent()
    zipped_entropies = ent.results

    assert all(
        e1.entropy < e2.entropy for e1, e2 in zip(unzipped_entropies, zipped_entropies)
    )
