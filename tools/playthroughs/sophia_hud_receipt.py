"""Bind passive Sophia HUD command/catch-up evidence; never controls an emulator."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    root = args.folder
    manifest = json.loads((root / "manifest.json").read_text())
    flow = rows(root / "hud-flow.csv")
    consumers = rows(root / "hud-consumer-commands.csv")
    producers = rows(root / "hud-buffer-writes.csv")
    malformed = [r for r in consumers if r["length"] == "0" and r["hi"] not in ("0", "255")]
    examples = []
    for command in malformed[:8]:
        cycle, pointer = int(command["cycle"]), int(command["pointer"])
        before = [r for r in producers if int(r["cycle"]) < cycle and int(r["address"]) == pointer]
        publication = before[-1] if before else None
        setup_cycle = int(publication["cycle"]) if publication else cycle
        prior = lambda name: next((r for r in reversed(flow) if r["event"] == name and int(r["cycle"]) <= setup_cycle), None)
        following = [r for r in producers if int(r["cycle"]) > cycle and int(r["address"]) in (pointer + 1, pointer + 2)][:8]
        examples.append({"consumer": command, "publication": publication,
                         "preceding_catchup": prior("GoToNextFrameImmediately"),
                         "preceding_GameLoop": prior("GameLoop"),
                         "preceding_SetupNums": prior("SetupNums"),
                         "NMI_entry": next((r for r in reversed(flow) if r["event"] == "NMIEntry" and int(r["cycle"]) < cycle), None),
                         "following_producer_writes": following})
    counts = {}
    for name in ("GoToNextFrameImmediately", "GameLoop", "GameLoopProtected", "SetupNums"):
        counts[name] = sum(r["event"] == name and r["NmiDisable"] == "0" and r["ShouldSkipDrawSprites"] == "1" for r in flow)
    protected = [r for r in flow if r["event"] == "GameLoopProtected"]
    setup = [r for r in flow if r["event"] == "SetupNums"]
    protection = {"protected_body_observations": len(protected),
                  "protected_body_not_busy255": [r for r in protected if r["NmiDisable"] != "255"][:8],
                  "SetupNums_observations": len(setup),
                  "SetupNums_not_busy255_count": sum(r["NmiDisable"] != "255" for r in setup)}
    trace = rows(root / "trace.csv")
    inputs = rows(root / "inputs.csv")
    controls = {"host_inputPolled_events": len(inputs), "observed_frames": len(trace),
                "one_host_input_event_each_frame": all(int(r["poll"]) == i and int(r["frame"]) == i for i, r in enumerate(inputs, 1)),
                "qualification": "Host input events are controller delivery only. Skipped NMIs can omit actual4016 sampling; this field does not prove one native read per frame.",
                "stage_entries": json.loads((root / "result.json").read_text())["stage_entries"],
                "furthest_normal_1_1_x": max((int(r["x"]) for r in trace if r["world"] == "0" and r["level"] == "0" and r["engine"] == "8"), default=None)}
    files = ["manifest.json", "result.json", "inputs.csv", "policy.lua", "hud-flow.csv",
             "hud-consumer-commands.csv", "hud-buffer-writes.csv", "hud-port-writes.csv", "hud-state.csv"]
    files += [p.name for p in root.glob("first-bad.*")]
    first_bad = json.loads((root / "first-bad.json").read_text()) if (root / "first-bad.json").exists() else None
    receipt = {"scope": "Passive ordinary-controller diagnostic; not a route proof or final video",
               "rom_sha256": manifest["rom_sha256"], "controller_only": manifest["controller_only"],
               "memory_or_register_writes": manifest["memory_or_register_writes"],
               "result": json.loads((root / "result.json").read_text()),
               "first_bad_static_HUD": first_bad,
               "unprotected_busy0_drawSkip1_counts": counts,
               "candidate_protection": protection, "actual_controller_progression": controls,
               "nonterminator_zero_length_native_commands": len(malformed),
               "partial_command_examples": examples,
               "frame_convention": "physicalFrame is previous endFrame + 1; memory callback RAM is prewrite, eventValue is written value",
               "sha256": {name: sha(root / name) for name in files}}
    out = root / "passive-hud-receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"folder": str(root), "receipt_sha256": sha(out), "first_bad": first_bad,
                      "malformed_commands": len(malformed), "unprotected_counts": counts}))


if __name__ == "__main__":
    main()
