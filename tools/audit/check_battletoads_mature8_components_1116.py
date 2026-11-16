"""Actual91dc strict/header/public maturity primitive scopes, zero outputs."""
from pathlib import Path
from unittest.mock import patch
from itertools import product
import argparse,json
import current_battletoads_mature8_1116 as Current

C,W,N=Current.C,Current.W,Current.N

def strict(parent,image):
    reads=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Portable boundary reread mutable Nightly'
        return reads(path)
    rejects=[]
    with patch.object(Path,'read_bytes',read):
        assert C.inverse(image)==parent and C.proposal(parent)[0]==image
        for label,bad,fn in(('parent_inverse',parent,C.inverse),('candidate_forward',image,C.proposal),('truncated',image[:-1],C.inverse),('unknown',bytes(len(image)),C.inverse)):
            try:fn(bad)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Wrong image accepted',label))
        for label,at in(('unowned',90000),('entry',1989717),('stub',1995283),('cookie',765863),('Bowser',1998147),('Hot118',545972),('carry',244078),('camera',1995254)):
            for generation,raw,fn in(('forward',parent,C.proposal),('inverse',image,C.inverse)):
                bad=bytearray(raw);bad[at]^=1
                try:fn(bytes(bad))
                except AssertionError:rejects.append(generation+'_'+label)
                else:raise AssertionError(('Dirty image accepted',label,generation))
    return dict(passed=True,portable_inverse_exact6a3=True,strict_rejections=rejects,mutable_reads_after_initial=0,
        composition=C.proposal(parent)[1],primitive_only=True)

def public(m,slot=23,a=0,x=5,y=0,p=0x32):
    m[0x16a]=a;m[0x16c]=(0xb020+3*slot)&255;m[0x16d]=(0xb020+3*slot)>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a=215;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    low=c.sp;entries=[];returns=[]
    for _ in range(20000):
        if c.pc==0x5b00:break
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if tag==3 and c.pc in(0xa045,0xb603,0xb602,0xae3e):entries.append(dict(PC=c.pc,SP=c.sp,P=c.p,A=c.a))
        low=min(low,c.sp);assert m[c.pc],('Actual public BRK',slot,c.pc,tag);c.step()
    else:raise AssertionError(('Actual public bound',slot,c.pc))
    assert c.sp==224
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,minimum_SP=low,entries=entries)

def matrix(parent,image):
    seed,opening=Current.cold(image,'rash',True);b=seed.bundle;rows=[];cases=0;minimum=255
    def test(state,changes=None,p=0x32):
        nonlocal cases,minimum
        m=N.fork(seed);values=dict(BtHostReady=1,SelectedCharacter=33,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
        values.update(changes or{})
        for n,v in values.items():
            at=W.address(b,n)
            if n.startswith('Bt'):m.ram[3][at&8191]=v
            else:m[at]=v
        m[W.address(b,'Enemy_State')+5]=state;before=bytes(m.ram[3]);above=bytes(m[0x1e1:0x200])
        out=public(m,p=p)
        expected=state>=128 and values['BtHostReady']==1 and values['SelectedCharacter']==33 and values['OperMode']==1 and values['GameEngineSubroutine']==8 and values['GamePauseStatus']&1==0 and values['TimerControl']==0
        assert bool(out['P']&1)==expected,(state,changes,out)
        assert(out['X'],out['Y'])==(5,0)and(out['P']^p)&0x4c==0
        assert bytes(m.ram[3])==before and bytes(m[0x1e1:0x200])==above,'Admission has no private or above-entry stack writes'
        cases+=1;minimum=min(minimum,out['minimum_SP'])
        if changes or state in(0,6,17,127,128,192):rows.append(dict(state=state,changes=changes,P=p,result=out))
    for state in range(256):test(state)
    for field in('BtHostReady','OperMode','GameEngineSubroutine','GamePauseStatus','TimerControl'):
        for v in(0,1,2,8,11,127,128,255):test(128,{field:v})
    for p in range(256):test(128,p=p)
    faults=[]
    for i in range(16):
        m=N.fork(seed);m.ram[3][0x1fe0+i]^=1
        result=N.invoke(m,'BtCheck',a=85,x=7,y=91,p=0xe9);assert result['P']&1==0
        out=public(m);assert out['P']&1==0 and not any(r['PC']==0xb603 for r in out['entries'])
        faults.append(dict(byte=i,check=result,public=out))
    retired=N.fork(seed);retired.ram[3][0x1fe0]=0
    assert N.invoke(retired,'BtCheck')['P']&1==0 and public(retired)['P']&1==0
    foreign=[]
    for owner in range(256):
        m=N.fork(seed);N.put(m,SelectedCharacter=owner)
        out=N.invoke(m,'BtCheck',a=85,x=7,y=91,p=0x69);assert bool(out['P']&1)==(owner==33)
        if owner!=33:
            result=public(m);assert not any(r['PC']==0xb603 for r in result['entries'])
            foreign.append(dict(owner=owner,C=result['P']&1,A=result['A'],P=result['P']))
    return dict(passed=True,actual_candidate_cold=opening,actual_public_cases=cases,minimum_SP=minimum,samples=rows,
        full16_corrupt_header_cases=faults,retired_cookie_rejected=True,all256_actual_BtCheck_owners=True,
        foreign_public_no_new_private_entry=foreign,primitive_only=True,gameplay_qualification=False)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','matrix'));a=ap.parse_args()
    parent=C.ROM.read_bytes();assert C.digest(parent)==C.PIN;image,composition=C.proposal(parent)
    def deny(*args,**kw):raise AssertionError('Candidate component attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Current.Previous.Cold.Runner.Native,'run',deny):
        q=strict(parent,image)if a.mode=='strict'else matrix(parent,image)
    q['mode']=a.mode;q['candidate_SHA256']=C.CANDIDATE;q['outputs']=0
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    if a.mode=='matrix':
        q=dict(passed=q['passed'],mode=a.mode,candidate_SHA256=C.CANDIDATE,
            actual_public_cases=q['actual_public_cases'],minimum_SP=q['minimum_SP'],
            corrupt_cookie_bytes=len(q['full16_corrupt_header_cases']),retired_cookie_rejected=q['retired_cookie_rejected'],
            actual_BtCheck_owners=256,foreign_no_new_entry_cases=len(q['foreign_public_no_new_private_entry']),
            exact_original_private_and_above_entry_stack=True,source_receipt_SHA256=q['source_receipt_SHA256'],
            primitive_only=True,outputs=0)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
