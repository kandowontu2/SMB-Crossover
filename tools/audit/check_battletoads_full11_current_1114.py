"""Genuine current Battletoads cold construction and bounded route discovery."""
import argparse,json
from hashlib import sha256
from unittest.mock import patch
import replay_battletoads_full11_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner

W,N=Factory.W,Factory.N


def cold(raw,key):
    q=Factory.bindings(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in q['navigation']:W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]==q['name'] and N.get(m,'SelectedCharacter')==33
    s=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
    N.invoke(m,'PauseRoutine',a=0)
    def private(name):return m.ram[3][W.address(b,name)&8191]
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert private('BtHostReady')==1 and private('BtVariant')==q['variant']
            assert private('BtSrc_Objects_Life')==47 and private('BtSrc_Objects_death_timer')==0
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Runner.Frames.frame(m,cold=True)
    raise AssertionError('Actual Battletoads constructor bound')


def run(raw,key,limit=10000):
    assert sha256(open(Runner.__file__,'rb').read()).hexdigest()=='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',Factory.metadata):
        return Runner.run(raw,key,limit)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True);p.add_argument('--limit',type=int,default=10000);p.add_argument('--metadata',action='store_true');a=p.parse_args();raw=Factory.ROM.read_bytes()
    q=Factory.metadata(raw,a.identity)if a.metadata else run(raw,a.identity,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
