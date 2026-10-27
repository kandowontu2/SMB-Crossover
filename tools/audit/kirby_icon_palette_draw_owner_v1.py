"""Execute actual compiled Draw callers/RTS to qualify narrow native owner metadata."""
from pathlib import Path
import hashlib,itertools,json
from kirby_icon_palette_controls_v1 import N,NEW,arena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
R=Path(__file__).resolve().parents[2];B=R/'build';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert sha(N)==NEW;out=B/'kirby_world_icon_palette_draw_owner.json';assert not out.exists();b=scoped_load(N)
 cfg=json.loads((B/'current-3d59-kirby-icon-palettes-hard-v1/config.json').read_text());entry=cfg['hooks']['IconDrawEntry'];ret=cfg['hooks']['IconDrawReturn'];rows=[];original=NesMPU.step
 for copy,shot,offset,rotation in itertools.product([2,7,9],[0,2],[4,220,252],[0,32]):
  if shot==2 and copy!=2:continue
  q=arena(b,copy,shot,offset,rotation);scope=None;observed=[]
  def step(c):
   nonlocal scope
   k=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
   if c.pc==entry['pc']and k in entry['banks']:
    assert scope is None
    ptr=q.get('R0')+256*q.get('R1');icon=next((o for o in cfg['palette_icons'].values()if o['pc']==ptr and q.m.banks[(ptr-0x8000)//8192]==o['bank']),None)
    if icon:
     actual_ret=q.m[256+(c.sp+1)%256]+256*q.m[256+(c.sp+2)%256]+1;kind='hud'if actual_ret==cfg['draw_returns']['hud']else'shell'if actual_ret==cfg['draw_returns']['shot']else None
     assert kind and k==cfg['draw_returns']['bank']and icon['family']==copy
     if kind=='shell':assert q.get('KbShotType',q.get('KbSavedSlot'))==3 and q.get('KbShotKind',q.get('KbSavedSlot'))==2
     scope=dict(sp=c.sp,kind=kind,icon=icon,offset=q.get('CurrentOAMOffset'),rotation=rotation,x=q.get('R4'),y=q.get('R6'),return_PC=actual_ret)
   if c.pc==ret['pc']and k in ret['banks']and scope:
    o=scope;scope=None;assert c.sp==o['sp'];length=o['icon']['bytes'][0];after=q.get('CurrentOAMOffset')
    if o['offset']+length>255:assert after==o['offset'];observed.append(dict(kind=o['kind'],rejected=True,SP=c.sp));original(c);return
    assert after==o['offset']+length;parts=[]
    for j in range(length//4):
     at=1+(length//4-1-j)*4;data=o['icon']['bytes'];xoff=data[at+3];yoff=data[at+2];xoff=xoff-256 if xoff>=128 else xoff;yoff=yoff-256 if yoff>=128 else yoff
     slot=(o['offset']+rotation+j*4)&255;want=[o['y']+yoff,data[at],data[at+1]&243,o['x']+xoff];actual=[q.m[512+slot+i]for i in range(4)];assert actual==want and actual[2]&3==1
     parts.append(dict(slot=slot,bytes=actual))
    observed.append(dict(kind=o['kind'],family=copy,return_PC=o['return_PC'],SP=c.sp,parts=parts))
   original(c)
  NesMPU.step=step
  try:q.invoke('KbDrawShots')
  finally:NesMPU.step=original
  assert scope is None and observed
  if offset==4:assert any(x['kind']=='hud'and not x.get('rejected')for x in observed)
  if shot==2 and offset==4:assert any(x['kind']=='shell'and not x.get('rejected')for x in observed)
  rows.append(dict(copy=copy,shot=shot,offset=offset,rotation=rotation,actual_source_scopes=observed))
 # Foreign or unrelated records cannot enter icon scope: only genuine Draw
 # entry+bank and one of three exact ROM pointers is admitted, never a slot ID.
 assert all(x['family']in[2,7,9]and x['bank']==73 for x in cfg['palette_icons'].values())
 z=dict(passed=True,native_run=False,source_CPU_only=True,candidate_sha256=NEW,actual_compiled_Draw_scope_cases=rows,static_callbacks_registered_before_runtime=True,exact_real_entry_return_PC_SP_and_four_callsite_metadata=True,full_OAM_rejection_clears_scope=True,limits='Python executes real compiled callers/renderer and mirrors the explicit narrow Lua owner/readback predicates; not LuaVM or native DMA/PPU proof. No emulated state modified by callbacks. Native adds actual physical OAM/DMA/palette observation and still requires ROOT launch.',bindings={str(p):sha(p)for p in[Path(__file__),N,N.with_suffix('.dbg'),B/'current-3d59-kirby-icon-palettes-hard-v1/config.json',B/'current-3d59-kirby-icon-palettes-hard-v1/fixture.lua',R/'tools/audit/kirby_icon_palette_native_prepare_v1.py']});out.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,cases=len(rows),path=str(out),sha256=sha(out))))
if __name__=='__main__':main()
