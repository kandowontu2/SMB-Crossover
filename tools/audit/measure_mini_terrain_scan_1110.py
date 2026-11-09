"""Measure the native parser's empty-ceiling skip with no ROM output."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess

from prepare_mini_mario_native_power_1103_v56 import N, address, bundle, location
from prepare_mini_side_alias_1108 import compare_memory
from prepare_selected_native_packet_v1 import R, sha


BASE = R/'build/mini-current-peak-1110/adder/candidate.nes'
TRACE = R/'build/mini-current-peak-1110/capture/instruction-sample.json'
PIN = 'd7a91c05b27d080e89ff60c0e1420e23eb07d762a386ff6a28a81117d8d87c3c'
START, END = 0xa27b, 0xa2e4
BEFORE = bytes.fromhex(
    'ac5307d00cad6407c907d005a9624c96a2b9e3a1ac4607f002a988850a'
    'a200ad2a070aa8b9e7a18503c88404ad4607f00ae000f006a50329088503a000'
    'b97b8c2403f008a50a9da1049d7168e8e00df018ad5307c902d008e00bd004'
    'a954850ac8c008d0d8a404d0bb')
SOURCE = r'''
.setcpu "6502"
.segment "TERRAIN"
RendTerr:
 ldy AreaType
 bne TerrainTile
 lda WorldNumber
 cmp #7
 bne TerrainTile
 lda #$62
 bne StoreTerrain
TerrainTile:
 lda TerrainMetatiles,y
 ldy CloudTypeOverride
 beq StoreTerrain
 lda #$88
StoreTerrain:
 sta R7
 ldx #0
 lda TerrainControl
 asl a
 tay
LoadMask:
 lda TerrainRenderBits,y
 iny
 sty R1
 cpx #0
 bne FloorMask
 tay                         ; Only test A here. NextMask reloads the index.
 bne SaveMask
 ldx #8
 bne NextMask                ; Empty ceiling leaves the existing scenery.
FloorMask:
 ldy CloudTypeOverride
 beq SaveMask
 and #8
SaveMask:
 sta R0
 ldy #$f8
CheckBit:
 lda Bitmasks-$f8,y            ; Same eight bytes with Y wrapping after bit7.
 bit R0
 beq NextRow
 lda R7
 sta MetatileBuffer,x
 sta GuestTerrainColumn,x
NextRow:
 inx
 cpx #13
 beq RendBBuf
 cpx #11
 bne MoreBits
 lda AreaType
 cmp #2
 bne MoreBits
 lda #$54
 sta R7
MoreBits:
 iny
 bne CheckBit
NextMask:
 ldy R1
 bne LoadMask
RendBBuf:
.assert *-RendTerr=105,error,"Existing terrain span must stay exact"
'''


def assemble(output, old):
    names = ('AreaType','WorldNumber','TerrainMetatiles','CloudTypeOverride','R7',
             'TerrainControl','TerrainRenderBits','R1','R0','Bitmasks',
             'MetatileBuffer','GuestTerrainColumn')
    asm,cfg,obj,linked = (output/f'terrain.{ext}' for ext in ('s','cfg','o','bin'))
    asm.write_text(''.join(f'{name}=${address(old,name):04x}\n' for name in names)+SOURCE)
    cfg.write_text('MEMORY{T:start=$a27b,size=$0069,file=%O;}SEGMENTS{TERRAIN:load=T,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    for command in ((cc/'ca65.exe',asm,'-o',obj),(cc/'ld65.exe','-C',cfg,obj,'-o',linked)):
        out = subprocess.run(command,capture_output=True,text=True)
        assert out.returncode == 0,out.stderr
    obj.unlink()
    cfg.unlink()
    return linked.read_bytes()


def seed_terrain(m,values,pattern):
    area,control,cloud,world = values
    N.put(m,AreaType=area,TerrainControl=control,CloudTypeOverride=cloud,WorldNumber=world)
    for name in ('MetatileBuffer','GuestTerrainColumn'):
        start = address(m.bundle,name)
        m[start:start+13] = bytes((pattern+13*row)&255 for row in range(13))
    m[3:11] = bytes.fromhex('8a35a36fbb7d45aa')


def run_scan(m,flags):
    m.raw_page(1,130)
    N.put(m,CurrentBank=130)
    c = N.NesMPU(memory=m,pc=START)
    c.a,c.x,c.y,c.p,c.sp = 91,27,57,flags,199
    for _ in range(600):
        if c.pc == END:
            return (c.a,c.x,c.y,c.p,c.sp),c.processorCycles
        assert m[c.pc] != 0,hex(c.pc)
        c.step()
    raise AssertionError(('terrain scan bound',hex(c.pc)))


def check_scans(old,new):
    cases = Counter()
    selected = []
    for area,control,cloud,world,flags in product(range(4),range(16),[0,1,3,255],[0,7],[0x20,0x65,0xf1]):
        values = (area,control,cloud,world)
        pair = [N.Bus(b) for b in (old,new)]
        for m in pair:
            seed_terrain(m,values,control*17)
        outcomes = [run_scan(m,flags) for m in pair]
        a,b = (row[0] for row in outcomes)
        assert a[:2]+a[3:] == b[:2]+b[3:] and (a[2],b[2]) == (4,252),(values,a,b)
        compare_memory(*pair)
        saved = outcomes[0][1]-outcomes[1][1]
        cases[saved] += 1
        if (area,control,cloud,world,flags) == (1,1,0,0,0x20):
            selected = [row[1] for row in outcomes]
    return dict(cases=sum(cases.values()),cycle_savings=dict(sorted(cases.items())),X750_shape_cycles=selected)


def check_full_parser(old,new):
    cases = Counter()
    for area,control,cloud,scenery,owner in product(range(4),range(16),[0,3],range(4),[0,41]):
        values = (area,control,cloud,7 if control&1 else 0)
        outcomes = []
        pair = [N.Bus(b) for b in (old,new)]
        for m in pair:
            N.put(m,AreaPointer=0x25,SelectedCharacter=owner)
            N.invoke(m,'GetAreaDataAddrs')
            seed_terrain(m,values,control*17)
            N.put(m,BackgroundScenery=scenery,ForegroundScenery=3-scenery,
                  CurrentPageLoc=control&3,CurrentColumnPos=control,BlockBufferColumnPos=control+16*(area&1))
            # Use actual area data and object decoder; only the legal header
            # selectors above vary. Both buffer pages and shadows are live.
            outcomes.append(N.invoke(m,'AreaParserCore',a=83,x=71,y=109,p=0x61))
        a,b = outcomes
        assert all(a[k] == b[k] for k in ('A','X','Y','P')),(values,scenery,owner,a,b)
        compare_memory(*pair)
        cases[a['CPU']-b['CPU']] += 1
    return dict(cases=sum(cases.values()),cycle_savings=dict(sorted(cases.items())))


def memory_image(proof=None):
    raw = BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    old = bundle(raw)
    at = location(old,'RendTerr')
    assert (at,address(old,'RendTerr'),address(old,'RendBBuf')) == (0x428b,START,END)
    assert raw[at:at+len(BEFORE)] == BEFORE
    if proof is None:
        return raw,old,at
    p, = proof['patches']
    assert p['offset'] == at and bytes.fromhex(p['preimage']) == BEFORE
    body = bytes.fromhex(p['replacement'])
    return raw[:at]+body+raw[at+len(body):]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    raw,old,at = memory_image()
    args.output.mkdir()
    body = assemble(args.output,old)
    assert len(body) == len(BEFORE) == END-START
    candidate = raw[:at]+body+raw[at+len(body):]
    new = bundle(candidate)
    trace = json.loads(TRACE.read_text())
    assert trace['scene']['x'] == 750
    ops = {row['key']:row for row in trace['opcodes']}
    assert [ops[f'2:{pc:04x}']['visits'] for pc in (0xa2b8,0xa2bf,0xa2a7,0xa2d3) if f'2:{pc:04x}' in ops] == [13,2,2]
    scans = check_scans(old,new)
    assert scans['X750_shape_cycles'][0]-scans['X750_shape_cycles'][1]>200
    print(json.dumps(dict(terrain_scan=scans)),flush=True)
    parser_rows = check_full_parser(old,new)
    changed = dict(offset=at,preimage=BEFORE.hex(),replacement=body.hex())
    refs = [Path(__file__),BASE,TRACE,R/'src/level_tiles.s',R/'src/level_variants.s',
            args.output/'terrain.s',args.output/'terrain.bin']
    result = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=hashlib.sha256(candidate).hexdigest(),
        terrain_scan=scans,full_parser=parser_rows,patches=[changed],ROM_written=False,Mesen_run=False,
        bindings={str(p.resolve()):sha(p) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(full_parser=parser_rows,SHA256=result['expected_memory_only_SHA256'])),flush=True)


if __name__ == '__main__':
    main()
