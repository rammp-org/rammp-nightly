import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_members_json_round_trips():
    out = subprocess.run(
        [sys.executable, ROOT / "scripts" / "stack_members.py",
         ROOT / "stacks" / "kinova-arm.yml"],
        capture_output=True, text=True, check=True)
    members = json.loads(out.stdout)
    assert set(members) == {"rammp-interfaces-ros2", "RAMMP-docker",
                            "kinova-gen3-driver", "RAMMP-CuRobo",
                            "kinova-gen3-ros2"}
    assert members["RAMMP-docker"]["branch"] == "main"
    assert members["kinova-gen3-driver"]["url"].endswith("kinova-gen3-driver.git")
