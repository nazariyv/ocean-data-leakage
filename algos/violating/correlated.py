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

    did = did[0]

    l.debug(f"LISTDIR INPUTS:\n{os.listdir(inputs)}")

    input_ = os.path.join(inputs, did, "0")

    df1 = pd.read_csv(input_)
    df1 = df1.apply(lambda col: col + 1)

    outputs = os.getenv("OUTPUTS")

    df1.to_csv(os.path.join(outputs, "output1.csv"))
    l.debug(f'OUTPUTS:\n{os.listdir(os.environ["OUTPUTS"])}')


if __name__ == "__main__":
    main()
