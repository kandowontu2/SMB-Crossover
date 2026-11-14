"""Rejected cache-only hidden-head diagnostics; no qualified controller."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import compose_smb2_hidden_head_1114 as C
import replay_smb2_hidden_oneup_1113 as Frozen

PIN=C.CANDIDATE


def controller(raw,variant=0,strategy='immediate'):
    parent=C.inverse(raw);public=C.public_image(parent)
    text=Frozen.controller(public,variant)
    assert text.count(Frozen.PIN)==1
    text=text.replace(Frozen.PIN,PIN)
    # Preserve the frozen44ec immediate-chase failure separately: original
    # kind3 admits contact once state6 is visible. Walk away using ordinary
    # input until its actual grow routine reaches state128, then chase it.
    before='if item then pad=s.x<item.x-5 and 1 or s.x>item.x+4 and 2 or 0;return end'
    after='''if item then
  if item.state<128 then pad=oneupSettle(984);return end
  pad=s.x<item.x-5 and 1 or s.x>item.x+4 and 2 or 0
  if own.S2Air==0 and own.S2Held&128==0 and not oneup.catch_jump then oneup.catch_jump=updates end
  if oneup.catch_jump and updates-oneup.catch_jump<24 then pad=pad|128 end
  return
 end'''
    assert strategy in('immediate','mature-jump')
    if strategy=='mature-jump':
        assert text.count(before)==1;text=text.replace(before,after)
    Frozen.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_run(raw,variant=0,limit=2800):
    assert sha256(raw).hexdigest()==PIN
    with patch.object(Frozen.OldReplay,'controller',lambda image,v,mode:controller(image,v)),patch.object(Frozen.Runner,'PIN',PIN):
        q=Frozen.Runner.run_controller(raw,variant,'natural-hidden-oneup',limit)
    receipt=q.pop('receipt')or{}
    q.update(reason=receipt.get('reason'),all_returned_Main=receipt.get('all_returned_Main'),
             oneup=receipt.get('oneup'),physical_native_claim=False)
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--cpu',action='store_true');p.add_argument('--limit',type=int,default=2800)
    args=p.parse_args();raw=C.proposal(C.parent_image())[0]
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant,args.limit)if args.cpu else dict(ROM_SHA256=PIN,variant=variant,
            controller_SHA256=sha256(controller(raw,variant).encode()).hexdigest(),outputs=0,Mesen_run=False)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Natural hidden1UP must qualify without gameplay seeds'
