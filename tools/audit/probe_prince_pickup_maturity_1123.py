"""Exact6201 actual C7B3/AF71 pickup maturity components, stdout only.

Explicit actor/health/status inputs are declared CPU fixtures. No natural
pickup, full CD765 image, emulator or installation qualification is claimed.
"""
import json
from pathlib import Path
from unittest.mock import patch

import probe_prince_wram1_funding_1123 as B

F,H,W,N=B.F,B.H,B.W,B.N
OLD=bytes.fromhex('adcfc6f031b5344ad032b51f1028b00c')
NEW=bytes.fromhex('adcfc6f031b51f102db5344ad02eb00c')
SLOT=5


def setup(seed,kind,state,hp,tier,patched=False):
    m=N.fork(seed)
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,PlayerStatus=tier,ObjectOffset=SLOT)
    for name,value in (('Enemy_Flag',1),('Enemy_ID',46),('Enemy_State',state),
                       ('PowerUpType',kind),('Enemy_Y_HighPos',1),('Enemy_Y_Position',128),
                       ('Enemy_PageLoc',4),('Enemy_X_Position',0)):
        m[W.address(m.bundle,name)+SLOT]=value
    m.ram[2][0x6cf]=hp
    if patched:
        assert bytes(m.ram[2][0x7b3:0x7b3+len(OLD)])==OLD
        m.ram[2][0x7b3:0x7b3+len(NEW)]=NEW
    safecall=W.address(m.bundle,'SafecallA_SMC')+1
    target=W.address(m.bundle,'FarcallJmpTarget_SMC')+1
    m[safecall]=83;m[target:target+2]=(0xc7b3).to_bytes(2,'little')
    return m


def gameplay(m):
    read=lambda n,i=0:m[W.address(m.bundle,n)+i]
    return dict(flag=read('Enemy_Flag',SLOT),state=read('Enemy_State',SLOT),kind=read('PowerUpType',SLOT),
        HP=m.ram[2][0x6cf],sword=m.ram[2][0x6ee],tier=read('PlayerStatus'),
        lives=read('NumberofLives'),star=read('StarInvincibleTimer'),
        popup=read('FloateyNum_Control',SLOT),popup_timer=read('FloateyNum_Timer',SLOT),
        music=read('AreaMusicQueue'),cue=read('Square2SoundQueue'),
        score=bytes(m[W.address(m.bundle,'Player1ScoreDisplay'):W.address(m.bundle,'Player1ScoreDisplay')+6]).hex())


def snapshot(m):
    return bytes(m[:0x800]),tuple(bytes(x)for x in m.ram)


def invoke(m,p):
    c=N.NesMPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'))
    c.a,c.x,c.y,c.p,c.sp=3,SLOT,0,p,224;c.stPushWord(0x5aff)
    entries=[];erases=0;minimum=224
    for _ in range(100000):
        if c.pc==0x5b00:break
        minimum=min(minimum,c.sp)
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else None
        if c.pc==0xaf71 and tag==131:
            entries.append(dict(PC=hex(c.pc),bank=tag,A=c.a,P=c.p,state=m[0x1f+SLOT],kind=m[0x34+SLOT]))
        if c.pc==0x8d2f and tag==254:erases+=1
        assert m[c.pc],('Actual pickup BRK',hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError('Actual C7B3 dispatch instruction bound')
    assert c.sp==224 and c.p&1
    assert m.rawtags[1:3]==[3,2]
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],carry=bool(c.p&1),CPU=c.processorCycles,
                AF71=entries,EraseEnemyObject_calls=erases,minimum_SP=minimum)


def unchanged(before,m):
    native,private=before
    # Only owned dead stack and the existing FarCall SMC return-A operand
    # can change on a handled reject. Audio queues0100..0104 stay checked.
    ignored=set(range(0x17b,0x1e1))|{0x162,0x179}
    assert all(a==b or i in ignored for i,(a,b)in enumerate(zip(native,m[:0x800])))
    assert tuple(bytes(x)for x in m.ram)==private


