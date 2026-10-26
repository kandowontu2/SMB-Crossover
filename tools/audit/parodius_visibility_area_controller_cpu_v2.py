"""Source-only natural-button policy feasibility through compiled native motion/contact."""
from pathlib import Path
import argparse,hashlib,json,sys
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ROOT=Path(__file__).resolve().parents[2]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'


def plain(v):
 if hasattr(v,'items'):return {str(k):plain(x)for k,x in v.items()}
 return v


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rom=a.candidate/'candidate.nes';assert sha(rom)==SHA
 sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 b=scoped_load(rom);policy=ROOT/'tools/audit/parodius_visibility_area_controller_v2.lua';outcomes=[];synthetic=[];contacts=[]
 def setup(x,y,screen=112,fx=0):
  q=Arena(b,18);camera=x-screen;sx=screen+8;sy=y-24
  q.put(SelectedCharacter=18,CrossoverBehaviorVersion=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
        VvVariant=1,VvInitialized=0x76,VvLife=2,VvAlive=1,NumberofLives=2,VvNeedEntry=0,VvSpeed=0,
        PnInitialized=0x50,PnType=1,PnActive=128,PnDrawFlags=1,PnSkin=1,PnX=sx,PnY=sy,PnXF=fx,PnYF=0,
        VvObjX=sx,VvObjY=sy,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,
        ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,ScrollLock=0)
  q.array('Block_Buffer_1',[0]*416)
  for wx,v in [(912,0x10),(928,0x11)]:q.set('Block_Buffer_1',v,(wx//256%2)*208+((144-32)//16)*16+(wx%256)//16)
  return q
 def block(q,wx,yy):
  if yy<32 or yy>=240:return 0
  return q.get('Block_Buffer_1',(int(wx)//256%2)*208+((int(yy)-32)//16)*16+(int(wx)%256)//16)
 try:
  # Exact geometry remains measured on this actual composition, not inherited
  # from a historical ROM label. This is an isolated two-cell source arena.
  for y in [135,136,143,151,152]:
   for x in range(912,937):
    for buttons in [0,4]:
     q=setup(x,y);q.put(SavedJoypadBits=buttons,Up_Down_Buttons=buttons&12)
     q.invoke('VvMovement::MotionReady');entered=q.get('GameEngineSubroutine')==3
     assert entered==(917<=x<=922 and 136<=y<=151 and buttons==4),(x,y,buttons,entered)
     contacts.append(dict(x=x,y=y,buttons=buttons,entered=entered))
  for start_x in [700,780,800]:
   for screen in [80,112,160]:
    for start_y in [88,104,135]:
     for fraction in [0,255]:
      q=setup(start_x,start_y,screen,fraction);rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(policy.read_text());events=[]
      choose=rt.globals().PARODIUS_AREA_CONTROLLER_FACTORY(lambda kind,info:events.append(dict(kind=kind,details=plain(info))))
      sequence=[]
      for tick in range(500):
       x=q.get('Player_X_Position')+256*q.get('Player_PageLoc');camera=q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc');y=q.get('Player_Y_Position')
       c=rt.table_from(dict(x=x,y=y,camera=camera,engine=q.get('GameEngineSubroutine'),poll=tick,block=lambda wx,yy:block(q,wx,yy)))
       buttons=choose(c,'initial','initial');buttons=plain(buttons)
       assert not(buttons.get('left')and buttons.get('right'))and not(buttons.get('up')and buttons.get('down'))
       mask=sum(v for k,v in [('a',128),('up',8),('down',4),('left',2),('right',1)]if buttons.get(k))
       q.put(SavedJoypadBits=mask,Up_Down_Buttons=mask&12)
       q.invoke('VvMovement');entered=q.get('GameEngineSubroutine')==3
       after=q.get('Player_X_Position')+256*q.get('Player_PageLoc');ay=q.get('Player_Y_Position')
       sequence.append(dict(tick=tick,x=after,y=ay,camera=camera,buttons=mask,engine=q.get('GameEngineSubroutine')))
       assert not q.get('MmDeathFlag'),('Policy hit native fatal terrain',start_x,screen,start_y,fraction,sequence[-8:],events)
       if entered:break
       q.invoke('VvScrollGate')
      else:raise AssertionError(('No real compiled pipe entry',start_x,screen,start_y,fraction,sequence[-8:],events))
      assert 917<=after<=922 and 136<=ay<=151 and q.get('ChangeAreaTimer')==48
      outcomes.append(dict(start_x=start_x,start_y=start_y,start_screen=screen,start_fraction=fraction,updates=len(sequence),
                           final_x=after,final_y=ay,actual_engine=3,events=events,sequence=sequence,
                           isolated_world=True,real_area_loader_not_executed=True))
  # Controller state negatives: discard an unrecoverable target, do not chase
  # the old failed target, and change policy only after actual loader identity.
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(policy.read_text());events=[]
  choose=rt.globals().PARODIUS_AREA_CONTROLLER_FACTORY(lambda k,v:events.append(dict(kind=k,details=plain(v))))
  def context(x,y,camera,engine=8):return rt.table_from(dict(x=x,y=y,camera=camera,engine=engine,poll=0,block=lambda wx,yy:0x10 if(wx,yy)==(912,144)else 0x11 if(wx,yy)==(928,144)else 0))
  choose(context(800,104,688),'initial','initial');choose(context(925,104,813),'initial','initial')
  assert any(e['kind']=='natural-pipe-target-passed'for e in events)
  synthetic.append(dict(case='target-passed-between-controller-observations',discarded=True,events=events))
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(policy.read_text());events=[]
  choose=rt.globals().PARODIUS_AREA_CONTROLLER_FACTORY(lambda k,v:events.append(dict(kind=k,details=plain(v))))
  choose(context(925,104,688),'initial','initial');assert any(e['kind']=='natural-pipe-already-passed'for e in events)
  assert not any(e['kind']=='natural-enterable-pipe-found'for e in events)
  synthetic.append(dict(case='historical925-104-screen237',passed_target_not_selected=True,events=events))
  assert plain(choose(context(920,136,808,3),'initial','initial'))=={}
  synthetic.append(dict(case='native-pipe-engine3',ordinary_buttons={},no_controller_outcome_write=True))
  result=plain(choose(context(40,136,0),'initial','actual-new-area'))
  assert result.get('right')and result.get('up')and not result.get('down')
  synthetic.append(dict(case='actual-loaded-area-identity-change',buttons=result,does_not_retarget_initial_pipe=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),outcomes=outcomes,contacts=contacts,synthetic=synthetic),indent=2)+'\n');raise
 for name,data in [('contact-cases',contacts),('motion-cases',outcomes),('controller-state-cases',synthetic)]:
  (a.output/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 old=(ROOT/'tools/audit/parodius_visibility_hud_transition_v1.lua').read_text();new=(ROOT/'tools/audit/parodius_visibility_hud_transition_v2.lua').read_text()
 start=old.index('local target=nil\n');end=old.index('\nemu.addEventCallback(function()\n ticks=',start)
 ns=new.index('local areaController=');ne=new.index('\nemu.addEventCallback(function()\n ticks=',ns)
 assert old[:start]==new[:ns]and old[end:]==new[ne:]
 q=dict(passed=True,native_run=False,ROM_sha256=SHA,compiled_contact_cases=len(contacts),actual_native_motion_pipe_cases=len(outcomes),
        compiled_motion_updates=sum(x['updates']for x in outcomes),controller_state_cases=len(synthetic),
        exact_entry_playerX=[917,922],exact_entry_playerY=[136,151],all_original_lifecycle_hook_and_terminal_guard_bodies_exact=True,
        no_area_loader_Buffer2_or_native_replay_claim=True,tool_sha256=sha(Path(__file__)),
        bindings={str(f.resolve()):sha(f)for f in [rom,rom.with_suffix('.dbg'),policy,ROOT/'tools/audit/parodius_visibility_hud_transition_v1.lua',ROOT/'tools/audit/parodius_visibility_hud_transition_v2.lua']},
        files={f.name:sha(f)for f in a.output.glob('*.json')},
        limits='Source-only actual CPU with explicitly isolated empty world/two native pipe cells and legal source actor setup. Controller emits only ordinary buttons. Production motion/contact owners reach real engine3/ChangeAreaTimer48; this is not natural area reachability, physical PPU/NMI/DMA timing, area loader or pendingBuffer2catch-up qualification. A separately granted native run must still fail if those coverage assertions are not met.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
