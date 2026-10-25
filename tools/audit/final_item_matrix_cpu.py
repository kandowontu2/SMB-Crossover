"""Actual linked mode predicate and progressive transformation controls; no Mesen."""
from pathlib import Path
import argparse,hashlib,json
from final_item_matrix import ROSTER
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 b=scoped_load(a.rom);modes=[];transforms=[]
 for name,slot,char,variant,value,family in ROSTER:
  for mode in [0,1]:
   q=Arena(b,char);q.put(CrossoverBehaviorVersion=mode)
   if variant:q.set(variant,value)
   cpu,_=q.invoke('InventoryLegacyLeaf')
   expected=char==15 or(family=='cv3')or(family=='z2')or(mode==0 and char in range(1,6))
   assert bool(cpu.p&1)==expected,(name,mode,cpu.p,expected)
   modes.append(dict(identity=name,mode=mode,classic_predicate=bool(cpu.p&1)))
 for char in [6,7,12]:
  for mode in [0,1]:
   for status in [0,1,2]:
    q=Arena(b,char);q.put(CrossoverBehaviorVersion=mode,PlayerStatus=status,GuestPowerupActive=0,RgPose=0,DarkwingVariant=0)
    q.invoke('GuestBeginPowerup');expected=min(2,status+1)
    if status<2:
     assert q.get('GuestPowerupTarget')==expected and q.get('GuestPowerupActive')==1 and q.get('TimerControl')==255 and q.get('GameEngineSubroutine')==9
     for tick in range(1,61):
      q.set('TimerControl',254) # Actual GameLoop decrement before player dispatch.
      q.invoke('GuestPowerupUpdate')
      assert q.get('PlayerStatus')==(status if tick<60 else expected)
      assert q.get('GuestPowerupActive')==(1 if tick<60 else 0)
     assert q.get('TimerControl')==0 and q.get('GameEngineSubroutine')==8
    else:assert q.get('GuestPowerupActive')==0 and q.get('PlayerStatus')==2
    transforms.append(dict(character=char,mode=mode,before=status,after=q.get('PlayerStatus'),native_transform_updates=60 if status<2 else 0))
 proof=dict(passed=True,goal_complete=False,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),mode_predicates=modes,transform_controls=transforms,scope='Actual assembled read-only mode predicate74 cases and progressive transform18 controls/720 update calls. Direct CPU calls; no physical delivery, native timing, PPU/NMI/audio or campaign claim.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,mode_predicates=len(modes),transforms=len(transforms),updates=sum(x['native_transform_updates']for x in transforms),ROM_sha256=proof['ROM_sha256'])))

if __name__=='__main__':main()
