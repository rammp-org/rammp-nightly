# rammp-nightly

Nightly integration sets for the RAMMP kinova arm stack. This repo orchestrates the
nightly build, records what was built, and publishes it. It holds no stack code itself.

## What a nightly set is

Each night we take the same-instant dev SHAs of the stack's five repos
(rammp-interfaces-ros2, RAMMP-docker, kinova-gen3-driver, RAMMP-CuRobo, kinova-gen3-ros2),
build them together, and run their CI tests together. If everything is green, that
combination becomes a "blessed set": immutable dated image tags plus a vcstool manifest
pinning the exact SHAs.

The guarantee is compile plus CI tests, together, and nothing more. A set has NOT passed the
Jetson real-time gate or on-arm validation. That is what releases are for.

## Consuming a set

Images (latest known-good, or a pinned dated set):

    docker pull ghcr.io/rammp-org/<image>:nightly
    docker pull ghcr.io/rammp-org/<image>:nightly-YYYYMMDD

From source, using a blessed set's manifest (written under `manifests/kinova-arm/`):

    vcs import src < manifests/kinova-arm/<set>.repos   # once a set has been blessed

## The four images

rammp-base, rammp-cuda, rammp-curobo, kinova-gen3-ros2. rammp-base and rammp-cuda publish
from RAMMP-docker's packages; rammp-curobo and kinova-gen3-ros2 from their own repos'
packages (`ghcr.io/rammp-org/<image>`).

## Immutability

Dated sets (`nightly-YYYYMMDD` tags and their manifests) are never rebuilt or overwritten;
the manifest writer refuses to touch an existing set, and dated tags are never pushed over.
Sets with an `-rcN` suffix (`nightly-YYYYMMDD-rcN`) are rehearsal/pre-flight sets, not nightly
channel sets. The `:nightly` tag moves only when a
whole set goes green.

## Red nights

If any build or test fails, nothing publishes. `:nightly` keeps serving the last green set,
so the channel goes stale but never broken. A `nightly-red` tracking issue in this repo is
the signal that a night failed.

## Phase 0

For now the builds run inside this repo's workflow, because the member repos are frozen and
can't take changes. The target state moves each build behind a `workflow_dispatch` contract
in its own repo, with this repo only dispatching, collecting results, and blessing the set.
