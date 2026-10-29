"""Save reviewed private source units, with their native/integration limits.

Never copies cartridge/debug/object files or a capture tree. Historical negative
receipts are byte-bound historical evidence, not reclassified as release tests.
"""
from pathlib import Path
import hashlib
import json
import zipfile
from checkpoint_roster_packets_v1 import ROOT, DEST, archive, verify


def binding(path):
    p = Path(path).resolve()
    data = p.read_bytes()
    return dict(path=str(p), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def goku():
    handoff = ROOT / "build/dragon-power-movement-v1/handoff.json"
    h = json.loads(handoff.read_text())
    seen = {}
    verify(h, seen)
    for key in ["bindings", "actual_ASM_dependencies"]:
        for p, digest in h[key].items():
            b = binding(p)
            assert b["sha256"] == digest, p
            seen[p] = digest
    folder = handoff.parent
    allowed = {".s", ".inc", ".cfg", ".patch", ".json", ".txt", ".d", ".c", ".log"}
    files = [Path(p) for p in h["bindings"] if Path(p).is_relative_to(folder)
             and Path(p).suffix in allowed]
    files += [Path(p) for p in h["owned_new_tools"]]
    files += [ROOT / "build/dragon_power_movement_host_v1.inc",
              ROOT / "docs/qa/dragon-power-movement-host-2026-10-28.txt", handoff]
    target = DEST / "goku-real-main-movement-source"
    assert not target.exists()
    target.mkdir()
    members = {}
    with zipfile.ZipFile(target / "frozen-source-packet.zip", "w", zipfile.ZIP_DEFLATED,
                         compresslevel=9) as z:
        for p in dict.fromkeys(files):
            content = p.read_bytes()
            name = p.resolve().relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, (2026, 10, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, content)
            members[name] = hashlib.sha256(content).hexdigest()
    with zipfile.ZipFile(target / "frozen-source-packet.zip") as z:
        assert {n: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist()} == members
    review = dict(status="Root-reviewed PRIVATE source/CPU movement checkpoint; no playable or native admission",
                  handoff=binding(handoff), candidate=h["candidate"],
                  verified_actual_ASM_dependencies=len(h["actual_ASM_dependencies"]),
                  verified_all_plain_bindings=len(h["bindings"]),
                  verified_unique_bindings=len(seen), archive_members=members,
                  archive=binding(target / "frozen-source-packet.zip"),
                  explicit_limits=h["limits"],
                  historical_scope="Earlier failed/provisional receipts retain their original hash/scope; only release/final receipts qualify current9c7b",
                  original_bound_files=seen)
    (target / "root-review.json").write_text(json.dumps(review, indent=2)+"\n")
    print(json.dumps(dict(checkpoint=str(target.relative_to(ROOT)),
                          unique_bindings=len(seen), archived_files=len(members))))


def rogue():
    folder = ROOT / "build/rogue-dawn-audio-source-v2"
    folder.mkdir(exist_ok=True)
    path = folder / "handoff.json"
    assert not path.exists()
    owned = [ROOT / "tools/audit" / (name+".py") for name in [
        "rogue_dawn_audio_closure_v1", "rogue_dawn_audio_campaigns_v1", "rogue_dawn_audio_context_v1"]]
    owned += [ROOT / "docs/qa" / name for name in [
        "rogue-dawn-audio-source-closure-2026-10-28.json",
        "rogue-dawn-audio-campaigns-2026-10-28.json",
        "rogue-dawn-audio-weapon-context-2026-10-28.json"]]
    data = dict(status="Original-cartridge source observations only; NO assembled host audio port or allocation qualification",
                owned_files=[binding(p) for p in owned],
                limits="Static1231 instruction CFG plus69409 original source callbacks and288 context cases/27648 updates. Code/data relocation, full data-bound closure, atomic cues, host mixer/RAM/leases/NMI/DMC/native audio remain open.")
    path.write_text(json.dumps(data, indent=2)+"\n")
    archive("rogue-actual-audio-source-observations", str(path.relative_to(ROOT)),
            lambda d: d["owned_files"], [],
            dict(original_only=True, actual_static_instructions=1231,
                 original_callbacks=69409, context_cases=288, context_updates=27648,
                 candidate_storage="97:A480..BFFF7040B (A770-only proposal insufficient); MIKE_GFX0000..0408 preserved; full fit not qualified",
                 foreground_reads="010E RdMissileMode;6878 RdGear;0308 RdVY;061F RdBeamSfx",
                 limitations=data["limits"]))


def main():
    archive("smb2-authentic-audio-source", "build/smb2-roster-audio-v1/handoff.json",
            lambda d: d["owned_files"] + [r for r in d["output_bindings"]
                if Path(r["path"]).suffix in {".json", ".txt", ".s", ".c", ".log", ".d"}],
            [], dict(original_compiled_calls=11580, IRQ_sites=837,
                     A74_code_bytes=2817, C117_data_bytes=5623, C117_remaining_bytes=9,
                     preserved_samples="Seven complete payloads plus original DrumA prefix/length/rate; same-final127 clones119/120/125",
                     open="Actual Main cue protocol, NMI/lag scheduler, channel/status/DMC mixer and owner transitions, native timing/listening; not playable"))
    goku()
    rogue()


if __name__ == "__main__":
    main()
