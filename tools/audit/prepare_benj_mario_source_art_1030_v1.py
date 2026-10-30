"""Recover complete v44 Toad/Peach art through the donor's real cache/upload API.

Outputs remain private: no menu lease, port, native validation or unlock claim.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from benj_mario_donor_trace_1030_v1 import Bus, MPU, DONOR, EXPECTED

R = Path(__file__).resolve().parents[2]
FIXTURE = R / "build/benj-donor-peach-discovery-1030-v3"


def bind(p):
    p = Path(p).resolve()
    return dict(path=str(p), bytes=p.stat().st_size,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def call(bus, cpu, entry, a=0):
    cpu.pc = entry
    cpu.a = a
    cpu.sp = 0xfd
    bus.ram[0x1fe:0x200] = bytes([0xff, 2])
    start = cpu.processorCycles
    for count in range(2000):
        if cpu.pc == 0x300:
            return cpu.processorCycles - start
        assert bus[cpu.pc] != 0, ("BRK", hex(cpu.pc))
        cpu.step()
    raise AssertionError(("bounded donor API did not return", hex(cpu.pc)))


def pixels(patterns):
    result = {}
    for t in range(8):
        data = patterns[t * 16:(t + 1) * 16]
        for y in range(8):
            for x in range(8):
                value = ((data[y] >> (7 - x)) & 1) | (((data[y + 8] >> (7 - x)) & 1) << 1)
                if value:
                    result[(t % 2 * 8 + x, t // 2 * 8 + y)] = value
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    assert not out.exists()
    raw = DONOR.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    state = json.loads((FIXTURE / "discovery.json").read_text())
    native_ram = (FIXTURE / "ram.bin").read_bytes()
    assert native_ram[0x7310:0x731c] == bytes([0, 0, 1, 2, 0, 26, 52, 78, 104, 130, 156, 182])
    assert native_ram[0x731c:0x7327] == bytes.fromhex("8d38644a4a4a8500ae5307")
    records = []
    for char in (2, 3):
        for pose in range(26):
            for status in range(3):
                for custom_art in (0, 1):
                    bus = Bus(raw)
                    bus.ram[:0x8000] = native_ram
                    bus.reg = list(state["mapper_registers"])
                    bus.select = state["mapper_select"]
                    bus.ctrl = state["ctrl"]
                    bus.remap()
                    cpu = MPU(memory=bus, pc=0x731c)
                    bus.cpu = cpu
                    for address, value in {0x753: 0, 0x620b: char, 0x756: status,
                                           0x623f: custom_art, 0x6478: 0,
                                           0x6470: 0, 0x6424: 0, 0x642b: 255}.items():
                        bus.ram[address] = value
                    bus.ram[0x6400:0x6404] = bytes(4)
                    cache_cycles = call(bus, cpu, 0x731c, pose * 8)
                    global_frame = char * 52 + pose
                    fire = status == 2 and custom_art and (pose < 12 or pose >= 24)
                    if fire:
                        global_frame += 26
                    expected_bank = 10 + global_frame // 64
                    expected_column = global_frame % 64
                    assert bus.ram[0x6424:0x6429] == bytes([1, expected_bank, expected_column, 16, 0])
                    upload_cycles = call(bus, cpu, 0xe57a)
                    assert sum(bus.uploads.values()) == 128 and bus.ram[0x6424] == 0
                    expected_offsets = [16 + expected_bank * 8192 + expected_column + n * 64 for n in range(128)]
                    assert bus.chr_provenance[0x1000:0x1080] == expected_offsets
                    expected_bytes = bytes(raw[i] for i in expected_offsets)
                    assert bus.chr[0x1000:0x1080] == expected_bytes
                    assert bus.banks == state["prg_banks"], "native uploader must restore PRG mapping"
                    records.append(dict(character=char, pose=pose, status=status,
                                        custom_art=custom_art, global_frame=global_frame,
                                        cache_cycles=cache_cycles, upload_cycles=upload_cycles,
                                        native_upload_sha256=hashlib.sha256(expected_bytes).hexdigest()))

    out.mkdir(parents=True)
    outputs = []
    palette = [(24, 27, 38), (92, 136, 220), (226, 178, 112), (250, 246, 234)]
    atlas = Image.new("RGB", (13 * 48, 4 * 88), palette[0])
    draw = ImageDraw.Draw(atlas)
    for cindex, (char, name) in enumerate([(2, "toad"), (3, "peach")]):
        packed = bytearray(7 * 1024)
        descriptors = []
        for frame in range(52):
            global_frame = char * 52 + frame
            bank, column = 10 + global_frame // 64, global_frame % 64
            source = bytes(raw[16 + bank * 8192 + column + n * 64] for n in range(128))
            # Retain full16x32 anatomy. Each hardware8x16 pair joins vertical
            # source8x8 tiles, rather than joining the two horizontal neighbors.
            packed_frame = b"".join(source[t * 16:(t + 1) * 16] for t in [0, 2, 1, 3, 4, 6, 5, 7])
            packed[frame * 128:(frame + 1) * 128] = packed_frame
            expected = pixels(source)
            for face in (1, 2):
                descriptor = []
                decoded = {}
                for part in range(4):
                    x = part % 2 * 8
                    y = part // 2 * 16
                    descriptor.extend([frame % 8 * 8 + part * 2,
                                       64 if face == 2 else 0, y,
                                       8 - x if face == 2 else x])
                    tile = packed_frame[part * 32:(part + 1) * 32]
                    for yy in range(16):
                        for xx in range(8):
                            bit = xx if face == 2 else 7 - xx
                            iy = yy % 8 + (yy // 8) * 16
                            value = ((tile[iy] >> bit) & 1) | (((tile[iy + 8] >> bit) & 1) << 1)
                            if value:
                                decoded[((8 - x if face == 2 else x) + xx, y + yy)] = value
                target = {(15 - x if face == 2 else x, y): v for (x, y), v in expected.items()}
                assert decoded == target
                descriptors.append(dict(frame=frame, face=face, relative_chr_page=frame // 8,
                                        record=[16] + descriptor))
            # One atlas row per normal/fire form; neutral index colors only.
            # Title OAM output is kept separately as the real native reference.
            if frame < 26:
                ox = frame % 13 * 48
                oy = cindex * 176 + frame // 13 * 88
                draw.text((ox + 1, oy + 1), f"{name[0].upper()}{frame:02}", fill="white")
                for (x, y), value in expected.items():
                    for sy in range(2):
                        for sx in range(2):
                            atlas.putpixel((ox + x * 2 + sx, oy + 17 + y * 2 + sy), palette[value])
        chr_path = out / f"{name}-source-52-pose.chr"
        chr_path.write_bytes(packed)
        desc_path = out / f"{name}-source-descriptors.json"
        desc_path.write_text(json.dumps(descriptors, separators=(",", ":")) + "\n")
        outputs.extend([bind(chr_path), bind(desc_path)])
    atlas.save(out / "normal-pose-atlas.png")
    proof = dict(status="PRIVATE_EXACT_DONOR_ART_RECOVERY_NOT_PORTED_OR_UNLOCKED",
                 credit="Super Duper Mario Bros. 4P v44 — Benj Edwards",
                 source=bind(DONOR), bindings=[bind(__file__), bind(Path(__file__).with_name("benj_mario_donor_trace_1030_v1.py")),
                                             bind(FIXTURE / "discovery.json"), bind(FIXTURE / "ram.bin")],
                 checks=dict(actual_donor_cache_and_upload=dict(passed=True, cases=len(records),
                             entrypoints=["RAM731C", "fixedE57A", "RAM7000 unrolled128-byte upload"],
                             all128_bytes_and_original_source_ROM_offsets_exact=True,
                             native_PRG_restore=True),
                             complete_8x16_repacking=dict(passed=True, poses=104, facings=2,
                             visible_pixel_indices_exact=True, parts_per_pose=4)),
                 outputs=outputs + [bind(out / "normal-pose-atlas.png")],
                 cases=records,
                 source_float=dict(native_entry="F6B3", code_file_range=["3F6C3", "3F770"],
                                   counter="6390+player", source_duration_updates=60,
                                   source_velocity_table="F758..F75F",
                                   behavior="Peach-specific held-jump float, source landing reset and ceiling/support callbacks must be ported together; not yet implemented here."),
                 limits="Instruction-level donor API with initialized legal cold-title context. No native PPU/timing, palette adaptation, physics port, menu implementation, readiness or campaign claim.")
    (out / "source-art-proof.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(dict(status=proof["status"], native_upload_cases=len(records),
                          packed_poses=104, facing_pixel_checks=208,
                          output_chr_bytes=2 * 7 * 1024, proof=bind(out / "source-art-proof.json"))))


if __name__ == "__main__":
    main()
