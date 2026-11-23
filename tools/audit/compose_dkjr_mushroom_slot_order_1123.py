"""Selective row0 native slot ordering, strict82e8 lineage, memory only.

The added336 helper searches4..0; the existing13 retain5..0. Constructor,
SMC save/carry and original motor addresses remain fixed. No output writer.
"""
import argparse,json
from functools import lru_cache
from pathlib import Path
from contextlib import redirect_stdout
from unittest.mock import patch
import io
from py65.devices.mpu6502 import MPU
import compose_dkjr_mushroom_scrooge_1123 as Previous

Old,Check,H=Previous.Old,Previous.Check,Previous.H
PIN=Previous.PIN
CANDIDATE='ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
PREVIOUS_SHA='a1022eeb90927bceb2525f899daec71bc25dc90a7887b5eb1422aee261cdbaa9'
LAYOUT=dict(PIPE=(0xd18b,117),REFRESH=(0xb624,129),REFRESH_TARGET=(0xb7b8,3))


@lru_cache(maxsize=1)
def program():
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    assert H(Old.Old.GIRDER.read_bytes())==Old.GIRDER_SHA
    source=Old.Old.GIRDER.read_text()
    one=Check.Replay.one
    for before,after in (
        ('ActorCount = 13','ActorCount = 14'),
        ('WorldColumns: .byte 26,','WorldColumns: .byte 21,26,'),
        ('    cpy #8\n    beq Horizontal','    cpy #9\n    beq Horizontal'),
        ('OscillatorY: .byte 128,','OscillatorY: .byte 188,128,'),
        ('    ldx #5\nFind:','    ldx #4\n    ldy PipeSeenThrough\n    beq Find\n    inx\nFind:'),
        ('DkSetPlatformTypeAndPosition:\n    ldy PipeSeenThrough\n','DkSetPlatformTypeAndPosition:\n'),
        ('    tya\n    sta EnemyY,x\n    sec\n    rts','    sty EnemyY,x\n    sec\n    lda #<InitEnemyObject\n    ldy #>InitEnemyObject\n    rts'),
        ('    lda #<InitEnemyObject\n    ldy #>InitEnemyObject\n    jsr DkNativeFarCall','    jsr DkNativeFarCall'),
        ('    sbc R0\n    bcc Reject\n','    sbc R0\n')):
        source=one(source,before,after)
    p=Old.M.assemble(source,Old.Old.GIRDER_LAYOUT)
    assert p['used']['PIPE']==117 and p['used']['REFRESH']==129
    assert p['symbols']['DkAfterNativeConstructor']==0xd1f0
    assert p['symbols']['OscillatorY']==Old.programs()[1]['symbols']['OscillatorY']
    assert p['images']['ROWS']==Old.programs()[1]['images']['ROWS']
    return p


def proposal(parent):
    assert H(parent)==PIN
    frozen,q=Previous.proposal(parent)
    before=Old.programs()[1]
    p=program();out=bytearray(frozen);owned=set()
    for name,(pc,size) in LAYOUT.items():
        a,b=before['images'][name],p['images'][name]
        assert len(a)==len(b)==size
        for (at,old),(other,new) in zip(Old.chunks(pc,a),Old.chunks(pc,b),strict=True):
            assert at==other and frozen[at:at+len(old)]==old
            out[at:at+len(new)]=new;owned.update(range(at,at+len(new)))
    cookie=b'\xa7\x28\x01'+bytes.fromhex(H(Old.Head.payload(out)))[:13]
    out[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16]=cookie
    owned.update(range(Old.Head.COOKIE_AT,Old.Head.COOKIE_AT+16))
    result=bytes(out)
    assert {i for i,(a,b) in enumerate(zip(frozen,result,strict=True)) if a!=b}<=owned
    if CANDIDATE is not None:assert H(result)==CANDIDATE
    return result,dict(parent_SHA256=PIN,previous_SHA256=Previous.CANDIDATE,candidate_SHA256=H(result),
        cookie=cookie.hex(),new_row0_scan=list(range(4,-1,-1)),other_rows_scan=list(range(5,-1,-1)),
        scope_PC=p['symbols']['DkPipeScope'],try_PC=p['symbols']['DkPipeTry'],
        constructor_return_PC=p['symbols']['DkAfterNativeConstructor'],used=p['used'],
        original_jump_head_carry_SMC_bytes_unchanged=True,new_RAM=0,new_capacity=0,outputs=0,native_qualified=False)


