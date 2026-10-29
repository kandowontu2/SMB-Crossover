"""Freeze the exact native Goku HUD timing diagnosis; this is not a route pass."""
from pathlib import Path
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/audit"))
from checkpoint_roster_packets_v1 import archive

OUT = ROOT / "build/verification/dragon-power-admission-nmi-diagnostic-v1"
PARENT = ROOT / "build/verification/dragon-power-admission-native-easy-v4"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size, sha256=sha(path))


def main():
    ready = json.loads((OUT / "ready.json").read_text())
    assert sha(OUT / "ready.json") == "9e9c90eea247c59cc922db94fe9f76e3fe0e55933f445f6eb4312a1c9b98533e"
    assert len(ready["bindings"]) == 36
    for path, expected in ready["bindings"].items():
        assert sha(path) == expected, path
    result = json.loads((OUT / "result.json").read_text())
    prior = json.loads((PARENT / "result.json").read_text())
    launch = json.loads((OUT / "launch.json").read_text())
    assert launch["exit_code"] == 1 and launch["changed_inputs"] == []
    assert launch["settings_before"] == launch["settings_after"] == "66d3c35063c1692c595bab6e07a21854f37b4af970597251a4e320b91d37a9aa"
    assert not result["passed"] and not prior["passed"]
    assert result["frames"] == prior["frames"] == 2654
    assert result["reason"] == prior["reason"] == "Active render enable precedes pre-render vertical reload"
    assert (OUT / "inputs.csv").read_bytes() == (PARENT / "inputs.csv").read_bytes()
    actual = list(csv.DictReader((OUT / "trace.csv").open()))
    original = list(csv.DictReader((PARENT / "trace.csv").open()))
    assert len(actual) == len(original) == 2654
    for left, right in zip(actual, original):
        assert {k: v for k, v in left.items() if k != "captured"} == {
            k: v for k, v in right.items() if k != "captured"}
    rows = [json.loads(line) for line in (OUT / "nmi-queues.jsonl").read_text().splitlines()]
    assert len(rows) == 354 and (OUT / "nmi-queues.jsonl").stat().st_size == 274841
    raw_log = (OUT / "nmi-queues.jsonl").read_bytes()
    assert raw_log.count(b"\r\n") == 354
    assert len(raw_log.replace(b"\r\n", b"\n")) == result["diagnostic"]["bytes"] == 274487
    assert len(rows) < 2048 and (OUT / "nmi-queues.jsonl").stat().st_size < 2 * 1024 * 1024

    def one(frame, kind, predicate=lambda _: True):
        found = [row for row in rows if row["stamp"]["ppu_frame"] == frame
                 and row["kind"] == kind and predicate(row)]
        assert len(found) == 1, (frame, kind, len(found))
        return found[0]

    early = one(2652, "GokuHUD-entry")
    late = one(2652, "GokuHUD-return")
    lag1 = one(2652, "NMI-entry")
    lag2 = one(2653, "NMI-entry")
    nmi = one(2654, "NMI-entry")
    update = one(2654, "UpdateScreen-entry", lambda r: r["data"]["pointer"] == 1199)
    terminal = one(2654, "UpdateScreen-entry", lambda r: r["data"]["pointer"] == 1258)
    chr_entry = one(2654, "BankSwitchCHR-entry")
    chr_return = one(2654, "BankSwitchCHR-return")
    dma_entry = one(2654, "OAMandReadJoypad-entry")
    dma_done = one(2654, "actual-DMA-completion")
    render = one(2654, "PPUMASK-write", lambda r: r["data"]["value"] & 0x18)
    assert [r["data"]["NmiDisable"] for r in (lag1, lag2, nmi)] == [255, 255, 0]
    assert early["data"]["VRAM_Buffer1_Offset"] == 30
    assert late["data"]["VRAM_Buffer1_Offset"] == 45
    assert early["data"]["DpClock"] == 0 and early["data"]["DpHP"] == 76
    assert lag2["data"]["VRAM_Buffer1_Offset"] == nmi["data"]["VRAM_Buffer1_Offset"] == 59
    commands = nmi["data"]["selected_packet"]["commands"]
    assert [c["count"] for c in commands] == [2, 2, 2, 6, 3, 12, 2, 6]
    assert commands[5]["destination"] == 0x2023
    assert commands[5]["data"] == "111900070624190124200000"
    assert all(not c["repeat_byte"] and not c["vertical"] for c in commands)
    assert render["stamp"]["bank"] == 127 and render["stamp"]["pc"] == 0xE00B
    assert (render["stamp"]["line"], render["stamp"]["dot"]) == (1, 167)
    cycle = lambda r: r["stamp"]["cycle"]
    timing = dict(nmi_to_render=cycle(render)-cycle(nmi),
                  parser=cycle(terminal)-cycle(update),
                  terminal_to_chr=cycle(chr_entry)-cycle(terminal),
                  chr=cycle(chr_return)-cycle(chr_entry),
                  chr_to_dma=cycle(dma_entry)-cycle(chr_return),
                  dma_entry_to_completion=cycle(dma_done)-cycle(dma_entry),
                  completion_to_render=cycle(render)-cycle(dma_done))
    assert timing == dict(nmi_to_render=2548, parser=1368, terminal_to_chr=82,
                         chr=429, chr_to_dma=12, dma_entry_to_completion=523,
                         completion_to_render=4)
    # Use actual recursive parser entry intervals, not a guessed packet budget.
    entries = [row for row in rows if row["stamp"]["ppu_frame"] == 2654
               and row["kind"] == "UpdateScreen-entry"]
    intervals = [cycle(b)-cycle(a) for a, b in zip(entries, entries[1:])]
    assert intervals == [136, 136, 136, 200, 152, 272, 136, 200]
    assert sum(intervals) == timing["parser"]
    assert result["full_frames"] == 0 and result["adapter"]["container_bytes"] == 0
    assert not any(OUT.glob("*.png")) and not any(OUT.glob("*.nesppuv1"))
    report = dict(
        status="EXPECTED_NATIVE_FAILURE_REPRODUCED_AND_DIAGNOSED",
        product_passed=False, native_route_passed=False,
        exact_input_bytes=True, exact_trace_except_capture_bookkeeping=True,
        ready_bindings_rehashed=36, native_hardware_guards_unchanged=True,
        global_settings_unchanged=True, real_deaths=0,
        actual_render=dict(bank=127, pc="E00B", scanline=1, dot=167, ppu_frame=2654),
        observed_queue=dict(before_optional_HUD=30, after_optional_HUD=45,
                            retained_across_lag=59, commands=commands,
                            parser_CPU_intervals=intervals),
        actual_CPU_cycles=timing,
        cause="Early optional12-cell Goku HUD command added15 queue bytes after a lag NMI; a later native coin/score pair grew the retained queue to59 bytes. At2654 the normal parser plus429-cycle CHR publication and DMA enabled rendering on visible scanline1.",
        proposed_fix_scope="Owned optional HUD admission after native producers, with exact-owner retraction if it survives a lag NMI; eventual HUD refresh and original/native packets must remain intact. No render-guard waiver or physics change.",
        limits="No new product candidate or route pass. Same fb28 immutable ROM and identical2653 controller polls. No media, screenshots or per-frame files. Parent whole-image failure review remains independently frozen.",
        log_rows=len(rows), log_bytes=(OUT/"nmi-queues.jsonl").stat().st_size,
        result_counter_scope="Lua text-mode output expands354 LF newlines to CRLF on Windows:274487 Lua-string bytes become274841 disk bytes. All354 rows are present; both sizes are below the2MiB cap.",
    )
    (OUT / "root-diagnosis.json").write_text(json.dumps(report, indent=2) + "\n")
    owned = [p for p in OUT.iterdir() if p.is_file() and p.name != "handoff.json"]
    owned += [Path(__file__), ROOT/"tools/audit/dragon_power_nmi_queue_prepare_v1.py",
              ROOT/"tools/audit/dragon_power_nmi_queue_observer_v1.lua"]
    handoff = dict(status=report["status"], owned_files=[binding(p) for p in owned],
                   runtime_references=[binding(ROOT/"build/dragon-power-admission-v1/candidate.nes")],
                   ready_bound_references=[binding(p) for p in ready["bindings"]],
                   root_diagnosis=report)
    (OUT / "handoff.json").write_text(json.dumps(handoff, indent=2) + "\n")
    archive("goku-actual-nmi-queue-diagnosis", str((OUT/"handoff.json").relative_to(ROOT)),
            lambda d: d["owned_files"], [], report)


if __name__ == "__main__":
    main()
