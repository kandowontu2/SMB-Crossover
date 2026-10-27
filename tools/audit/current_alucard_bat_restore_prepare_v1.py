"""Prepare one input-readback fix for Alucard bat restore; no emulator launch."""
from pathlib import Path
from types import SimpleNamespace
import csv,difflib,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_alucard_bat_gap_prepare_v1 import authored_model
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from luigi_mario_profile731_cpu_v1 import full,tick
from mario_luigi731_coefficients_v1 import coord
SHA='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def controls(b):
 rows=[]
 for missed in [0,1,2,3]:
  for fixed in [False,True]:
   q=full(b,0,1);q.put(SelectedCharacter=5,Cv3Variant=3,MarioVariant=0,NumberofLives=2,
     AreaPointer=194,WorldNumber=0,LevelNumber=0,Player_X_Position=2373%256,Player_PageLoc=9,
     Player_Y_Position=144,Player_Y_HighPos=1,Player_State=0,ScreenLeft_PageLoc=9,
     ScreenLeft_X_Pos=0,ScreenRight_PageLoc=9,ScreenRight_X_Pos=255,
     Player_Rel_XPos=69,Player_Pos_ForScroll=69)
   authored_model(q);phase='approach';pending=missed;requested=False;skipped=0;updates=0;history=[];request_rows=[]
   for poll in range(420):
    x,y,bat=coord(q,'X'),q.get('Player_Y_Position'),q.get('Cv3Bat');bits=129 if poll==0 else 1
    if phase=='approach'and x>=2380 and y<=128:phase='release'
    if phase=='release':
     if bat:phase='cross'
     elif not q.get('Cv3Previous')&128 and q.get('Cv3AttackAge')==q.get('Cv3HurtAge')==0 and q.get('Cv3Hearts',2)>0:bits=132
     else:bits=0
    if phase=='cross':
     if bat==1:bits=0
     elif bat==2:
      floor=any(q.get('Block_Buffer_1',((x+8)//256%2)*208+(yy-32)//16*16+(x+8)%256//16)not in [0,0x23,0x26,0xc2,0xc3]for yy in range(max(96,y+40),225,8))
      if x>=2512 and y<=80 and floor:
       bits=0 if q.get('Cv3Previous')&128 else 132
       if bits:phase='restore'if fixed else'land';requested=True
      else:bits=1+(8 if y>64 else 0)+(4 if y<56 else 0)
     else:bits=0
    elif phase=='restore':
     if bat==2:bits=0 if q.get('Cv3Previous')&128 else 132
     else:phase='land';bits=0
    elif phase=='land':bits=0
    run=not(requested and pending>0)
    if not run:pending-=1;skipped+=1;q.set('SavedJoypadBits',bits)
    else:tick(q,bits);updates+=1
    after=dict(poll=poll+1,input=bits,foreground=run,x=coord(q,'X'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),bat=q.get('Cv3Bat'),hearts=q.get('Cv3Hearts',2),phase=phase)
    if not history or after['bat']!=history[-1]:history.append(after['bat'])
    if requested and len(request_rows)<12:request_rows.append(after)
    assert q.get('MmDeathFlag')==q.get('InjuryTimer')==q.get('GuestHurtTicks')==0
    if phase=='land'and after['bat']==0 and after['state']==0:break
   passed=after['bat']==0 and after['state']==0 and after['x']>=2512
   assert skipped==missed
   assert passed==(fixed or missed==0),(fixed,missed,after)
   if passed:assert history==[0,1,2,3,0]and after['hearts']==8
   else:assert after['bat']==2 and after['y']==62 and after['hearts']>0
   rows.append(dict(readback_fix=fixed,deliberately_unconsumed_physical_polls=missed,actual_foreground_calls=updates,physical_polls=poll+1,landed=passed,final=after,actual_bat_transitions=history,restore_request_prefix=request_rows))
 return dict(passed=True,source_CPU_only=True,paired_cases=rows,
    contract='Literal old/new controller state machines over actual full PlayerCtrl/background/CV3 ability calls. On the first restore input,0/1/2/3 physical polls have no foreground call; only input changes, no bat/hearts/velocity/form outcomes forced. Actual Cv3Bat and Cv3Previous readbacks acknowledge consumption. All eight original/new source traces retained in this compact receipt.',
    limits='No actual native NMI/input scheduling, Lua VM, full failed RAM, original level parser, hardware/APU/PPU, campaign clear or cadence inference. Declared finite stair scene/viewport is inherited unchanged from v3 source model.')

def main():
 old=ROOT/'build/verification/compact-next-alucard-9ea-easy-v3';out=ROOT/'build/verification/compact-next-alucard-9ea-easy-v4'
 origin=ROOT/'tools/playthroughs/current_roster_alucard_bat_gap_v2.lua';policy=ROOT/'tools/playthroughs/current_roster_alucard_bat_restore_v3.lua'
 rom=ROOT/'build/bill_early_cache.nes';assert sha(rom)==SHA and not out.exists()and not policy.exists()
 prior=json.loads((old/'ready.json').read_text());failed=json.loads((old/'result.json').read_text())
 assert sha(origin)==prior['bindings'][str(origin)]=='8937aa1e31dd632be07f8828d5ccc3c4a449731048b3a1061e7dd841392b412b'
 assert not failed['passed']and failed['zero_deaths']and failed['frames']==3070 and failed['stationary_watchdog']['consecutive']==300
 trace=list(csv.DictReader((old/'trace.csv').open(newline='')));assert trace[-1]['x']=='2538'and trace[-1]['y']=='62'and trace[-1]['mask']=='0'
 raw=origin.read_text();old_line="if c.r('Cv3Previous')&128==0 then crossing='land';return{down=true,a=true,b=false}end"
 new_line="if c.r('Cv3Previous')&128==0 then crossing='restore';return{down=true,a=true,b=false}end"
 insertion=""" if crossing=='restore'then
  -- A physical input poll can be replaced before a foreground update reads
  -- it. Hold/retry the genuine request until the native bat state changes.
  if bat==2 then
   if c.r('Cv3Previous')&128==0 then return{down=true,a=true,b=false}end
   return{a=false,b=false}
  end
  crossing='land'
 end
"""
 anchor=" if crossing=='land'then\n"
 assert raw.count(old_line)==raw.count(anchor)==1
 text=raw.replace(old_line,new_line).replace(anchor,insertion+anchor,1)
 assert text.replace(insertion,'',1).replace(new_line,old_line)==raw
 assert not re.search(r'\bemu\.(?:write\w*|setState|setInput|loadSavestate|reset)\s*\(',text)and'io.open'not in text
 b=scoped_load(rom);cpu=controls(b)
 policy.write_text(text,newline='\n');prepare(SimpleNamespace(rom=rom,expected_sha256=SHA,output=out,identity='alucard',mode='easy',frames=8000,policy=policy,replay=None))
 put(out/'source-poll-readback-controls.json',cpu)
 (out/'controller.patch').write_text(''.join(difflib.unified_diff(raw.splitlines(True),text.splitlines(True),fromfile=origin.name,tofile=policy.name)),newline='\n')
 receipt=ROOT/'docs/qa/alucard-easy-9ea-v3-stationary-failure-2026-10-27.json'
 put(receipt,dict(status='NATIVE_FALSE_PRESERVED',ROM_sha256=SHA,frame=3070,reason=failed['reason'],zero_deaths=True,route_clear=False,
   actual=dict(final_trace=trace[-1],complete256_DMAs=failed['completed_DMAS'],completed_loops=failed['completed_loops'],whole_PPU_frames=failed['full_frames']),
   cause='Original policy changed to neutral land phase on issuing one physical Down+A request, without waiting for actual Cv3Bat transition. Actual trace crosses the gap but later becomes stationary2538/Y62 with mask0. Bat/previous-A RAM was not logged, so exact native missed consumption remains inferred; the paired actual-CPU source model reproduces lost one-poll requests without altering ability state.',
   correction='Keep restore pending until actual Cv3Bat3/0 readback. While bat2, hold Down+A until consumed; if native previousA is already set, release before the next genuine fresh edge. All flight/landing/scoping, original8000cap, shared assertions and native resource rules unchanged.',
   ledger_fields=dict(identity='alucard',mode=0,ROM_sha256=SHA,outcome='FALSE',frame=3070,zero_death=True,route_clear=False,remaining='Fresh readback-driven controller route, then independent replay.'),
   bindings=[dict(path=str(old/n),sha256=sha(old/n))for n in ['ready.json','result.json','trace.csv','inputs.csv','captures.nesppuv1','captures-index.jsonl']]))
 ready=out/'ready.json';z=json.loads(ready.read_text());z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']='v4 route / owned v3 policy: restore input is pending until actual Cv3Bat3/0; missed physical polls do not prematurely enter neutral landing.'
 for p in [Path(__file__).resolve(),origin,ROOT/'tools/audit/current_alucard_bat_gap_prepare_v1.py',receipt,out/'source-poll-readback-controls.json',out/'controller.patch',ROOT/'src/cv3_core.s',ROOT/'src/cv3_abilities.s',ROOT/'tools/audit/luigi_mario_profile731_cpu_v1.py',ROOT/'tools/audit/mario_luigi731_coefficients_v1.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/robots_weapon_cpu_v1.py']:
  z['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,h in z['bindings'].items():assert sha(p)==h,p
 put(ready,z);assert origin.read_text()==raw
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),receipt=str(receipt))))

if __name__=='__main__':main()
