"""Authored compiled IRQ injection at every reached optimized scan boundary.

Complements actual native DB, whose real IRQs land outside the changed span.
"""
from pathlib import Path
import collections,hashlib,importlib.util,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-audio-scan-h'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=H/'scan-irq-components-dc.json';assert not out.exists()
 assert sha(H/'native-irq-cz/cpu-native-review-db.json')=='fa7464b1ff17fb6d4f5dc0a8e823e00ee031f5dc013e8ed3cfb7e99e953dff3e'
 mp=V/'agent49-samus-bill-arsenal-a/palette_native_model_cu.py';spec=importlib.util.spec_from_file_location('scan_ISR_DC',mp);model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
 im=model.q.Image(H/'source/build/smb-crossover-mmc3.nes');old=model.q.Image(R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/smb-crossover-mmc3.nes');irq=im.hook('IrqScrollSplit');size=im.sym('IrqScrollSplit')['size'];o=old.hook('IrqScrollSplit');assert im.raw[irq['rom_offset']:irq['rom_offset']+size]==old.raw[o['rom_offset']:o['rom_offset']+size]
 banks=[im.hook('MetroidAudio'+str(k))['physical_bank']for k in[0,1,2,4,5]];assert len({im.raw[16+k*8192+0x14d8:16+k*8192+0x14fb]for k in banks})==1
 at=lambda ad:ad if ad<2048 else ad-0x6000+2048
 def execute(initial,regs,inject):
  b=model.Bus(im,initial,{0x8000:62,0xa000:banks[1],0xc000:13,0xe000:63},());c=model.q.core.NesMPU(memory=b);c.a,c.x,c.y,c.p,c.sp=regs;c.pc=0xb4d8;c.processorCycles=0;steps=0;index=0;boundary=[];pushed=set();injected=False
  def step():
   b.pc=c.pc;b.op=b.data[c.pc];popped=b.data[0x100+((c.sp+1)&255)]if b.op in(0x28,0x40)else None;op=b.op;c.step()
   if popped is not None:assert c.p==popped|0x30;c.p=popped&0xcf
   return op
  while c.pc!=0x5d00 or not steps:
   boundary.append(c.pc)
   if index==inject:
    before=dict(regs=[c.a,c.x,c.y,c.p,c.sp,c.pc],ram=b.ram(),banks=dict(b.banks),selector=b.selector);assert not c.p&4
    start=len(b.trace);b.pc=c.pc;b.op=0;c.irq();c.p&=0xcf;assert c.pc==irq['address']
    for j in range(200):
     op=step()
     if op==0x40:break
    else:raise AssertionError('Bounded compiled IRQ')
    assert [c.a,c.x,c.y,c.p,c.sp,c.pc]==before['regs']and b.banks==before['banks']and b.selector==before['selector'],'IRQ restores every register/SP/PC/mapper selector'
    trace=b.trace[start:];cells={z[3]for z in trace if 0x100<=z[3]<0x200};assert all(p<=0x100+before['regs'][4]for p in cells)
    assert all(z[2]in[0x2005,0x2006,0xe000]for z in trace if z[2]>=0x8000 or 0x2000<=z[2]<0x6000),'No audio ports or mapper bank writes in IRQ'
    now=b.ram()
    for i,(x,y)in enumerate(zip(before['ram'],now)):
     if x!=y:assert i in cells,('IRQ changes only its individually produced dead stack cells',i)
    pushed|=cells;injected=True
   step();index+=1;steps+=1;assert steps<100
  return dict(regs=[c.a,c.x,c.y,c.p,c.sp,c.pc],ram=b.ram(),banks=b.banks,selector=b.selector,boundaries=boundary,pushed=pushed,injected=injected)
 count=0;pcs=collections.Counter();digest=hashlib.sha256()
 for flags in[2,0xc9]:
  for mask in range(256):
   initial=bytearray(10240);initial[at(im.ram['SmAudioRam']+0x4d)]=mask;initial[0xe0:0xe2]=bytes([0,0xb2]);initial[im.ram['BankShadow']]=0x47;initial[im.ram['GuestHudIrqDelay'] if im.ram['GuestHudIrqDelay']<2048 else at(im.ram['GuestHudIrqDelay'])]=[13,28][mask&1]
   stack=0xc0+((mask+flags)&31);initial[0x101+stack]=0xff;initial[0x102+stack]=0x5c;regs=[mask^0xa5,mask,(mask+73)&255,flags,stack]
   base=execute(initial,regs,-1)
   for n,pc in enumerate(base['boundaries']):
    if not 0xb4dd<=pc<0xb4ef:continue
    got=execute(initial,regs,n);assert got['injected']
    for name in['regs','banks','selector']:assert got[name]==base[name],name
    for i,(x,y)in enumerate(zip(base['ram'],got['ram'])):
     if x!=y:assert i in got['pushed'],('Composed leaf RAM differs outside actual IRQ pushes',i)
    assert got['ram'][0x101+stack:0x200]==base['ram'][0x101+stack:0x200],'Every live incoming caller stack byte'
    pcs[pc]+=1;count+=1;digest.update(bytes(got['regs'][:5]));digest.update(got['ram'])
 assert count>2000
 out.write_text(json.dumps(dict(status='PASS_AUTHORED_H_SCAN_IRQ_BOUNDARY_COMPOSITION',script_sha256=sha(__file__),native_DB_sha256=sha(H/'native-irq-cz/cpu-native-review-db.json'),cases=count,all256_masks=True,input_P=[2,201],input_SP_domain=list(range(0xc0,0xe0)),injected_boundary_counts=dict(pcs),compiled_IRQ_bytes_literal_G=True,five_banks_same_scan_bytes=True,digest=digest.hexdigest(),scope='Authored CPU components inject compiled IRQ at every reached changed-scan instruction boundary for all256 masks/two status classes/32 SP values. Not native IRQ timings. Exact registers, physical banks, IRQ RAM effects and every live caller stack byte; individually produced now-dead ISR push cells are the only whole-call RAM differences.',native_captured_IRQs_inside_changed_span=0,native_captured_IRQs_total=258,main_changed=False,goal_complete=False),indent=2)+'\n');print('IRQ_BOUNDARY_COMPONENTS',count,sha(out))
if __name__=='__main__':main()
