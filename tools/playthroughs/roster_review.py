"""Decode every final video frame and correlate read-only emulator evidence.

Keeps a bounded contact sheet, never a directory of every video frame. Flags
are candidates for visual/audio inspection; an automated review is not a claim
that a person manually watched every frame or that source waveforms match.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image, ImageDraw


def rows(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def number(row, key, default=0):
    return int(row.get(key, default) or default)


def active(row):
    return row and all(number(row, k) == v for k, v in (("mode", 1), ("task", 3), ("engine", 8)))


def room(row):
    return tuple(number(row, k) for k in ("world", "level", "area", "areaType"))


def read_exact(pipe, size):
    data = bytearray()
    while len(data) < size:
        chunk = pipe.read(size - len(data))
        if not chunk:
            break
        data.extend(chunk)
    return data


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def review(directory: Path):
    manifest = json.loads((directory / "manifest.json").read_text())
    cfg = manifest.get("config", manifest.get("settings", {}))
    trace = {number(r, "frame"): r for r in rows(directory / "trace.csv")}
    render = {number(r, "frame"): r for r in rows(directory / "render.csv")}
    events = rows(directory / "events.csv")
    sounds = rows(directory / "audio-events.csv")
    splits = rows(directory / "scroll-writes.csv")
    chr_changes = rows(directory / "chr.csv")
    stomp_events = rows(directory / "stomp-events.csv")
    stomp_path = directory / "stomp-summary.json"
    stomp_summary = json.loads(stomp_path.read_text()) if stomp_path.exists() else None
    telemetry = {n: (directory / (n + ".csv")).exists() for n in ("render", "oam", "chr", "scroll-writes", "audio-events")}
    wanted = {}
    for event in stomp_events:
        if number(event, "illegalGuest"):
            wanted[number(event, "frame")] = "illegal guest native stomp"
    for event in events:
        if event.get("event") == "stage":
            f = number(event, "frame")
            wanted[f] = f"entered {number(event, 'world') + 1}-{number(event, 'level') + 1}"
            wanted[f + 30] = "stage movement"
    if trace:
        wanted[max(trace)] = "endpoint"
    motion = []
    previous = None
    for frame, t in trace.items():
        if active(t) and active(previous) and room(t) == room(previous):
            dx = number(t, "x") - number(previous, "x")
            y = number(t, "y") + 256 * (number(t, "yHigh", 1) - 1)
            py = number(previous, "y") + 256 * (number(previous, "yHigh", 1) - 1)
            dy = y - py
            dc = number(t, "camera") - number(previous, "camera")
            if abs(dx) > 8 or abs(dy) > 16 or abs(dc) > 8:
                motion.append({"frame": frame, "dx": dx, "dy": dy, "camera_delta": dc})
                if len(motion) <= 20:
                    wanted[frame] = "motion candidate"
        previous = t
    pose_first = {}
    for frame, r in render.items():
        if not active(r):
            continue
        key = tuple(number(r, k) for k in ("power", "pose", "crouch", "attack", "shoot", "wall", "ceiling", "hover", "pitFlight"))
        # Attack timers vary continuously. Bucket them into active/inactive.
        key = key[:3] + tuple(int(v > 0) for v in key[3:])
        if key not in pose_first:
            pose_first[key] = frame
            if len(pose_first) <= 80:
                wanted[frame + 1] = "pose " + str(key)

    by_split = {}
    for r in splits:
        if active(r) and number(r, "screenDisabled") == 0:
            by_split.setdefault(number(r, "frame"), []).append(r)
    bad_splits = []
    for frame, rr in by_split.items():
        final = rr[-2:]
        if len(final) != 2 or any(number(r, "scanline") != 31 or not 257 <= number(r, "dot") <= 320 for r in final):
            bad_splits.append({"frame": frame, "writes": final})
            if len(bad_splits) <= 12:
                wanted[frame + 1] = "HUD split candidate"
    bad_chr = [r for r in chr_changes if number(r, "lagNmi") and number(r, "engine") == 8]
    for r in bad_chr[:12]:
        wanted[number(r, "frame") + 1] = "lag CHR change"

    source_count = 0
    audio_unconfirmed = []
    audio_observed = []
    for e in sounds:
        if number(e, "engine") != 8:
            continue
        frame, event = number(e, "frame"), e["event"]
        source_count += 1
        nearby = [render.get(f, {}) for f in range(frame, frame + 7)]
        if event == "AvAudioRequest":
            owned = any(number(r, "sourceMask") for r in nearby)
        elif event in ("BassAudioRequest", "BassSourceId", "MmAudioShotType"):
            owned = any(number(r, "nativeMask") for r in nearby)
        else:
            bit = {"Square1SoundQueue": 1, "Square2SoundQueue": 2, "NoiseSoundQueue": 8}.get(event, 0)
            owned = any((number(r, "worldMask") | number(r, "nativeMask") | number(r, "sourceMask")) & bit for r in nearby)
            # Mario/Luigi use the native buffers, rather than an overlay owner.
            if cfg.get("character") in (0, 8):
                owned = any(number(r, "apuMask") & bit for r in nearby)
        writes = any(number(r, "apuWrites") or number(r, "expansionWrites") for r in nearby)
        evidence = {"frame": frame, "event": event, "value": number(e, "value"), "voice_owned": owned, "physical_audio_writes": writes}
        (audio_observed if owned and writes else audio_unconfirmed).append(evidence)

    video = directory / "playthrough-lossless.mkv"
    lossless_proof = video.with_suffix(".verification") / "report.json"
    if video.exists():
        proof = json.loads(lossless_proof.read_text())
        assert proof["result"] == "passed-exact-rgb-and-pcm"
        assert proof["output"]["sha256"] == sha(video)
        video_kind = "verified lossless native RGB and PCM master"
    else:
        video = directory / "playthrough.mp4"
        if not video.exists():
            video = directory / "native.avi"
        video_kind = "delivery copy or native AVI"
    captures = {}
    pixel_flags = []
    background_flashes = []
    decoded = compared = 0
    video_error = None
    if video.exists():
        command = ["ffmpeg", "-v", "error", "-i", str(video), "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        previous_profile = previous_pixels = previous_t = None
        previous_black = 0
        while True:
            raw = read_exact(process.stdout, 256 * 240 * 3)
            if not raw:
                break
            if len(raw) != 256 * 240 * 3:
                raise RuntimeError("Partial decoded video frame")
            decoded += 1
            pixels = np.frombuffer(raw, np.uint8).reshape(240, 256, 3)
            t = trace.get(decoded)
            profile = pixels[202:240, 16:240].mean(axis=1)
            black = float((pixels[40:200].max(axis=2) < 16).mean())
            comparable = active(t) and active(previous_t) and room(t) == room(previous_t) and abs(number(t, "camera") - number(previous_t, "camera")) < 5
            if comparable:
                compared += 1
                costs = [float(np.abs(profile[4 + d:34 + d] - previous_profile[4:34]).mean()) for d in range(-3, 4)]
                best = int(np.argmin(costs)) - 3
                if best and costs[3] > costs[best + 3] * 2 + 3:
                    flag = {"frame": decoded, "vertical_offset": best, "unshifted_error": round(costs[3], 3), "shifted_error": round(costs[best + 3], 3)}
                    pixel_flags.append(flag)
                    if len(pixel_flags) <= 20:
                        wanted[decoded] = "vertical stage candidate"
                if abs(black - previous_black) > .35:
                    background_flashes.append({"frame": decoded, "black_fraction": round(black, 4), "previous": round(previous_black, 4)})
                    if len(background_flashes) <= 12:
                        wanted[decoded] = "background flash candidate"
            if decoded in wanted and len(captures) < 180:
                captures[decoded] = Image.fromarray(pixels.copy())
                if previous_pixels is not None and decoded - 1 not in captures and len(captures) < 180:
                    captures[decoded - 1] = Image.fromarray(previous_pixels.copy())
            previous_profile, previous_pixels, previous_t, previous_black = profile, pixels.copy(), t, black
        error = process.stderr.read().decode()
        process.wait()
        if process.returncode:
            video_error = error
    else:
        video_error = "No recorded video"

    selected = sorted(captures)[:144]
    for offset in range(0, len(selected), 48):
        batch = selected[offset:offset + 48]
        sheet = Image.new("RGB", (4 * 256, ((len(batch) + 3) // 4) * 268), "#202020")
        draw = ImageDraw.Draw(sheet)
        for j, frame in enumerate(batch):
            x, y = j % 4 * 256, j // 4 * 268
            sheet.paste(captures[frame], (x, y))
            label = wanted.get(frame, "preceding frame")[:40]
            draw.text((x + 3, y + 242), f"{frame}: {label}", fill="white")
        sheet.save(directory / f"review-contact-{offset // 48 + 1}.png")
    result = manifest.get("result", {})
    summary = {
        "rom_sha256": manifest.get("rom_sha256"), "character": cfg.get("character"), "variant": cfg.get("variant", 0),
        "verified_controller_clear": manifest.get("verified_through_2_2", False), "result": result,
        "every_recorded_frame_decoded": bool(decoded and not video_error
            and decoded == result.get("frames", 0) - 1), "decoded_video_frames": decoded,
        "trace_frames": len(trace), "video_frame_delta": decoded - max(trace, default=0), "video_error": video_error,
        "video_sha256": sha(video) if video.exists() else None,
        "video_kind": video_kind,
        "telemetry_files_present": telemetry, "comparable_background_frames": compared,
        "committed_dma_transactions": sum(1 for _ in (directory / "oam.csv").open()) - 1 if telemetry["oam"] else 0,
        "gameplay_split_frames": len(by_split), "split_timing_candidates": bad_splits,
        "lag_chr_change_candidates": bad_chr, "motion_candidates": motion,
        "video_vertical_shift_candidates": pixel_flags, "video_background_flash_candidates": background_flashes,
        "overloaded_sprite_frames": sum(number(r, "maxSprites") > 8 for r in render.values() if active(r)),
        "lag_hardware_frames": sum(number(r, "lagNmi") for r in render.values() if active(r)),
        "audio_source_event_count": source_count, "audio_events_with_voice_and_physical_writes": len(audio_observed),
        "native_stomp_audit": stomp_summary,
        "illegal_guest_native_stomps": [e for e in stomp_events if number(e, "illegalGuest")],
        "audio_events_needing_priority_or_audible_review": audio_unconfirmed,
        "physical_apu_writes": sum(number(r, "apuWrites") for r in render.values()),
        "physical_expansion_audio_writes": sum(number(r, "expansionWrites") for r in render.values()),
        "contact_sheet_frames": len(selected),
        "limits": "Automated per-frame decoding and telemetry audit; flagged frames still need inspection. Audio ownership/writes do not certify waveform parity or human listening."
    }
    (directory / "review.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"directory": str(directory), "decoded_frames": decoded, "split_flags": len(bad_splits), "chr_flags": len(bad_chr), "motion_flags": len(motion), "pixel_flags": len(pixel_flags), "audio_unconfirmed": len(audio_unconfirmed)}))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path)
    args = parser.parse_args()
    for directory in args.directories:
        review(directory.resolve())


if __name__ == "__main__":
    main()
