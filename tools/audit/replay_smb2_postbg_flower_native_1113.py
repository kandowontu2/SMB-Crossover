"""Pure ROM-identity adapter for unchanged natural SMB2 Flower controls."""
from hashlib import sha256
import argparse
import json
from pathlib import Path

import compose_smb2_postbg_mirror_1113 as C
import replay_smb2_natural_flower_1113 as Flower

FROZEN_SOURCE = '52f1d6f743b0df158f71123e58a39faa195236d45add1b5b515c34d33c4c4890'
SCOPES = Flower.SCOPES


def controller(raw,variant=4,scope='collect'):
    assert sha256(raw).hexdigest() == C.CANDIDATE
    assert 0<=variant<8 and scope in SCOPES
    assert sha256(Path(Flower.__file__).read_bytes()).hexdigest() == FROZEN_SOURCE
    parent = C.inverse(raw)
    assert sha256(parent).hexdigest() == C.PIN == Flower.PIN
    text = Flower.controller(parent,variant,scope)
    expected = {'collect':Flower.COLLECT_SHA,'throw':Flower.THROW_SHA,'hit':Flower.HIT_SHA}[scope][variant]
    assert sha256(text.encode()).hexdigest() == expected
    assert text.count(C.PIN) == 1
    rebound = text.replace(C.PIN,C.CANDIDATE)
    assert rebound.count(C.CANDIDATE) == 1 and rebound.replace(C.CANDIDATE,C.PIN) == text
    Flower.Parent.Root.Base.LuaRuntime().compile(rebound)
    assert all(word not in rebound for word in ('emu.write','emu.setState','takeScreenshot','io.open'))
    return rebound


def metadata(raw,variant=4,scope='collect'):
    text=controller(raw,variant,scope)
    parent_SHA={'collect':Flower.COLLECT_SHA,'throw':Flower.THROW_SHA,'hit':Flower.HIT_SHA}[scope][variant]
    return dict(ROM_SHA256=C.CANDIDATE,parent_ROM_SHA256=C.PIN,variant=variant,scope=scope,
                controller_SHA256=sha256(text.encode()).hexdigest(),parent_controller_SHA256=parent_SHA,
                only_ROM_identity_changed=True,original_inputs_observers_and_endpoint_exact=True,
                new_helpers=0,state_or_actor_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='4')
    p.add_argument('--scope',choices=SCOPES+('quick',),default='quick')
    args=p.parse_args()
    raw=C.Owner.NIGHTLY.read_bytes()
    if sha256(raw).hexdigest()==C.PIN:
        raw=C.proposal(raw)[0]
    else:
        assert sha256(raw).hexdigest()==C.CANDIDATE
        assert sha256(C.inverse(raw)).hexdigest()==C.PIN
    variants=range(8)if args.variant=='all'else(int(args.variant),)
    scopes=('collect','hit')if args.scope=='quick'else(args.scope,)
    for variant in variants:
        for scope in scopes:print(json.dumps(metadata(raw,variant,scope),separators=(',',':')),flush=True)
