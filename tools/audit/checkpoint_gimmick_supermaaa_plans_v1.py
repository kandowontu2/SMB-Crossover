"""Preserve verified source plans and record nonoverlapping private reservations."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools/audit"), str(ROOT / "tools")]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from checkpoint_roster_packets_v1 import verify


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bound(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    gimmick = ROOT / "build/gimmick-source-handoff-v1.json"
    maaa = ROOT / "build/supermaaa-neck-audit-v1/host-plan.json"
    assert sha(gimmick) == "36aebf51909b65be5005ae600ea10ba94fb96cec8a1f9264501d160ac3ffdc2c"
    assert sha(maaa) == "d301c9d8abd638db5305c6f6ba26c1642d238fc978db76d1add7758ba031f9e3"
    gh = json.loads(gimmick.read_text())
    mh = json.loads(maaa.read_text())
    verified = {}
    verify(gh, verified)
    for path, digest in mh["bindings"].items():
        assert sha(path) == digest, path
        verified[str(Path(path).resolve())] = digest
    parent = ROOT / "build/pit-retold-host-v3/candidate.nes"
    assert sha(parent) == "ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2"
    b = scoped_load(parent)
    reservations = []
    spans = [
        ("SuperMaaa", 66, 0x1680, 0x19A8, "A", "state/terrain/cold"),
        ("SuperMaaa", 68, 0x1B20, 0x1F20, "C", "pose construction/data; replaces conflicting C73 proposal"),
        ("Gimmick", 24, 0x0E80, 0x1C00, "A", "core"),
        ("Gimmick", 122, 0x1740, 0x2000, "A", "core"),
        ("Gimmick", 75, 0x19C0, 0x2000, "A", "optional cold core"),
        ("Gimmick", 73, 0x1920, 0x2000, "C", "source art records/tables"),
    ]
    for owner, bank, lo, hi, window, role in spans:
        data = b["raw"][16 + bank * 8192 + lo:16 + bank * 8192 + hi]
        assert data == bytes([255]) * (hi - lo), (owner, bank)
        emitted = []
        for segment in b["segs"].values():
            if "ooffs" not in segment or not int(segment["size"], 0):
                continue
            offset = int(segment["ooffs"], 0) - 16
            if offset // 8192 != bank:
                continue
            start = offset % 8192
            end = start + int(segment["size"], 0)
            assert hi <= start or lo >= end, (owner, segment)
            emitted.append(dict(name=segment["name"].strip('"'), offset=[start, end]))
        base = 0xA000 if window == "A" else 0xC000
        reservations.append(dict(owner=owner, physical_bank=bank, offset=[lo, hi],
                                 CPU_window=window, start=hex(base + lo), end_exclusive=hex(base + hi),
                                 bytes=hi - lo, role=role, FF_preimage=True,
                                 no_emitted_segment_overlap=True, emitted_owners=emitted))
    for i, a in enumerate(reservations):
        for z in reservations[i + 1:]:
            if a["physical_bank"] == z["physical_bank"]:
                assert a["offset"][1] <= z["offset"][0] or z["offset"][1] <= a["offset"][0]
    chr_reservations = []
    for owner, first, count in [("SuperMaaa", 813, 3), ("Gimmick", 816, 4)]:
        at = 16 + 1048576 + first * 1024
        assert b["raw"][at:at + count * 1024] == bytes(count * 1024)
        chr_reservations.append(dict(owner=owner, first=first, last=first + count - 1,
                                     bytes=count * 1024, zero_preimage=True))
    receipt = ROOT / "docs/qa/gimmick-supermaaa-private-reservations-2026-10-29.json"
    assert not receipt.exists()
    output = dict(
        status="Exclusive private reservations; no host implementation or native admission in this receipt",
        parent=[bound(parent), bound(parent.with_suffix(".dbg")), bound(parent.with_suffix(".lbl"))],
        frozen_source_plans=[bound(gimmick), bound(maaa)],
        verified_source_bindings=len(verified), PRG=reservations, CHR=chr_reservations,
        RAM=[dict(owner="SuperMaaa", span="5C7F", gate="raw0/MarioVariant2", condition="Constructor before reads; prove scene/global clear and true-life reset"),
             dict(owner="Gimmick", span="5C00..5C7F", gate="raw26", condition="Keep own12 persistent bytes inside active128; retain own same-life scenes, constructor before reads")],
        authored_pickup_policy=dict(Gimmick_mushroom="Source capacity/refill cap4", Gimmick_flower="Physical earned native-special inventory reward, alternating source type1/type2", Easy="Host ordinary stomp allowed", Hard="Native star attacks and support"),
        open_before_using_PRG="Owner must close genuine absolute/indirect/native code-as-data extents and final private union, not only FF or linker segment gaps. No additional private lease conflicts known at reservation time.",
        explicit_exclusions=["Maaa original C73:D980..<DD80 proposal superseded, never allocated", "Rogue upper audio91/92/99 tails retained", "No new5F RAM", "No shared installed source/Downloads/native emulator changes"],
        audio_limit="Gimmick source uses3 Sunsoft5B voices plus APU/DPCM; deliberate MMC5 arrangement and original callback scheduling still required. Gameplay/art may proceed privately meanwhile.",
        tool=bound(__file__),
    )
    receipt.write_text(json.dumps(output, indent=2) + "\n")
    wrapper = dict(mh)
    wrapper.update(status="Frozen original-source CPU plan; private implementation authorized separately",
                   actual_ASM_dependencies={},
                   original_handoff=bound(maaa), reservation_receipt=bound(receipt),
                   owned_files=[bound(ROOT / p) for p in [
                       "tools/audit/supermaaa_neck_source_v1.py",
                       "tools/audit/supermaaa_neck_host_plan_v1.py",
                       "docs/qa/supermaaa-neck-source-and-host-plan-2026-10-29.txt"]],
                   limits="Original bounded CPU evidence only; no complete Main/NMI/native or implemented host claim.")
    wrapper_path = maaa.parent / "root-handoff.json"
    assert not wrapper_path.exists()
    wrapper_path.write_text(json.dumps(wrapper, indent=2) + "\n")
    for handoff, name in [(gimmick, "gimmick-original-source-and-host-plan"),
                          (wrapper_path, "supermaaa-original-source-and-host-plan")]:
        subprocess.run([sys.executable, "-B", str(ROOT / "tools/audit/checkpoint_roster_component_v5.py"),
                        "--handoff", str(handoff), "--name", name,
                        "--extra", str(receipt), "--extra", str(Path(__file__).resolve())], check=True, cwd=ROOT)
    progress = ROOT / "docs/qa/new-character-source-progress-2026-10-28.json"
    state = json.loads(progress.read_text())
    state["Gimmick_original_source_found"].update(
        status="Frozen byte-exact original-source plan; private gameplay/art implementation now active under nonoverlapping reservations. Native and Sunsoft5B arrangement remain open.",
        source_handoff=bound(gimmick), checkpoint="checkpoints/2026-10-28/gimmick-original-source-and-host-plan")
    state["SuperMaaa_source_plan"] = dict(
        status="Six original source sections and full8KBCHR match;2051 bounded CPU controls; private implementation active, no host/native qualification yet.",
        source_handoff=bound(maaa), checkpoint="checkpoints/2026-10-28/supermaaa-original-source-and-host-plan",
        controls="No neck button; +1px per actual game-timer decrement, cap160; normal shell/Goomba stomp halves; true life loss clears.",
        caveat="Original long-neck scan costs4052..5021CPU and coin callbacks reuse scan scratch; host safety/deadline integration remains required.")
    state["private_reservations"] = bound(receipt)
    progress.write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps(dict(receipt=bound(receipt), frozen_plans=2, native=False)))


if __name__ == "__main__":
    main()
