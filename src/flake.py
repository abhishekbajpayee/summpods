# Shim used to run flake from a Bazel py_test

import os
import sys
import logging
from flake8.api import legacy as flake8

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    root = os.path.dirname(sys.argv[0])
    os.chdir(root)

    style_guide = flake8.get_style_guide(ignore=["E501"])

    input_files = sys.argv[1:]

    report = style_guide.check_files(input_files)

    # check if no errors found
    assert report.get_statistics('E') == []
