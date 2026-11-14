"""Current Mr Gimmick source route, genuine UI/constructor; zero files."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import replay_mr_gimmick_full11_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_bub_current_budget_1113 as Frames

W,N=Factory.W,Factory.N


def cold(raw,key='mr_gimmick'):
    c=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in c['navigation']:W.UI.key(m,pad)
    assert N.get(m,'SelectedCharacter')==26 and W.UI.menu_name(m)[0]==c['name']
    s=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'GmReady')==71
            assert N.get(m,'GmRam0346')==N.get(m,'GmRam002B')==2 and N.get(m,'GmRam0039')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual Gimmick constructor bound')


def run(raw,metadata=False):
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'mr_gimmick')if metadata else Runner.run(raw,'mr_gimmick',9000)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Source Gimmick checker attempted output/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):q=run(raw,a.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Mr Gimmick full source route remains unqualified'
