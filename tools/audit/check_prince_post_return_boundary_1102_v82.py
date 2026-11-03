"""Compact diagnosis of the remaining full-frame native lag-NMI difference."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_core_1102_v79 as A
import check_prince_native_stack_1102_v72 as S
N,O=S.N,A.O;address=S.address


def main():
 b,m,lab=A.loaded();S.fatal(m,b)
 for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v
 for epoch in range(20):N.put(m,FrameCounter=epoch);S.run(m,'GameCoreRoutine',lab)
 N.put(m,FrameCounter=20);S.clear(m);seed=N.fork(m);ref=S.run(m,'GameCoreRoutine',lab);expected=S.state(m)
 z=N.fork(seed);got=S.run(z,'GameCoreRoutine',lab,('lagNMI',(346,154,3)))
 diffs=[]
 for i,(a,v)in enumerate(zip(expected[4],bytes(z[0x200:0x800]))):
  if a!=v:
   pos=i+0x200;names=[n for n,s in b['syms'].items()if int(s['val'],0)==pos];diffs.append(dict(address=pos,names=names,reference=a,lagNMI=v))
 private=[(k,i,a,v)for k in range(4)for i,(a,v)in enumerate(zip(expected[0][k],z.ram[k]))if a!=v]
 q=dict(diagnostic_only=True,qualified=False,regs=[ref['regs'],got['regs']],private_differences=private,native_differences=diffs,scratch=[list(expected[1]),list(z[3:11])],SMC=[list(expected[2]),list(z[0x15a:0x17b])],maps=[expected[3],z.rawtags],minimum_SP=got['minSP'])
 (O/'post-return-boundary-v82.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
