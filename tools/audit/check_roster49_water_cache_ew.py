"""Compiled WaterPosition ABI, exact cached vectors and nonuniform fallback."""
from pathlib import Path
import collections,hashlib,importlib.util,itertools,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-water-cache-eq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=J/'cpu-review-ew.json';assert not out.exists()
 assert sha(J/'build-review-es.json')=='3178b6bf146e507bdc39895d070bfa8cb590fcdfb04b9bed86ffdad1f53f5a7b'
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';sp=importlib.util.spec_from_file_location('water_ew_model',mp);model=importlib.util.module_from_spec(sp);sp.loader.exec_module(model)
 # Local CPU table repair only. Native instruction capture AZ independently
 # identified py65's CE/DEC-absolute entry as3; actual 2A03 executes6 cycles.
 class CPU(model.q.core.NesMPU):
  cycletime=list(model.q.core.NesMPU.cycletime)
  cycletime[0xce]=6
 results=[];digest=hashlib.sha256()
 for mapper in ['mmc3','mmc5']:
  before=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h'/f'smb-crossover-{mapper}.nes';after=J/'source/build'/before.name
  images=[model.q.Image(before),model.q.Image(after)];assert images[0].ram==images[1].ram;L=images[0].ram
  def put(raw,n,v,i=0):
   ad=L[n]+i;at=ad if ad<2048 else ad-0x6000+2048;raw[at]=v&255
  stats=collections.defaultdict(collections.Counter);count=0
  for angle,radius,direction,hit in itertools.product(range(256),[22,63,127,179,180],(1,2),(False,True)):
   number=count;initial=bytearray((i*37+angle*11+radius)&255 for i in range(10240));slot=number%10
   for n,v in [('RgSlot',slot),('SsWaterScaleKey',(angle&31) if hit else ((angle+1)&31)),('SsWaterRadius',radius),('SsWaterExpand',1),('SsWaterX',(angle*31)&255),('SsWaterPage',(angle%7)),('SsWaterY',32+number%200)]:put(initial,n,v)
   for n,v in [('SsAngleHi',angle),('SsAngleLo',number&255),('RgShotDir',direction),('RgShotType',17),('SsHidden',0)]:put(initial,n,v,slot)
   stack=0xe0+(number%16);initial[0x100+stack+1]=0xff;initial[0x100+stack+2]=0x5c
   regs=[number&255,slot,(number*7)&255,(number*17)&0xcf,stack];both=[]
   for im in images:
    mem=model.Bus(im,initial,{0x8000:62,0xa000:60,0xc000:13,0xe000:63},());cpu=CPU(memory=mem);cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=regs;cpu.pc=im.hook('WaterPosition',scope='SpecialWeapons')['address'];cpu.processorCycles=0;steps=0
    while cpu.pc!=0x5d00 or cpu.sp!=stack+2:
     mem.pc=cpu.pc;mem.op=mem.data[cpu.pc];cpu.step();steps+=1;assert steps<2500
    ensure=im.hook('EnsureWaterScale',scope='SpecialWeapons')['address'];calls=[];keep=[]
    for z in mem.trace:
     pc,op,ad,physical,value=z
     if op==0x20 and mem.data[pc+1]+256*mem.data[pc+2]==ensure:
      assert physical in [0x100+stack,0x100+stack-1] and physical<0x100+stack+1
      assert value in [(pc+2)>>8,(pc+2)&255];calls.append(z)
     else:keep.append(z[1:])
    both.append(dict(regs=[cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc],ram=mem.ram(),trace=keep,calls=calls,cycles=cpu.processorCycles,banks=mem.banks,selector=mem.selector,ports=mem.ports))
   a,b=both
   for key in ['regs','trace','banks','selector','ports']:assert a[key]==b[key],(mapper,number,key)
   assert len(a['calls'])==2 and len(b['calls'])==(0 if hit else 2)
   dead={0x100+stack,0x100+stack-1}
   for i,(x,y)in enumerate(zip(a['ram'],b['ram'])):
    if x!=y:assert model.q.g.RAMS[i]in dead,(mapper,number,model.q.g.RAMS[i],x,y)
   saved=a['cycles']-b['cycles'];assert saved==(12 if hit else 0),(mapper,number,saved)
   stats['hit'if hit else'miss'][saved]+=1;digest.update(bytes(b['regs'][:5]));digest.update(b['ram']);count+=1
  results.append(dict(mapper=mapper,cases=count,cycle_saving_histograms={k:dict(v)for k,v in stats.items()},before_sha256=sha(before),after_sha256=sha(after)));print(mapper,count,flush=True)
 out.write_text(json.dumps(dict(status='PASS_COMPILED_WATER_CACHE_HIT_AND_FALLBACK_ABI',script_sha256=sha(__file__),build_review_sha256=sha(J/'build-review-es.json'),results=results,digest=digest.hexdigest(),compared='AXYP/SP/return, all10240RAM except two explicitly executed dead EnsureWaterScale JSR cells, all remaining ordered writes with PC locations removed, mapper banks/selector/ports. All256angles, five radii including kill threshold, both directions, hit/miss, all10slots.',CPU_local_correction='Copy cycletime table and set opcodeCE to6; shared py65 remains untouched. Native timings remain authoritative.',limits=['Authored isolated compiled units, no native interrupt composition, ordinary acquisition or populated frame-rate proof.','Cache-hit JSR/RTS removed12cycles per reused ball; no claim that all WaterShield lag is solved.'],main_changed=False,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out),flush=True)
if __name__=='__main__':main()
