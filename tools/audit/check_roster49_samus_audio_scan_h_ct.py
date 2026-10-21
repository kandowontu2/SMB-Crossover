"""Private compiled scan ABI and actual-entry isolated audio comparison."""
from pathlib import Path
import collections,hashlib,importlib.util,json,statistics
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-audio-scan-h'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=H/'cpu-review-ct.json';assert not out.exists()
 assert sha(H/'build-review.json')=='b3c597eecd63eaaab3b15fad6e31766d8c051d2413a6e92536b49420b1a0e18b'
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';assert sha(mp)=='213c1de880b418a19911f7af654f936bfb942c019e229bf6e871699a964bc94b'
 sp=importlib.util.spec_from_file_location('scan_CT',mp);model=importlib.util.module_from_spec(sp);sp.loader.exec_module(model)
 a=model.q.Image(R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/smb-crossover-mmc3.nes');b=model.q.Image(H/'source/build/smb-crossover-mmc3.nes');assert a.ram==b.ram
 banks=[a.hook('MetroidAudio'+str(k))['physical_bank']for k in [0,1,2,4,5]]
 class Bus(model.Bus):
  def __init__(self,*args):super().__init__(*args);self.locations=[]
  def write(self,ad,physical,value):
   self.locations.append(self.banks.get(self.pc&0xe000,-1)if self.pc>=0x8000 else-1);n=len(self.trace);super().write(ad,physical,value);assert len(self.trace)==n+1,'No DMA in isolated audio closure'
 def run(im,initial,regs,bs,pc,stop,stopSP):
  mem=Bus(im,initial,bs,());cpu=model.q.core.NesMPU(memory=mem);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=regs;cpu.pc=pc;cpu.processorCycles=0;steps=0
  while cpu.pc!=stop or cpu.sp!=stopSP or not steps:
   mem.pc=cpu.pc;mem.op=mem.data[cpu.pc];popped=mem.data[0x100+((cpu.sp+1)&255)]if mem.op in(0x28,0x40)else None;cpu.step()
   if popped is not None:assert cpu.p==popped|0x30;cpu.p=popped&0xcf
   steps+=1;assert steps<25000
  return dict(regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc],ram=mem.ram(),trace=mem.trace,locations=mem.locations,cycles=cpu.processorCycles,banks=mem.banks,selector=mem.selector,ports=mem.ports)
 def compare(old,new,initial,sp):
  for k in ['regs','banks','selector','ports']:assert old[k]==new[k],k
  removed=[];kept=[]
  for loc,z in zip(old['locations'],old['trace']):
   if loc in banks and z[0]in[0xb4dd,0xb4de,0xb4eb]:removed.append(z)
   else:kept.append((loc,z))
  assert kept==list(zip(new['locations'],new['trace'])),'Every remaining ordered write including stack/mapper/APU literal'
  pushes={z[3]for z in removed if z[0]==0xb4dd};assert all(0x100<=p<=0x100+sp for p in pushes)
  diffs=[]
  for i,(x,y)in enumerate(zip(old['ram'],new['ram'])):
   if x!=y:assert i in pushes,(i,x,y);diffs.append(i)
  assert old['cycles']>=new['cycles']
  return removed,diffs
 # The complete replacement bytes are identical at all five selected banks.
 patterns=[]
 for bank in banks:
  offset=16+bank*8192+0x14d8;patterns.append(b.raw[offset:offset+35])
 assert len(set(patterns))==1
 hist=collections.Counter();digest=hashlib.sha256();count=0
 maskaddr=a.ram['SmAudioRam']+0x4d;mi=maskaddr-0x6000+2048
 for p in range(256):
  for mask in range(256):
   initial=bytearray(10240);initial[mi]=mask;initial[0xe0:0xe2]=bytes([0,0xb2]);initial[a.ram['BankShadow']]=0x47
   stack=0xd0+((p+mask)&15);initial[0x100+((stack+1)&255)]=0xff;initial[0x100+((stack+2)&255)]=0x5c
   bs={0x8000:62,0xa000:banks[1],0xc000:13,0xe000:63};regs=[(mask*3+p)&255,p^mask,(p+mask)&255,p,stack]
   old=run(a,initial,regs,bs,0xb4d8,0x5d00,(stack+2)&255);new=run(b,initial,regs,bs,0xb4d8,0x5d00,(stack+2)&255);removed,diffs=compare(old,new,initial,stack)
   expected=[(0x100+stack,mask)];value=mask
   for i in range(8):
    expected.append((maskaddr,value));carry=value&128;value=(value<<1)&255;expected.append((maskaddr,value))
    if carry:break
   expected.append((maskaddr,mask));assert [(z[2],z[4])for z in removed]==expected,'Explicit old PHA/every ASL RMW/restoration oracle'
   digest.update(bytes(new['regs'][:5]));digest.update(new['ram']);hist[old['cycles']-new['cycles']]+=1;count+=1
 assert count==65536
 native=R/'build/roster-through-2-2/root49-g-samus-Fclock-ci-2-v0-mmc3';raw=(native/'audio-starts.ram').read_bytes();starts=[json.loads(s)for s in(native/'audio-starts.jsonl').read_text().splitlines()]
 profile=V/'root49-audio-isolated-cq/report.json';assert sha(profile)=='d4557ba6645dda4371bb976102f0642ee0e14381ffc8d1d6895651a0f89c56f2';original=json.loads(profile.read_text())['sample_results'];results=[]
 for z,ref in zip(starts,original):
  initial=raw[z['ramOffset']:z['ramOffset']+10240];stack=z['SP'];stop=(initial[0x100+((stack+1)&255)]+256*initial[0x100+((stack+2)&255)]+1)&65535
  bs={ad:z[n]for ad,n in [(0x8000,'bank8'),(0xa000,'bankA'),(0xc000,'bankC'),(0xe000,'bankE')]};regs=[z[n]for n in ['A','X','Y','P','SP']]
  old=run(a,initial,regs,bs,a.hook('AudioUpdate')['address'],stop,(stack+2)&255);new=run(b,initial,regs,bs,b.hook('AudioUpdate')['address'],stop,(stack+2)&255)
  assert old['cycles']==ref['cycles'] and old['regs']==ref['output_registers'] and hashlib.sha256(old['ram']).hexdigest()==ref['output_ram_sha256'],'G/F original isolated audio literal'
  removed,diffs=compare(old,new,initial,stack);results.append(dict(frame=z['frame'],old_cycles=old['cycles'],new_cycles=new['cycles'],saved=old['cycles']-new['cycles'],explicit_removed_scan_writes=len(removed),individually_dead_stack_differences=diffs))
 report=dict(status='PASS_PRIVATE_H_COMPILED_SCAN_ABI_AND_ISOLATED_AUDIO',script_sha256=sha(__file__),build_review_sha256=sha(H/'build-review.json'),exhaustive=dict(cases=count,all256masks_all256P=True,five_banks_literal_same_replacement=True,cycle_saving_histogram=dict(hist),digest=digest.hexdigest(),old_writes_oracle='Each PHA(mask), every actual ASL old/new RMW pair, final STA(originalmask) individually checked. All other ordered writes literal.',RAM_scope='All10240 bytes exact except each individually identified now-dead scan PHA cell. All actual incoming live stack bytes unchanged.'),actual_entry_isolated=dict(samples=len(results),original_profile_sha256=sha(profile),median_old=statistics.median(z['old_cycles']for z in results),median_new=statistics.median(z['new_cycles']for z in results),median_saved=statistics.median(z['saved']for z in results),min_saved=min(z['saved']for z in results),max_saved=max(z['saved']for z in results),results=results),main_changed=False,native_validation_pending=True,limits=['Actual F entry snapshots re-executed on G and private H without interrupt injection; no native H elapsed/end-state or audible fidelity claim.','No MMC5 or baseline byte changes. Runtime/main remain G.','Native current-H audio/SFX, ISR composition and ordinary Samus progression required before adoption.'],goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],cases=count,median_saved=report['actual_entry_isolated']['median_saved'],median_old=report['actual_entry_isolated']['median_old'],median_new=report['actual_entry_isolated']['median_new'],sha256=sha(out))))
if __name__=='__main__':main()
