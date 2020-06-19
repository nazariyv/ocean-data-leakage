import logging
import sys

root = logging.getLogger()
if root.hasHandlers():
    root.handlers = []
root.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s |"
    " [%(filename)s:%(lineno)s - %(funcName)s()]"
)
stdout_handler.setFormatter(formatter)
root.addHandler(stdout_handler)
l = root