def parity(a,b,qa,qb):
    assert qa['regs']==qb['regs']
    ignored=set(range(0x17b,0x1e1))
    diff=[(hex(i),x,y)for i,(x,y)in enumerate(zip(a[:0x800],b[:0x800]))if x!=y]
    assert all(int(i,16)in ignored for i,_,_ in diff),diff[:16]
    for bank in range(len(a.ram)):
        skip=set(range(0x7b3,0x7b3+len(OLD)))if bank==2 else set()
        assert all(x==y or i in skip for i,(x,y)in enumerate(zip(a.ram[bank],b.ram[bank]))),bank
    assert gameplay(a)==gameplay(b)
    return len(diff)


def main():
    raw=F.Q.P.G.ROM.read_bytes();proof=B.binding(raw)
    assert H(raw)==B.PIN
    b=dict(W.Symbols.bundle(),raw=raw)
    native=raw[16+3*8192+0xf71:16+3*8192+0xf71+34]
    assert native.hex()=='202f8da90620b598a9208d0401b534c902900fc903f065a9238d9c07a9408d010160'
    def auth(image):assert image==raw;return proof
    def deny(*a,**k):raise AssertionError('Pickup maturity probe attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        seed=F.Q.P.clone(F.Q.P.cold,dict(authenticate=auth))(raw)
        for _ in range(12):seed.controller_pad=0;F.Q.Engine.Frames.frame(seed,cold=True)
        assert bytes(seed.ram[2][0x7b3:0x7b3+len(OLD)])==OLD
        immature=[];rows=[]
        for kind in (2,3):
            for state in (0,1,16,127):
                for flags in (0x20,0x21):
                    a=setup(seed,kind,state,4,1);b=setup(seed,kind,state,4,1,True)
                    before=gameplay(b);snap=snapshot(b)
                    qa=invoke(a,flags);qb=invoke(b,flags)
                    assert qa['AF71'] and qa['EraseEnemyObject_calls']==1 and gameplay(a)['flag']==0
                    assert not qb['AF71'] and not qb['EraseEnemyObject_calls'] and gameplay(b)==before
                    unchanged(snap,b)
                    immature.append(dict(kind=kind,state=state,input_P=flags,before=before,
                        original=dict(call=qa,after=gameplay(a)),guarded=dict(call=qb,after=gameplay(b))))
        maturity_parity=0;dead_stack_differences=0
        for kind in range(4):
            for hp in range(6):
                for tier in range(3):
                    for state in (128,129,255):
                        for flags in (0x20,0x21):
                            a=setup(seed,kind,state,hp,tier);b=setup(seed,kind,state,hp,tier,True)
                            qa=invoke(a,flags);qb=invoke(b,flags)
                            dead_stack_differences+=parity(a,b,qa,qb)
                            assert gameplay(b)['flag']==int(hp==0)
                            maturity_parity+=1
        # The actual one-up award is delayed by the existing popup core.
        delayed=[]
        for patched in (False,True):
            m=setup(seed,3,1,4,1,patched);before=gameplay(m);invoke(m,0x20)
            for _ in range(6):N.invoke(m,'FloateyNumbersCore',x=SLOT,y=0,p=0x21)
            after=gameplay(m)
            assert after['lives']==before['lives']+int(not patched)
            delayed.append(dict(patched=patched,before=before,after=after))
    report=dict(passed=True,ROM=H(raw),original_pickup=OLD.hex(),candidate_pickup=NEW.hex(),
        actual_AF71_bytes=native.hex(),immature_cases=len(immature),
        immature_examples=[r for r in immature if r['state']==1 and r['input_P']==32],
        mature_all_kinds_parity=maturity_parity,dead_stack_byte_differences=dead_stack_differences,
        immature_oneup_delayed_effect=delayed,all_rejects_SEC=True,
        reject_SEC_does_not_mean_collection=True,declared_actor_component_inputs=True,
        CD765_full_image_or_natural_or_native_claim=False,outputs=0)
    digest=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_PICKUP_MATURITY '+json.dumps(dict(report,SHA256=digest),separators=(',',':')),flush=True)


if __name__=='__main__':main()
