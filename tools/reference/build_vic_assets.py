"""Extract Vic Viper's original NES poses and weapon records, without redrawing."""
from pathlib import Path
import hashlib
import importlib.util
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/verification/vic-viper-lq/art'
ROM = Path('C:/NES/Gradius (USA).nes')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = ROM.read_bytes()
    assert hashlib.sha1(raw).hexdigest() == '92645fe142861c3d3fda209bb906ad2b0e353988'
    prg, chr_data = raw[16:16+32768], raw[16+32768:]
    spec = importlib.util.spec_from_file_location('gradius_meta', ROOT/'reference/gradius-nes/export_metasprites.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    poses = module.records(prg)
    def b(a): return prg[a-0x8000]
    palette = list(prg[0x879a-0x8000:0x879a-0x8000+16])
    ids = sorted({1,2,3,4,5,8,10,16,17,18,
                  *[x for x in prg[0xc0fa-0x8000:0xc101-0x8000] if x],
                  *prg[0xa0e0-0x8000:0xa0e0-0x8000+6]})
    meta = {str(i): poses[i] for i in ids if i in poses}
    # Stock ship/shot pixels repeat in all four CNROM banks. Prove rather than
    # assuming the player's art belongs to the stage background bank.
    tiles = sorted({r[1] for records in meta.values() for r in records})
    tile_pairs = {}
    for tile in tiles:
        address = (tile & 1)*4096 + (tile & 0xfe)*16
        data = chr_data[address:address+32]
        assert all(chr_data[bank*8192+address:bank*8192+address+32] == data for bank in range(4)), ('CNROM-dependent sprite',tile)
        tile_pairs[tile] = data
    # Standard NES RGB preview values. Only original palette indices enter the
    # ROM; this display transform is neither sprite recoloring nor asset data.
    rgb = {0x0f:(0,0,0),0x0c:(0,64,88),0x26:(248,120,88),
           0x30:(252,252,252),0x2c:(0,232,216),0x21:(60,188,252),0x06:(108,6,0)}
    canvas = Image.new('RGBA',(128*4,56*((len(meta)+3)//4)),(0,0,0,0))
    for number,(key,records) in enumerate(meta.items()):
        for dy,tile,attr,dx in records:
            dx = dx if dx<128 else dx-256
            dy = dy if dy<128 else dy-256
            data = tile_pairs[tile]
            for y in range(16):
                for x in range(8):
                    yy=15-y if attr&128 else y;xx=7-x if attr&64 else x
                    off=(yy//8)*16+yy%8
                    color=((data[off]>>(7-xx))&1)|(((data[off+8]>>(7-xx))&1)<<1)
                    if color:
                        dest=(number%4*128+48+dx+x,number//4*56+24+dy+y)
                        if 0<=dest[0]<canvas.width and 0<=dest[1]<canvas.height:
                            canvas.putpixel(dest,(*rgb[palette[(attr&3)*4+color]],255))
    canvas.save(OUT/'source-poses.png')
    report=dict(rom_sha256=hashlib.sha256(raw).hexdigest(), source='Original USA Gradius ROM',
        palette_address=0x879a, palette=palette, records=meta,
        weapon_tables=list(prg[0xa0e0-0x8000:0xa0e0-0x8000+9]),
        missile_tables=list(prg[0xa1a4-0x8000:0xa1a4-0x8000+6]),
        original_tile_pairs=tiles, bank_identical=True,
        capsule_source='Original$AEC1 promotion to status6; original animation16/17/18.',
        death_walk_address=0xc0fa,death_walk=list(prg[0xc0fa-0x8000:0xc101-0x8000]),
        art_status='EXTRACTED_ORIGINAL_RECORDS_NOT_YET_GAME_IMPLEMENTATION')
    (OUT/'source-records.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'original-pairs.bin').write_bytes(b''.join(tile_pairs[t] for t in tiles))
    print(json.dumps(dict(poses=ids,tiles=tiles,palette=palette,weapon_tables=report['weapon_tables'])))


if __name__=='__main__': main()
