"""Strict owningcb95; frozen54b projection is metadata/config only."""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
from unittest.mock import patch
import compose_rogue_missile_9826_1116 as C
import current_rogue_missile_dispatch_54b_v2_1116 as Previous

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
PIN=C.CANDIDATE
C_SHA='f38d2e2859631b1156ad5805d29a481a89f6e68e77b17a4f509de8af7d19d3a1'
PREVIOUS_SHA='14bf500c56dbcba5ebeae30f5f89888273000e1839820ad81578c23e11164410'
INPUT={}


@lru_cache(maxsize=1)
def reference(raw):
    assert H(Path(C.__file__).read_bytes())==C_SHA and H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    parent=C.inverse(raw);base=C.Plan.Sonic.inverse(C.Plan.Mini.inverse(parent))
    ref=C.Plan.Rogue.proposal(base)[0];assert H(ref)==Previous.PIN
    return ref


@lru_cache(maxsize=1)
def bindings(raw):
    ref=reference(raw);old=Previous.bindings(ref);q=dict(old,bundle=dict(old['bundle'],raw=raw),hooks=deepcopy(old['hooks']))
    assert q['bundle']['raw']is raw
    for row in q['hooks'].values():
        if 'file'not in row:continue
        at=row['file'];assert raw[at:at+16]==ref[at:at+16]
        bank=(at-16)//8192
        if 'bank_SHA256'in row:row['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
    q.update(owning_SHA256=PIN,metadata_reference_SHA256=Previous.PIN,
        protected_Mini20_Sonic94=True,owning_grant_SHA256=C.GRANT_SHA)
    return q


def cold(raw):
    b=bindings(raw)['bundle']
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in(1,1,32):W.UI.key(m,bits)
    assert(W.UI.menu_name(m)[0],N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),N.get(m,'RdVariant'))==('ROGUE DAWN',2,2,1)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert m.bundle['raw']is raw and N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Owningcb95 actual compiled Rogue cold bound')


def load_parent():
    actual=ROM.read_bytes();pin=H(actual);mini=C.Plan.Mini
    if pin==mini.PARENT:parent=mini.proposal(actual)[0];kind='leasedMini proposal on exacta2 in RAM'
    else:assert pin==C.PARENT,'Exact installeda2/9826 reader only';mini.inverse(actual);parent=actual;kind='exact9826'
    INPUT.update(actual_input_SHA256=pin,parent9826_SHA256=C.PARENT,owning_execution_SHA256=PIN,normalization=kind)
    return parent


def load_current_image():return C.proposal(load_parent())[0]
