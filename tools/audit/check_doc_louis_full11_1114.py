"""Genuine Doc Louis cold/full CPU route; frozen driver, no files/Mesen."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json

import replay_doc_louis_full11_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_bub_current_budget_1113 as Frames

W,N=Factory.W,Factory.N
HARNESS_SOURCE='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'


def cold(raw,key='doc'):
    q=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for k in(4,2,2,32):W.UI.key(m,k)
    assert W.UI.menu_name(m)[0]=='DOC LOUIS'and N.get(m,'SelectedCharacter')==15 and N.get(m,'MacVariant')==1
    s=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'LmReady')==0x4d and N.get(m,'LmHealth')==96 and N.get(m,'NumberofLives')==2
            assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual boxing constructor bound')


def run(raw,*,metadata_only=False,limit=9000):
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()==HARNESS_SOURCE
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'doc')if metadata_only else Runner.run(raw,'doc',limit)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');args=p.parse_args()
    q=run(Factory.ROM.read_bytes(),metadata_only=args.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Doc Louis current full source route remains unqualified'
