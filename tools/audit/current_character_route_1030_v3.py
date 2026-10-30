"""Prepare or run one bounded current-build controller-only character route.

Reuse the tracked compact-lossless observer and its genuine native hooks.
Extend its graph reader to the real32-cell roster; never modify frozen helpers.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / "tools/audit"), str(R / "tools")]
import current_roster_compact_11_v1 as C


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def navigation(raw, location, target):
    edges = {key: list(raw[location("X5Menu" + key.title()):location("X5Menu" + key.title()) + 32])
             for key in ("left", "right", "up", "down")}
    assert all(0 <= v < 32 for row in edges.values() for v in row)
    answer = []
    for start in range(32):
        queue, seen = [(start, [])], {start}
        for node, route in queue:
            if node == target:
                answer.append(route[0] if route else "")
                break
            for key, table in edges.items():
                nxt = table[node]
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, route + [key]))
        else:
            raise AssertionError("Native roster graph cannot reach selected identity")
    return answer


def prepare(args):
    C.BASE.update(celeste=(0, 0, "MarioVariant", 4), popo=(19, 20, "IcVariant", 0),
                  nana=(19, 20, "IcVariant", 1))
    C.navigation = navigation
    C.SCRIPT = R / "tools/audit/current_character_sparse_11_1030_v1.lua"
    C.MARKERS = ["first-active", "mushroom", "wall-contact", "flower", "dash", "flagpole", "endpoint", "failure"]
    args.policy = args.policy.resolve()
    args.replay = None
    C.prepare(args)
    out = args.output.resolve()
    ready = out / "ready.json"
    data = json.loads(ready.read_text())
    # The old isolated runner expects an obsolete source anchor. Its printed
    #600s command is not used. The bound packet below uses the current driver
    #with its real SMB_RUN_OUTPUT interface and a stricter native reservation.
    packet = dict(prepared=True, native=False, ROM_sha256=args.expected_sha256,
                  ROM=str(args.rom.resolve()), ready=str(ready), ready_sha256=sha(ready),
                  script=str(out / "run.lua"), maximum_emulated_frames=args.frames,
                  emulator="C:/mesen2/Mesen.exe", emulator_timeout_seconds=45,
                  process_timeout_seconds=60, capture_bytes=512 * 1024 * 1024,
                  capture_files=64, maximum_selected_PNG_frames=8,
                  settings=["--doNotSaveSettings", "--nes.removeSpriteLimit=false",
                            "--nes.ramPowerOnState=AllZeros", "--nes.randomizeCpuPpuAlignment=false",
                            "--nes.randomizeMapperPowerOnState=false"],
                  bindings=data["bindings"] | {str(Path(__file__).resolve()): sha(__file__)},
                  route_scope="Natural cold controller selection; no cheats or emulated writes. Source-independent native endpoints and physical OAM/CHR/interrupt checks; selected visual review required separately.")
    p = out / "native-packet.json"
    assert not p.exists()
    p.write_text(json.dumps(packet, indent=2) + "\n")
    print(json.dumps(dict(packet=str(p), packet_sha256=sha(p), run_not_started=True)))


def run(args):
    p = args.packet.resolve()
    h = json.loads(p.read_text())
    assert h["prepared"] and not h["native"]
    assert sha(h["ROM"]) == h["ROM_sha256"] and sha(h["ready"]) == h["ready_sha256"]
    assert all(sha(name) == expected for name, expected in h["bindings"].items())
    assert h["capture_bytes"] == 512 * 1024 * 1024 and h["capture_files"] == 64
    assert h["emulator_timeout_seconds"] == 45 and h["process_timeout_seconds"] == 60
    active = subprocess.run(["powershell", "-NoProfile", "-Command",
                             "Get-CimInstance Win32_Process -Filter \"Name='Mesen.exe'\" | Select-Object -ExpandProperty ProcessId"],
                            capture_output=True, text=True, check=True).stdout.strip()
    assert not active, "An existing Mesen process is live; do not launch or touch it"
    out = p.parent
    assert not (out / "native-launch.json").exists(), "No automatic retry of a native packet"
    import audit.capture_budget as B
    import run_mesen as M
    assert M.run.__globals__["run_capped"] is B.run_capped, "Guard module identity must match the real driver"
    B.RUN_BYTES = h["capture_bytes"]
    B.PAYLOAD_BYTES = B.RUN_BYTES - 1_000_000
    original_preflight = B.preflight
    B.preflight = lambda output: original_preflight(output, reserved_bytes=B.RUN_BYTES, reserved_files=64)
    os.environ["SMB_RUN_OUTPUT"] = str(out)
    (out / "native-launch.json").write_text(json.dumps(dict(packet_sha256=sha(p),
        exact_ROM_sha256=h["ROM_sha256"], no_existing_Mesen=True, automatic_retries=False,
        capture_bytes=B.RUN_BYTES, process_timeout_seconds=60), indent=2) + "\n")
    code = M.run(Path(h["script"]), Path(h["ROM"]), h["emulator"],
                 h["emulator_timeout_seconds"], emulator_options=h["settings"])
    print(json.dumps(dict(native_exit_code=code, output=str(out))))
    return code


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="action", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--identity", choices=["celeste", "popo", "nana"], required=True)
    p.add_argument("--mode", choices=["easy", "hard"], default="easy")
    p.add_argument("--rom", type=Path, required=True)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--frames", type=int, default=6000)
    p.add_argument("--policy", type=Path, required=True)
    p = sub.add_parser("run")
    p.add_argument("--packet", type=Path, required=True)
    args = ap.parse_args()
    return prepare(args) if args.action == "prepare" else run(args)


if __name__ == "__main__":
    raise SystemExit(main())
