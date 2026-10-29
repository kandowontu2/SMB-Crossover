"""Controller-only power-on route discovery/replay through the end of World 2-2.

Policies may read telemetry and supply ordinary controller buttons. This runner
does not write emulated RAM, ROM, registers, or decoded save states. A discovery
is a candidate until its complete CSV is independently replayed with --replay.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import run_mesen
from workspace_storage import CAP_BYTES, locate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def workspace_bytes(root: Path) -> int:
    """Measure physical workspace files using cached Windows directory metadata.

    Reparse points (including symlinks and junctions) are not traversed. This
    avoids crossing the workspace boundary or counting linked trees twice.
    """
    total = 0
    pending = [root]
    while pending:
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                try:
                    info = entry.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue  # Another bounded capture may finish during scan.
                if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
                    continue
                if stat.S_ISDIR(info.st_mode):
                    pending.append(entry.path)
                elif stat.S_ISREG(info.st_mode):
                    total += info.st_size
    return total


def recording_metadata(path: Path, frames: int) -> dict:
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)],
                           capture_output=True, text=True)
    if probe.returncode:
        return {"passed": False, "failure": "ffprobe could not read encoded capture", "details": probe.stderr}
    try:
        streams = json.loads(probe.stdout).get("streams", [])
        video = next((v for v in streams if v.get("codec_type") == "video"), {})
        audio = next((v for v in streams if v.get("codec_type") == "audio"), {})
        count = int(video.get("nb_frames", 0))
        video_seconds = float(video.get("duration", 0))
        audio_seconds = float(audio.get("duration", 0))
        sample_rate = int(audio.get("sample_rate", 0))
        channels = int(audio.get("channels", 0))
    except (ValueError, TypeError):
        return {"passed": False, "failure": "Encoded capture has incomplete frame/audio metadata"}
    volume = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-sn", "-dn",
                             "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    peak_match = re.search(r"max_volume:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*dB", volume.stderr)
    peak = float(peak_match[1]) if peak_match else float("-inf")
    # The native recorder commits the prior image after Lua's endFrame callback.
    # A bounded 650-frame calibration records exactly 649 physical images.
    passed = bool(video.get("width") == 256 and video.get("height") == 240
                  and count == frames - 1 and video_seconds > 0
                  and sample_rate >= 8000 and channels > 0 and audio_seconds > 0
                  and volume.returncode == 0 and peak > -80
                  and abs(audio_seconds - video_seconds) <= 0.1)
    return {"passed": passed, "video_frames": count, "emulator_frames": frames,
            "frame_offset": count - frames, "width": video.get("width"), "height": video.get("height"),
            "frame_rate": video.get("avg_frame_rate"), "video_seconds": video_seconds,
            "audio_seconds": audio_seconds, "audio_sample_rate": sample_rate, "audio_channels": channels,
            "audio_peak_dbfs": peak if math.isfinite(peak) else None,
            "audio_duration_samples": round(audio_seconds * sample_rate), "mp4_sha256": sha(path)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--character", type=int, required=True, choices=range(13))
    p.add_argument("--variant", type=int, default=0, choices=(0, 1))
    p.add_argument("--behavior", choices=("easy", "hard"), default="easy",
                   help="Choose the real Options menu setting through controller input")
    p.add_argument("--mapper", default="mmc3", choices=("mmc3", "mmc5"))
    p.add_argument("--rom", type=Path, help="Frozen checkpoint ROM with matching .lbl/.dbg files")
    p.add_argument("--tag", required=True)
    p.add_argument("--policy", type=Path, default=ROOT / "tools/playthroughs/roster_policy.lua")
    p.add_argument("--prefix", type=Path, help="Fixed ordinary-controller prefix, then policy discovery")
    p.add_argument("--replay", type=Path, help="Complete fixed-controller stream; no discovery tail")
    p.add_argument("--frames", type=int, default=36000)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--record", action="store_true")
    p.add_argument("--record-segments", action="store_true",
                   help="Lossless bounded AVI windows plus continuous native WAV; implies --record")
    p.add_argument("--segment-frames", type=int, default=512)
    p.add_argument("--discovery-fast", action="store_true",
                   help="Omit per-frame graphics/audio audit for discovery only; incompatible with --record/--replay")
    p.add_argument("--allow-deaths", action="store_true")
    p.add_argument("--keep-avi", action="store_true")
    p.add_argument("--workspace-cap-gb", type=float, default=CAP_BYTES / 1_000_000_000)
    a = p.parse_args()
    if a.record_segments:
        a.record = True
        assert 128 <= a.segment_frames <= 1024
        assert a.frames <= 100000
    assert not (a.prefix and a.replay), "Choose --prefix or --replay"
    assert not (a.discovery_fast and (a.record or a.replay)), "Final fixed replay and recording require the full frame audit"
    assert a.variant == 0 or a.character in (1, 3), "Variant 1 is Proto Man or Lance; Luigi is character 8"
    assert a.frames > 600
    used = workspace_bytes(ROOT)
    cap = min(int(a.workspace_cap_gb * 1_000_000_000), CAP_BYTES)
    assert cap > 0, "Workspace cap must be positive"
    print(json.dumps({"workspace_bytes_before": used, "workspace_cap_bytes": cap}), flush=True)
    if used + 64 * 1024 * 1024 > cap:
        raise RuntimeError(f"Archive older evidence before starting another run under the {cap / 1_000_000_000:g} GB cap")
    for name in ('rom', 'policy', 'prefix', 'replay'):
        value = getattr(a, name)
        if value is not None:
            setattr(a, name, locate(value))
    recording_reserve = a.frames * (256 * 240 * 4 + 4096) + 512 * 1024 * 1024
    if a.record_segments:
        recording_reserve = (a.segment_frames * (256 * 240 * 4 + 16384)
                             + a.frames * 8192 + 512 * 1024 * 1024)
    if a.record and used + recording_reserve > cap:
        raise RuntimeError(f"Recording needs {recording_reserve:,} bytes below the workspace cap")
    out = ROOT / "build/roster-through-2-2" / f"{a.tag}-{a.character}-v{a.variant}-{a.mapper}"
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Output tag already has evidence; choose a fresh tag: {out}")
    out.mkdir(parents=True, exist_ok=True)
    source = a.rom.resolve() if a.rom else ROOT / f"build/smb-crossover-{a.mapper}.nes"
    header = source.read_bytes()[:16]
    actual_mapper = (header[6] >> 4) | (header[7] & 0xf0) | ((header[8] & 15) << 8)
    assert actual_mapper == (5 if a.mapper == "mmc5" else 4), "Declared mapper differs from the actual cartridge"
    variant_symbol = "BillVariant" if a.character == 3 else "ProtoVariant" if a.character == 1 else None
    if a.character == 1 and a.variant:
        labels = source.with_suffix('.lbl').read_text()
        assert a.mapper == 'mmc5' and re.search(r'^al [0-9A-Fa-f]+ \.ProtoVariant$', labels, re.M), "Proto Man requires the expanded MMC5 cartridge"
    rom = out / source.name
    for extension in (".nes", ".lbl"):
        shutil.copyfile(source.with_suffix(extension), rom.with_suffix(extension))
    debug = source.with_suffix('.dbg')
    if debug.exists():
        raw_debug = debug.read_bytes()
        packed_debug = gzip.compress(raw_debug, mtime=0)
        assert gzip.decompress(packed_debug) == raw_debug
        rom.with_suffix('.dbg.gz').write_bytes(packed_debug)
    else:
        shutil.copyfile(source.with_suffix('.dbg.gz'), rom.with_suffix('.dbg.gz'))
    policy = out / "policy.lua"
    shutil.copyfile(a.policy.resolve(), policy)
    core = out / "harness.lua"
    shutil.copyfile(ROOT / "tools/playthroughs/roster_harness.lua", core)
    audit = out / "audit.lua"
    shutil.copyfile(ROOT / "tools/playthroughs/roster_audit.lua", audit)
    bridge = ROOT / "build/capture_bridge.dll"
    bridge_source = None
    if a.record_segments:
        bridge_source = out / 'capture_segments.c'
        shutil.copyfile(ROOT / 'tools/playthroughs/capture_segments.c', bridge_source)
        bridge = out / 'capture_segments.dll'
        compile = subprocess.run(['gcc', '-shared', '-O2', '-Wall', '-Wextra',
            '-Wno-cast-function-type', '-o', str(bridge), str(bridge_source)], capture_output=True, text=True)
        (out / 'capture-compile.log').write_text(compile.stdout + compile.stderr)
        assert compile.returncode == 0, compile.stderr
        os.environ.update(SMB_CAPTURE_SEGMENT_DIR=out.as_posix(), SMB_CAPTURE_WORKSPACE=str(ROOT),
            SMB_CAPTURE_CAP_BYTES=str(cap), SMB_CAPTURE_SEGMENT_FRAMES=str(a.segment_frames),
            SMB_CAPTURE_FRAME_LIMIT=str(a.frames))
    elif a.record:
        if not bridge.exists():
            subprocess.run(["gcc", "-shared", "-O2", "-Wall", "-Wextra", "-Wno-cast-function-type", "-o", str(bridge), str(ROOT / "tools/playthroughs/capture_bridge.c")], check=True)
        os.environ["SMB_CROSSOVER_CAPTURE_AVI"] = (out / "native.avi").as_posix()
    config = {
        "character": a.character, "variant": a.variant, "mapper": a.mapper,
        "variantSymbol": variant_symbol, "behavior": a.behavior,
        "limit": a.frames, "out": out.as_posix() + "/", "record": a.record,
        "allowDeaths": a.allow_deaths, "bridge": bridge.as_posix(),
        "policy": policy.as_posix(), "replay": a.replay.resolve().as_posix() if a.replay else None,
        "audit": None if a.discovery_fast else audit.as_posix(),
        "prefix": a.prefix.resolve().as_posix() if a.prefix else None,
        "workspaceCapBytes": cap,
        "segmented": a.record_segments, "segmentFrames": a.segment_frames,
    }
    script = out / f"run-{a.tag}-{a.character}-v{a.variant}-{a.mapper}.lua"
    # JSON is not Lua: strings, integers, booleans and nil are serialized here.
    def lua(v):
        return "nil" if v is None else str(v).lower() if isinstance(v, bool) else json.dumps(v)
    script.write_text("ROSTER_CONFIG={\n" + "".join(f"  {k}={lua(v)},\n" for k, v in config.items()) + "}\ndofile(" + json.dumps(core.as_posix()) + ")\n", encoding="utf-8")
    manifest = {
        "rom_sha256": sha(rom), "policy_sha256": sha(policy), "harness_sha256": sha(core), "audit_sha256": sha(audit),
        "controller_only": True, "memory_inspection": True, "memory_or_register_writes": False,
        "full_frame_audit": not a.discovery_fast,
        "workspace_bytes_before": used,
        "recording_reserve_bytes": recording_reserve if a.record else 0,
        "config": config, "verified_through_2_2": False,
    }
    for name, path in (("prefix", a.prefix), ("replay", a.replay)):
        if path:
            manifest[f"{name}_sha256"] = sha(path)
    if bridge_source:
        manifest.update(capture_bridge_source_sha256=sha(bridge_source), capture_bridge_dll_sha256=sha(bridge),
            recording_mode='Native ZMBV windows with continuous native PCM WAV; per-window workspace guard')
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    options=["--nes.ramPowerOnState=AllZeros", "--nes.randomizeCpuPpuAlignment=false", "--nes.randomizeMapperPowerOnState=false"]
    if a.record_segments:
        options.append('--audio.sampleRate=48000')
    result = run_mesen.run(script, rom, timeout=a.timeout, emulator_options=options)
    report_path = out / "result.json"
    if report_path.exists():
        manifest["result"] = json.loads(report_path.read_text())
        manifest["verified_through_2_2"] = bool(result == 0 and a.replay and manifest["result"].get("cleared") and manifest["result"].get("all_six_stages") and not manifest["result"].get("failure") and (a.allow_deaths or manifest["result"].get("deaths") == 0))
    if (out / "inputs.csv").exists():
        manifest["inputs_sha256"] = sha(out / "inputs.csv")
    recording_ok = not a.record
    if a.record_segments and not (out / 'capture-budget-stop.json').exists() and (out / 'native-audio.wav').exists():
        assembled = subprocess.run([sys.executable, str(ROOT / 'tools/playthroughs/assemble_capture_segments.py'),
            '--directory', str(out), '--output', str(out / 'playthrough-lossless.mkv'),
            '--expected-frames', str(manifest.get('result', {}).get('frames', 0) - 1),
            '--workspace-cap-bytes', str(cap)], capture_output=True, text=True)
        (out / 'assemble.log').write_text(assembled.stdout + assembled.stderr)
        proof = out / 'playthrough-lossless.verification/report.json'
        recording_ok = assembled.returncode == 0 and proof.exists() and json.loads(proof.read_text())['result'] == 'passed-exact-rgb-and-pcm'
        manifest.update(assemble_exit=assembled.returncode, native_parts_retained=True,
            lossless_verification_sha256=sha(proof) if proof.exists() else None)
        if recording_ok:
            delivery = subprocess.run([sys.executable, str(ROOT / 'tools/playthroughs/encode_capture_delivery.py'),
                '--master', str(out / 'playthrough-lossless.mkv'), '--output', str(out / 'playthrough.mp4'),
                '--emulator-frames', str(manifest['result']['frames']),
                '--workspace-cap-bytes', str(cap)], capture_output=True, text=True)
            (out / 'delivery.log').write_text(delivery.stdout + delivery.stderr)
            manifest['delivery_exit'] = delivery.returncode
            dp = out / 'playthrough.delivery.json'
            if dp.exists():
                manifest['delivery_report_sha256'] = sha(dp)
                manifest['recording_metadata'] = json.loads(dp.read_text())['metadata']
            recording_ok = delivery.returncode == 0
    elif a.record and not a.record_segments and (out / "native.avi").exists():
        # Preserve native NES audio, reducing the final storage footprint.
        encode = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(out / "native.avi"), "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out / "playthrough.mp4")], capture_output=True, text=True)
        manifest["encode_exit"] = encode.returncode
        if encode.returncode:
            (out / "encode.log").write_text(encode.stderr)
        else:
            manifest["recording_metadata"] = recording_metadata(out / "playthrough.mp4", manifest.get("result", {}).get("frames", 0))
            recording_ok = manifest["recording_metadata"]["passed"]
            if recording_ok and not a.keep_avi:
                (out / "native.avi").unlink()
    if a.record:
        manifest["recording_verified"] = bool(recording_ok and manifest["verified_through_2_2"])
        if not recording_ok:
            manifest["recording_failure"] = "Native video/audio capture is missing, failed encoding, or does not match the emulator frame/audio duration"
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(out), "verified_through_2_2": manifest["verified_through_2_2"], "result": manifest.get("result")}), flush=True)
    return result or (0 if recording_ok and manifest.get("result", {}).get("cleared") else 2)


if __name__ == "__main__":
    raise SystemExit(main())
