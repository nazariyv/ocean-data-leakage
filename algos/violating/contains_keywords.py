#!/usr/bin/env python
# type: ignore
import pandas as pd
import logging
import os

l = logging.getLogger("[algo_log]")
l.setLevel("DEBUG")
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sh.setFormatter(formatter)
l.addHandler(sh)


def main():
    df = pd.DataFrame.from_dict({"c": [7, "fractals", 9], "d": [10, 11, 12]})

    outputs = os.getenv("OUTPUTS")

    df.to_csv(os.path.join(outputs, "output2.csv"))


if __name__ == "__main__":
    main()
