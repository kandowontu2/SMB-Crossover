"""Bounded, controller-only 1-1 discovery for the eight new SMB2/FF identities.

Reuse existing native observers without changing frozen helpers. A route result
does not establish every powerup, an independent replay, or every-frame art QA.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / "tools/audit"), str(R / "tools")]
import current_roster_compact_11_v1 as C
from current_character_route_1030_v4 import navigation

IDENTITIES = {
    "smb2-mario": (24, 25, "S2Variant", 0),
    "smb2-luigi": (24, 25, "S2Variant", 1),
    "smb2-toad": (24, 25, "S2Variant", 2),
    "smb2-peach": (24, 25, "S2Variant", 3),
    "ff-fighter": (21, 22, "FfVariant", 0),
    "ff-white-mage": (21, 22, "FfVariant", 1),
    "ff-black-mage": (21, 22, "FfVariant", 2),
    "ff-thief": (21, 22, "FfVariant", 3),
}


def prepare(a):
    source = a.source_handoff.resolve()
    assert C.sha(source) == a.expected_source_sha256
    handoff = json.loads(source.read_text(encoding="utf-8"))
    assert handoff["source"] and handoff["candidate"] == a.expected_sha256
    for path, digest in handoff["bindings"].items():
        assert C.sha(path) == digest, ("Source dependency changed", path)
    C.BASE.update(IDENTITIES)
    C.navigation = navigation
    C.SCRIPT = R / "tools/audit/current_ice_sparse_11_1030_v1.lua"
    a.policy = R / "tools/playthroughs/full_roster_policy_og.lua"
    a.replay = None
    C.prepare(a)
    out = a.output.resolve()
    ready = out / "ready.json"
    data = json.loads(ready.read_text(encoding="utf-8"))
    bindings = handoff["bindings"] | data["bindings"]
    bindings |= {str(source): C.sha(source), str(Path(__file__)): C.sha(__file__),
                 str(R / "tools/audit/current_character_route_1030_v4.py"):
                 C.sha(R / "tools/audit/current_character_route_1030_v4.py")}
    packet = dict(
        prepared=True, native=False, ROM=str(a.rom.resolve()),
        ROM_sha256=a.expected_sha256, source=str(source),
        source_sha256=C.sha(source), ready=str(ready), ready_sha256=C.sha(ready),
        script=str(out / "run.lua"), maximum_emulated_frames=a.frames,
        emulator="C:/Mesen2/Mesen.exe", emulator_timeout_seconds=105,
        process_timeout_seconds=120, capture_bytes=512 * 1024 * 1024,
        capture_files=64, maximum_selected_PPU_frames=8,
        settings=["--doNotSaveSettings", "--nes.removeSpriteLimit=false",
                  "--nes.ramPowerOnState=AllZeros",
                  "--nes.randomizeCpuPpuAlignment=false",
                  "--nes.randomizeMapperPowerOnState=false"],
        bindings=bindings,
        scope="Cold boot, genuine menu selection and zero-death 1-1 discovery "
              "to controlled 1-2. No cheats or emulated writes. Existing OAM, "
              "physical CHR, camera and interrupt guards retained. Eight selected "
              "whole PPU screens maximum; not all abilities or every-frame review.",
    )
    target = out / "native-packet.json"
    assert not target.exists()
    target.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(prepared=str(target), sha256=C.sha(target),
                          launched=False, dependencies=len(bindings))))


def run(a):
    packet = a.packet.resolve()
    h = json.loads(packet.read_text(encoding="utf-8"))
    assert h["prepared"] and not h["native"]
    assert C.sha(h["ROM"]) == h["ROM_sha256"]
    assert C.sha(h["source"]) == h["source_sha256"]
    assert C.sha(h["ready"]) == h["ready_sha256"]
    for path, digest in h["bindings"].items():
        assert C.sha(path) == digest, ("Packet dependency changed", path)
    assert h["capture_bytes"] == 536870912 and h["capture_files"] == 64
    assert h["emulator_timeout_seconds"] == 105
    assert h["process_timeout_seconds"] == 120
    active = subprocess.run([
        "powershell", "-NoProfile", "-Command",
        "Get-CimInstance Win32_Process -Filter \"Name like '%Mesen%'\" | "
        "Select-Object ProcessId,Name | ConvertTo-Json -Compress",
    ], capture_output=True, text=True, check=True).stdout.strip()
    if active:
        print(json.dumps(dict(launched=False, reason="Existing Mesen left alone",
                              processes=active)))
        return 3
    out = packet.parent
    assert not (out / "native-launch.json").exists(), "No automatic native retry"
    import audit.capture_budget as B
    import run_mesen as M
    assert M.run.__globals__["run_capped"] is B.run_capped
    B.RUN_BYTES = h["capture_bytes"]
    B.PAYLOAD_BYTES = B.RUN_BYTES - 1_000_000
    preflight = B.preflight
    B.preflight = lambda output: preflight(output, reserved_bytes=B.RUN_BYTES,
                                           reserved_files=h["capture_files"])
    os.environ["SMB_RUN_OUTPUT"] = str(out)
    (out / "native-launch.json").write_text(json.dumps(dict(
        packet_sha256=C.sha(packet), ROM_sha256=h["ROM_sha256"],
        no_existing_Mesen=True, automatic_retries=False,
        capture_bytes=B.RUN_BYTES, process_timeout_seconds=120,
    ), indent=2) + "\n", encoding="utf-8")
    code = M.run(Path(h["script"]), Path(h["ROM"]), h["emulator"],
                 h["emulator_timeout_seconds"], emulator_options=h["settings"])
    print(json.dumps(dict(native_exit_code=code, output=str(out))))
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--identity", choices=IDENTITIES, required=True)
    p.add_argument("--mode", choices=("easy", "hard"), default="easy")
    p.add_argument("--rom", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--source-handoff", type=Path, required=True)
    p.add_argument("--expected-source-sha256", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--frames", type=int, default=8000)
    p = sub.add_parser("run")
    p.add_argument("--packet", type=Path, required=True)
    p = sub.add_parser("review")
    p.add_argument("--ready", type=Path, required=True)
    p.add_argument("--sheet", action="store_true")
    p.add_argument("--compare", type=Path)
    a = parser.parse_args()
    if a.action == "prepare":
        return prepare(a)
    if a.action == "review":
        return C.review(a)
    return run(a)


if __name__ == "__main__":
    raise SystemExit(main())
