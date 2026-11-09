"""Exact linked Mini floor-pair fast path on e90d and its b3bd side successor."""

import argparse
from collections import defaultdict
from itertools import product
import json
from pathlib import Path
import subprocess

import check_mini_lift_admission_fast_1108_v1 as F


R,N = F.ROOT,F.N
SOURCE = R/'tools/reference/mini_floor_pair_fast_1108_v1.s'
INPUTS = {'e90d': ('mini-frame-budget-1108','e90d30c1c9636be6eb304a7b3b1506b862f8171dc2773d809482e25b0a5417df'),
          'b3bd': ('mini-native-side-dispatch-rom-1108','b3bda384a54b2685e4cfc8a857304de71f390edc0460d52d051a2d68de746d1f')}
PC = 0xbe34
BANK = 20
OFFSET = 16+BANK*8192+(PC&8191)
OLD = bytes.fromhex('a00e2086958504208695c504d014c900f00ec954d00ca68e3008a5bd290fd00238601860')


def compile_probe(out, decorative):
    cfg, obj, binary = (out/f'floor.{ext}' for ext in ('cfg','o','bin'))
    cfg.write_text('MEMORY{P:start=$be34,size=36,file=%O;} '
                   'SEGMENTS{MINI_FLOOR_PAIR:load=P,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    source = SOURCE
    if decorative:
        text = SOURCE.read_text()
        assert text.count('and #$aa')==text.count('submask of $55')==1
        source = out/'floor-decor.s'
        source.write_text(text.replace('and #$aa','and #$a8').replace('submask of $55','submask of $57'))
    subprocess.run([cc/'ca65.exe',source,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
    result = binary.read_bytes()
    assert len(result)==len(OLD)==36
    return result,source


def tiles(bus, x, y, left, right, head=0, side=0):
    def put(px,py,tile):
        buf = 'Block_Buffer_2' if px&256 else 'Block_Buffer_1'
        address = F.address(bus.bundle,buf)+((px>>4)&15)+(py&0xf0)-32
        bus[address] = tile
    put(x+3,y+32,left)
    put(x+12,y+32,right)
    put(x+8,y+18,head)
    if side:
        put(x+13,y+24,side)


def setup(bus,x,y,left,right,*,speed=0,down=0,head=0,side=0,actor=41,mode=0,seed=0):
    F.setup_main(bus,x,7,mode,5)
    N.put(bus,Player_Y_Position=y,Player_Y_HighPos=1,Player_Y_Speed=speed,Player_State=seed,
          SavedJoypadBits=down,SavedJoypad1Bits=down,Up_Down_Buttons=down,
          SelectedCharacter=actor,PreviousA_B_Buttons=0,Player_Y_MoveForce=23,
          StompChainCounter=5,Player_CollisionBits=0,CurrentBankC=2)
    bus[0x5116]=2
    tiles(bus,x,y,left,right,head,side)


def stable(bus):
    return F.state(bus)


def game_state(bus):
    state=stable(bus)
    # BillNativeCaptureP/A are write-before-read within the old rare leaf.
    # The shortcut can omit that leaf; neither byte is an output here.
    return (state[0][:3]+state[0][11:],state[1],state[2][:0x1ff4]+state[2][0x1ff6:])+state[3:]


def run(bus,name):
    result = N.invoke(bus,name,a=0,x=0,y=0,p=0x31)
    return result['CPU'], tuple(result[k] for k in ('A','X','Y','P'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--decorative',action='store_true')
    args=parser.parse_args()
    out=args.output.resolve();out.mkdir(exist_ok=True)
    code,source=compile_probe(out,args.decorative)
    mask = 0xa8 if args.decorative else 0xaa
    domain = [t for t in range(256) if not t&mask]
    patch=dict(bank=BANK,pc=PC,file_offset=OFFSET,old_hex=OLD.hex(),new_hex=code.hex())
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,patches=[patch],comparisons={})
    for build,(folder,pin) in INPUTS.items():
        path=R/'build'/folder/'candidate.nes'
        rom=path.read_bytes()
        assert F.sha(rom)==pin and rom[OFFSET:OFFSET+36]==OLD
        new=rom[:OFFSET]+code+rom[OFFSET+36:]
        attr=(16+127*8192+(0xef36&8191))
        assert all(rom[attr+t]&2==0 for t in domain)
        assert not set(domain)&{0x5f,0x60,0x67,0x68,0xc2,0xc3,0xc5}
        parents=[F.bundle(v) for v in (rom,new)]
        for b in parents:
            b['segs']['mini_floor_pair'] = dict(start=str(0xbdf4),ooffs=str(16+BANK*8192+0x1df4))
            b['syms']['MiniBackground'] = dict(val=str(0xbdf4),seg='mini_floor_pair')
            b['syms']['ProbeFloor'] = dict(val=str(PC),seg='mini_floor_pair')
        seeds=[F.fixture(b,0,False,False) for b in parents]

        # Execute the exact new floor instructions for every admitted raw tile
        # pair, both a same-page and a cross-page native foot probe.
        checks=0
        floor=N.fork(seeds[1])
        for x,(left,right),buttons in product((744,758),product(domain,repeat=2),(0,4,8)):
            setup(floor,x,112,left,right,down=buttons)
            result=N.invoke(floor,'ProbeFloor',a=0,x=0,y=14,p=0x30)
            raw=left|right
            expect=not raw or not (buttons&4 and not raw&4)
            assert bool(result['P']&1)==expect, (build,x,left,right,buttons,result)
            assert floor[4]==raw, (build,x,left,right,buttons,floor[4])
            checks+=1

        rows=defaultdict(list)
        nominal=((0,0),(0x54,0x54),(0x54,0),(0,0x54),
                 (0x10,0),(0,0x10),(0x11,0),(0,0x11),(0x10,0x11))
        if args.decorative:
            nominal+=((0x12,0),(0,0x12),(0x13,0),(0,0x13),(0x12,0x13))
        scenarios=[('ordinary',x,y,l,r,dict(down=down,speed=speed))
                   for x,y,(l,r),down,speed in product((744,758),(32,96,112,176,192),
                       nominal,(0,4),(0,2,255))]
        scenarios.extend(('effect',758,y,l,r,options) for y,(l,r),options in product(
            (112,113,116), ((0x11,0),(0,0x11),(0x54,0x54),(0x10,0x11)),
            (dict(head=0xc2),dict(side=0xc2),dict(head=0x67),dict(side=0x24),dict(actor=0),dict(actor=6))))
        special=(0,0x11,0x54,0x5f,0x60,0x67,0x68,0xc2,0xc3,0xc5)+((0x13,) if args.decorative else ())
        scenarios.extend(('special_floor',758,112,l,r,dict()) for l,r in product(special,repeat=2))
        for label,x,y,left,right,kw in scenarios:
            pair=[N.fork(seed) for seed in seeds]
            for m in pair:
                setup(m,x,y,left,right,**kw)
            out_before,out_after=(run(m,'MiniBackground') for m in pair)
            assert game_state(pair[0])==game_state(pair[1]), (build,label,x,y,left,right,kw,'Background state')
            if kw.get('actor',41)!=41 or out_before[0]==out_after[0]:
                assert out_before[1]==out_after[1], (build,label,x,y,left,right,kw,out_before,out_after)
            if left==0x10 and right==0x11 and kw.get('down')==4 and not kw.get('speed'):
                assert N.get(pair[1],'GameEngineSubroutine')==3
            if (left,right)==(0x12,0x13) and kw.get('down')==4 and not kw.get('speed'):
                assert N.get(pair[1],'GameEngineSubroutine')==8
            raw=left|right
            row='asymmetric_pipe' if left!=right and raw in (0x10,0x11) and not kw else label
            if left!=right and raw==0x13 and (not left or not right) and not kw:
                row='asymmetric_decor_pipe'
            rows[row].append(out_before[0]-out_after[0])

        for mode,(left,right),down in product((0,1),nominal,(0,4)):
            pair=[N.fork(seed) for seed in seeds]
            for m in pair:
                setup(m,758,112,left,right,down=down,mode=mode)
            out_before,out_after=(run(m,'GameCoreRoutine') for m in pair)
            assert game_state(pair[0])==game_state(pair[1]),(build,mode,left,right,down,'GameCore state')
            assert out_before[1]==out_after[1],(build,mode,left,right,down,'GameCore AXYP')
            label='whole_GameCore_pipe' if (left,right) in ((0x11,0),(0,0x11)) and not down else 'whole_GameCore_other'
            if (left,right) in ((0x13,0),(0,0x13)) and not down:
                label='whole_GameCore_decor_pipe'
            rows[label].append(out_before[0]-out_after[0])

        report['comparisons'][build] = dict(parent_SHA256=pin,memory_only_SHA256=F.sha(new),
            floor_instruction_cases=checks,background_cases=len(scenarios),actual_GameCore_cases=4*len(nominal),
            cycle_deltas={label:dict(cases=len(values),min_saved=min(values),max_saved=max(values))
                          for label,values in rows.items()})
        if build=='e90d':
            compact=dict(passed=True,parent_SHA256=pin,expected_memory_only_SHA256=F.sha(new),
                         patches=[patch],qualification=report['comparisons'][build])
            (out/'proposal-e90d.json').write_text(json.dumps(compact,indent=2)+'\n')
            print(json.dumps(compact['qualification']),flush=True)
    report['scope']='Exact linked CPU floor geometry and GameCore, source classes and native special fallbacks. R0..R7 and Bill rare return A/P scratch excluded from terminal comparison. No native route or interrupt proof.'
    report['floor_mask']=mask
    report['floor_domain']=domain
    report['bindings']={str(p):F.sha(p.read_bytes()) for p in {source,SOURCE,Path(__file__)}}
    (out/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['comparisons']))


if __name__=='__main__':
    main()
