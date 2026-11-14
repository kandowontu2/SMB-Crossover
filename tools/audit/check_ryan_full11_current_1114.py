"""Current Ryan genuine compiled menu/constructor and source full-stage route."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import replay_ryan_full11_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_bub_current_budget_1113 as Frames

W,N=Factory.W,Factory.N


def cold(raw,key='ryan'):
    c=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in c['navigation']:W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='RYAN'and N.get(m,'SelectedCharacter')==21 and N.get(m,'RcVariant')==1
    s=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'RcVariant')==N.get(m,'RcSavedVariant')==1
            assert N.get(m,'RcMarker')==199 and N.get(m,'RcHealth',1)==48 and N.get(m,'RcTier',1)==0
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual Ryan constructor bound')


def run(raw,metadata=False):
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()=='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'ryan')if metadata else Runner.run(raw,'ryan',9000)


def lease(raw):
    b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in Factory.bindings(raw)['navigation'][:-1]:W.UI.key(m,pad)
    assert N.get(m,'SelectedCharacter')==21 and N.get(m,'RcVariant')==0
    # Explicit mapper-resource fixture, separate from the unseeded full route.
    N.invoke(m,'X5SetPhysicalChr',a=55,x=3,y=7)
    assert m[0x73e7]==131
    W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]=='RYAN'and N.get(m,'RcVariant')==1 and m[0x73e7]==0
    N.invoke(m,'X5PublishChr',a=0,x=0,y=0)
    assert m.chr_latches[1:4]==[16,17,18]and m.chr_latches[7]==21
    return dict(ROM_SHA256=sha256(raw).hexdigest(),actual_name='RYAN',slot=20,owner=21,variant=1,
        explicit_old_DK_window7_resource_fixture=True,actual_UI_Select_retires_old_lease=True,
        actual_published_sprite_banks=m.chr_latches[:8],modes=list(m[0x73e0:0x73ec]),
        separate_unseeded_full_route=True,Mesen_run=False,outputs=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');p.add_argument('--lease',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Ryan source checker attempted file/Mesen output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):
        q=lease(raw)if a.lease else run(raw,a.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not(a.metadata or a.lease):assert q['passed'],'Ryan full route remains source-unqualified'
