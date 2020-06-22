#!/usr/bin/env python
# type: ignore
import pandas as pd
import logging
import os

# ! this is a dummy algo that you may use for your compute job

l = logging.getLogger("[algo_log]")
l.setLevel("DEBUG")
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
l.addHandler(sh)


def main():
    inputs = os.getenv("INPUTS")
    did = os.getenv("DIDS")

    l.debug(f"ENVIRON:\n{os.environ}")
    l.debug(f"INPUTS:\n{inputs}")
    l.debug(f"DID:\n{did}")

    did = did[0]

    l.debug(f"LISTDIR INPUTS:\n{os.listdir(inputs)}")

    df1 = pd.DataFrame.from_dict({"a": [1, 2, 3], "b": [4, 5, 6]})
    df2 = pd.DataFrame.from_dict({"c": [7, 8, 9], "d": [10, 11, 12]})

    outputs = os.getenv("OUTPUTS")

    df1.to_csv(os.path.join(outputs, "output1.csv"))
    df2.to_csv(os.path.join(outputs, "output2.csv"))

    l.debug(f'OUTPUTS:\n{os.listdir(os.environ["OUTPUTS"])}')


if __name__ == "__main__":
    main()
    l.debug(f'OUTPUTS AGAIN:\n{os.listdir(os.environ["OUTPUTS"])}')