def inverse(raw):
    assert CANDIDATE is not None and H(raw)==CANDIDATE
    out=bytearray(raw);before=Old.programs()[1]
    for name,(pc,_) in LAYOUT.items():
        for at,data in Old.chunks(pc,before['images'][name]):out[at:at+len(data)]=data
    # Frozen656 and3b7 share their complete DK packet and cookie.
    out[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16]=bytes.fromhex('a72801557ae2839b6011fab841f8371e')
    previous=bytes(out)
    assert H(previous)==Previous.CANDIDATE
    parent=Previous.inverse(previous)
    assert proposal(parent)[0]==raw
    return previous


def controller(raw,*,cutoff=180,route=False):
    prior=inverse(raw)
    text=Previous.controller(prior,cutoff=cutoff,route=route)
    assert text.count(Previous.CANDIDATE)==1
    result=text.replace(Previous.CANDIDATE,H(raw),1)
    # The private DK cookie also changes; the first-item observer binds the
    # header from the actual ROM, while full-route observers use a literal.
    if route:
        before=prior[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16].hex()
        after=raw[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16].hex()
        assert result.count(before)==1;result=result.replace(before,after,1)
    Check.LuaRuntime().compile(result)
    return result


def full_controller(raw):
    prior=inverse(raw);text=Previous.full_controller(prior)
    original=text;changes=[]
    assert text.count(Previous.CANDIDATE)==2
    for before,after in (
        (f'local rom="{Previous.CANDIDATE}"',f'local rom="{H(raw)}"'),
        (f"assert(rom=='{Previous.CANDIDATE}'",f"assert(rom=='{H(raw)}'")):
        text=Check.Replay.one(text,before,after);changes.append((before,after))
    before=prior[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16].hex()
    after=raw[Old.Head.COOKIE_AT:Old.Head.COOKIE_AT+16].hex()
    before,after=f"cookie=='{before}'",f"cookie=='{after}'"
    text=Check.Replay.one(text,before,after);changes.append((before,after))
    restored=text
    for before,after in reversed(changes):restored=Check.Replay.one(restored,after,before)
    assert restored==original and Previous.CANDIDATE not in text and text.count(H(raw))==2
    Check.LuaRuntime().compile(text)
    return text


def fixture(p):
    mem=[0]*65536
    for name,data in p['images'].items():
        at=Old.Old.GIRDER_LAYOUT[name][0];mem[at:at+len(data)]=data
    return MPU(memory=mem)


def call(c,pc,*,x=0,y=0,carry=1,stops=()):
    c.pc,c.sp,c.a,c.x,c.y,c.p=pc,0xfd,0x5a,x,y,0x20|carry
    c.memory[0x1fe],c.memory[0x1ff]=0xff,0x7f
    start=c.processorCycles
    for _ in range(500):
        if c.pc==0x8000 or c.pc in stops:return c.processorCycles-start
        c.step()
    raise AssertionError(('Fixture instruction bound',hex(c.pc)))


def units():
    before=Old.programs()[1];after=program();a,b=fixture(before),fixture(after)
    cases,worst=0,0
    for page in range(13):
        for xpos in range(256):
            for seen in range(15):
                answers=[];cost=[]
                for c,p in ((a,before),(b,after)):
                    c.memory[0x71d],c.memory[0x71f],c.memory[0xd6],c.memory[0xc8fd]=page,xpos,0xce,seen
                    cost.append(call(c,p['symbols']['DkPipeScope']))
                    ok=c.p&1
                    answers.append((ok,c.memory[0xc8fd],(c.y,c.memory[4]) if ok else None))
                assert answers[0]==answers[1],(page,xpos,seen,answers)
                worst=max(worst,cost[1]-cost[0]);cases+=1
    allocations=0
    for row in range(14):
        for mask in range(64):
            b.memory[0xc8fd]=row
            for i in range(6):b.memory[0x10+i]=bool(mask&(1<<i))
            call(b,after['symbols']['DkPipeTry'],y=0x62,
                 stops=(after['symbols']['Birth'],after['symbols']['RefreshStart']))
            expected=next((i for i in range(4 if row==0 else 5,-1,-1) if not mask&(1<<i)),None)
            actual=b.x if b.pc==after['symbols']['Birth'] else None
            assert actual==expected,(row,mask,actual,expected)
            assert b.y==row
            allocations+=1
    for row in range(14):
        for slot in range(6):
            call(b,after['symbols']['DkSetPlatformTypeAndPosition'],x=slot,y=row)
            assert (b.a,b.y,b.p&1)==(0x4f,0xa7,1)
            assert b.memory[0x17+slot]==(40 if row==9 else 37)
            assert b.memory[0xbe+slot]==(208 if row==9 else 192)
            assert b.memory[0x76+slot]==(after['images']['ROWS'][row]*16)&255
    return dict(scope_cases=cases,scope_selection_identical=True,worst_extra_reject_cycles=worst,
        all_row_actor_masks=allocations,constructor_parameters=84,actual_incoming_Y=0x62,
        original_constructor_return_PC=0xd1f0,output_files=0)


