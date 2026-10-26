"""Replay captured Main entry states without interrupts; attribute executed farcalls/NOPs."""
from pathlib import Path
import argparse,collections,hashlib,json,re
from check_tmnt_render_oa import load,address,location,Memory
from verify_native_relocation import NesMPU
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);prep=json.loads((a.fixture/'preparation.json').read_text());b=load(Path(prep['ROM']));cfg=json.loads((a.fixture/'configuration.json').read_text());snapshots=[json.loads(x)for x in(a.fixture/'profile-snapshots.jsonl').read_text().splitlines()];raw=(a.fixture/'profile-snapshots.ram').read_bytes();native=[json.loads(x)for x in(a.fixture/'profile-spans.jsonl').read_text().splitlines()];source=D/'cv3-remaining-current50b-v1/baseline-source';overlay=D/'root-chip-native-adapter-v6/source';proc=set()
 for src in[source/'src',overlay/'src']:
  for f in src.rglob('*'):
   if f.is_file()and f.suffix in['.s','.inc']:proc.update(re.findall(r'^\s*\.proc\s+([A-Za-z_]\w*)',f.read_text(errors='replace'),re.M|re.I))
 intervals=[];names=collections.defaultdict(list)
 for n,s in b['syms'].items():
  if s.get('type')!='lab':continue
  try:pc=address(b,n);bank=(location(b,n)-16)//8192
  except Exception:continue
  if pc<0x8000 or not 0<=bank<128:continue
  names[(bank,pc)].append(n)
  if n in proc and s.get('size'):intervals.append((bank,pc,pc+int(s['size'],0),n))
 def name(bank,pc):return sorted(names.get((bank,pc),['unknown']),key=lambda n:(n not in proc,len(n)))[0]
 def owner(bank,pc):
  items=[q for q in intervals if q[0]==bank and q[1]<=pc<q[2]];return min(items,key=lambda q:q[2]-q[1])[3]if items else name(bank,pc)
 class Bus(Memory):
  def __getitem__(self,at):
   if isinstance(at,int)and getattr(self,'observe',False)and 0x2000<=at<0x5c00:self.io_reads.append(at)
   return super().__getitem__(at)
 results=[]
 choices=[s for s in snapshots if s['kind']=='component-entry'and s['detail']=='GameLoop'][:4]
 for ix,snap in enumerate(choices):
  m=Bus(b);m.observe=False;m.io_reads=[];m.banks=snap['banks'][:];at=snap['ramOffset'];payload=raw[at:at+snap['ramBytes']];pos=0
  for lo,hi in cfg['ram_ranges']:
   for at in range(lo,hi+1):list.__setitem__(m,at,payload[pos]);pos+=1
  c=NesMPU(memory=m,pc=snap['pc']);c.a,c.x,c.y,c.p,c.sp=[snap[n]for n in['a','x','y','p','sp']];ret=(m[0x100+(c.sp+1)%256]|m[0x100+(c.sp+2)%256]<<8)+1;ret&=65535;returnSP=(c.sp+2)&255;far=[];openfar=[];nop=collections.Counter();nop_runs=[];run=None;regions=[];openregions=[];publications=[];m.writes=[];m.observe=True
  def phys(pc):return m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
  for steps in range(100000):
   for f in openfar:
    if f.get('bodyStart')is not None and f.get('bodyCycles')is None and c.pc==f['bodyRet']and c.sp==f['bodySP']:
     f['bodyCycles']=c.processorCycles-f['bodyStart'];f['bodyResult']=[c.a,c.x,c.y,c.p,c.sp];f['bodyNonstackWrites']=[(x,v)for x,v in m.writes[f['bodyWriteIndex']:]if not 0x100<=x<0x200]
   while openfar and c.pc==openfar[-1]['ret']and c.sp==openfar[-1]['returnSP']and phys(c.pc)==openfar[-1]['returnBank']:
    f=openfar.pop();f['fullCycles']=c.processorCycles-f['start'];f['scaffoldCycles']=f['fullCycles']-f.get('bodyCycles',0);far.append(f)
   while openregions and c.pc==openregions[-1]['ret']and c.sp==openregions[-1]['returnSP']and phys(c.pc)==openregions[-1]['returnBank']:
    f=openregions.pop();f['cycles']=c.processorCycles-f['start'];regions.append(f)
   if c.pc==ret and c.sp==returnSP:break
   bank=phys(c.pc)
   for h in cfg['functions']:
    if c.pc==h['address']and bank==h['physical_bank']:
     rr=((m[0x100+(c.sp+1)%256]|m[0x100+(c.sp+2)%256]<<8)+1)&65535
     if not(openregions and openregions[-1]['entry']==c.pc and openregions[-1]['entrySP']==c.sp):openregions.append(dict(name=h['name'],entry=c.pc,entrySP=c.sp,ret=rr,returnSP=(c.sp+2)&255,returnBank=phys(rr),start=c.processorCycles))
   if c.pc==address(b,'FarCallCommon'):
    rr=((m[0x100+(c.sp+1)%256]|m[0x100+(c.sp+2)%256]<<8)+1)&65535;target=m[address(b,'FarcallJmpTarget_SMC')+1]|m[address(b,'FarcallJmpTarget_SMC')+2]<<8;openfar.append(dict(target=name(c.a&127,target),targetPC=target,targetBank=c.a&127,start=c.processorCycles,ret=rr,returnSP=(c.sp+2)&255,returnBank=phys(rr),nativeRegion=openregions[-1]['name']if openregions else'none',entryAXYP=[c.a,c.x,c.y,c.p]))
   if c.pc==address(b,'FarcallJmpTarget_SMC')and openfar:
    f=openfar[-1];f.update(bodyStart=c.processorCycles+6,bodyRet=c.pc+3,bodySP=c.sp,bodyWriteIndex=len(m.writes))
   op=m[c.pc]
   if op==0xea:
    label=owner(bank,c.pc);nop[label]+=1
    if run and run['bank']==bank and run['start']+run['count']==c.pc:run['count']+=1
    else:
     if run:nop_runs.append(run)
     run=dict(bank=bank,start=c.pc,count=1,owner=label)
   elif run:nop_runs.append(run);run=None
   before=len(m.writes);start=c.processorCycles;c.step()
   if any(x==address(b,'NmiDisable')and v==0 for x,v in m.writes[before:]):publications.append(dict(instructionStartCycle=start,instructionEndCycle=c.processorCycles,PC_after_store=c.pc))
  else:raise AssertionError('Counterfactual Main timeout')
  if run:nop_runs.append(run)
  expected=next(x for x in native if x['name']=='GameLoop'and x['startCycle']==snap['cpuCycle']);assert c.processorCycles==expected['cpuCycles'],('Seeded no-interrupt replay cost differs from native exclusive-ISR total',ix,c.processorCycles,expected)
  row=dict(snapshot_index=snapshots.index(snap),actual_native_entry=snap,actual_native_Main=expected,counterfactual_CPU_cycles=c.processorCycles,actual_native_CPU_cycles=expected['cpuCycles'],cycles_exact=True,actual_IO_reads=sorted(set(m.io_reads)),modeled_IRQ_NMI_PPU_DMC_DMA=False,farcall_records=far,unclosed_farcalls=openfar,native_regions=regions,unclosed_regions=openregions,executed_NOP_counts=dict(nop),executed_NOP_runs=nop_runs,publication_CPU_offsets=publications)
  (a.output/f'Main-{ix}.json').write_text(json.dumps(row,indent=2)+'\n');results.append(dict(snapshot_index=row['snapshot_index'],native_entry_cycle=snap['cpuCycle'],CPU_cycles=c.processorCycles,native_CPU_cycles=expected['cpuCycles'],farcalls=len(far),unclosed_farcalls=len(openfar),NOP_cycles=2*sum(nop.values()),IO_reads=row['actual_IO_reads'],file_sha256=sha(a.output/f'Main-{ix}.json')))
 result=dict(passed=True,native_executed=False,ROM_sha256=prep['ROM_sha256'],replayed_actual_Main_entry_states=results,all_no_interrupt_CPU_cycles_match_native_ISR_excluded_totals=True,scope='Deterministic CPU-only replays from actual captured Main entry RAM/AXYP/SP/physical banks. No emulated NMI/PPU/DMA/DMC timing is reproduced. Agreement for these exact entries supports cost attribution only, not optimized gameplay correctness or the uncaptured first normal Main entry.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
