"""Exact421 SMB3 full routes; explicit compiled frontend and frozen driver."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_smb3_alts_full11_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_bub_current_budget_1113 as Frames

W,N=Factory.W,Factory.N
HARNESS_SOURCE='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'


def cold(raw,key):
    q=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    W.UI.key(m,4);W.UI.key(m,4)
    for _ in range(q['cycle']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==q['name']and N.get(m,'SelectedCharacter')==17 and N.get(m,'M3Variant')==q['variant']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'SelectedCharacter')==17 and N.get(m,'M3Variant')==q['variant']and N.get(m,'M3Ready')==0xb3
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual current SMB3 cold constructor bound')


def run(raw,key,*,metadata_only=False,limit=7000):
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()==HARNESS_SOURCE
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,key)if metadata_only else Runner.run(raw,key,limit)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');args=p.parse_args()
    q=run(Factory.ROM.read_bytes(),args.identity,metadata_only=args.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'SMB3 full-stage source route remains unqualified'
