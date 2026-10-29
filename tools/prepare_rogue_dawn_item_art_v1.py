"""Original Rogue Dawn typed pickups, including their four real flash phases.

Extract actual A5FE..A63A + DE4A with real MMC3 leases. Host item top-left
adapts source center by(+8,+8). No actor/emergence/palette-mixer admission.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools/audit")]
import prepare_rogue_dawn_art_v1 as art
import rogue_dawn_map_v1 as ref
import rogue_dawn_render_controls_v1 as host
from rogue_dawn_audio_owner_v1 import Memory
from verify_native_relocation import NesMPU

OUT = ROOT / "build/rogue-dawn-item-art-v1"
BASE = ROOT / "build/roster-shared-celeste-small-chr-v1"
CHR = ROOT / "chr/characters/rogue-dawn-items.chr"
INC = ROOT / "src/rogue_dawn_item_art.inc"
REPORT = ROOT / "docs/qa/rogue-dawn-item-art-source-2026-10-28.json"
NAMES = ["Bombs", "High Jump", "Wall Jump", "Screw Attack", "Spring Ball",
         "Environmental Suit", "Wave Beam", "Ice Beam", "Energy Tank", "Missile Tank"]


def source(raw, item, phase, area):
    m = Memory(raw)
    seed = {0x23: area//2, 0x4b: 0x40, 0x4c: 0, 0x748: item,
            0x74f: 0, 0x340: 1, 0x34d: 128, 0x34e: 128,
            0x49: 2, 0x55: 0, 0x2d: phase*2}
    for address, value in seed.items():
        bytearray.__setitem__(m, address, value)
    c = NesMPU(memory=m, pc=0xa5fe)
    c.sp = 0xfd
    for _ in range(20000):
        if c.pc == 0xa63a:
            assert c.sp == 0xfd and m.banks[:2] == [area, 61]
            assert m[0x343] == 0x50+item
            parts = [list(m[i:i+4]) for i in range(0x200, 0x200+m[0x5b], 4)]
            return parts, art.source_pixels(raw, parts), c.processorCycles
        assert m[c.pc] != 0, (item, phase, area, hex(c.pc))
        c.step()
    raise AssertionError(("Source item draw did not reach actual contact boundary", hex(c.pc)))


def pack(pixels, pairs):
    record = []
    minx, maxx = min(x for x, y in pixels), max(x for x, y in pixels)
    miny, maxy = min(y for x, y in pixels), max(y for x, y in pixels)
    for attr in sorted(set(attr for value, attr in pixels.values())):
        for y in range(miny, maxy+1, 16):
            for x in range(minx, maxx+1, 8):
                pair = art.encode(pixels, x, y, attr)
                if not any(pair):
                    continue
                if pair not in pairs:
                    pairs.append(pair)
                # Odd tile selects NES8x16 pattern table1, windows6/7.
                record += [129+2*pairs.index(pair), attr, (y+7)&255, (x+8)&255]
    assert len(pairs) <= 64 and len(record) <= 124
    return bytes([len(record)]+record)


def drawn(chrdata, record, flags):
    s = host.symbols(BASE.with_suffix(".lbl"))
    raw = BASE.with_suffix(".nes").read_bytes()
    m = art.Memory(bytes((i*7+11)&255 for i in range(65536)))
    m[0xa000:0xc000] = raw[16+4*8192:16+5*8192]
    m[0xde00:0xde00+len(record)] = record
    for name, value in {"CurrentOAMOffset": 0, "GuestOamRotationActive": 0,
                        "RgOamRotation": 0, "R0": 0, "R1": 0xde, "R3": 0,
                        "R4": 120, "R5": 0, "R6": 120, "R7": 1}.items():
        m[s[name]] = value
    c = art.call(m, s["MetaspriteRenderLoop"], p=flags)
    parts = [list(m[i:i+4]) for i in range(0x200, 0x200+m[s["CurrentOAMOffset"]], 4)]
    pixels = {}
    for y, tile, attr, x in reversed(parts):
        assert tile&1
        start = ((tile&254)-128)*16
        for yy in range(16):
            sy = 15-yy if attr&128 else yy
            for xx in range(8):
                sx = 7-xx if attr&64 else xx
                at = start+(sy//8)*16+sy%8
                value = ((chrdata[at]>>(7-sx))&1) | (((chrdata[at+8]>>(7-sx))&1)<<1)
                if value:
                    pixels[x-128+xx, y+1-128+yy] = value, attr&0x23
    return pixels, parts, c.processorCycles


def main():
    assert not (OUT / "handoff.json").exists(), "Preserve frozen packet"
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    assert ref.digest(BASE.with_suffix(".nes").read_bytes()) == "f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9"
    frozen = ROOT / "chr/characters/rogue-dawn.chr"
    assert ref.digest(frozen.read_bytes()) == "4b31e0309b20c9fd408fe126670186e183f7b3059027cff052612e062680fe96"
    assert frozen.read_bytes()[14*1024:] == bytes(2048)
    pairs, records, facts = [], [], []
    source_masks = []
    for item, name in enumerate(NAMES):
        for phase in range(4):
            parts, pixels, cycles = source(raw, item, phase, 2)
            record = pack(pixels, pairs)
            records.append(record)
            source_masks.append(pixels)
            facts.append(dict(type=item, name=name, phase=phase,
                              source_frame=0x50+item, source_OAM=parts,
                              source_cycles=cycles, opaque=len(pixels),
                              host_parts=(len(record)-1)//4))
    data = b"".join(pairs)+bytes(2048-32*len(pairs))
    # Exact40-way index, no duplicate/placeholder icon substitutions.
    unique = list(dict.fromkeys(records))
    sizes = sum(map(len, unique))+80
    assert sizes <= 512, ("Approved source descriptor tail", sizes)
    lines = ["; Authenticated Rogue1.21 pickups. Rawtype0..9, phase=(sourceClock>>1)&3.",
             "; Include after HOST_AUX code, with RdWxAuxStart=$ad60 in physical121.",
             "; Intentional C121 data lease; no permission to replace native world palettes.",
             "RD_ITEM_FIRST_CHR=694", "RD_ITEM_FIRST_WINDOW=6",
             "RD_ITEM_LO_C=$de00", "RD_ITEM_HI_C=$de28",
             ".pushseg", '.segment "ROGUE_DAWN_HOST_AUX"',
             '.assert (*-RdWxAuxStart)<=$10a0,error,"Reserve original item ART tail"',
             ' .res $10a0-(*-RdWxAuxStart),$ff',
             ".export RdItemLoA,RdItemHiA,RD_ITEM_FIRST_CHR,RD_ITEM_FIRST_WINDOW",
             ".export RD_ITEM_LO_C,RD_ITEM_HI_C", "RdItemLoA:",
             " .byte "+",".join(f"<(RdItemRecord{unique.index(r)}+$2000)" for r in records),
             "RdItemHiA:",
             " .byte "+",".join(f">(RdItemRecord{unique.index(r)}+$2000)" for r in records)]
    for i, record in enumerate(unique):
        lines += [f"RdItemRecord{i}:", " .byte "+",".join(f"${v:02x}" for v in record)]
    lines += ["RdItemArtEnd:",
              '.assert .loword(RdItemLoA)=$be00,lderror,"C121 mirrored item pointers"',
              '.assert RdItemArtEnd-RdItemLoA<=512,error,"Original item512B tail"',
              ".popseg", ""]
    OUT.mkdir(exist_ok=True)
    CHR.write_bytes(data)
    INC.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    tests, areas = [], []
    for index, (fact, expected) in enumerate(zip(facts, source_masks)):
        for flags in [0x30, 0x31, 0x70, 0xf3]:
            actual, oam, cycles = drawn(data, records[index], flags)
            assert actual == expected, (fact["name"], fact["phase"], flags)
            tests.append(dict(type=fact["type"], phase=fact["phase"], flags=flags,
                              opaque=len(actual), host_parts=len(oam), CPU=cycles))
        for area in [2, 4, 6, 8, 10]:
            oam, actual, cycles = source(raw, fact["type"], fact["phase"], area)
            assert actual == expected and oam == fact["source_OAM"]
            areas.append(dict(type=fact["type"], phase=fact["phase"], area=area, CPU=cycles))
    palette_roles = [art.palettes(raw, bank) for bank in [2, 4, 6, 8, 10]]
    report = dict(passed=True, source_only=True, native_run=False,
                  status="Original ten pickup icons/four phases; actual actor and final hardware leases still open",
                  source=ref.binding(ref.ROM), actual_source_path="A5FE..A63A before contact; actual DB4A/MMC3 area mapping/DE4A/C716 return",
                  special_palette_rule="Original A61F..A638 fixes top-right source tile palette0 for types2/6 and palette1 for type7; included before encoding",
                  frames=facts, actual_host_pixel_cases=tests, actual_five_area_cases=areas,
                  original_area_palette_roles=palette_roles,
                  private_CHR_pages=[694, 695], sprite_windows=[6, 7],
                  odd_encoded_tiles=True, unique_8x16_pairs=len(pairs),
                  records=len(unique), descriptor_and_table_bytes=sizes,
                  mirror_data="121:BE00..BFFF exposed at C121DE00..DFFF",
                  native_geometry_adaptation="Original item center=(host item top-leftX+8,Y+8)",
                  frozen_body_weapon_and_death_assets_unchanged=True,
                  remaining=["Genuine compiled auxiliary object and mirror pointer consumer",
                             "Actual native emerging/mature actor identity, contact/erase/score and announcement",
                             "Prove sprite6/7 lease doesn't replace world/enemy/effect patterns",
                             "Compose source palette roles with actual native world rather than overwrite shared enemy/backdrop colors",
                             "Native displayed emergence and hardware OAM/scanline/cadence"],
                  bindings=[ref.binding(p) for p in [Path(__file__), ref.ROM,
                      ROOT / "tools/prepare_rogue_dawn_art_v1.py",
                      ROOT / "tools/rogue_dawn_render_controls_v1.py",
                      ROOT / "tools/audit/rogue_dawn_audio_owner_v1.py",
                      ROOT / "tools/audit/verify_native_relocation.py",
                      BASE.with_suffix(".nes"), BASE.with_suffix(".lbl"),
                      BASE.with_suffix(".dbg"), frozen, CHR, INC]])
    REPORT.write_text(json.dumps(report, indent=2)+"\n")
    (OUT / "handoff.json").write_text(json.dumps(dict(passed=True, source_only=True,
        outputs=[ref.binding(p) for p in [CHR, INC, REPORT]], bindings=report["bindings"]), indent=2)+"\n")
    print(json.dumps(dict(pairs=len(pairs), unique_records=len(unique), bytes=sizes,
                         host_cases=len(tests), area_cases=len(areas), report_SHA256=ref.digest(REPORT.read_bytes()))))


if __name__ == "__main__":
    main()
