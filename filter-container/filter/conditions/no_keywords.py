import os
import json
import yaml
import logging
import confuse
import pandas as pd
from typing import List

from filter.conditions.utils import validate_inputs_outputs, dataCategory

l = logging.getLogger("[no_keywords]")

SUPPORTED_FILES = ["csv", "txt", "json"]


class NoKeywords:
    """
        Checks whether the file has any forbidden keywords that are "baked into" the
        docker image that the pod will run. This is an immutable solution. For the rationale
        versus picking ConfigMap, check the Readme.md file.

        Limitations: if the malicious agent changes the keywords into leet speak, this
        algorithm won't pick it up. Therefore, a different way to implement this algo
        would be using something like Levenshtein’s edit distance metric or similar.
        That way keywords do not have to be 1-1 exact match. This algorithm is known to
        be O(N * M). This might give hints about how to better implement it:
        https://link.springer.com/chapter/10.1007/978-981-13-0755-3_6

        This is a very computationally expensive condition. For every value in each file
        we need to compare it to the pre-specified keywords. The time complexity of such
        an algorithm is O(X * Y * Z) where X is the number of words in the text file, Y is
        the average number of keywords for a given file type and Z is the number of files
    """

    def __init__(self, hostname: str = None) -> None:
        self.name = "Keywords"
        self.config = confuse.Configuration(__name__)

        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config", "no_keywords.yaml"
        )

        if not os.path.exists(config_path):
            raise ValueError(f"could not find config path in {config_path}")

        with open(config_path, "r",) as f:
            # ! this is not safe, add loader
            y = yaml.load(f)
            self.config.add(y)

        self.dids = json.loads(os.getenv("DIDS", "[]"))
        # ! you need to add an environment variable called ENVIRONMENT in kuberneted, that will tell
        # ! us what environment we are operating it, so that the we use correct keywords from
        # ! no_keywords.yaml. This is only necessary if we will have different keywords for different
        # ! environments
        self.environment = os.getenv("ENVIRONMENT", "development")

    def __call__(self) -> bool:
        """Wrapper for private _check_no_keywords. You can extra stuff here if necessary.

        Returns:
            bool: is condition met? All otuput files do not have any keywords associated
            with their category.
        """
        # ! do not delete from here. we might define dids after instantiation
        # ! for example, in tests
        self.dids = json.loads(os.getenv("DIDS", "[]"))

        if len(self.dids) < 1:
            l.error(
                "no dids, therefore there is nothing to compare against. condition not met"
            )
            return False

        is_valid = self._check_no_keywords()
        return is_valid

    def _check_no_keywords(self) -> bool:
        """We define functions to handle different file types here. We get the list
        of all of the files in the outputs mount and loop through them, determining
        the file extension. Each file has to have a file extension. Once determined,
        we read it and check if it contains the keywords. As you might have guessed,
        the time complexity of such an approach is quite poor.

        Returns:
            bool: all the files won't have any keywords if True. If False, at least
            one file contains at least one keyword.
        """
        # * note that inputs here are not required, but if they are missing
        # * then other conditions won't pass so it does not hurt us to check
        # * outputs here
        is_valid = validate_inputs_outputs()

        outputs_loc = os.getenv("OUTPUTS")  # type: ignore
        output_files = os.listdir(outputs_loc)

        # * poor mypy linting again
        if not all(
            self.check_no_keywords_in_file(os.path.join(outputs_loc, f))  # type: ignore
            for f in output_files
        ):
            return False

        return True

    def check_no_keywords_in_file(self, full_path: str) -> bool:
        parts = os.path.split(full_path)

        if len(parts) < 1:
            l.error(f"unknown error, could not parse file's location: {parts}")
            return False

        file_name = parts[-1]
        extension_parts = file_name.split(".")

        if len(extension_parts) < 1:
            # ! the algorithm must output the file in a known extension
            l.error(f"unknown file extension in: {full_path}, conditions not met")
            return False

        extension = extension_parts[-1]
        extension_lower = extension.lower()

        if extension_lower not in SUPPORTED_FILES:
            l.error(
                f"unsupported file extension in file: {full_path}, supported types are: {SUPPORTED_FILES}"
            )
            return False

        if extension_lower == "csv":
            return self.check_csv(full_path)
        elif extension_lower == "txt":
            return self.check_txt(full_path)
        elif extension_lower == "json":
            return self.check_json(full_path)
        # * to add more here when we support more file types
        else:
            l.error("unknown error")
            return False

        # * never reachable
        return True

    def check_csv(self, file_path: str) -> bool:
        """Loops through every column name and cell value. If anything contains the
        keyword, returns False, i.e. no keyword condition is not met

        Args:
            file_path (str): path of the .csv file to read

        Returns:
            bool: think of this as is_valid. If True, then everything is OK, and there
            are no keywords in the file.
        """
        l.debug(f"checking the csv file for keywords: {file_path}")

        f = pd.DataFrame()

        try:
            f = pd.read_csv(file_path)
        except Exception as e:
            l.error(str(e))
            return False

        # ! all dids other than the first one are ignored
        data_categories = self._get_did_categories(self.dids[0])
        if data_categories[0] == "":
            l.error("could not pull data categories from the meta db")
            return False

        keywords: List[str] = []

        for data_category in data_categories:
            keywords.extend(
                self.config["environments"][self.environment]["keywords"][
                    data_category
                ].get(list)
            )

        for k, v in f.iteritems():
            if k in keywords:
                l.error(f"{k} column from file {file_path} is in keywords: {keywords}")
                return False
            for _v in v:
                if _v in keywords:
                    l.error(
                        f"{_v} value from file {file_path} is in keywords: {keywords}"
                    )
                    return False

        return True

    def check_txt(self, file_path: str) -> bool:
        # ! to be implemented
        raise NotImplementedError("this should be implemented")
        return False

    def check_json(self, file_path: str) -> bool:
        # ! to be implemented
        raise NotImplementedError("this should be implemented")
        return False

    def _get_did_categories(self, did: str) -> List[str]:
        """Brizo pulls the meta for us and gives it to us in the workflow stages input dict.
        We then pull the category from there.

        Args:
            did (str): the identification of the input file

        Returns:
            List[str]: data categories pertaining to the did
        """

        categories = json.loads(os.getenv("DATA_CATEGORIES", "[]"))
        resolved = []

        for category in categories:
            resolved.append(dataCategory(category))

        return resolved
