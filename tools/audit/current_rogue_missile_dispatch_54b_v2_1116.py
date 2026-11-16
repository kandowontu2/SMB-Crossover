"""Strict owning54b facade and explicitly typed1327/a2 reference reader."""
from functools import lru_cache
from pathlib import Path
from copy import deepcopy
import compose_rogue_missile_dispatch_1327_1116 as C
import current_rogue_missile_hurt_clear_1327_1116 as Previous
import replay_rogue_natural_mf_1327_1116 as Frozen

R,ROM,N,W,Frames,H=Previous.R,Previous.ROM,Previous.N,Previous.W,Previous.Frames,Previous.H
PIN=C.CANDIDATE
C_SHA='3b4b914ff59acb3f7779cd1f8237289664ce13e83578245f9db8b0fb1fb84a14'
PREVIOUS_SHA='8e8e52cdb0c6542334c7fd79786aa5a645bec2faf0e29e3c190ecee43d030244'
FROZEN_SHA='1e91a4a715c7aaad49323ceb78a6572c63267debf363d2188f0569cff1853d22'
INPUT={}


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(Path(C.__file__).read_bytes())==C_SHA
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA and H(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    parent=C.inverse(raw);old=Previous.bindings(parent);q=dict(old,bundle=dict(old['bundle'],raw=raw))
    assert q['bundle']['raw']is raw
    assert raw[:C.AT]==parent[:C.AT]and raw[C.AT+2:]==parent[C.AT+2:]
    q['owning_SHA256']=PIN;q['metadata_reference_SHA256']=C.PIN
    q['hooks']=deepcopy(old['hooks'])
    for name,row in q['hooks'].items():
        if 'file'not in row:continue
        at=row['file'];assert raw[at:at+16]==parent[at:at+16]
    return q


def policy_text(raw):return Previous.policy_text(C.inverse(raw))


@lru_cache(maxsize=1)
def mf_controller(raw):
    bindings(raw);parent=C.inverse(raw);old=Frozen.controller(parent)
    assert old.count(C.PIN)==1
    text=old.replace(C.PIN,PIN)
    assert text.replace(PIN,C.PIN)==old
    Frozen.LuaRuntime().compile(text);return text


def mf_metadata(raw):
    text=mf_controller(raw)
    return dict(owning_SHA256=PIN,parent_SHA256=C.PIN,C_SHA256=C_SHA,
        facade_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(text.encode()),
        parent_controller_SHA256=H(Frozen.controller(C.inverse(raw)).encode()),controls_restoration_exact=True,
        outputs=0,native=False)


def cold(raw):
    q=bindings(raw);b=q['bundle']
    from unittest.mock import patch
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in(1,1,32):W.UI.key(m,bits)
    assert W.UI.menu_name(m)[0]=='ROGUE DAWN'
    assert tuple(N.get(m,n)for n in('CrossoverMenuIndex','SelectedCharacter','RdVariant'))==(2,2,1)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert m.bundle['raw']is raw and N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual54b compiled Rogue cold bound')


def load_parent():
    actual=ROM.read_bytes();pin=H(actual)
    if pin==C.PIN:parent=actual;kind='exact1327'
    elif pin=='a2d9d1218504dedf186cfe352ee4c927160529af4f8d09fe6e2aafccfae477c7':
        import compose_sonic_ceiling_complete_1327_1116 as Sonic
        assert H(Path(Sonic.__file__).read_bytes())=='c4456eb759fd35f48022fee64a24b05e37b4968a1ddaf139dceebad154187413'
        parent=Sonic.inverse(actual);kind='typed a2 inverse to historical1327 reference'
    else:raise AssertionError(('Unsupported installed input; old APIs remain strict',pin))
    assert H(parent)==C.PIN
    INPUT.update(actual_input_SHA256=pin,reference_SHA256=C.PIN,normalization=kind,
        execution_SHA256=PIN,combined_latest_image_qualified=False)
    return parent


def load_current_image():return C.proposal(load_parent())[0]
