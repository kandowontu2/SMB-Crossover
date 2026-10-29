"""Root review/checkpoint of immutable router and original death sprite units."""
from pathlib import Path
import hashlib
import json
import zipfile
from checkpoint_roster_packets_v1 import archive

ROOT = Path(__file__).resolve().parents[2]
SHA = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    hp = ROOT / "build/nr_router_compact_handoff_v1.json"
    assert SHA(hp) == "353ea30bd7b046133303eacb8510b2423edbe9bd1643353cccb85fcb2fe8c139"
    h = json.loads(hp.read_text())
    for path, expected in h["bindings"].items():
        assert SHA(path) == expected, path
    old = (ROOT / "build/roster-shared-celeste-small-chr-v1.nes").read_bytes()
    new = Path(h["ROM"]).read_bytes()
    changed = [i for i, (x, y) in enumerate(zip(old, new)) if x != y]
    assert len(old) == len(new) and len(changed) == 1067
    assert all((i-16)//8192 == 124 for i in changed)
    assert old[:16] == new[:16] and old[16+1048576:] == new[16+1048576:]
    gap = 16+124*8192+0xda4
    assert new[gap:gap+42] == bytes([255])*42
    for path, expected in h["proofs"].items():
        assert SHA(path) == expected and json.loads(Path(path).read_text())["passed"]
    dest = ROOT / "docs/qa/checkpoints/2026-10-28/router-compaction-source"
    assert not dest.exists()
    dest.mkdir()
    files = [hp, Path(h["source_leaf"]), Path(h["exact_byte_diff"])]
    files += list(map(Path, h["proofs"]))
    files += [ROOT / "build" / n for n in [
        "nr_router_compact_v1.patch", "nr_router_compact_preimage_v1.zip",
        "nr_router_compact_v1.d", "nr_router_compact_build_v1.json",
        "nr_router_compact_matrix_interrupted_v1.json",
        "nr_router_compact_controls_slow_snapshot_v1.py",
        "nr_router_compact_controls_symbol_fixture_negative.py",
        "nr_router_compact_controls_quick_v1.json"]]
    members = {}
    output = dest / "frozen-source-packet.zip"
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path in files:
            name = path.resolve().relative_to(ROOT).as_posix()
            content = path.read_bytes()
            info = zipfile.ZipInfo(name, (2026, 10, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, content)
            members[name] = hashlib.sha256(content).hexdigest()
    with zipfile.ZipFile(output) as z:
        assert {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()} == members
    review = dict(status="Root source review; no shared source adoption or native claim",
                  bindings_verified=len(h["bindings"]), candidate_SHA256=SHA(h["ROM"]),
                  root_byte_diff_verified=1067, only_bank=124,
                  source_review="SavedY/P restored before genuine FarCallCommon+3; target-entry/return and explicit ordered page1 SMC evidence retained",
                  costs="Whole typed GameLoop0..+89CPU; nested Ice/City injury+36/+28. No lag improvement claim.",
                  remaining="Combine rehomed Rogue42B helper atADA4; actual new-character routing and native cadence require separate evidence",
                  errata=h["fixture_errata"], archive_sha256=SHA(output), archive_members=members)
    (dest / "root-review.json").write_text(json.dumps(review, indent=2)+"\n")
    archive("rogue-death-original-art", "build/rogue-dawn-death-art-v1/handoff.json",
            lambda d: d["outputs"] + [{"path": str(ROOT / "tools/prepare_rogue_dawn_death_art_v1.py")}],
            ["build/rogue-dawn-death-art-v1/first-distinct-facing-negative.json"],
            dict(source_frame="35hex", authentic_source_cursorX=24,
                 body_page=689, mirrored_records=["95:DF00", "95:DF19"],
                 actual_host_pixel_cases=40, complete_opaque_pixels=210,
                 remaining="Real source callback/first-record C95 lease/lifecycle and native death motion"))
    print(json.dumps(dict(router_bindings=len(h["bindings"]), router_archive=SHA(output))))


if __name__ == "__main__":
    main()
