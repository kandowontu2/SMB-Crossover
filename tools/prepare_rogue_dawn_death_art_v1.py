"""Add the missing original Rogue Dawn frame35 without changing frozen art.

Source CPU decoder -> original pixels -> one8x16 host page/record -> actual
current compiled metasprite loop. No death timing or native display claim.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools/audit")]
import prepare_rogue_dawn_art_v1 as art
import rogue_dawn_map_v1 as ref
import rogue_dawn_render_controls_v1 as host

OUT = ROOT / "build/rogue-dawn-death-art-v1"
BASE = ROOT / "build/roster-shared-celeste-small-chr-v1"
CHR = ROOT / "chr/characters/rogue-dawn-death.chr"
INCLUDE = ROOT / "src/rogue_dawn_death_art.inc"
REPORT = ROOT / "docs/qa/rogue-dawn-death-art-source-2026-10-28.json"


def native(raw, face, area):
    m = art.Memory(ref.cpu_image(raw, lower_bank=area))
    for address, value in {0x4b: 0, 0x55: 1, 0x300: 1, 0x303: 0x35,
                           0x30d: 128, 0x30e: 128, 0x49: 2,
                           0x6b: 0x10 if face else 0}.items():
        m[address] = value
    for i in range(0x200, 0x300, 4):
        m[i] = 248
    c = art.call(m, 0xde4a)
    parts = [list(m[i:i+4]) for i in range(0x200, 0x200+m[0x5b], 4)]
    pixels = art.source_pixels(raw, parts)
    return m, c, parts, pixels


def pack(pixels, pairs):
    record = []
    # A fixed grid preserves source center geometry. Keep the priority role;
    # encode the source flips into pixels rather than changing their shape.
    minx = min(x for x, y in pixels)
    maxx = max(x for x, y in pixels)
    miny = min(y for x, y in pixels)
    maxy = max(y for x, y in pixels)
    for attr in sorted(set(attr for value, attr in pixels.values())):
        for y in range(miny, maxy+1, 16):
            for x in range(minx, maxx+1, 8):
                pair = art.encode(pixels, x, y, attr)
                if not any(pair):
                    continue
                if pair not in pairs:
                    pairs.append(pair)
                record += [2*pairs.index(pair), attr, (y+15)&255, (x+8)&255]
    assert len(pairs) <= 32 and len(record) <= 124
    return bytes([len(record)]+record)


def host_draw(page, record, flags):
    s = host.symbols(BASE.with_suffix(".lbl"))
    raw = BASE.with_suffix(".nes").read_bytes()
    m = art.Memory(bytes((i*7+11)&255 for i in range(65536)))
    m[0xa000:0xc000] = raw[16+4*8192:16+5*8192]
    m[0xdf00:0xdf00+len(record)] = record
    m[s["CurrentOAMOffset"]] = 0
    m[s["GuestOamRotationActive"]] = 0
    m[s["RgOamRotation"]] = 0
    for name, value in {"R0": 0, "R1": 0xdf, "R3": 0, "R4": 120,
                        "R5": 0, "R6": 112, "R7": 1}.items():
        m[s[name]] = value
    c = art.call(m, s["MetaspriteRenderLoop"], p=flags)
    parts = [list(m[i:i+4]) for i in range(0x200, 0x200+m[s["CurrentOAMOffset"]], 4)]
    pixels = {}
    for y, tile, attr, x in reversed(parts):
        start = (tile & 254)*16
        for yy in range(16):
            sy = 15-yy if attr&128 else yy
            for xx in range(8):
                sx = 7-xx if attr&64 else xx
                at = start+(sy//8)*16+sy%8
                value = ((page[at]>>(7-sx))&1) | (((page[at+8]>>(7-sx))&1)<<1)
                if value:
                    pixels[x-128+xx, y+1-128+yy] = value, attr&0x23
    return pixels, parts, c.processorCycles


def main():
    assert not (OUT / "handoff.json").exists(), "Preserve frozen packet"
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    assert ref.digest(BASE.with_suffix(".nes").read_bytes()) == "f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9"
    frozen = ROOT / "chr/characters/rogue-dawn.chr"
    frozen_bytes = frozen.read_bytes()
    assert ref.digest(frozen_bytes) == "4b31e0309b20c9fd408fe126670186e183f7b3059027cff052612e062680fe96"
    assert frozen_bytes[9*1024:10*1024] == bytes(1024)
    OUT.mkdir(exist_ok=True)
    source, originals, pairs, records = [], [], [], []
    for area in [2, 4, 6, 8, 10]:
        for face in [0, 1]:
            m, c, parts, pixels = native(raw, face, area)
            record = pack(pixels, pairs)
            assert c.x == 24 and m[0x301:0x303] == bytes(2)
            source.append(dict(area=area, face=face, parts=parts, opaque=len(pixels),
                               AXYP=[c.a, c.x, c.y, c.p], cycles=c.processorCycles,
                               source_radius=list(m[0x301:0x303]), record_hex=record.hex()))
            originals.append(pixels)
            records.append(record)
    assert all(r == records[i % 2] for i, r in enumerate(records))
    page = b"".join(pairs) + bytes(1024-32*len(pairs))
    CHR.write_bytes(page)
    INCLUDE.write_text("\n".join([
        "; Additive original Rogue Dawn1.21 frame35, generated from actual DE4A.",
        "; Include AFTER A95 host code. Preserve frozen C94/CORE/body asset.",
        "; Callback sets the C95 pointer without mapping away its live C94 bridge.",
        "; Actual first-record owner must lease C95 for this frame before reading.",
        "RD_DEATH_CHR=689", "RD_DEATH_RECORD_C=$df00",
        f"RD_DEATH_RECORD_LEFT_C=${0xdf00+len(records[0]):04x}", "RD_DEATH_SOURCE_X=24",
        '.pushseg', '.segment "ROGUE_DAWN_HOST"',
        '.assert (*-RdHsFrozenDispatch) <= $1900,error,"Reserve death ART tail"',
        ' .res $1900-(*-RdHsFrozenDispatch),$ff',
        '.export RdDeathRecordA,RD_DEATH_RECORD_C,RD_DEATH_CHR,RD_DEATH_SOURCE_X',
        '.export RdDeathRecordLeftA,RD_DEATH_RECORD_LEFT_C',
        'RdDeathRecordA:',
        ' .byte '+','.join(f'${v:02x}' for v in records[0]),
        'RdDeathRecordLeftA:',
        ' .byte '+','.join(f'${v:02x}' for v in records[1]),
        'RdDeathRecordEnd:',
        '.assert .loword(RdDeathRecordA)=$bf00,lderror,"C95 mirrored descriptor"',
        '.assert *-RdDeathRecordA <= 256,error,"Original A95 tail reservation"',
        '.popseg', '']), encoding="utf-8", newline="\n")
    rows = []
    for i, (fact, expected) in enumerate(zip(source, originals)):
        for p in [0x30, 0x31, 0x70, 0xf3]:
            actual, parts, cycles = host_draw(page, records[i], p)
            assert actual == expected, (fact["area"], fact["face"], p)
            rows.append(dict(area=fact["area"], face=fact["face"], flags=p,
                             host_parts=len(parts), opaque=len(actual), host_cycles=cycles))
    proof = dict(passed=True, source_only=True, native_run=False,
                 status="Authentic missing death frame35 asset; not full death/lifecycle qualification",
                 source_ROM=ref.binding(ref.ROM), source_decoder="62:DE4A with original area data",
                 original_context="source8x8 cursor0, both facings, five actual area banks",
                 source_rows=source, actual_compiled_host_loop_cases=rows,
                 body_page=689, body_window=0, unique_8x16_pairs=len(pairs),
                 descriptor_bytes=sum(len(r) for r in records[:2]), descriptor_C95=["DF00", f"{0xdf00+len(records[0]):04X}"],
                 descriptor_physical_A95="BF00", source_returnX=24,
                 source_radii=[0, 0], frozen_art_and_CHR_unchanged=True,
                 remaining=["Add through genuine private assembly and current ABI-preserving draw-callback dispatch",
                            "Actual first-record C95 mapping, source callback timing and lifecycle",
                            "Original death explosion motion, palette and native displayed frames"],
                 bindings=[ref.binding(p) for p in [Path(__file__), ref.ROM,
                     ROOT / "tools/prepare_rogue_dawn_art_v1.py",
                     ROOT / "tools/rogue_dawn_map_v1.py",
                     ROOT / "tools/rogue_dawn_render_controls_v1.py",
                     BASE.with_suffix(".nes"), BASE.with_suffix(".lbl"), BASE.with_suffix(".dbg"),
                     frozen, CHR, INCLUDE, OUT / "first-distinct-facing-negative.json"]])
    REPORT.write_text(json.dumps(proof, indent=2)+"\n")
    packet = dict(passed=True, source_only=True, outputs=[ref.binding(p) for p in [CHR, INCLUDE, REPORT]],
                  report=ref.binding(REPORT), bindings=proof["bindings"])
    (OUT / "handoff.json").write_text(json.dumps(packet, indent=2)+"\n")
    print(json.dumps(dict(report_sha256=ref.digest(REPORT.read_bytes()), pairs=len(pairs),
                          descriptor_bytes=sum(len(r) for r in records[:2]), cases=len(rows))))


if __name__ == "__main__":
    main()
