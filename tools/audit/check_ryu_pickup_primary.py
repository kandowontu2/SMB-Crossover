"""Qualify actual equipment-change owners before accepting a Ryu repro."""
from pathlib import Path
import argparse, hashlib, json
from robots_weapon_cpu_v1 import Arena, load


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(exist_ok=False)
    rows=[]
    for name,path in [('baseline',a.baseline),('candidate',a.candidate)]:
        b=load(path)
        for item in range(1,5):
            q=Arena(b,char=10)
            q.put(AvSlash=1,AvFlip=1,Player_State=1,GamePauseStatus=1,
                  SavedJoypad1Bits=2,InvPrevious=0)
            q.set('InvSelected',5,10);q.set('InvOwnedLo',1|32|(1<<item),10)
            q.invoke('InventoryUiTick')
            assert q.get('InvSelected',10)==item and q.get('AvSlash')==0
            # Thus InventoryCycle alone is not a legal paused-UI reproduction.
            q=Arena(b,char=10)
            q.put(AvSlash=1,AvFlip=1,Player_State=1,GamePauseStatus=0)
            q.set('InvSelected',5,10);q.set('InvOwnedLo',1|32,10)
            q.invoke('InventoryGrant',a=item)
            assert q.get('InvSelected',10)==item and q.get('AvSlash')==1
            q.put(SavedJoypadBits=64,RgPreviousButtons=0,XgWall=0)
            q.invoke('ExpandedWeapons')
            expected=14 if name=='baseline'else 0
            assert q.get('RgAttack')==expected and q.get('AvSlash')==1
            rows.append(dict(ROM=name,item=item,selected=q.get('InvSelected',10),
                             slash=q.get('AvSlash'),primary_timer=q.get('RgAttack')))
    proof=dict(passed=True,goal_complete=False,adopted=False,
               baseline_ROM_sha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest(),
               candidate_ROM_sha256=hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
               actual_UI_controls=8,actual_grant_then_primary_cases=8,cases=rows,
               correction='Full paused InventoryUiTick clears AvSlash; the earlier direct InventoryCycle reproduction omits its cleanup owner. Actual InventoryGrant auto-equips each new ninjitsu while airborne and preserves Slash, reproducing the forbidden primary through its real grant owner.',
               scope='Full assembled InventoryUiTick, InventoryGrant and ExpandedWeapons, real farcalls/no external traps. Explicit legal airborne/pickup staging. No native physical pickup, IRQ/PPU/audio proof or installation.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
