"""Save compact immutable source milestones without ROMs or capture forests."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
Q = R / "docs/qa/checkpoints/2026-10-30"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def archive(out, files, receipt):
    assert not out.exists()
    out.mkdir(parents=True)
    target = out / "source-and-controls.zip"
    members = sorted(set(files) | {Path(__file__).resolve()})
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=7) as z:
        for p in members:
            assert p.is_file() and p.suffix.lower() not in {".nes", ".exe", ".o", ".dep", ".dbg", ".lbl", ".map", ".mp4", ".avi"}, p
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        for name in z.namelist():
            assert hashlib.sha256(z.read(name)).hexdigest() == sha(R / name), name
    receipt.update(archive_sha256=sha(target), archive_bytes=target.stat().st_size,
                   archive_members=len(members), all_members_verified=True,
                   no_ROM_files=True, root_tool_sha256=sha(__file__))
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(dict(checkpoint=out.name, members=len(members), bytes=target.stat().st_size,
                          verified_bindings=receipt["verified_bindings"])))


def main():
    p = R / "build/ff-fx-palette-lifecycle-v8"
    handoff = p / "handoff.json"
    assert sha(handoff) == "2922f377c941cc3f4c41162acc31d16360298a1df6a2f15dee157cac44b38d32"
    h = json.loads(handoff.read_text())
    assert h["passed"] and not h["native"] and not h["admitted"]
    for name, expected in h["bindings"].items():
        assert sha(name) == expected, name
    files = {handoff}
    for name in h["bindings"]:
        f = Path(name)
        if f.suffix.lower() in {".py", ".s", ".json", ".md", ".patch", ".cfg"} and (
                "ff_fx_palette" in f.name or "ff-palette" in f.name or f.parent == p):
            files.add(f)
    files.update(Path(n) for n in h["retained_negatives"])
    files.update((p / "joint").glob("*.json"))
    files.add(p / "joint/private.cfg")
    archive(Q / "ff-palette-retirement-order-source", files,
            dict(status="PRIVATE_SOURCE_PALETTE_RETIREMENT_ORDER_FIXED",
                 candidate_sha256=h["candidate_sha256"], parent_sha256=h["parent_sha256"],
                 original_handoff_sha256=sha(handoff), verified_bindings=len(h["bindings"]),
                 parent_source_checkpoint="shared-quick-ff-arthur-source/source-lineage.zip",
                 native=False, installed=False, admitted=False, scheduler=False,
                 measured_foreign_normal_NMI_CPU_delta=41,
                 measured_foreign_lag_NMI_IRQ_CPU_delta=0,
                 own_tail_bytes=327, own_tail_free_bytes=138,
                 findings=["Retirement restoration runs before the complete original native palette chain; later native colors win.",
                           "The fixed3color writer matches real C116-mapped UpdateScreen, including both status reads, control mirror and scroll/latch behavior.",
                           "1056 real interrupt pairs and252 lifecycle instruction cuts pass; native deadlines and gameplay cadence are unqualified.",
                           "Near-call wrong-bank BRK, missing second status read and old late-native overwrite negatives remain retained.",
                           "The future world marker and spell palette scheduler are not installed."]))

    p = R / "build/benj-mario-source-art-1030-v1"
    handoff = p / "source-art-proof.json"
    assert sha(handoff) == "64aba62722786b15189bd025ac1bdab392b661fe4d69dbac8803e334d19a1ce8"
    h = json.loads(handoff.read_text())
    assert all(x["passed"] for x in h["checks"].values())
    for b in h["bindings"] + h["outputs"]:
        f = Path(b["path"])
        assert f.stat().st_size == b["bytes"] and sha(f) == b["sha256"], f
    files = set(p.iterdir()) | {Path(b["path"]) for b in h["bindings"]}
    for char in ["mario", "toad", "peach"]:
        files.update((R / f"build/benj-donor-{char}-discovery-1030-v3").glob("*.bin"))
        files.add(R / f"build/benj-donor-{char}-discovery-1030-v3/discovery.json")
    archive(Q / "benj-toad-peach-exact-source-art", files,
            dict(status=h["status"], original_handoff_sha256=sha(handoff),
                 source=h["source"], credit=h["credit"], verified_bindings=len(h["bindings"]) + len(h["outputs"]),
                 donor_API_upload_cases=312, full_source_poses=104,
                 complete_facing_pixel_checks=208, output_CHR_bytes=14336,
                 native=False, installed=False, admitted=False,
                 findings=["Exact requested v44 donor pinned; current author repository only publishes patches and is not substituted for the local v44.",
                           "Real RAM731C frame lookup and fixedE57A/RAM7000 upload recover original whole poses and restore source PRG mapping.",
                           "Two52-pose sets retain native normal/fire artwork and are packed into4 complete8x16 parts per body.",
                           "Peach source float has a60-update budget and related landing/support/ceiling hooks; those mechanics still require host integration.",
                           "No new global ROM/CHR/RAM lease or roster/menu change is made by this asset checkpoint."]))


if __name__ == "__main__":
    main()
