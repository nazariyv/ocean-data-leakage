import pytest  # type: ignore
import os

from filter.conditions.not_encrypted import Entropy


def test_entropy_end_to_end_csv():
    file_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "s1.csv"
    )
    assert os.path.exists(file_loc)

    ent = Entropy()
    block_entropies = ent(file_loc)

    assert len(block_entropies) > 0
    assert all(e.entropy > 0 and e.entropy <= 1 for e in block_entropies)


def test_entropy_end_to_end_zip():
    file_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "s1.zip"
    )
    assert os.path.exists(file_loc)

    ent = Entropy()
    block_entropies = ent(file_loc)

    assert len(block_entropies) > 0
    assert all(e.entropy > 0 and e.entropy <= 1 for e in block_entropies)


def test_encrypted_entropy_higher():
    """A good rule of thumb is that the zipped / encrypted file should have
    higher entropy than the unzipped one.
    """
    unzipped_file_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "s1.csv"
    )
    zipped_file_loc = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "s1.zip"
    )

    file_loc = os.path.join(unzipped_file_loc)
    assert os.path.exists(file_loc)
    file_loc = os.path.join(zipped_file_loc)
    assert os.path.exists(file_loc)

    ent = Entropy()

    unzipped = ent(unzipped_file_loc)
    zipped = ent(zipped_file_loc)

    assert all(e1.entropy < e2.entropy for e1, e2 in zip(unzipped, zipped))
