"""Link and verify a single three-shadow clear in the native terrain parser."""

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_enemy_ordinary_dispatch_1110 as Q
import measure_mini_parser_health_batch_1108_v2 as H
import measure_mini_terrain_scan_1110 as T
from check_mini_funded_actor_1108_v3 import install


N, P, D, R = Q.N,Q.P,Q.D,Q.R
SOURCE = R/'tools/reference/native_parser_triple_shadow_1110.s'
DUAL = R/'build/parser-dual-shadow-1109'
FIXED, LEVEL = 0x9076,0xbfdd
SPANS = ((126,FIXED,92,'fixed'),(2,LEVEL,18,'level'))
EXPECTED_FIXED = bytes.fromhex('d004a8e00d60a25da95120c790a50448a50b1869a08503a50c6901850420ddbf688504'
                               'a9c08503a263a9d120c790a200a000e00b900abd7168f009dda104f00118a9002a910b'
                               '98186910a8e8e00d90e2606509850b8a650a850c60ea')
EXPECTED_LEVEL = bytes.fromhex('a0c0a90038910b910398e910a8a900b0f460')
CALLER = bytes.fromhex('a200a0008403bca104b936ef293ff00198a403910998186910a8e8e00d90e5ac0260184c7690ea')


def ingress(raw):
    for _,pc,count,name in SPANS:
        assert len((DUAL/f'{name}.bin').read_bytes())==count
    for bank,pc,expected,name in ((126,FIXED,EXPECTED_FIXED,'fixed'),(2,LEVEL,EXPECTED_LEVEL,'level')):
        assert (DUAL/f'{name}.bin').read_bytes()==expected
        D.check_span(raw,bank,pc,expected)
    for bank,pc,expected in (
        (126,0x95d8,bytes.fromhex('00d00303484a4a4a4aa8b9da95850a68290f1879d895850960')),
        (2,0xa2e7,bytes.fromhex('ada00420dc95')+CALLER),
        (126,0x8825,bytes.fromhex('0a0a0a0a8da004')),
        (2,0xa0f6,bytes.fromhex('eea004ada004291f8da00460')),
    ):
        D.check_span(raw,bank,pc,expected)

    prg = raw[16:16+128*8192]
    for code,sites in (
        ('4c7690',[(2,0x0310)]),('207690',[]),('6c7690',[]),
        ('20ddbf',[(126,0x1093)]),('4cddbf',[]),
        ('8da004',[(2,0x00fe),(126,0x0829)]),('eea004',[(2,0x00f6)]),
        ('8ca004',[]),('8ea004',[]),('cea004',[]),
    ):
        word = bytes.fromhex(code)
        hits = [(i//8192,i%8192) for i in range(len(prg)-2) if prg[i:i+3]==word]
        assert hits==sites,(code,hits)
    game = (R/'src/game.s').read_text()
    tile = (R/'src/level_tiles.s').read_text()
    assert game.count('sta BlockBufferColumnPos')==1 and 'and #%00000001' in game
    assert tile.count('sta BlockBufferColumnPos')==1 and 'and #%00011111' in tile

    b = P.bundle(raw)
    for name,at in (('Block_Buffer_1',0x300),('Block_Buffer_2',0x3d0),('MmBrickHealth',0x6051),
                    ('MmCoinHits',0x61f1),('MmSolidTerrain',0x66d1),('GuestTerrainColumn',0x6871)):
        assert P.address(b,name)==at
    m = N.Bus(b)
    actual = []
    for col in range(32):
        N.invoke(m,'GetBlockBufferAddr',a=col)
        pointer = m[9]+256*m[10]
        assert pointer==0x300+0xd0*(col>>4)+(col&15)
        actual.append(pointer)
    return dict(legal_columns=32,physical_BlockBuffer_pointers=actual,
                sole_native_health_entry=[2,0xa310],normal_page0_writer=[126,0x8829],
                native_increment_then_mask=[[2,0xa0f6],[2,0xa0fe]])


def link(raw,out):
    assert P.sha(raw)==Q.PIN
    owners = ingress(raw)
    cc = R/'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(prefix='shadow-link-',dir=out) as temporary:
        work = Path(temporary)
        cfg,obj,binary,lbl = (work/f'health.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY { F:start=$9076,size=$5c,file=%O; L:start=$bfdd,size=$12,file=%O; } '
                       'SEGMENTS { FIXED:load=F,type=ro; LEVEL:load=L,type=ro; }\n')
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
        data = binary.read_bytes()
        labels = {p[2][1:]:int(p[1],16) for s in lbl.read_text().splitlines() if (p:=s.split())}
    assert labels['ResetHealthColumn']==FIXED and labels['ClearSecond']==LEVEL
    assert len(data)==110
    patches = []
    for (bank,pc,size,_),old in zip(SPANS,(EXPECTED_FIXED,EXPECTED_LEVEL),strict=True):
        new,data = data[:size],data[size:]
        patches.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+size],file_offset=D.offset(bank,pc),
                            old_hex=old.hex(),new_hex=new.hex()))
    assert not data
    return install(raw,patches),patches,labels,owners


def whole(before,after):
    images = [P.bundle(q) for q in (before,after)]
    return dict(GameCore=H.check_mains(*images),full_parser=T.check_full_parser(*images))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    args.output.mkdir(exist_ok=True)
    before = Q.BASE.read_bytes()
    after,patches,labels,owners = link(before,args.output)
    print('Linked',P.sha(after),labels,flush=True)
    unit = H.check_tails(*[P.bundle(q) for q in (before,after)])
    assert set(unit['cycle_savings']) and min(unit['cycle_savings'])==0 and max(unit['cycle_savings'])>200
    print('Tails',unit,flush=True)
    frames = whole(before,after)
    inputs = (Path(__file__),SOURCE,DUAL/'fixed.bin',DUAL/'level.bin',DUAL/'parser-dual.s',
              R/'src/game.s',R/'src/level_tiles.s',R/'src/megaman_weapons.s',Path(H.__file__),Path(T.__file__))
    result = dict(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                  patches=patches,labels=labels,source_ingress=owners,column_tails=unit,whole=frames,
                  bindings={str(path.resolve()):P.sha(path.read_bytes()) for path in inputs})
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Whole parser',frames['full_parser'],flush=True)


if __name__=='__main__':
    main()
