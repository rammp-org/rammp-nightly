"""Print a stack file's members as JSON: {name: {url, branch}}."""
import json
import sys

import yaml


def main():
    with open(sys.argv[1]) as f:
        print(json.dumps(yaml.safe_load(f)["members"]))


if __name__ == "__main__":
    main()
