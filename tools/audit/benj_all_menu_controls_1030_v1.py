"""Preserve the62 enabled profiles while admitting two source Benj alternates."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import arthur_quick_functional_admission_v1 as A
P=R/'build/coherent62-lives-fixes-v1/joint'
J=R/'build/benj-menu-unlocked-1030-v3/joint'
O=J.parent


def collect(path, expanded):
 counts=A.COUNTS[:];counts[31]=2
 if expanded:counts[0]=7
 rows={}
 for slot,count in enumerate(counts):
  m=A.fresh(path,slot)
  A.call(m,'MenuResolveCharacter');A.call(m,'QueueSelection')
  for v in range(count):
   if v:A.button(m,32)
   actual=m.get('MarioVariant')if slot==0 else v
   r=A.call(m,'FmPending')[0]
   pending=bool(r['P']&1)
   name=[q for q in A.commands(m)if q['address']==0x2328]
   starts=[]
   for key in [16,128]:
    for flags in [0x30,0x31,0x71,0xf1]:
     z=A.start_boundary(A.T.fork(m),key,flags)
     assert z['launch']!=pending,(slot,v,key,flags,z)
     starts.append(z)
   rows[slot,actual]=dict(slot=slot,actual_variant=actual,raw=m.get('SelectedCharacter'),
       pending=pending,name=name,Starts_A_4flag_patterns=starts)
 return rows


def main():
 out=O/'all-menu-controls.json';assert not out.exists()
 assert A.sha(J/'candidate.nes')=='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6'
 old,new=collect(P,False),collect(J,True)
 assert len(old)==81 and len(new)==83
 for key,row in old.items():assert new[key]==row,('Existing menu/Start ABI changed',key)
 assert sum(not row['pending']for row in old.values())==62
 assert sum(not row['pending']for row in new.values())==64
 assert set(new)-set(old)=={(0,5),(0,6)}
 for v in [5,6]:assert new[0,v]['raw']==0 and not new[0,v]['pending']
 d=dict(passed=True,source_CPU=True,native=False,candidate=A.sha(J/'candidate.nes'),
   original_profiles=81,current_profiles=83,original_enabled=62,enabled_if_native_qualified=64,
   original_existing_individuals=80,new_individuals=2,generic_BT_placeholder=1,
   all_existing_names_and_Start_A_boundaries_exact=True,actual_Start_A_cases=664,
   rows=list(new.values()),bindings={str(p):A.sha(p)for p in [Path(__file__),P/'candidate.nes',P/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg',O/'handoff.json']})
 out.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps({k:v for k,v in d.items()if k not in['rows','bindings']}))


if __name__=='__main__':main()
