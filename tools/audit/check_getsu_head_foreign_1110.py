"""Compare foreign head-service entry state before the unchanged canonical gateway."""
import argparse,json
from pathlib import Path
from itertools import product
import check_getsu_head_callback_1110 as Head
Q=Head.Q

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(exist_ok=True)
 old=Head.BASE.read_bytes();new=Path('build/getsu-callback-final-native-1110/candidate.nes').read_bytes()
 b=[Q.Earned.D.Current.Getsu.W.bundle(raw) for raw in (old,new)]
 seeds=[Q.Earned.H.prepare(x) for x in b];N=Q.Earned.N;cases=0
 for raw,acc,flags in product((i for i in range(44) if i!=42),(0,0x55,255),(0x21,0x25,0x61,0x65)):
  ends=[]
  for seed in seeds:
   # Both preludes are read-only. Reuse the seed instead of cloning2MiB per case.
   m=seed;N.put(m,SelectedCharacter=raw);m[0x5115]=193;m[0x16a]=acc
   start=len(m.writes)
   c=N.NesMPU(memory=m,pc=0xb0aa);c.a=acc;c.x=71;c.y=109;c.sp=224
   c.p=(flags&~0x82)|(0x80 if acc&128 else 0)|(2 if acc==0 else 0)
   for _ in range(20):
    if c.pc==0xa740:break
    c.step()
   assert c.pc==0xa740
   assert len(m.writes)==start
   ends.append((c.a,c.x,c.y,c.p,c.sp,bytes(m[3:11]),bytes(m[0x15a:0x17b]),tuple(m.rawtags)))
  assert ends[0]==ends[1],(raw,acc,flags,ends);cases+=1
 q=dict(passed=True,foreign_entries=cases,scope='Foreign farcall entryAXYP/SP/SMC/maps exact at unchanged canonical native head gateway; raw42 intentionally restored.')
 (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(q)

if __name__=='__main__':main()
