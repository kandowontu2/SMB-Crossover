"""Strict actual79fd facade; cb95 metadata only, all CPU fetches own79fd."""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
from unittest.mock import patch
import compose_rogue_hud_scene_dirty_cb95_1116 as C
import current_rogue_missile_cb95_1116 as Previous

R,ROM,H,N,W,Frames=Previous.R,Previous.ROM,Previous.H,Previous.N,Previous.W,Previous.Frames
PIN=C.CANDIDATE
C_SHA='d7b924cbba68c99a2c3db6ec23e2b41e47b8ceb9e74476af3bcccc2bda52aa45'
PREVIOUS_SHA='aba571d7bc7740fb84af705c6e06371b0d09e03d4406e321c485c9716736ee38'


@lru_cache(maxsize=1)
def reference(raw):
    assert H(Path(C.__file__).read_bytes())==C_SHA
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    return C.inverse(raw)


@lru_cache(maxsize=1)
def bindings(raw):
    ref=reference(raw);old=Previous.bindings(ref)
    q=dict(old,bundle=dict(old['bundle'],raw=raw),hooks=deepcopy(old['hooks']))
    assert q['bundle']['raw']is raw
    own=set(range(C.AT,C.AT+14))
    for row in q['hooks'].values():
        if 'file'not in row:continue
        at=row['file'];assert not own.intersection(range(at,at+16))
        assert raw[at:at+16]==ref[at:at+16]
        bank=(at-16)//8192
        if 'bank_SHA256'in row:row['bank_SHA256']=H(raw[16+bank*8192:16+(bank+1)*8192])
    q.update(owning_SHA256=PIN,metadata_reference_SHA256=Previous.PIN,
        owning_grant_SHA256=C.GRANT_SHA,protected_Mini20_Sonic94_Rogue2=True)
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
    raise AssertionError('Owning79fd actual compiled Rogue cold bound')


def load_current_image():
    actual=ROM.read_bytes();pin=H(actual)
    if pin==PIN:reference(actual);return actual
    assert pin==C.PARENT,('Strict exactcb95/79fd reader only',pin)
    return C.proposal(actual)[0]
