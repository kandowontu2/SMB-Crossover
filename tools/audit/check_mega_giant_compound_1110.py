"""Bind Giant body and destructive source probes to the current native Mario adapter."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import subprocess
import tempfile

from check_mega_giant_geometry_1110_v1 import DONOR, DONOR_PIN, M, R, SOURCE, address, bundle, sha
from check_mega_giant_pipe_ingress_1110_v1 import cell, place, world_x
from check_mega_giant_ppu_mapping_1110_v1 import start_stage
from prepare_mini_side_alias_1108 import compare_memory


HOST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
BASE = 0x5b80
STOP = 0x5b00
BANK, ENTRY = 93, 0xafe7
CRUSH = R/'tools/reference/mega_giant_mario_crush_1110_v1.s'
ROUTE = R/'tools/reference/mega_giant_mario_compound_1110.s'
EFFECT_BANK, EFFECT_PC = 137, 0xbe8b


def assemble(out, b):
    crush = CRUSH.read_text()
    names = [n for line in crush.splitlines() if line.startswith('.import')
             for n in line.split(' ', 1)[1].split(', ')]
    names += ['DisableCollisionDet', 'SwimmingFlag', 'Player_X_Speed', 'PlayerBGCollision']
    names = sorted(set(names))
    defs = ''.join(f'{n}=${address(b,n):04x}\n' for n in names)
    src = defs + ROUTE.read_text() + '\n' + re.sub(r'^\.import(?:zp)? .*\n', '', crush, flags=re.M)
    src += '\n' + SOURCE.read_text()
    with tempfile.TemporaryDirectory(prefix='link-', dir=out) as folder:
        temp = Path(folder)
        asm, obj, cfg, binary, labels = (temp/f'giant.{ext}' for ext in ('s','o','cfg','bin','lbl'))
        asm.write_text(src)
        cfg.write_text('MEMORY { CODE:start=$5b80,size=$400,file=%O; } '
                       'SEGMENTS { GIANT_ROUTE:load=CODE,type=ro; GIANT_CRUSH:load=CODE,type=ro; '
                       'GIANT:load=CODE,type=ro; }\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe', asm, '-o', obj], check=True)
        subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        symbols = {row.split()[2][1:]:int(row.split()[1],16) for row in labels.read_text().splitlines()}
        return binary.read_bytes(), symbols


def plain_call(mem, pc, witness):
    c = M.NesMPU(memory=mem, pc=pc)
    c.sp, c.p = 252, 0x31
    c.stPushWord(STOP-1)
    for _ in range(12000):
        if c.pc == STOP:
            assert c.sp == 252
            return
        witness(c)
        assert mem[c.pc], (hex(pc),hex(c.pc))
        c.step()
    raise AssertionError(('isolated call did not return',hex(pc),hex(c.pc)))


def donor_groups(raw, donor, code, labels):
    old = bytearray(65536)
    old[0x8000:] = donor[16:32784]
    new = bytearray(65536)
    new[0x8000:0xa000] = raw[16+126*8192:16+127*8192]
    new[BASE:BASE+len(code)] = code
    poses = visited = 0
    signatures = set()
    for duck, speed, y, page, x in product((0,1),(0,24,232),(0,20,31,32,63,96,127,176,225,239,255),(0,1,2),(4,127,250)):
        old[0x41], old[0x55], old[0x57], old[0xce], old[0xb5], old[0x86], old[0x6d] = (11 if duck else 0),0,speed,y,page,x,1
        new[0x717], new[0x46], new[0xbd], new[0xa4], new[0x75], new[0x5c] = duck,speed,y,page,x,1
        # Both buffers contain air. Compare actual donor call dispatch and
        # 16-bit admission, independently of host tile interpretation.
        a,z = [],[]
        plain_call(old,0xdd24,lambda c:a.append(c.y) if c.pc==0xe42b else None)
        plain_call(new,labels['GiantSweep'],lambda c:z.append(c.y) if c.pc==labels['GiantSweepProbe'] else None)
        assert a == z, (duck,speed,y,page,x,a,z)
        poses += 1
        visited += len(a)
        signatures.add(tuple(a))
    return dict(poses=poses,actual_donor_probe_calls=visited,distinct_probe_sequences=len(signatures))


def tag(m, pc):
    return m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else None


def vector(c, kind):
    m=c.memory
    entry=(c.pc,c.sp,c.a,c.x,c.y,c.p&0xef,tuple(m.rawtags),bytes(m[0x15a:0x17b]))
    if kind=='irq':
        m[0x5204]=0x80
        c.irq()
        assert c.sp == entry[1]-3, (hex(entry[0]),hex(entry[5]))
    else:
        assert M.get(m,'NmiDisable')==255
        c.nmi()
    handler=c.pc
    for _ in range(100000):
        if (c.pc,c.sp)==entry[:2]:
            break
        assert m[c.pc], ('vector BRK',kind,hex(c.pc))
        c.step()
    else:
        raise AssertionError(('vector return bound',kind,hex(c.pc)))
    assert (c.pc,c.sp,c.a,c.x,c.y,c.p&0xef,tuple(m.rawtags),bytes(m[0x15a:0x17b]))==entry,(kind,hex(entry[0]))
    return dict(kind=kind,pc=entry[0],handler=handler,SP=entry[1])


def play(m, labels, keys=0, cut=None):
    M.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,NmiDisable=255)
    c=M.NesMPU(memory=m,pc=address(m.bundle,'GameLoop'))
    c.sp,c.p=252,0x31
    c.stPushWord(STOP-1)
    seen=dict(mario_gate=0,giant_gate=0,native_bg=0,effects=0)
    cuts=[]
    low=c.sp
    box=None
    for _ in range(100000):
        pc=c.pc
        if pc==STOP:
            break
        bank=tag(m,pc)
        if (bank,pc)==(BANK|128,ENTRY):
            seen['mario_gate']+=1
        if pc==labels['GiantMarioRoute']:
            seen['giant_gate']+=1
        if (bank,pc)==(254,address(m.bundle,'PlayerBGCollision')):
            seen['native_bg']+=1
            box=list(m[0x658:0x65c])
        if (bank,pc)==(EFFECT_BANK,EFFECT_PC):
            seen['effects']+=1
        if cut and not cuts and pc==cut[1] and (cut[2] is None or bank==cut[2]):
            cuts.append(vector(c,cut[0]))
        low=min(low,c.sp)
        assert m[pc], ('GameLoop BRK',hex(pc),m.rawtags)
        c.step()
    else:
        raise AssertionError(('GameLoop return bound',hex(c.pc)))
    assert c.sp==252
    return dict(**seen,box=box,cuts=cuts,SP_minimum=low,cycles=c.processorCycles,
                AXYP=[c.a,c.x,c.y,c.p&0xef])


def bind(seed, b, code):
    m=M.fork(seed)
    m.bundle=b
    m[BASE:BASE+len(code)]=code
    return m


def enter_owner(b, slot, cycle):
    m=M.fresh(b)
    M.put(m,CrossoverMenuIndex=slot)
    for name in ('MenuResolveCharacter','QueueSelection','DrawSelectionPreview'):
        M.invoke(m,name)
    for i in range(cycle+1):
        key=16 if i==cycle else 32
        M.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
        start=M.invoke(m,'CrossoverMenuInput',p=0x30)
    assert M.get(m,'CrossoverMenuState')==0,(slot,cycle)
    M.invoke(m,'ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    M.invoke(m,'PauseRoutine',a=0)
    for _ in range(600):
        if (M.get(m,'OperMode_Task'),M.get(m,'GameEngineSubroutine'))==(3,8):
            return m
        M.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,NmiDisable=255)
        M.invoke(m,'GameLoop',x=0,y=0)
        M.consume(m)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
    raise AssertionError(('Native menu entrance',slot,cycle))


def foreign(cold, b, candidate, code, labels):
    rows=[]
    seeds=[(enter_owner(b,slot,cycle),slot,cycle,8,0,0,False)
           for slot,cycle in [(0,i) for i in range(9)]+[(2,1)]]
    seeds += [(cold,0,None,engine,disabled,water,True)
              for engine,disabled,water in ((7,0,0),(8,1,0),(8,0,1))]
    for seed,slot,cycle,engine,disabled,water,inactive in seeds:
        a,z=bind(seed,b,code),bind(seed,candidate,code)
        if inactive:
            for m in (a,z):
                M.put(m,MarioVariant=9,GameEngineSubroutine=engine,DisableCollisionDet=disabled,SwimmingFlag=water)
        raw,variant=M.get(a,'SelectedCharacter'),M.get(a,'MarioVariant')
        try:
            q,r=play(a,labels),play(z,labels)
        except AssertionError as e:
            raise AssertionError((slot,cycle,raw,variant,engine,e.args)) from e
        assert (q['AXYP'],q['box'],q['effects'])==(r['AXYP'],r['box'],r['effects']),(raw,variant,engine,q,r)
        compare_memory(a,z)
        rows.append(dict(slot=slot,menu_select_presses=cycle,raw=raw,variant=variant,engine=engine,disabled=disabled,swimming=water,
                         legacy_gate=q['mario_gate'],patch_extra_cycles=r['cycles']-q['cycles']))
    assert any(q['raw']==41 and q['variant']==8 for q in rows)
    # Quick's independent overlay does not finish this CPU model's first
    # foreground update. Preserve that exact incumbent failure separately.
    quick=enter_owner(b,9,2)
    rejected=[]
    for image in (b,candidate):
        try:
            play(bind(quick,image,code),labels)
        except AssertionError as e:
            rejected.append(e.args[0])
    assert rejected==[('GameLoop BRK','0x24ff',[254,1,2,255])]*2,rejected
    return rows,dict(Quick_Man_raw=9,incumbent_and_fixture_early_CPU_failure=rejected)


def check_box(m, donor, box):
    donor[0x3ad]=M.get(m,'Player_Rel_XPos')
    donor[0x3b8]=M.get(m,'Player_Rel_YPos')
    donor[0x3d0]=M.get(m,'Player_OffscreenBits')
    donor[0x499]=1+bool(M.get(m,'CrouchingFlag'))
    for pc in (0xe29c,0xeb5f):
        plain_call(donor,pc,lambda c:None)
    assert bytes(box)==bytes(donor[0x4ac:0x4b0]),(box,list(donor[0x4ac:0x4b0]))


def seeded(after, labels, donor):
    result=[]
    targets=[cell(x,y) for x,y in ((448,176),(448,192))]
    effect_pc=address(after.bundle,'PlayerHeadCollision')
    cuts=[None]+[(kind,pc,bank) for kind,(pc,bank) in product(('irq','lag_nmi'),(
        (labels['GiantMarioRoute'],None),(labels['GiantSweepProbe'],None),
        (labels['GiantSweepEffect'],None),(effect_pc,254)))]
    for cut in cuts:
        m=M.fork(after)
        M.put(m,SelectedCharacter=0,MarioVariant=9)
        place(m,417,1)
        before=[m[i] for i in targets]
        q=play(m,labels,cut=cut)
        assert before==[0x12,0x14],before
        assert q['effects']==2 and q['native_bg']==q['giant_gate']==1,q
        assert bool(q['cuts'])==bool(cut),(cut,q)
        assert [m[i] for i in targets]==[0x23,0x23]
        assert (world_x(m),M.get(m,'Player_Y_Position'))==(417,176)
        check_box(m,donor,q['box'])
        M.consume(m)
        result.append(q)
    return result


def route(m, labels, jump_at=264, jump_hold=35):
    # Keep the private alternate selected for the entire live controller
    # trajectory. A single ordinary early jump avoids the first Goomba.
    M.put(m,MarioVariant=9)
    cells=[cell(x,y) for x,y in ((448,176),(448,192),(464,176),(464,192))]
    route_lives=M.get(m,'NumberofLives')
    first=None
    effects=boxes=0
    holding=0
    jumped=False
    grounded_before_pipe=None
    low=255
    pipe_changes=[]
    last=None
    for age in range(290):
        x=world_x(m)
        if not jumped and x>=jump_at:
            holding=jump_hold
            jumped=True
        if first is None and x>=400 and [m[i] for i in cells]==[0x12,0x14,0x13,0x15]:
            first=dict(update=age,x=x,tiles=[m[i] for i in cells])
        keys=65+(128 if holding else 0)
        if x>=402 and grounded_before_pipe is None:
            if M.get(m,'Player_Y_Position')==176 and M.get(m,'Player_State')==0:
                grounded_before_pipe=dict(update=age,x=x)
            else:
                keys=2 if 0<M.get(m,'Player_X_Speed')<128 else 0
        q=play(m,labels,keys)
        effects+=q['effects']
        boxes+=q['native_bg'] if q['giant_gate'] else 0
        low=min(low,q['SP_minimum'])
        holding=max(0,holding-1)
        M.consume(m)
        if x>=385:
            state=[m[i] for i in cells]
            if state!=last or q['effects'] or age%10==0:
                pipe_changes.append(dict(age=age,x=world_x(m),y=M.get(m,'Player_Y_Position'),
                                         tiles=state,effects=q['effects']))
            last=state
        assert M.get(m,'MarioVariant')==9
        assert M.get(m,'NumberofLives')==route_lives,(age,x)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        if world_x(m)>=481 and M.get(m,'Player_Y_Position')==176:
            break
    endpoint=dict(update=age+1,world_X=world_x(m),native_Y=M.get(m,'Player_Y_Position'),
                  lives_counter=M.get(m,'NumberofLives'),engine=M.get(m,'GameEngineSubroutine'),
                  native_BG_with_Giant=boxes,native_effect_calls=effects,first_pipe=first,
                  final_cells=[m[i] for i in cells],SP_minimum=low,pipe_changes=pipe_changes,
                  grounded_before_pipe=grounded_before_pipe)
    assert first and endpoint['world_X']>=481 and endpoint['native_Y']==176 and endpoint['engine']==8,endpoint
    assert grounded_before_pipe and grounded_before_pipe['x']<448,endpoint
    assert all(any(row['tiles'][i]==0x23 for row in pipe_changes) for i in range(4)),endpoint
    assert any(row['x']<448 and row['y']==176 and not any(row['tiles']) for row in pipe_changes),endpoint
    assert effects>=4 and not any(endpoint['final_cells']),endpoint
    return endpoint


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(HOST)==PIN and sha(DONOR)==DONOR_PIN
    args.output.mkdir(exist_ok=True)
    raw,donor_raw=HOST.read_bytes(),DONOR.read_bytes()
    b=bundle(raw)
    code,labels=assemble(args.output,b)
    at=16+8192*BANK+(ENTRY&8191)
    assert raw[at:at+7].hex()=='ad0a73c902f0db'
    patch=bytes.fromhex('4c805beaea')
    patched=raw[:at]+patch+raw[at+len(patch):]
    candidate=bundle(patched)
    groups=donor_groups(raw,donor_raw,code,labels)
    print('Donor groups',groups,flush=True)
    cold,_=start_stage(b)
    after=bind(cold,candidate,code)
    preserved,negative=foreign(cold,b,candidate,code,labels)
    print('Foreign full GameLoop',len(preserved),flush=True)
    traversed=route(M.fork(after),labels)
    print('Controller trajectory',traversed,flush=True)
    # Reuse the real parser snapshot around the first pipe for reproducible
    # interrupted cuts, without touching a natural route's gameplay state.
    from check_mega_giant_pipe_ingress_1110_v1 import reach_pipe
    pipe,_=reach_pipe(b)
    donor=bytearray(65536)
    donor[0x8000:]=donor_raw[16:32784]
    interrupted=seeded(bind(pipe,candidate,code),labels,donor)
    out=dict(passed=True,ROM_written=False,source_CPU_only=True,menu_admitted=False,resident_executable=False,
             parent_SHA256=PIN,donor_SHA256=DONOR_PIN,code_bytes=len(code),
             code_SHA256=hashlib.sha256(code).hexdigest(),symbols=labels,
             exact_host_ingress=dict(physical_PRG=BANK,PC=ENTRY,file_offset=at,
                old_hex=raw[at:at+5].hex(),fixture_hex=patch.hex(),private_CPU_fixture=BASE),
             donor_groups=groups,foreign=preserved,retained_negative=negative,controller_trajectory=traversed,
             interrupt_cut_results=interrupted,
             limits=['No executable placement or persistent cold owner allocation',
                     'Cold title selects stock Mario. Variant 9 is seeded once after the live stage starts',
                     'Source side/upper foreground crush uses the existing host block-effects adaptation',
                     'Compared donor standing/crouching probe schedules with prior source climbing state excluded',
                     'Native floor/head responses, movement, render, enemy combat, end-level and palette are still host behavior'],
             bindings={str(p):sha(p) for p in (Path(__file__),ROUTE,CRUSH,SOURCE,HOST,DONOR,
                R/'tools/audit/check_mega_giant_pipe_ingress_1110_v1.py',
                R/'tools/audit/check_mega_giant_ppu_mapping_1110_v1.py',
                R/'tools/audit/check_mega_giant_geometry_1110_v1.py',
                R/'tools/audit/check_hogan_current_bounded_v1.py',
                R/'tools/audit/prepare_mini_side_alias_1108.py')})
    (args.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,code_bytes=len(code),interrupt_cases=len(interrupted)-1,
                          controller_trajectory=traversed),sort_keys=True))


if __name__=='__main__':
    main()
