"""Finite compiled projectile-HUD/caller/IRQ costs; no native or game writes."""
from pathlib import Path
import hashlib,itertools,json,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from samus_hud_icon_controls_v1 import setup,run,execute

R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 old=scoped_load(B/'smb-crossover-mmc5-expanded.nes');new=scoped_load(B/'samus_projectile_hud.nes');held=scoped_load(B/'samus_hud_icon.nes')
 assert sha(B/'smb-crossover-mmc5-expanded.nes')=='2082c19a7364920f828e97f70040d37f1f7059bde1ea136b5c2c4532324abf36'
 assert sha(B/'samus_projectile_hud.nes')=='4e5cbb99014ef5735b45da3301e6dd6982646ec798fc7e07b15f59b18801f88e'
 rows=[]
 for (char,item,mixed),offset,rot in itertools.product([(2,2,False),(2,2,True),(2,0,False),(2,1,False),(2,3,False),(2,7,False),(3,2,False),(9,1,False)],[0,220,236,244,248],[False,True]):
  qs=[];regs=[];events=[];costs=[];counts=[];leases=[]
  for b in [old,held,new]:
   q=setup(b,char,item,offset,rot,mixed)
   for i in range(64):q.m[512+i*4]=248;q.m[514+i*4]=0
   c,w,e=run(q);regs.append([c.a,c.x,c.y,c.p,c.sp]);events.append(w)
   hud=[(a,v)for a,v,index in w if index==20];ys=[q.m[a]for a,v in hud if(a-512)%4==0]
   q.put(SmFreezeRenderState=1);q.set('AvFrozen',180,0);f,_=q.invoke('SamusFreezeRenderFinish')
   costs.append([c.processorCycles,f.processorCycles,c.processorCycles+f.processorCycles]);counts.append([len(hud),sum(0<=y<239 for y in ys)]);leases.append([q.get('SsChrActive'),q.get('SsChrPhysical')]);qs.append(q)
  foreign=not(char==2 and item==2)
  if foreign:
   assert events[0]==events[2]and regs[0]==regs[2]
   # Existing top64 stack bytes contain dead JSR return slots. Compare all
   # other modeled application RAM, including the live lower stack.
   assert qs[0].m[:0x1c0]==qs[2].m[:0x1c0]and qs[0].m[0x200:0x8000]==qs[2].m[0x200:0x8000]
  rows.append(dict(char=char,item=item,mixed=mixed,offset=offset,rotation=rot,cycles_parent_b403_candidate=costs,HUD_stores_visible_parts=counts,leases=leases,RemainingDraw_AXYP_SP_equal=regs[0]==regs[2],foreign_OAM_RAM_live_stack_exact=foreign,delta_parent=costs[2][2]-costs[0][2],delta_b403=costs[2][2]-costs[1][2],nonHUD_OAM_stores=[sum(i!=20 for a,v,i in e)for e in events]))
 outer=[]
 for char,item,mixed,freeze in [(2,2,False,0),(2,2,False,1),(2,2,True,0),(2,2,True,1),(2,1,False,0),(2,7,False,0),(3,2,False,0),(9,1,False,0)]:
  values=[]
  for b in [old,held,new]:
   q=setup(b,char,item,0,False,mixed);q.put(SmFreezeRenderState=freeze)
   if freeze:q.set('AvFrozen',180,0)
   c,_=q.invoke('SamusFreezeDrawAll');values.append(dict(cycles=c.processorCycles,AXYP_SP=[c.a,c.x,c.y,c.p,c.sp],OAM_offset=q.get('CurrentOAMOffset'),source256=list(q.m[512:768])))
  assert values[0]['AXYP_SP']==values[2]['AXYP_SP'],'Full outer continuation must return genuine caller registers'
  if not(char==2 and item==2):assert values[0]['source256']==values[2]['source256']
  outer.append(dict(char=char,item=item,mixed=mixed,freeze=freeze,cycles=[v['cycles']for v in values],all_outer_AXYP_SP_exact=True,delta_parent=values[2]['cycles']-values[0]['cycles'],delta_b403=values[2]['cycles']-values[1]['cycles']))
 # Reuse the existing actual IRQ-vector runner at every executed helper PC.
 q=setup(new);q.m.page(1,61);q.set('CurrentBank',189);image=list(q.m);banks=q.m.banks[:]
 def fresh():
  m=Memory(new);list.__setitem__(m,slice(None),image);m.banks=banks[:];return m
 m=fresh();c,trace=execute(new,m,'RemainingDraw',record=True)
 keys=sorted({(pc,k)for pc,k in trace if k==61 and 0xbfae<=pc<0xbfba})
 def flat(m):return bytes(m[:256]+m[512:2048]+m[0x6000:0x8000])
 def bus(m):return[w for i,w in enumerate(m.writes)if i not in m.irq_write_indices and not 256<=w[0]<512]
 expected=(c.a,c.x,c.y,c.p&207,c.sp,flat(m),m.banks,bus(m))
 for key in keys:
  m=fresh();c,_=execute(new,m,'RemainingDraw',inject=key)
  assert(c.a,c.x,c.y,c.p&207,c.sp,flat(m),m.banks,bus(m))==expected
 proof=dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(B/'samus_projectile_hud.nes'),compiled_RemainingDraw_frame_scan_cases=len(rows),rows=rows,complete_SamusFreezeDrawAll_cases=outer,IRQ_boundaries=keys,IRQ_scope='Existing hardware-vector runner; AXYP/SP,banks,ordered non-IRQ writes and listed RAM regions. Not all-PPU/NMI proof.',limits='Two-part HUD may fit when old five-part HUD rejected, increasing work at that boundary. Family6/page215 changes mixed actor admission, not world source capsule art. Foreign selected HUDs +19cycles; none-selected +0. Native cadence, actual glyph/first-eight visibility, crowded high jump and full NMI remain unqualified.',bindings={str(p):sha(p)for p in[Path(__file__),B/'samus_projectile_hud.nes',B/'samus_projectile_hud.dbg',B/'samus_projectile_hud_build.json',R/'tools/audit/samus_hud_icon_controls_v1.py',R/'tools/audit/samus_hud_icon_candidate_v1.py']})
 out=B/'samus_projectile_hud_controls.json';assert not out.exists();out.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
 print(json.dumps(dict(passed=True,output=str(out),sha256=sha(out),cases=len(rows),outer=outer,IRQ_cases=len(keys))))

if __name__=='__main__':main()
