"""Link the six actual Rogue Dawn lower music banks into unused PRG tails.

This is a read-only storage component. It installs no music driver, scheduler,
mapper reader or menu entry. All 49,152 original lower-bank bytes are retained;
identical 256-byte pages share storage. No finite playback trace chooses bytes.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rogue_dawn_map_v1 as source

OUT = ROOT / "build/rogue-dawn-audio-pages-v2"
PARENT = ROOT / "build/roster-shared-celeste-small-chr-v1.nes"
PARENT_SHA = "f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9"
LOWER_BANKS = [52, 48, 53, 54, 50, 51]  # Actual C238 source area order.
# Physical offsets, not virtual link addresses. Every span is independently
# checked against the qualified parent's FF preimage and existing segment map.
SLOTS = [(79, 0x1600, 10), (80, 0x0E00, 18), (78, 0x1D00, 3),
         (71, 0x1000, 16), (116, 0x1000, 16), (90, 0x0F00, 17),
         (87, 0x1100, 15), (72, 0x1100, 15), (67, 0x1300, 13),
         (88, 0x1400, 12), (83, 0x1600, 10), (84, 0x1600, 7)]
MAP_BANK, MAP_OFFSET = 62, 0x1BA7  # after actual Kamikaze core end BBA7.
MAP_BYTES = 6 * 32 * 2


def sha(data):
    return hashlib.sha256(data).hexdigest()


def binding(path):
    p = Path(path)
    data = p.read_bytes()
    return dict(path=str(p.resolve()), bytes=len(data), sha256=sha(data))


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


def byte_lines(data):
    return [" .byte " + ",".join(f"${v:02x}" for v in data[i:i+24])
            for i in range(0, len(data), 24)]


def main():
    assert not (OUT / "proof.json").exists(), "Preserve qualified source unit"
    OUT.mkdir(parents=True, exist_ok=True)
    parent = PARENT.read_bytes()
    original = source.ROM.read_bytes()
    assert sha(parent) == PARENT_SHA and sha(original) == source.EXPECTED
    assert original[16+62*8192+0x238:16+62*8192+0x23E] == bytes(LOWER_BANKS)
    # Free space is derived from the qualified parent's actual segment end;
    # the preimage check is an additional guard, not a substitute for ownership.
    future = ROOT / "build/smb2-roll-relocation-v1/candidate.nes"
    assert sha(future.read_bytes()) == "1b38535bca411ec400a7c3efd15ee61b9823a247d4ee0f59572f38a6beff0b85"
    # The accepted SMB2-audio prerequisite moves Roll into two current FF
    # tails. Both actual maps are checked, even though that unit is not live.
    ownership_inputs = [PARENT.with_suffix(".dbg"), future.with_suffix(".dbg")]
    cfg = (ROOT / "smb1base-mmc5-expanded.cfg").read_text()
    memories = {}
    import re
    for name, start, bank in re.findall(
            r"^\s*(\w+):\s*start\s*=\s*\$([0-9a-f]+),.*?bank\s*=\s*\$([0-9a-f]+);",
            cfg, re.I | re.M):
        memories[int(bank, 16)] = (name, int(start, 16))
    # DBG records physical output offsets, not mapper bank fields.
    occupied = []
    for line in "\n".join(p.read_text() for p in ownership_inputs).splitlines():
        if not line.startswith("seg\t"):
            continue
        fields = dict(re.findall(r'(\w+)=((?:"[^"]*")|[^,]+)', line[4:]))
        if "ooffs" in fields and "start" in fields and "size" in fields:
            offset = int(fields["ooffs"], 0)-16
            size = int(fields["size"], 0)
            if size and 0 <= offset < 1048576:
                remaining = size
                while remaining:
                    bank, lo = divmod(offset, 8192)
                    length = min(remaining, 8192-lo)
                    occupied.append((bank, lo, lo+length, fields.get("name", "?")))
                    offset += length
                    remaining -= length
    assert occupied, "Actual segment-owner inspection must not be empty"
    leases = [(b, off, off+count*256) for b, off, count in SLOTS]
    leases.append((MAP_BANK, MAP_OFFSET, MAP_OFFSET+MAP_BYTES))
    for bank, lo, hi in leases:
        assert hi <= 8192 and lo < hi
        assert parent[16+bank*8192+lo:16+bank*8192+hi] == b"\xff"*(hi-lo)
        collisions = [o for o in occupied if o[0] == bank and lo < o[2] and o[1] < hi]
        assert not collisions, (bank, hex(lo), collisions)
    pages, index = [], {}
    areas = []
    for bank in LOWER_BANKS:
        row = []
        for page in range(32):
            data = original[16+bank*8192+page*256:16+bank*8192+(page+1)*256]
            if data not in index:
                index[data] = len(pages)
                pages.append(data)
            row.append(index[data])
        areas.append(row)
    assert len(pages) == 152 == sum(count for _, _, count in SLOTS)
    positions = [(bank, off+i*256) for bank, off, count in SLOTS for i in range(count)]
    src = ROOT / "src/rogue_dawn_audio_pages_v2.s"
    lines = ["; Original Rogue Dawn lower music banks, byte-complete page depot.",
             "; Storage only. No audio callback or logical mapper is installed.",
             "; Bank tables name temporary A-window mappings, irrespective of",
             "; a storage bank's normal A/C linker view. Reader remains separate.",
             ".export RdaLowerBankTable,RdaLowerHighTable,RdaLowerMapsEnd"]
    for slot, (bank, off, count) in enumerate(SLOTS):
        lines += [f'.segment "ROGUE_AUDIO_PAGES_{slot}"']
        first = positions.index((bank, off))
        for page_id in range(first, first+count):
            lines += [f"RdaPage{page_id}:"] + byte_lines(pages[page_id])
    lines += ['.segment "ROGUE_AUDIO_PAGE_MAP"', "RdaLowerBankTable:"]
    lines += byte_lines(bytes(positions[i][0] | 0x80 for row in areas for i in row))
    lines += ["RdaLowerHighTable:"]
    lines += byte_lines(bytes(0xA0+(positions[i][1] >> 8) for row in areas for i in row))
    lines += ["RdaLowerMapsEnd:",
              '.assert RdaLowerMapsEnd-RdaLowerBankTable=384,error,"Six exact source page maps"']
    src.write_text("\n".join(lines)+"\n")
    extra = []
    for slot, (bank, off, _) in enumerate(SLOTS):
        memory, start = memories[bank]
        extra.append(f"    ROGUE_AUDIO_PAGES_{slot}: load={memory},type=ro,start=${start+off:04x},optional=yes;")
    memory, start = memories[MAP_BANK]
    extra.append(f"    ROGUE_AUDIO_PAGE_MAP: load={memory},type=ro,start=${start+MAP_OFFSET:04x},optional=yes;")
    overlay = OUT / "overlay"
    overlay.mkdir(exist_ok=True)
    cfg = once(cfg, "}\nSYMBOLS {", "\n"+"\n".join(extra)+"\n}\nSYMBOLS {")
    (overlay / "smb1base-mmc5-expanded.cfg").write_text(cfg)
    # Genuine separate object: no pressure on entrypoint's segment-count cap.
    builder = (ROOT / "tools/build_mmc5_expanded.py").read_text()
    builder = once(builder, "a=p.parse_args(); root=a.workspace.resolve(); overlay=(a.source_overlay or root).resolve()",
                   "a=p.parse_args(); root=a.workspace.resolve(); overlay=(a.source_overlay or root).resolve(); sys.path.insert(0,str(root/'tools'))")
    builder = once(builder, "command += [str(objects/'main.c'),str(objects/'entrypoint.s')]",
                   "command += [str(objects/'main.c'),str(objects/'entrypoint.s')]\n if flag: command += ["+repr(str(src))+ "]")
    private = OUT / "private_builder.py"
    private.write_text(builder)
    command = [sys.executable, "-B", str(private), "--workspace", str(ROOT),
               "--source-overlay", str(overlay), "--output", str(OUT / "candidate.nes")]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (OUT / "build.log").write_text(run.stdout+run.stderr)
    assert run.returncode == 0, run.stdout+run.stderr
    result = (OUT / "candidate.nes").read_bytes()
    assert result[:16] == parent[:16] and result[16+1048576:] == parent[16+1048576:]
    changed = []
    for bank in range(128):
        for off, (a, b) in enumerate(zip(parent[16+bank*8192:16+(bank+1)*8192],
                                       result[16+bank*8192:16+(bank+1)*8192])):
            if a != b:
                assert any(bank == cb and lo <= off < hi for cb, lo, hi in leases), (bank, off)
                changed.append((bank, off))
    for area, source_bank in enumerate(LOWER_BANKS):
        recovered = bytearray()
        for page in range(32):
            ordinal = area*32+page
            b = result[16+MAP_BANK*8192+MAP_OFFSET+ordinal] & 127
            h = result[16+MAP_BANK*8192+MAP_OFFSET+192+ordinal]
            assert 0xA0 <= h <= 0xBF
            off = (h-0xA0)*256
            recovered.extend(result[16+b*8192+off:16+b*8192+off+256])
        assert recovered == original[16+source_bank*8192:16+(source_bank+1)*8192]
    proof = dict(status="PASS_SOURCE_STORAGE_ONLY_NO_AUDIO_DRIVER_OR_NATIVE", passed=True,
                 parent=binding(PARENT), original=binding(source.ROM), candidate=binding(OUT / "candidate.nes"),
                 source_area_order=LOWER_BANKS, source_bytes=49152, unique_pages=152,
                 stored_bytes=38912, exact_recovered_banks=6, page_maps_bytes=MAP_BYTES,
                 all_source_addresses_8000_9FFF_preserved=True,
                 actual_parent_segment_owners_inspected=len(occupied),
                 leases=[dict(bank=b, physical_start=lo, physical_end_exclusive=hi) for b,lo,hi in leases],
                 modified_bytes=len(changed), modified_banks=sorted({b for b,_ in changed}),
                 header_CHR_and_existing_bytes_outside_leases_exact=True,
                 command=command, bindings=[binding(p) for p in [Path(__file__), src,
                     ROOT / "tools/build_mmc5_expanded.py", ROOT / "smb1base-mmc5-expanded.cfg",
                     *ownership_inputs, future, private, overlay / "smb1base-mmc5-expanded.cfg"]],
                 retained_rejected_draft=dict(proof=binding(ROOT / "build/rogue-dawn-audio-pages-v1/proof.json"),
                     reason="v1 storage bytes recovered correctly but consumed accepted future Roll destinations. It was never installed; v2 checks both actual segment-owner maps."),
                 limitations="Read-only storage/link component. No executing audio reader, register projection, private audio context, scheduler/Main cues, mixed playback, source-vs-assembled callback or native qualification. No claim that all retained bytes are music; complete original lower banks intentionally bound all reads.")
    (OUT / "proof.json").write_text(json.dumps(proof, indent=2)+"\n")
    print(json.dumps({k:proof[k] for k in ["status", "source_bytes", "stored_bytes", "candidate", "modified_banks"]}))


if __name__ == "__main__":
    main()
