"""Current82 source route with actual compiled Rogue selection/constructor."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import replay_rogue_full11_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_bub_current_budget_1113 as Frames

W,N=Factory.W,Factory.N


def cold(raw,key='rogue'):
    Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(1,1,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='ROGUE DAWN'and N.get(m,'SelectedCharacter')==2 and N.get(m,'RdVariant')==1
    s=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'NumberofLives')==2 and N.get(m,'RdVariant')==1
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual Rogue constructor bound')


def run(raw,metadata=False):
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()=='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'rogue')if metadata else Runner.run(raw,'rogue',9000)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');a=p.parse_args()
    q=run(Factory.ROM.read_bytes(),a.metadata);print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Current Rogue full source route remains unqualified'
