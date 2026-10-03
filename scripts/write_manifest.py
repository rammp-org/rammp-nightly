"""Write an immutable blessed set: <id>.repos (vcstool) + <id>.images.json."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--stack", required=True)
    p.add_argument("--set-id", required=True)
    p.add_argument("--shas", required=True)
    p.add_argument("--digests", required=True)
    p.add_argument("--out-dir", required=True)
    a = p.parse_args()

    stack = yaml.safe_load(Path(a.stack).read_text())
    shas = json.loads(Path(a.shas).read_text())
    digests = json.loads(Path(a.digests).read_text())

    out = Path(a.out_dir)
    repos_path = out / f"{a.set_id}.repos"
    images_path = out / f"{a.set_id}.images.json"
    for path in (repos_path, images_path):
        if path.exists():
            sys.exit(f"error: {path} already exists; blessed sets are immutable")
    for name in stack["members"]:
        if name not in shas:
            sys.exit(f"error: no SHA for member {name}")

    repos = {"repositories": {
        name: {"type": "git", "url": m["url"], "version": shas[name]}
        for name, m in stack["members"].items()}}
    images = {
        "set": a.set_id,
        "stack": stack["stack"],
        "generated": datetime.now(timezone.utc).isoformat(),
        "images": digests,
    }
    out.mkdir(parents=True, exist_ok=True)
    repos_path.write_text(yaml.dump(repos, sort_keys=False))
    images_path.write_text(json.dumps(images, indent=2) + "\n")


if __name__ == "__main__":
    main()