def cadence(parent,raw):
    machines=[Check.Head.cold(image)[0] for image in (parent,raw)]
    phases={}
    for name,pad,count in (('standing',0,24),('walking',1,24)):
        rows=[[],[]];nmi=[[],[]];returns=[0,0]
        for _ in range(count):
            for i,m in enumerate(machines):
                def observe(memory,cpu):
                    if Check.Head.point(cpu)==(3,0xb8f0):returns[i]+=1
                cycles,vblank=Check.B.main_step(m,pad,Check.Trace(observe))
                rows[i].append(cycles);nmi[i].append(vblank)
            assert Check.Head.state(machines[0])==Check.Head.state(machines[1])
        assert nmi[0]==nmi[1] and returns==[count,count]
        phases[name]=dict(completed_source_returns=returns,
            parent_Main_cycles=rows[0],candidate_Main_cycles=rows[1],
            delta_cycles=[b-a for a,b in zip(*rows,strict=True)],
            NMI_cycles_identical=True,final=Check.Head.state(machines[1]))
    old,new=Old.programs()[0],program();a,b=fixture(old),fixture(new)
    intervals=[];active=None
    for camera in range(2816):
        costs=[]
        for c,p in ((a,old),(b,new)):
            c.memory[0x71d],c.memory[0x71f]=divmod(camera,256)
            c.memory[0xd6],c.memory[0xc8fd]=0xce,14
            costs.append(call(c,p['symbols']['DkPipeScope']))
        delta=costs[1]-costs[0]
        if delta>0:
            if active is None:active=dict(camera_start=camera,camera_end=camera,min_extra=delta,max_extra=delta)
            else:
                active['camera_end']=camera;active['min_extra']=min(active['min_extra'],delta);active['max_extra']=max(active['max_extra'],delta)
        elif active is not None:intervals.append(active);active=None
    if active is not None:intervals.append(active)
    return dict(passed=True,parent_SHA256=H(parent),candidate_SHA256=H(raw),phases=phases,
        same_ordinary_menu_and_opening_inputs=True,opening_state_identical=True,
        scope_only_positive_cost_intervals=intervals,scope_unit_seen=14,
        physical_cadence_claim=False,outputs=0)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('compose','units','Mushroom','baseline','cadence'),default='compose')
    args=p.parse_args()
    parent=Old.M.ROM.read_bytes();raw,q=proposal(parent);print('DK SLOT COMPOSE '+json.dumps(q,separators=(',',':')),flush=True)
    if args.mode=='compose':return
    if args.mode=='units':result=units()
    elif args.mode=='cadence':result=cadence(parent,raw)
    elif args.mode=='Mushroom':
        with patch.object(Check,'controller',controller):result,_=Check.first_mushroom(raw)
    else:
        text=full_controller(raw)
        print('DK SLOT FULL SCRIPT '+H(text.encode()),flush=True)
        m,opening=Check.Head.cold(raw)
        with patch.object(Check.Route.Frames,'frame',Check.normal_frame):
            with redirect_stdout(io.StringIO()):result=Check.Route.route(m,raw,14000,controller_text=text)
        result.update(opening_Main=opening,ROM_SHA256=H(raw))
    result['source_SHA256']=H(Path(__file__).read_bytes())
    receipt=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('DK SLOT RESULT '+json.dumps(result,separators=(',',':')),flush=True)
    print('RECEIPT '+receipt,flush=True)
    if args.mode!='units':assert result['passed']


if __name__=='__main__':main()
