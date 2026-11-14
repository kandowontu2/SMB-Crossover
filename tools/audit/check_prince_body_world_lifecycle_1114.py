"""Compiled foreign cold parity, complete headers and public retirement seam.

Header corruptions are explicitly diagnostic units after genuine Prince
cold; they are not gameplay fixtures or character ability qualifications.
"""
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_body_world_1114 as Game

C,P,N=Game.C,Game.P,Game.N


def identity_cold(raw,cycles):
    assert C.digest(raw)in set(C.PARENTS.values())|set(C.CANDIDATES)
    bundle=dict(P.W.Symbols.bundle(),raw=raw);old=N.Bus;N.Bus=P.W.ControllerBus
    try:m=P.W.UI.seed(bundle,29)
    finally:N.Bus=old
    for _ in range(cycles):P.W.UI.key(m,32)
    owner=N.get(m,'SelectedCharacter');start=P.W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0);idle=P.W.address(bundle,'IdleLoop')
    for epoch in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;P.W.clear_logs(m);N.consume(m)
        cpu=N.NesMPU(memory=m,pc=idle);cpu.sp,cpu.p=255,0x31;cpu.stPushWord(0xe33b)
        for _ in range(4_000_000):
            if(cpu.pc,cpu.sp)==(idle+12,252):break
            assert m[cpu.pc],('Foreign cold BRK',owner,hex(cpu.pc));cpu.step()
        else:raise AssertionError('Foreign cold frame bound')
        assert not m.blocked
    else:raise AssertionError('Foreign cold stage bound')
    assert owner==N.get(m,'SelectedCharacter')and owner!=38
    return m,dict(owner=owner,compiled_select_cycles=cycles,parser_updates=epoch,
        x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),lives=N.get(m,'NumberofLives'))


def entries(raw):
    code=raw[16+65*8192:16+66*8192]
    check=[i for i in range(len(code)-19)if code[i:i+8]==bytes.fromhex('ad026038e925c907')and code[i+10:i+17]==bytes.fromhex('aaa50848a50948')]
    retire=[i for i in range(len(code)-11)if code[i:i+11]==bytes.fromhex('08488a489848a90148a2f8')]
    assert len(check)==len(retire)==1,(check,retire)
    return 0xa000+check[0],0xa000+retire[0]


def invoke(m,pc):
    m.raw_page(1,193);N.put(m,CurrentBank=193)
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,71,109,0x61,224;c.stPushWord(0x5ffe)
    for _ in range(300000):
        if(c.pc,c.sp)==(0x5fff,224):return[c.a,c.x,c.y,c.p,c.sp]
        assert m[c.pc],('Lifecycle primitive BRK',hex(c.pc));c.step()
    raise AssertionError(('Lifecycle return bound',hex(pc)))


def view(m):
    return tuple(map(bytes,m.ram)),bytes(m[3:11]),bytes(m[0x15a:0x17b]),tuple(m.rawtags),bytes(m[0x200:0x800])


def run(parent):
    raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    foreign=[]
    for cycles in(0,2):
        before,a=identity_cold(parent,cycles);after,b=identity_cold(raw,cycles)
        assert a==b and view(before)==view(after)and before.chr_latches==after.chr_latches
        foreign.append(dict(a,all_private_scratch_SMC_mapper_native_fields_and_CHR_exact=True))
    model,opening=Game.cold(raw);check,retire=entries(raw)
    m=N.fork(model);m.raw_page(1,193);N.put(m,CurrentBank=193)
    before=view(m);regs=invoke(m,check)
    assert regs[3]&1 and before==view(m)
    negatives=0
    for bank in(2,3):
     for byte in range(16):
        m=N.fork(model);m.raw_page(1,193);N.put(m,CurrentBank=193)
        m.ram[bank][0x1fe0+byte]^=1;before=view(m);regs=invoke(m,check)
        assert not regs[3]&1 and before==view(m),(bank,byte,regs)
        negatives+=1
    m=N.fork(model);regs=invoke(m,retire)
    assert regs[:3]==[83,71,109]and regs[3]&0xef==0x61 and regs[4]==224
    assert m.ram[2][0xab]==0 and m.ram[2][0xaa]==0
    assert all(m.ram[k][0x1fe0]==0 for k in(2,3))
    after=view(m);again=invoke(m,retire);assert after==view(m)and again==regs
    q=dict(passed=True,composition=composition,opening=opening,foreign_compiled_colds=foreign,
        valid_complete_header_admitted=True,corrupt_full_header_units_rejected=negatives,
        header_check_PC=hex(check),public_retire_PC=hex(retire),retirement_registers=regs,
        genuine_Prince_ready_and_epoch_cleared=True,both_headers_invalidated=True,repeat_retire_idempotent=True,
        diagnostic_header_units_not_gameplay=True,
        frontend_scope='Compiled menu arena and actual cold; no physical vblank/interactive menu claim',
        outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    import sys
    if '--inspect'in sys.argv:
        from py65.devices.mpu6502 import MPU
        from py65.disassembler import Disassembler
        raw=Game.Factory.ROM.read_bytes();assert C.digest(raw)in C.PARENTS.values()
        code=raw[16+65*8192:16+66*8192];m=[0]*65536;m[0xa000:0xc000]=code;d=Disassembler(MPU(memory=m));out=[]
        for start in(0xaee2,0xb08c):
            pc=start;rows=[]
            for _ in range(44):
                size,text=d.instruction_at(pc);rows.append([hex(pc),text]);pc+=size
                if text=='RTS':break
            out.append(rows)
        print(json.dumps(out),flush=True)
    else:print(json.dumps(run(Game.Factory.ROM.read_bytes()),separators=(',',':')),flush=True)
