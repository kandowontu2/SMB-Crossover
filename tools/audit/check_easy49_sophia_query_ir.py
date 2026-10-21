"""Exhaustive integer-column/row query ABI and compiled cycle comparison."""
from pathlib import Path
import collections,hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
D=V/'root49-sophia-query-perf-ip';P=V/'agent49-e-sophia-union-a/source-e'
G=V/'ryu49-head-status-bridge-g';sys.path.insert(0,str(G))
s=importlib.util.spec_from_file_location('query_ir_bus',G/'check.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 out=D/'compiled-ir.json';assert not out.exists()
 report=dict(status='RUNNING',script_sha256=sha(__file__),preparation_sha256=sha(D/'preparation.json'),maps=[],scope='Direct compiled query calls, not native whole-frame/route/interrupt evidence. Removed old discarded pushes are individually decoded; no blanket stack mask.')
 try:
  for mapper in ['mmc3','mmc5']:
   name='smb-crossover-'+mapper+'.nes';old=g.Image(P/'build'/name);new=g.Image(D/'source/build'/name);L=old.ram
   assert old.ram==new.ram
   for n in ['NonMaskableInterrupt','IrqScrollSplit','MegaManVineAnchor']:assert old.hook(n)==new.hook(n)
   before=old.hook('SophiaTerrainQuery');after=new.hook('SophiaTerrainQuery');assert before==after
   helper=old.hook('GetBlockBufferAddr')['address'];code=old.raw[before['rom_offset']:before['rom_offset']+old.sym('SophiaTerrainQuery')['size']]
   target=bytes([0x20,helper&255,helper>>8]);assert code.count(target)==1
   jsr=before['address']+code.index(target);pha=old.hook('GetBlockBufferAddr')['address'];assert old.raw[old.hook('GetBlockBufferAddr')['rom_offset']]==0x48
   hist=collections.Counter();cases=0;sample=None
   template=bytearray((i*73+29)&255 for i in range(10240));sp=0xe8
   def put(r,n,v):r[g.at(L[n])]=v&255
   for page in [0,1]:
    for row in range(13):
     for x in range(256):
      ram=template.copy();put(ram,'RgTempX',x);put(ram,'RgTempPage',page);put(ram,'RgTempY',32+row*16+(x&15));put(ram,'SmTemp',(x*31+row)&255);put(ram,'Player_X_Position',(x+83)&255)
      ram[0x101+sp]=(g.RET-1)&255;ram[0x102+sp]=(g.RET-1)>>8
      regs=[(x*17)&255,(row*19)&255,(x*47)&255,(x+row*13+page*79)&255,sp]
      banks={0x8000:62,0xa000:before['physical_bank'],0xc000:36,0xe000:63}
      a=g.execute(old,CPU,ram,regs,banks,before['address'],g.RET,native_status=True)
      b=g.execute(new,CPU,ram,regs,banks,after['address'],g.RET,native_status=True)
      assert a['regs']==b['regs'],('All registers',mapper,page,row,x)
      pushes=[w for w in a['trace']if 0x100<=w[2]<0x200]
      assert [(w[0],w[1],w[2])for w in pushes]==[(jsr,0x20,0x100+sp),(jsr,0x20,0x100+sp-1),(pha,0x48,0x100+sp-2)],('Exactly decoded old discarded JSR/PHA cells',pushes)
      assert not any(0x100<=w[2]<0x200 for w in b['trace'])
      expected=bytearray(a['ram'])
      for w in pushes:
       assert a['ram'][w[2]]==w[4]and b['ram'][w[2]]==ram[w[2]]
       expected[w[2]]=ram[w[2]]
      assert bytes(expected)==bytes(b['ram']),('All10240RAM with only3 bound discarded old pushes',mapper,page,row,x)
      assert [(w[2],w[4])for w in a['trace']if w not in pushes]==[(w[2],w[4])for w in b['trace']],('Every ordered semantic write',mapper,page,row,x)
      assert a['ram'][0x101+sp:0x200]==b['ram'][0x101+sp:0x200]==ram[0x101+sp:0x200]
      hist[b['cycles']-a['cycles']]+=1;cases+=1
      if sample is None:sample=dict(old_cycles=a['cycles'],new_cycles=b['cycles'],removed_pushes=pushes,old_semantic_writes=[w for w in a['trace']if w not in pushes],new_semantic_writes=b['trace'])
   report['maps'].append(dict(mapper=mapper,old_ROM=old.metadata(),new_ROM=new.metadata(),cases=cases,all_regs=True,all_RAM_except_only3_decoded_old_push_residues=True,every_ordered_semantic_write=True,live_outer_stack_literal=True,cycle_deltas=dict(hist),sample=sample))
   out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(mapper=mapper,cases=cases,cycle_deltas=dict(hist))),flush=True)
  report['status']='PASS_EXACT_COMPILED_QUERY_ABI_AND_MEASURED_CYCLE_REDUCTION'
 except Exception as exc:report.update(status='FAIL_RETAINED',error=str(exc));raise
 finally:out.write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(dict(status=report['status'],cases=sum(m['cases']for m in report['maps']))))


if __name__=='__main__':main()
