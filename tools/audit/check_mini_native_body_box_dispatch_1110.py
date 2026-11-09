"""Qualify the Mini body-box route through the incumbent row-16 admission."""

import argparse
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
import subprocess

import check_mini_lift_retention_1110_v1 as L
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from compose_mini_frame_budget_1108 import check_full_cpu
from prepare_mini_side_alias_1108 import compare_memory


N, M, R = L.N, L.M, L.R
BASE = R/'build/mini-lane-audio-native-1110/candidate.nes'
PIN = 'a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746'
SOURCE = R/'tools/reference/mini_native_body_box_dispatch_1110_v1.s'
SPANS = (('BOX93',93,0xa703,133),('STAGE86',86,0xa2a9,15),('CALL86',86,0xa454,15))
OLD = bytes.fromhex(
    '0848ad0260c913d01768288d6a01a91b8d6c01a9ac8d6d01a9d9205a014c76a7'
    '68280848200ca0b01768288d6a01a9c88d6c01a9ad8d6d01a9da205a014c76a7'
    '6828204e9f204aabad7105187d5dab8d5806ad7105187d63ab8d5a06ad7c05187d69ab'
    '8d5906ad7c051869208d5b06a200a0008d6a01a9008d6c01a9a08d6d01a9d64c5a01')


def offset(bank,pc):
    return 16+8192*bank+(pc&8191)


def assemble(output,raw):
    assert M.sha(raw)==PIN
    # Source pad predecessors jump over their explicitly declared tails.
    for pc,jump in ((0xa2a9,'4ccaa5'),(0xa454,'4c79a4')):
        at = offset(86,pc)
        assert raw[at-3:at+15]==bytes.fromhex(jump)+b'\xea'*15
    assert raw[offset(93,0xad8e):offset(93,0xad93)]==bytes.fromhex('68284c03a7')
    assert raw[offset(65,0xb0bc):offset(65,0xb0bf)]==bytes.fromhex('4c40a7')
    assert raw[offset(65,0xade7):offset(65,0xadea)]==bytes.fromhex('4c4e9f')
    x5 = (R/'src/x5_bounce.s').read_text()
    assert 'jmp X5OwnInventoryUi\n  .res 15,$ea' in x5
    assert 'jmp X5Cv3HorizontalFinish\n  .res 15,$ea' in x5
    cfg,obj,data = (output/f'dispatch.{ext}' for ext in ('cfg','o','bin'))
    cfg.write_text('MEMORY {\n'+''.join(f'{name}: start=${pc:04x},size={n},file=%O;\n'
        for name,_,pc,n in SPANS)+'}\nSEGMENTS {\n'+''.join(f'{name}: load={name},type=ro;\n'
        for name,*_ in SPANS)+'}\n',encoding='utf-8')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',data],check=True)
    obj.unlink()
    packed = data.read_bytes()
    assert len(OLD)==133 and len(packed)==163
    rows,cursor = [],0
    for (role,bank,pc,size),old in zip(SPANS,(OLD,b'\xea'*15,b'\xea'*15),strict=True):
        at = offset(bank,pc)
        assert raw[at:at+size]==old,role
        rows.append(dict(file_offset=at,old_hex=old.hex(),new_hex=packed[cursor:cursor+size].hex(),role=role))
        cursor += size
    return install(raw,rows),rows


def direct(seed,entry,flags):
    m = seed
    m.raw_page(1,0xdd)
    N.put(m,CurrentBank=0xdd)
    c = N.NesMPU(memory=m,pc=entry)
    c.sp,c.a,c.x,c.y,c.p = 230,0x61,0,0x39,flags
    c.stPushWord(0x5aff)
    stages = defaultdict(int)
    watch = {(193,0xb0bc):'auth',(3,0xa030):'source',(214,0xa000):'foot',
             (254,0x9f4e):'native',(214,0xa2a9):'fast', (214,0xa454):'call'}

    def observe(z):
        if z.pc<0x8000:
            return
        tag = z.memory.rawtags[(z.pc-0x8000)//8192]
        role = watch.get((tag,z.pc))
        if role:
            stages[role] += 1

    run(c,lambda z:(z.pc,z.sp)==(0x5b00,230),observe)
    return registers(c),c.processorCycles,dict(stages)


def differential(before,after):
    images = L.bundles(before,after)
    mini = [L.fixture(b,0,False,False) for b in images]
    foreign = [N.fresh(b) for b in images]
    stats = defaultdict(list)
    cases = [(raw,8,1,0x21,'foreign') for raw in range(42) if raw!=41]
    cases += [(41,engine,state,flags,proof) for engine,state,flags,proof in product(
              (4,7,8,9),(0,1,2),(0x21,0x60,0x65),
              ('active','epoch_stale','epoch_zero','ram2_marker','ram3_marker','ram2_tail','ram3_tail'))]
    for raw,engine,state,flags,proof in cases:
        pair = [slim_fork(m) for m in (foreign if proof=='foreign' else mini)]
        for m in pair:
            N.put(m,SelectedCharacter=raw,GameEngineSubroutine=engine,Player_State=state,
                  Player_Y_Speed=4,FrameCounter=7,Player_Rel_XPos=72,Player_Rel_YPos=176,
                  CrossoverBehaviorVersion=0)
            if proof!='foreign':
                m.ram[2][0x3f0] = 7
                if proof=='epoch_stale':
                    m.ram[2][0x3f0] = 6
                elif proof=='epoch_zero':
                    N.put(m,FrameCounter=0)
                    m.ram[2][0x3f0] = 0
                elif proof.startswith('ram'):
                    at = 0x1fe0 if proof.endswith('marker') else 0x1fe2
                    m.ram[int(proof[3])][at] ^= 0xff
        a,b = [direct(m,0xa703,flags) for m in pair]
        case = (raw,engine,state,flags,proof)
        assert a[0]==b[0],(case,a,b)
        compare_memory(*pair)
        assert pair[0][0x15a:0x17b]==pair[1][0x15a:0x17b],(case,a,b)
        assert a[2].get('foot')==b[2].get('foot')==1,(case,a,b)
        for role in ('auth','source','native'):
            assert a[2].get(role)==b[2].get(role),(case,role,a,b)
        assert b[2].get('fast',0)==int(raw==41)
        stats[proof].append(a[1]-b[1])
    return {name:dict(cases=len(cost),cycles_saved=[min(cost),max(cost)])
            for name,cost in stats.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    candidate,patches = assemble(args.output,raw)
    box = differential(raw,candidate)
    whole = check_full_cpu(raw,candidate,{})
    refs = (Path(__file__),SOURCE,BASE,R/'src/little_mac_terrain.s',R/'src/x5_bounce.s',
            R/'tools/reference/mini_mario_idle_fast.s')
    q = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(candidate),
             patches=patches,body_box=box,whole_GameCore=whole,
             bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (args.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('patches','bindings')}),flush=True)


if __name__=='__main__':
    main()
