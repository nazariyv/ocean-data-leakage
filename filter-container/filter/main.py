#!/usr/bin/env python
import os
import time
import shutil
import logging

from filter.conditions.no_keywords import NoKeywords
from filter.conditions.not_correlated import NotCorrelated
from filter.conditions.not_encrypted import NotEncrypted
from filter.conditions.small_size import SmallSize

l = logging.getLogger("[privacy_pod]")


def main():
    l.debug("initiating the filtering")
    with open("/etc/hosts", "r") as f:
        l.info(str(f.read()))
    l.debug(os.environ)
    all_conditions = [SmallSize(), NotEncrypted(), NotCorrelated(), NoKeywords()]
    conditions_met = []
    for condition in all_conditions:
        l.info(f"checking {condition.name} condition...")

        r = condition()

        if not r:
            l.warning(
                f"{condition.name} condition not met. overwriting the outputs file"
            )
            outputs = os.getenv("OUTPUTS")

            for filename in os.listdir(outputs):
                file_path = os.path.join(outputs, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    l.warn(f"failed to delete {file_path}. reason: {e}")

            with open(os.path.join(outputs, "output.txt"), "w") as f:
                f.write("contact ocean protocol for support")

            # * early exit
            return

    return


if __name__ == "__main__":
    main()
