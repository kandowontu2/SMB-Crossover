"""Actual frozen high3 loader row bounds, without current integration reads."""
from pathlib import Path
import hashlib,itertools,json,sys,zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from audit_karnov_carrier_closure_1101_v4 import FrozenSources,PACKET,F
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
import check_hogan_current_bounded_v1 as Menu

O=R/'build/karnov-carrier-loader-bounds-1101-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

class Bus(Menu.Bus):
 def __init__(self,b):
  self.pc=0;self.map_writes=[]
  super().__init__(b)
 def __setitem__(self,i,v):
  super().__setitem__(i,v)
  if i==0x512b:self.map_writes.append(dict(pc=self.pc,physical=self.chr_latches[11]))

def invoke(m,name,mapper,index):
 b=m.bundle;pc=address(b,name)
 m[address(b,'SafecallA_SMC')+1]=85
 m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255
 m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
 c=NesMPU(memory=m,pc=address(b,'FarCallCommon'))
 c.a=((location(b,name)-16)//8192)|128;c.x=7;c.y=91;c.p=0x31;c.sp=224;c.stPushWord(0x5aff)
 raw=((location(b,mapper)-16)//8192)|128;at=address(b,mapper);rows=[];lo=c.sp
 for _ in range(1500000):
  if c.pc==0x5b00:break
  m.pc=c.pc;lo=min(lo,c.sp)
  if c.pc==at and m.rawtags[(at-32768)//8192]==raw:rows.append(m[address(b,index)])
  assert m[c.pc]!=0,('Actual loader BRK',name,hex(c.pc),m.rawtags);c.step()
 else:raise AssertionError(('Actual loader bound',name,hex(c.pc),m.rawtags))
 assert c.sp==224
 return dict(success=bool(c.p&1),CPU=c.processorCycles,minimum_SP=lo,mapper_indices=rows,
  PPU_reads=m.ppu_reads,source_write_pages=sorted({q['physical']for q in m.map_writes if at<=q['pc']<at+40}),
  all_mapped_pages=sorted({q['physical']for q in m.map_writes}))

def main():
 O.mkdir(exist_ok=True)
 assert sha(F/'candidate.nes')=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
 with zipfile.ZipFile(PACKET)as z:prior=json.loads(z.read('build/karnov-combat-carrier-design-1101-v3/other-consumer-closure.json'))
 s=FrozenSources(prior);b=scoped_load(F/'candidate.nes')
 workers=[dict(owner='Quick',entry='QwLoad',mapper='QwMapPage',index='QuickManWork_00',raw=9,
   source='current-character-quick-cold-v12/joint/quick/loader.s',domain=list(range(9)),pages=list(range(884,893))),
  dict(owner='FF',entry='FwLoad',mapper='FwMapPage',index='R1',raw=22,
   source='contra-force-p1-coherent-cart-v2/joint/loader.s',domain=list(range(192,224,4)),pages=list(range(893,901))),
  dict(owner='Bowser',entry='BwLoad',mapper='BwMapPage',index='R1',raw=27,
   source='bowser-current64-v3/joint/bowser/copy.s',domain=list(range(192,224,4)),pages=list(range(927,935))),
  dict(owner='BT',entry='BtLoad',mapper='BtMapPage',index='R1',raw=33,
   source='bt-cf-coherent-source-1031-v1/joint/bt/loader.s',domain=list(range(192,224,4)),pages=list(range(919,927))),
  dict(owner='CF',entry='CfLoaderProposal',mapper='CfMapSourcePage',index='R2',raw=31,
   source='contra-force-projectile-contact-1031-v3/joint/cf-loader.s',domain=list(range(24)),pages=list(range(935,959)))]
 def setup(worker,oldwide=0,ctrl=160):
  m=Bus(b)
  Menu.put(m,SelectedCharacter=worker['raw'],FmAlts=32 if worker['owner']=='Quick' else 0,
   FmGroups=0,OperMode=1,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=ctrl,
   NmiDisable=255,FamilyMainCommit=1,ReloadCHRBank=1,X5WideChrActive=oldwide,
   HorizontalScroll=0,VerticalScroll=0)
  m.ppuctrl=ctrl
  for i in range(12):
   m[address(b,'CurrentCHRBank')+i]=100+i if oldwide else i
   m[address(b,'X5ChrMode')+i]=131 if oldwide else 0
  Menu.invoke(m,'X5PublishChr');m.map_writes.clear()
  return m
 result=[]
 for worker in workers:
  source=s.build(worker['source'])
  if worker['owner']=='Quick':
   assert 'sta QuickManWork_00            ; source stream page index0..8'in source
   assert 'cmp #7\n beq QwSecondBank\n cmp #9\n bne QwLoadPage'in source
   assert 'adc #$74'in source
  elif worker['owner']=='CF':
   assert 'inc R2\n lda R2\n cmp #24\n beq CfLoadVerified'in source
   assert 'adc #$a7'in source
  else:
   assert 'cmp #$e0\n bne '+dict(FF='FwLoadPage',Bowser='BwCopyPage',BT='BtLoadPage')[worker['owner']]in source
  cases=[]
  for oldwide,ctrl in itertools.product([0,1],[160,164]):
   m=setup(worker,oldwide,ctrl)
   out=invoke(m,worker['entry'],worker['mapper'],worker['index'])
   assert out['success'],(worker['owner'],out)
   assert out['mapper_indices']==[i for i in worker['domain']for _ in range(2)],(worker['owner'],out)
   assert out['source_write_pages']==worker['pages'],(worker['owner'],out)
   assert not set(out['all_mapped_pages'])&{1019,1020}
   cases.append(dict(old_wide=oldwide,PPUCTRL=ctrl,**out))
  negatives=[]
  for failure in['visible','protection','readback']:
   m=setup(worker,1)
   if failure=='visible':Menu.put(m,Mirror_PPUMASK=24,DisableScreenFlag=0)
   elif failure=='protection':m.protection=[0,0]
   else:m.corrupt_at=(1 if worker['owner']in['Quick','CF'] else 3,0)
   out=invoke(m,worker['entry'],worker['mapper'],worker['index'])
   assert not out['success'],(worker['owner'],failure,out)
   sequence=[i for i in worker['domain']for _ in range(2)]
   assert out['mapper_indices']==sequence[:len(out['mapper_indices'])],(worker['owner'],failure,out)
   assert set(out['source_write_pages'])<=set(worker['pages'])
   assert not set(out['all_mapped_pages'])&{1019,1020}
   if failure=='visible':assert not out['mapper_indices'] and not out['PPU_reads']
   negatives.append(dict(failure=failure,**out))
  result.append(dict(**worker,passed=True,cases=cases,negative_cases=negatives))
 q=dict(passed=True,audit_only=True,carrier_granted=False,source_ROM_sha256=sha(F/'candidate.nes'),
  actual_complete_cold_loader_cases=sum(len(q['cases'])for q in result),negative_cases=sum(len(q['negative_cases'])for q in result),workers=result,sources=s.used,
  limits=['Actual frozen CPU copy/verify paths and admitted loop domains only. This does not close ordinary retained-window/indirect ownership, all Main/ISR paths or final-current integrated image binding.','No live current integration build read or modified. No donor/source dependency tree restored.'],
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/audit_karnov_carrier_closure_1101_v4.py',R/'tools/audit/check_hogan_current_bounded_v1.py',R/'tools/audit/arthur_cache_host_controls_v1.py',R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py',F/'candidate.nes',F/'candidate.dbg',PACKET]})
 save(O/'loader-bounds.json',q)
 print(json.dumps(dict(passed=True,carrier_granted=False,cases=q['actual_complete_cold_loader_cases'],negative_cases=q['negative_cases'],owners=[q['owner']for q in result])))

if __name__=='__main__':main()
