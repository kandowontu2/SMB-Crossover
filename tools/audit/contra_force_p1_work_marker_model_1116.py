"""Explicit6a3/ffbb actual NesBus image; historicalbc5 is metadata only."""
from functools import lru_cache
from unittest.mock import patch
import compose_contra_force_p1_work_marker_1116 as C

P=C.Plan.Audit.P
W,N,Frames=P.W,P.N,P.Frames
IDENTITIES={'burns':('BURNS',0),'smith':('SMITH',1),'iron':('IRON',2),'beans':('BEANS',3)}


@lru_cache(maxsize=2)
def parent(raw):
    if C.H(raw)==C.PIN:C.Plan.inputs(raw);return raw
    return C.inverse(raw)


@lru_cache(maxsize=2)
def symbols(raw):
    owning=parent(raw);z,_=C.Plan.inputs(owning)
    b=dict(P.Model.symbols(z['reference']),raw=raw)
    assert b['raw']is raw
    return b


@lru_cache(maxsize=2)
def private_points(raw):
    owning=parent(raw);z,s=C.Plan.inputs(owning);labels=dict(s)
    if C.H(raw)==C.CANDIDATE:
        d=C.Plan.descriptor(owning);r,e,l=d['fragments'][0]['labels'],d['fragments'][1]['labels'],d['fragments'][2]['labels']
        for name,pc in list(labels.items()):
            key=f'Old_{pc:04X}'
            if 0xb3c4<pc<0xb5c8 and key in r:labels[name]=r[key]
        labels['CfP1Late']=l['Leaf'];labels['CfNativeP1MaskReadEnd']=e['NativeMaskReadEnd']
    return labels


def cold(raw,key='burns'):
    name,variant=IDENTITIES[key];b=symbols(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in([4]*3+[1]*6):W.UI.key(m,pad)
    for _ in range(variant):W.UI.key(m,32)
    assert(W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),(N.get(m,'FmGroups')>>3)&3)==(name,30,31,variant)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError(('Actual current CF constructor bound',key))
    empty(m,key);assert m.bundle['raw']is raw
    header=bytearray(raw[573373:573389]);header[2]=variant
    assert bytes(m.ram[2][-32:-16])==bytes(header)
    assert bytes(m.ram[3][-32:])==bytes(32)
    return m


def empty(m,key):
    variant=IDENTITIES[key][1]
    assert N.get(m,'SelectedCharacter')==31 and(N.get(m,'FmGroups')>>3)&3==variant
    assert m.ram[2][0xb1]==variant
    assert N.get(m,'NumberofLives')==2 and N.get(m,'PlayerStatus')==N.get(m,'StarInvincibleTimer')==0
    assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    assert not any(N.get(m,'Enemy_Flag',i)for i in range(6))
    assert not any(m.ram[2][0x382+i]for i in range(10,22))
