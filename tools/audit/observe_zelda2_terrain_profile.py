"""Observe actual linked Zelda II terrain rows and authenticated sprite bounds."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re
from check_tmnt_render_oa import load, address
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(pose, side, source, chr_bytes):
    tag = f'Z2Pose{pose}{side}:'
    body = source.split(tag, 1)[1].split('Z2Pose', 1)[0]
    parts = re.findall(r'MetaspriteVramOffset\{\$(..)\}, \{SPRITE_BANK_0\}, \$(..), (-?\d+), (-?\d+)', body)
    assert parts, (pose, side)
    points = []
    for tile, flags, dy, dx in parts:
        tile, flags, dy, dx = int(tile,16), int(flags,16), int(dy), int(dx)
        raw = chr_bytes[pose*1024+tile*16:pose*1024+tile*16+32]
        assert len(raw) == 32
        for y in range(16):
            for x in range(8):
                at = (y//8)*16+y%8
                value = ((raw[at]>>(7-x))&1) | (((raw[at+8]>>(7-x))&1)<<1)
                if value:
                    points.append((dx+(7-x if flags&64 else x),dy+(15-y if flags&128 else y)))
    return (dict(left=min(x for x,y in points),top=min(y for x,y in points),
                 right=max(x for x,y in points),bottom=max(y for x,y in points)) if points else None)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();out=args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    b=load(args.rom)
    assert (b['raw'][6]>>4)|(b['raw'][7]&240)==5
    rows=[]
    for variant,mode,crouch,state in itertools.product([0,1],[0,1],[0,1],[0,1,2]):
        memory=[0]*65536
        for page,bank in [(0,126),(1,1),(2,70),(3,127)]:
            memory[0x8000+page*8192:0xa000+page*8192]=b['raw'][16+bank*8192:16+(bank+1)*8192]
        fields=dict(SelectedCharacter=4,Z2Variant=variant,CrossoverBehaviorVersion=mode,
                    CrouchingFlag=crouch,Player_State=state,CurrentBank=129,CurrentBankC=198)
        for n,v in fields.items():memory[address(b,n)]=v
        cpu=NesMPU(memory=memory,pc=address(b,'MegaManCollisionAdder'))
        cpu.sp=0xfd;cpu.p=0x35;cpu.stPushWord(0x7eff)
        for _ in range(150):
            if cpu.pc==0x7f00:break
            cpu.step()
        else:raise AssertionError('Terrain selector did not return')
        assert cpu.p&1,'Actual selector admits guest terrain profile'
        row=cpu.y
        offset=memory[address(b,'BlockBufferAdderData')+row]
        adders=memory[address(b,'BlockBuffer_Y_Adder')+offset:address(b,'BlockBuffer_Y_Adder')+offset+7]
        rows.append(dict(variant=variant,mode=mode,crouch=crouch,state=state,
                         terrain_row=row,vertical_adders=adders,head_to_foot_height=adders[1]-adders[0]))
    source=ROOT/'src/zelda2_link_art.inc';chr_path=ROOT/'chr/characters/zelda2-link-body.chr'
    sprite_bounds={f'{pose}-{side}':bounds(pose,side,source.read_text(),chr_path.read_bytes())
                   for pose in [3,6,*range(11,27)]for side in ['Right','Left']}
    original_path=Path('C:/NES/Zelda II - The Adventure of Link (USA).nes')
    original=original_path.read_bytes()
    assert hashlib.sha256(original).hexdigest()=='9fca03064a5113e6a92f550d9f42bac9ac1ae248a84df1f653d7cd7f76a1803d'
    physical=16+7*16384
    horizontal=original[physical+0x2aa0:physical+0x2ac0]
    vertical=original[physical+0x2ac0:physical+0x2ae0]
    assert horizontal[:8]==bytes([23,9,23,9,20,12,20,12])
    assert vertical[:8]==bytes([0xe6,0xe6,0xfa,0xfa,0,0,0xe0,0xe0])
    original_cases=[]
    for fairy,shield,face in itertools.product([0,8],[0,1],[1,2]):
        memory=[0]*65536
        memory[0x8000:0xc000]=original[16+16384:16+2*16384]
        memory[0xc000:]=original[physical:physical+16384]
        memory[0x6000:0x8000]=[0x40]*8192
        for at,value in {0x4d:96,0x3b:0,0x29:80,0x5f:face,0x13:fairy,0x17:shield,0xb5:1,0x19:1}.items():
            memory[at]=value
        cpu=NesMPU(memory=memory,pc=0xe079);cpu.sp=0xfd;cpu.stPushWord(0x7eff)
        queries=[]
        for _ in range(3000):
            if cpu.pc in [0xe14a,0x7f00]:break
            if cpu.pc==0xeae8:
                i=cpu.y
                assert i<len(horizontal)
                queries.append(dict(native_index=i,source_dx=horizontal[i],
                                    source_buffer_dy=vertical[i]-256 if vertical[i]>=128 else vertical[i],
                                    adapted_port_dx=horizontal[i]-8,
                                    adapted_physical_dy=(vertical[i]-256 if vertical[i]>=128 else vertical[i])+32))
            cpu.step()
        else:raise AssertionError(('Original terrain observation timed out',hex(cpu.pc)))
        original_cases.append(dict(fairy=fairy,shield=shield,facing=face,queries=queries))
    report=dict(observation_complete=True,repair_passed=False,goal_complete=False,ROM_sha256=sha(args.rom),
                actual_selector_cases=rows,original_art_sha256=sha(source),original_CHR_sha256=sha(chr_path),
                opaque_source_sprite_bounds=sprite_bounds,
                original_ROM_sha256=sha(original_path),original_probe_table_CPU=['EAA0','EAC0'],
                original_probe_horizontal=list(horizontal),original_probe_buffer_vertical=list(vertical),
                original_actual_terrain_query_cases=original_cases,
                coordinate_conversion='Native art rebases originalX by+8 for the port origin; original generic collision rows exclude32px HUD. Adapted probe DX=sourceDX-8, physical DY=signed sourceDY+32. Native crouch shield state is observed, not assumed to halve terrain height.',
                scope='Actual assembled terrain-adder selector for original Link/ZeldaII alternate, both modes, crouch flags and native states; original prepared sprite masks decoded separately. This records the current mismatch. No ROM, game state, movement, terrain, hitbox or assertion repair is installed; not a native gameplay proof.')
    (out/'proof.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(observation_complete=True,repair_passed=False,terrain_rows=sorted(set(r['terrain_row']for r in rows)),
                         stand_bounds=sprite_bounds['3-Right'],crouch_bounds=sprite_bounds['6-Right'],
                         original_probe_cases=original_cases,
                         fairy_bounds={k:v for k,v in sprite_bounds.items()if k.endswith('Right')and int(k.split('-')[0])>=11})),flush=True)


if __name__=='__main__':main()
