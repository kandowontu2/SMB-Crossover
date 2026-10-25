"""Repack Gradius' six original power-bar cells into the existing SMB HUD page."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
O=R/'build/verification/vic-viper-lq/art/hud-mk'


def main():
    assert not O.exists()
    O.mkdir(parents=True)
    rom=Path('C:/NES/Gradius (USA).nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()=='38c44e0e6f531a2779271f10cd4daa08ee2616c59c49d476b6f4e9dc482bf5f3'
    source=rom[16+32768+8192:]
    native=bytearray((R/'chr/mmc5/bg_ground.chr').read_bytes()[:1024])
    # All standard HUD digits, alphabet, blank, dash, multiply and coin survive.
    keep=set(range(37))|{0x28,0x29,0x2e}
    free=sorted(set(range(64))-keep)
    pool={bytes(native[t*16:t*16+16]):t for t in keep}
    mapping={}
    for tile in [*range(9,32),0x62,0x63]:
        raw=source[tile*16:tile*16+16]
        # Source color1 is the dark interior;2/3 are frame/letters. The HUD
        # keeps their exact masks in SMB's white foreground, without recoloring
        # the level palettes or replacing any standard HUD glyph.
        mask=raw[8:]+bytes(8)
        if mask not in pool:
            assert free
            dest=free.pop(0)
            pool[mask]=dest
            native[dest*16:dest*16+16]=mask
        mapping[tile]=pool[mask]
    assert not free
    assert all(native[t*16:t*16+16]==(R/'chr/mmc5/bg_ground.chr').read_bytes()[t*16:t*16+16] for t in keep)
    (O/'vic-hud.chr').write_bytes(native)
    cells=[[9,10,11,12],[13,14,15,16],[17,18,19,20],[21,22,23,24],[25,26,27,28],[29,98,99,31],[29,30,30,31]]
    lines=['; Native Gradius cell masks, repacked into the standard HUD font page.','VvHudCells:']
    lines+=[' .byte '+','.join('$%02x'%mapping[t] for t in cell) for cell in cells]
    (O/'vic_hud.inc').write_text('\n'.join(lines)+'\n')
    report=dict(original_rom_sha256=hashlib.sha256(rom).hexdigest(),source_CHR_bank=1,source_pattern_table=0,physical_page=394,kept_native_HUD_tiles=sorted(keep),source_tile_mapping=mapping,adaptation='Original frame/letter pixel masks collapse source2/3 to native white; source1 uses backdrop. No global palette writes.')
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
