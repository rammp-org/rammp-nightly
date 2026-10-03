import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STACK = ROOT / "stacks" / "kinova-arm.yml"
MEMBERS = ["rammp-interfaces-ros2", "RAMMP-docker", "kinova-gen3-driver",
           "RAMMP-CuRobo", "kinova-gen3-ros2"]
SHAS = {n: f"{i:040x}" for i, n in enumerate(MEMBERS, 1)}
DIGESTS = {img: f"sha256:{i:064x}" for i, img in enumerate(
    ["rammp-base", "rammp-cuda", "rammp-curobo", "kinova-gen3-ros2"], 1)}


def run(tmp_path, shas=SHAS, digests=DIGESTS, set_id="nightly-20261002"):
    (tmp_path / "shas.json").write_text(json.dumps(shas))
    (tmp_path / "digests.json").write_text(json.dumps(digests))
    return subprocess.run(
        [sys.executable, ROOT / "scripts" / "write_manifest.py",
         "--stack", STACK, "--set-id", set_id,
         "--shas", tmp_path / "shas.json",
         "--digests", tmp_path / "digests.json",
         "--out-dir", tmp_path / "out"],
        capture_output=True, text=True)


def test_writes_vcstool_repos_and_images_json(tmp_path):
    r = run(tmp_path)
    assert r.returncode == 0, r.stderr
    repos = yaml.safe_load((tmp_path / "out" / "nightly-20261002.repos").read_text())
    assert repos["repositories"]["kinova-gen3-driver"] == {
        "type": "git",
        "url": "https://github.com/rammp-org/kinova-gen3-driver.git",
        "version": SHAS["kinova-gen3-driver"]}
    assert set(repos["repositories"]) == set(MEMBERS)
    images = json.loads(
        (tmp_path / "out" / "nightly-20261002.images.json").read_text())
    assert images["set"] == "nightly-20261002"
    assert images["stack"] == "kinova-arm"
    assert images["images"] == DIGESTS


def test_refuses_existing_set(tmp_path):
    assert run(tmp_path).returncode == 0
    second = run(tmp_path)
    assert second.returncode == 1
    assert "already exists" in second.stderr


def test_refuses_missing_member_sha(tmp_path):
    incomplete = {k: v for k, v in SHAS.items() if k != "RAMMP-CuRobo"}
    r = run(tmp_path, shas=incomplete, set_id="nightly-20261003")
    assert r.returncode == 1
    assert "RAMMP-CuRobo" in r.stderr


def test_refuses_malformed_set_id(tmp_path):
    for bad in ["20261002", "nightly-2026", "nightly-20261002-rc", "../x"]:
        r = run(tmp_path, set_id=bad)
        assert r.returncode == 1, bad
        assert "set-id" in r.stderr


def test_accepts_rc_set_id(tmp_path):
    assert run(tmp_path, set_id="nightly-20261002-rc12").returncode == 0


def test_refuses_missing_image_digest(tmp_path):
    r = run(tmp_path, digests={k: v for k, v in DIGESTS.items()
                               if k != "rammp-cuda"})
    assert r.returncode == 1
    assert "rammp-cuda" in r.stderr


def test_refuses_extra_image_digest(tmp_path):
    r = run(tmp_path, digests={**DIGESTS, "surprise": "sha256:0"})
    assert r.returncode == 1
    assert "surprise" in r.stderr
