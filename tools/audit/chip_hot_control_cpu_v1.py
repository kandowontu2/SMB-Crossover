"""Compare full caller states for private Chip hot control; no native timing claim."""
from pathlib import Path
import argparse,hashlib,json
from check_tmnt_render_oa import load,address,Memory
from verify_native_relocation import NesMPU
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def phys(m,pc):return m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
def setup(b,snap,raw,cfg):
 m=Memory(b)
 for slot,k in enumerate(snap['banks']):m.page(slot,k)
 p=0;payload=raw[snap['ramOffset']:snap['ramOffset']+snap['ramBytes']]
 for lo,hi in cfg['ram_ranges']:
  for at in range(lo,hi+1):list.__setitem__(m,at,payload[p]);p+=1
 c=NesMPU(memory=m,pc=snap['pc']);c.a,c.x,c.y,c.p,c.sp=[snap[n]for n in['a','x','y','p','sp']];m.writes=[];return m,c
def stop_pc(m,c):return ((m[0x100+(c.sp+1)%256]|m[0x100+(c.sp+2)%256]<<8)+1)&65535,(c.sp+2)&255
def run(m,c,limit=100000):
 ret,sp=stop_pc(m,c);start=c.processorCycles
 for _ in range(limit):
  if c.pc==ret and c.sp==sp:return c.processorCycles-start
  c.step()
 raise AssertionError(('timeout',c.pc,c.sp,ret,sp))
def clone(b,old,c):
 m=Memory(b)
 for slot,k in enumerate(old.banks):m.page(slot,k)
 for lo,hi in[(0,0x7ff),(0x5c00,0x7fff)]:list.__setitem__(m,slice(lo,hi+1),old[lo:hi+1])
 x=NesMPU(memory=m,pc=c.pc);x.a,x.x,x.y,x.p,x.sp=c.a,c.x,c.y,c.p,c.sp;m.writes=[];return m,x
def compare(old,new,oc,nc):
 # Only stale, inactive stack bytes are outside the caller contract; preserve
 # the actual copied SMC code within that page as well as SP and every register.
 smc=range(address(old.bundle,'__SMCCODE_RUN__'),address(old.bundle,'__SMCCODE_RUN__')+address(old.bundle,'__SMCCODE_SIZE__'))
 at=list(range(0x100))+list(range(0x200,0x800))+list(range(0x5c00,0x8000))+list(smc)
 diff=[dict(address=x,old=old[x],new=new[x])for x in at if old[x]!=new[x]]
 return dict(passed=not diff and(oc.a,oc.x,oc.y,oc.p,oc.sp,old.banks)==(nc.a,nc.x,nc.y,nc.p,nc.sp,new.banks),RAM_differences=diff,old_AXYPS=[oc.a,oc.x,oc.y,oc.p,oc.sp],new_AXYPS=[nc.a,nc.x,nc.y,nc.p,nc.sp],old_banks=old.banks,new_banks=new.banks)
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);parent=D/'root-chip-native-adapter-v6/candidate.nes';old=load(parent);new=load(a.candidate);f=D/'chip-idle-profiler-v1/fixture-v4';ss=[json.loads(x)for x in(f/'profile-snapshots.jsonl').read_text().splitlines()];raw=(f/'profile-snapshots.ram').read_bytes();cfg=json.loads((f/'configuration.json').read_text());results=[]
 for ix,s in enumerate([x for x in ss if x['kind']=='component-entry'and x['detail']=='GameLoop'][:4]):
  m,c=setup(old,s,raw,cfg)
  for _ in range(100000):
   if c.pc==address(old,'PlayerCtrlRoutine')and phys(m,c.pc)==1:break
   c.step()
  else:raise AssertionError('no PlayerCtrl')
  om,oc=clone(old,m,c);nm,nc=clone(new,m,c);ot=run(om,oc);nt=run(nm,nc);q=compare(om,nm,oc,nc);q.update(kind='actual captured Main→PlayerCtrl CPU state',snapshot=ss.index(s),old_cycles=ot,new_cycles=nt,delta=nt-ot);results.append(q)
 proof=dict(passed=all(x['passed']for x in results),native_executed=False,ROM_sha256=sha(a.candidate),parent_ROM_sha256=sha(parent),scope='Actual assembled complete PlayerCtrl CPU caller differential on captured states. NMI/PPU/DMA timing not modeled. RAM/SMC/banks/fullAXYPS preserved; only stale stack bytes outside copied SMC excluded.',cases=results,checker_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
