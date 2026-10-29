"""Archive three frozen source packets without copying ROMs or debug trees."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "docs/qa/checkpoints/2026-10-28"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(value, seen):
    if isinstance(value, dict):
        if "path" in value and "sha256" in value:
            path = Path(value["path"])
            data = path.read_bytes()
            assert digest(data) == value["sha256"], str(path)
            assert "bytes" not in value or len(data) == value["bytes"], str(path)
            seen[str(path.resolve())] = value["sha256"]
        for item in value.values():
            verify(item, seen)
    elif isinstance(value, list):
        for item in value:
            verify(item, seen)


def archive(name, handoff_path, rows, extra, scope):
    handoff = ROOT / handoff_path
    data = json.loads(handoff.read_text())
    seen = {}
    verify(data, seen)
    files = [Path(row["path"]) for row in rows(data)] + [handoff]
    files += [ROOT / item for item in extra]
    for path in files:
        if path.suffix == ".json":
            verify(json.loads(path.read_text()), seen)
    target = DEST / name
    assert not target.exists(), str(target)
    target.mkdir()
    members = {}
    with zipfile.ZipFile(target / "frozen-source-packet.zip", "w",
                         compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in dict.fromkeys(files):
            relative = path.resolve().relative_to(ROOT)
            # The four runtime/debug artifacts remain hash-bound references.
            assert path.suffix not in (".nes", ".dbg", ".map"), str(path)
            content = path.read_bytes()
            member = relative.as_posix()
            info = zipfile.ZipInfo(member, (2026, 10, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, content)
            members[member] = digest(content)
    proof = dict(status="Root-verified frozen source checkpoint; no shared or native admission",
                 scope=scope, verified_unique_bindings=len(seen),
                 handoff_sha256=digest(handoff.read_bytes()),
                 archive_sha256=digest((target / "frozen-source-packet.zip").read_bytes()),
                 archive_members=members, original_bound_files=seen)
    with zipfile.ZipFile(target / "frozen-source-packet.zip") as z:
        assert {n: digest(z.read(n)) for n in z.namelist()} == members
    (target / "root-review.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(dict(checkpoint=str(target.relative_to(ROOT)),
                          bindings=len(seen), members=len(members))))


def main():
    archive("rogue-body-f56a-source", "build/rogue-dawn-host-body-v1/handoff.json",
            lambda d: d["owned_publication_files"],
            ["build/rogue-dawn-host-body-v1/hook-address-erratum.json"],
            dict(ROM="f1ed39c8dc5d801567d1f6a5b86e581ed61da19d67f04716daf3c7429391745d",
                 body_bytes=561, remaining_A95_bytes=2045,
                 genuine_ASM_inputs=490, genuine_C_inputs=10,
                 corrected_hook_address="CrossoverBlockSize LOW126:9034 (display erratum only)",
                 verified="Source radii, real platform carry, window0 body ownership, palette0 producer, actual compiled Main/draw callers and finite IRQ seams",
                 open="Actual damage/lifecycle/visibility, typed items, weapons, audio, menu, hardware/native qualification",
                 retained_negative="Foreign Proto lag/catch-up typed fixture BRK0:BB1A on both old and new hashes; no blanket catch-up qualification"))
    # Preserve the original gameplay packet separately; it is not relabelled.
    frozen = json.loads((ROOT / "build/smb2-roster-component-v1/handoff.json").read_text())
    seen = {}
    verify(frozen, seen)
    assert len(seen) == 64
    archive("smb2-palette-c80-source", "build/smb2-roster-palette-v2/handoff.json",
            lambda d: d["owned_files"] + [r for r in d["outputs"]
                                          if Path(r["path"]).suffix not in (".nes", ".dbg")],
            [], dict(frozen_gameplay_bindings_unchanged=64,
                     genuine_farcall_readback_cases=64, actual_IRQ_points=29,
                     change="C80 palette pointers remain readable after ordinary A-window farcall restoration",
                     open="Actual shared palette composition, all-area colors and native display; eye/object role is original world1 only"))
    archive("smb2-audio-roll-prerequisite-plan", "build/smb2-roster-audio-plan-v1-handoff.json",
            lambda d: d["owned"] + [d["receipt"]],
            ["build/smb2-roster-audio-plan-v1-first-setup-negative.txt"],
            dict(read_only=True, incoming_Roll_far_calls=31,
                 core_destination="79:AB00..B5E0", world_destination="78:B000..BCC6",
                 source_audio_spans="74:B180..BFFF and117:CA00..DFFF",
                 original_immutable_noise_code_view_bytes=256,
                 open="Actual relocation and caller qualification, source audio implementation, final127 mirrors, DPCM and host/NMI lifecycle"))


if __name__ == "__main__":
    main()
