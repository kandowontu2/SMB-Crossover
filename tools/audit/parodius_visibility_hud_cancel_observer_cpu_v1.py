"""Source-only actual-CPU qualification of narrowly owned death observation."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_static_startup_v1 import MOCK
from parodius_visibility_menu_hint_observer_cpu_v3 import ObservedArena
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
SHA='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPOSE="""
function DEATH_GUARD_TEST_BEGIN()drawOwner=0;transaction={id=1};bodyPending=nil end
function DEATH_GUARD_TEST_OWNER()return deathRecordOwner end
"""


def runtime(LuaRuntime,script,expose=False):
 rt=LuaRuntime(unpack_returned_tuples=True)
 rt.execute(MOCK+"\nL={}\nMOCK_LOGS={};io.open=function(path,mode)if mode=='rb'then return nil end;MOCK_LOGS[path]=MOCK_LOGS[path]or'';return{write=function(self,x)MOCK_LOGS[path]=MOCK_LOGS[path]..x;return self end,flush=function()end,close=function()end}end")
 for line in script.with_name('candidate.lbl').read_text().splitlines():
  f=line.split()
  if len(f)>=3 and f[0]=='al':rt.globals().L[f[2].lstrip('.')]=int(f[1],16)
 rt.execute(script.read_text()+(EXPOSE if expose else ''))
 assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==0xffff')
 rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
 return rt


class FaultArena(ObservedArena):
 def sync(self):
  super().sync()
  if getattr(self,'fault',None) and not getattr(self,'fault_done',False) and self.cpu.pc==address(self.b,'MetaspriteRenderLoop'):
   self.fault_done=True;self.fault(self)


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['packet','old-profile','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 z=json.loads((a.packet/'death/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256'] and sha(script.with_name('candidate.nes'))==SHA
 cfg=json.loads(script.with_name('config.json').read_text());b=scoped_load(script.with_name('candidate.nes'))
 rows=[];negatives=[];lives=[]
 def setup(v=1,mode=0):
  rt=runtime(LuaRuntime,script,True);rt.globals().PARODIUS_VISIBILITY['variant']=v;rt.globals().PARODIUS_VISIBILITY['mode']=mode
  q=FaultArena(b,rt)
  q.put(SelectedCharacter=18,VvVariant=v,CrossoverBehaviorVersion=mode,VvInitialized=0x76,VvLife=2,VvAlive=1,
        PnInitialized=0x50,NumberofLives=2,OperMode=1,OperMode_Task=3,DisableScreenFlag=0,
        InvHudActive=2*v+1,InvHudPhysical=140,X5HudChrUpper=0x85)
  return rt,q
 try:
  rt=runtime(LuaRuntime,script,True);count=rt.eval('#callbacks')
  for frame in range(1,150):
   rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runread(0);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
  assert rt.eval('#callbacks')==count
  for mode in [0,1]:
   for key,source in cfg['death_sources'].items():
    rt,q=setup(source['variant'],mode);q.invoke('KillPlayer');q.set('PnFrame',source['frame']);q.invoke('VvGraphics')
    owner=rt.globals().DEATH_GUARD_TEST_OWNER();assert owner and owner['key']==key and owner['generation']==rt.globals().PARODIUS_LIFECYCLE_GENERATION()
    q.invoke('DrawAllMetasprites');v,pub,d=q.snapshot()
    assert pub['body']['source']['label']==source['label'] and pub['body']['pointer']==source['pointer']
    assert len(pub['oam'])==256 and len(pub['body']['parts'])>0 and pub['generation']==owner['generation']
    assert pub['body']['source']['physical_chr']==source['physical_chr']
    rows.append(dict(mode=mode,variant=source['variant'],frame=source['frame'],key=key,source=source['label'],
                     generation=int(pub['generation']),phase=pub['phase'],OAM_bytes=256,body_parts=len(pub['body']['parts'])))
  # Original131 records still enter the original byte-equality guard unchanged.
  # This explicitly synthesizes the caller's observation transaction and uses
  # the real generic compiled renderer; it is not a gameplay/caller fixture.
  for key,source in cfg['body_sources'].items():
   rt,q=setup();q.m.page(2,source['bank']);q.set('CurrentBankC',source['bank']|128)
   q.put(R0=source['pointer']&255,R1=source['pointer']>>8,R3=0,R4=96,R5=0,R6=160,R7=1,CurrentOAMOffset=0)
   rt.globals().DEATH_GUARD_TEST_BEGIN();q.invoke('MetaspriteRenderLoop')
   lives.append(dict(key=key,source=source['label'],original_live_source_accepted=True))
  old=json.loads((a.old_profile/'preparation.json').read_text());oldscript=Path(old['script']);assert sha(oldscript)==old['script_sha256']
  rt=runtime(LuaRuntime,oldscript);q=ObservedArena(b,rt)
  q.put(SelectedCharacter=18,VvVariant=1,CrossoverBehaviorVersion=0,VvInitialized=0x76,VvLife=2,VvAlive=1,PnInitialized=0x50,NumberofLives=2,OperMode=1,OperMode_Task=3,DisableScreenFlag=0)
  q.invoke('KillPlayer');q.invoke('VvGraphics')
  try:q.invoke('DrawAllMetasprites')
  except Exception as ex:assert 'Actual body immutable record alias'in str(ex)
  else:raise AssertionError('Old observer no longer rejects real death record')
  negatives.append(dict(case='original-observer-actual-death-path',rejected=True,original_assertion='Actual body immutable record alias',native_failure_not_retagged=True))
  for field,value in [('PnFrame',123),('PnSkin',9),('PnAnimation',88),('SmChrBank',123),('CurrentCHRBank',123),('X5ChrMode',0x81),('MmDeathFlag',0),('VvVariant',2),('SelectedCharacter',17),('ObjectMetasprite',232)]:
   rt,q=setup();q.invoke('KillPlayer');q.invoke('VvGraphics')
   q.fault=lambda q,n=field,v=value:list.__setitem__(q.m,address(b,n),v)
   # Variant/character faults happen exactly at the generic entry, after the
   # authentic body-owner callbacks, so they cannot evade the body assertion.
   try:q.invoke('DrawAllMetasprites')
   except Exception as ex:assert 'Actual body immutable record alias'in str(ex),(field,str(ex))
   else:raise AssertionError(('Invalid death state accepted',field))
   assert q.fault_done
   logs=rt.globals().MOCK_LOGS;path=cfg['output']+'first-body-record-alias-mismatch.json';saved=json.loads(logs[path])
   assert len(saved['record256'])==len(saved['source_OAM256'])==len(saved['hardware_OAM256'])==256
   negatives.append(dict(case='synthetic-boundary-'+field,value=value,rejected=True,preassertion_snapshots=True,source_only_fault=True))
  rt,q=setup();q.invoke('KillPlayer');q.invoke('VvGraphics');rt.globals().PARODIUS_INVALIDATE_PUBLICATION('synthetic-stale-death-owner')
  try:q.invoke('DrawAllMetasprites')
  except Exception as ex:assert 'Actual body immutable record alias'in str(ex)
  else:raise AssertionError('Stale-generation death owner accepted')
  negatives.append(dict(case='stale-generation',rejected=True,source_only_fault=True))
  rt,q=setup();q.invoke('KillPlayer');q.invoke('VvGraphics');ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
  q.fault=lambda q:list.__setitem__(q.m,ptr+1,q.m[ptr+1]^2)
  try:q.invoke('DrawAllMetasprites')
  except Exception as ex:assert 'Exact current body record bytes'in str(ex)
  else:raise AssertionError('Modified immutable death data accepted')
  negatives.append(dict(case='mutated-death-record-byte',rejected=True,original_exact_byte_guard=True,source_only_fault=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(ex),completed=rows,live_completed=lives,negatives=negatives),indent=2)+'\n');raise
 for name,data in [('death-cases',rows),('live-cases',lives),('negatives',negatives)]:
  (a.output/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 out=dict(passed=True,native_run=False,ROM_sha256=SHA,full_compiled_death_draws=len(rows),original_live_guard_controls=len(lives),negative_controls=len(negatives),
          memory_callbacks=count,runtime_registration_attempts=0,inactive_mock_frames=149,full_static_dispatcher_last=True,
          preserved_original_native_failures=True,observer_preparation_sha256=sha(a.packet/'proof.json'),script_sha256=sha(script),tool_sha256=sha(Path(__file__)),
          limits='Isolated actual CPU plus untimed read-only API mock. Explicit synthetic legal states and adversarial boundary faults; no native controller/PPU/IRQ/DMA timing or death/restart pass. Old native failures remain false.',
          files={f.name:sha(f)for f in a.output.glob('*.json')})
 (a.output/'proof.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':main()
