"""Finite source-CPU Link Easy last-stair controller correction; no Mesen."""
from pathlib import Path
from argparse import Namespace
import csv, difflib, json
from current_roster_compact_11_v1 import ROOT, prepare, sha
from current_darkwing_stairs_prepare_v1 import compiled_map
from current_darkwing_arrow_route_source_v1 import block, world
from current_link_simon_powerups_prepare_v1 import setup
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address

ROM=ROOT/'build/zelda2_easy_glove.nes'
EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
OLD=ROOT/'tools/playthroughs/link_simon_ryu_policy.lua'
POLICY=ROOT/'tools/playthroughs/current_roster_link_final_stair_v2.lua'
PARENT=ROOT/'build/verification/compact-326942-link-easy-v1'
OUT=ROOT/'build/verification/compact-326942-link-easy-v2'
PROOF=ROOT/'build/current_link_final_stair_v2_source.json'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

OLD_BLOCK=''' if c.world==0 and c.level==0 and c.x>=2390 and c.x<2480 and not outdoorStairReady then
  if c.grounded and c.x>=2430 and c.x<=2437 and c.y<=112 then
   outdoorStairReady=true;holdA=0;cooldown=4;return{right=true}
  end
  return finish({right=c.x<2433,left=c.x>2435,a=c.grounded and c.x<2430 and not c.lastA},c)
 end'''
NEW_BLOCK=''' -- Original Link Easy has gradual airborne braking, not an immediate stop.
 -- Brake before the final support edge, read back a genuine landing, then
 -- run to a fresh ground launch. Other actors/modes retain the old policy.
 if c.char==4 and c.r('Z2Variant')==0 and c.r('CrossoverBehaviorVersion')==0
  and c.world==0 and c.level==0 and c.x>=2390 and c.x<2544
  and c.block(2432,145)==0x61 and c.block(2440,145)==0x61
  and c.block(2456,145)==0 and c.block(2488,145)==0x61 then
  if linkFinalStair=='approach' and c.x>=2418 and c.y<=112 then linkFinalStair='brake' end
  if linkFinalStair=='approach' then return finish({right=true,a=c.grounded and not c.lastA},c) end
  if linkFinalStair=='brake' then
   holdA=0;cooldown=0
   if c.vx>0 and c.vx<128 then return{left=true}end
   linkFinalStair='land'
  end
  if linkFinalStair=='land' then
   holdA=0;cooldown=0
   if c.grounded and c.y<=112 and not c.lastA then linkFinalStair='runup'
   else return{}end
  end
  if linkFinalStair=='runup' then
   holdA=0;cooldown=0
   if c.grounded and c.x>=2432 and not c.lastA then linkFinalStair='cross';return finish({right=true,a=true},c)end
   return{right=true}
  end
  if linkFinalStair=='cross' then
   if c.grounded and c.x>=2480 then linkFinalStair='out' end
   return finish({right=true,a=true},c)
  end
  return{right=true}
 end
'''+OLD_BLOCK

def policy():
    old=OLD.read_text();assert old.count(OLD_BLOCK)==1
    anchor='local outdoorStairReady=false\n';assert old.count(anchor)==1
    text=old.replace(anchor,anchor+"local linkFinalStair='approach'\n").replace(OLD_BLOCK,NEW_BLOCK)
    assert text.replace(anchor+"local linkFinalStair='approach'\n",anchor).replace(NEW_BLOCK,OLD_BLOCK)==old
    if POLICY.exists():assert POLICY.read_text()==text
    else:POLICY.write_text(text,newline='\n')
    return old,text

class Controller:
    """Review mirror, one poll/Main; Lua VM and lag-poll scheduling excluded."""
    def __init__(self,old=False):self.phase='approach';self.hold=0;self.cool=0;self.previous=0;self.old=old;self.ready=False
    def finish(self,bits):
        if self.hold>0:
            bits|=128;self.hold-=1
            if self.hold==0:self.cool=4
        elif self.cool>0:bits&=~128;self.cool-=1
        elif bits&128:self.hold=31
        return bits
    def buttons(self,q):
        x,y=world(q),q.get('Player_Y_Position');ground=q.get('Player_State')==0;vx=q.get('Player_X_Speed');last=self.previous&128
        if self.old and 2390<=x<2480 and not self.ready:
            if ground and 2430<=x<=2437 and y<=112:self.ready=True;self.hold=0;self.cool=4;return 1
            return self.finish((1 if x<2433 else 0)|(2 if x>2435 else 0)|(128 if ground and x<2430 and not last else 0))
        if not self.old and 2390<=x<2544:
            if self.phase=='approach'and x>=2418 and y<=112:self.phase='brake'
            if self.phase=='approach':return self.finish(1|(128 if ground and not last else 0))
            if self.phase=='brake':
                self.hold=self.cool=0
                if 0<vx<128:return 2
                self.phase='land'
            if self.phase=='land':
                self.hold=self.cool=0
                if ground and y<=112 and not last:self.phase='runup'
                else:return 0
            if self.phase=='runup':
                self.hold=self.cool=0
                if ground and x>=2432 and not last:self.phase='cross';return self.finish(129)
                return 1
            if self.phase=='cross':
                if ground and x>=2480:self.phase='out'
                return self.finish(129)
            return 1
        obstacle=any(block(q,x+24,y+dy)not in[0,0x23,0x26,0xc2]for dy in[8,24])
        gap=block(q,x+20,min(y+40,232))in[0,0x23,0x26,0xc2]
        return self.finish(1|(128 if ground and not last and(obstacle or gap)else 0))

def consume_vram(q,b):
    ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0)
    q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)

def campaign(b,cols,old=False,start=2328,earn=False):
    q=Arena(b,4);q.put(Z2Variant=0,CrossoverBehaviorVersion=0,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.invoke('InventoryInit');q.array('GameTimerDisplay',[3,9,9]);earned_prefix=None
    if earn:
        setup(q,4,dict(kind='collect',item=0));growth=0
        for age in range(120):
            growth+=bool(q.get('GuestPowerupActive'))
            q.set('SavedJoypadBits',0);q.invoke('GameLoop');consume_vram(q,b)
            if q.get('PlayerStatus')==1 and q.get('GuestPowerupActive')==0:break
        assert q.get('PlayerStatus')==1 and q.get('GuestPowerupActive')==0 and q.get('Enemy_Flag',5)==0 and growth==60
        assert q.get('InvOwnedLo',4)==q.get('InvOwnedHi',4)==0
        earned_prefix=dict(actual_mature_mushroom_collection=True,GameLoop_calls=age+1,growth_updates=growth,PlayerStatus=1,no_tier_or_resources_seeded=True)
    setup(q,4,dict(kind='idle'))
    q.put(Player_X_Position=start&255,Player_PageLoc=start>>8,MmOldX=start&255,Player_Y_Position=176,WorldNumber=0,LevelNumber=0)
    for col in range(128,160):
        for row,value in enumerate(cols[col]):q.set('Block_Buffer_1',value,(col%32//16)*208+row*16+col%16)
    end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
    ctl=Controller(old);rows=[];transitions=[];previous_phase='';land=None;launch=None
    for tick in range(430):
        x,y=world(q),q.get('Player_Y_Position');oldstate=q.get('Player_State');bits=ctl.buttons(q)
        if ctl.phase!=previous_phase:transitions.append(dict(update=tick,phase=ctl.phase,x=x,y=y,vx=q.get('Player_X_Speed')));previous_phase=ctl.phase
        if ctl.phase=='runup' and land is None:land=dict(update=tick,x=x,y=y,vx=q.get('Player_X_Speed'))
        cam=max(2208,x-112);q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)
        prelaunch=dict(update=tick,x=x,y=y,state=oldstate,previous=ctl.previous,vx=q.get('Player_X_Speed'))
        q.set('SavedJoypadBits',bits);q.invoke('GameLoop');ctl.previous=bits
        row=dict(update=tick,phase=ctl.phase,buttons=bits,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vx=q.get('Player_X_Speed'),vy=q.get('Player_Y_Speed'),power=q.get('PlayerStatus'),engine=q.get('GameEngineSubroutine'));rows.append(row)
        if ctl.phase=='cross'and oldstate==0 and row['state']==1 and row['vy']>=128 and launch is None:launch=dict(before=prelaunch,after=dict(row))
        consume_vram(q,b)
        if row['engine']!=8 or q.get('MmDeathFlag') or row['y']>=240:break
        if row['x']>=2544 and row['state']==0:break
    passed=rows[-1]['x']>=2544 and rows[-1]['state']==0 and rows[-1]['engine']==8 and q.get('MmDeathFlag')==0
    return dict(passed=passed,original_policy=old,start_x=start,earned_prefix=earned_prefix,GameLoop_calls=len(rows),landing=land,fresh_launch=launch,transitions=transitions,terminal=rows[-1],rows=rows)

def main():
    assert sha(ROM)==EXPECTED and not PROOF.exists()
    old,text=policy();b=scoped_load(ROM);cols=compiled_map(b)
    sources=[campaign(b,cols,False,start)for start in[2320,2328]]+[campaign(b,cols,False,2328,True)]
    oldcase=campaign(b,cols,True)
    proof=dict(passed=all(x['passed']for x in sources),native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,source_cases=sources,source_original_control=oldcase,
        terrain_columns={str(c):cols[c]for c in range(149,157)},
        limits='Actual complete compiled GameLoop and parser-authored1-1 cells; typed player2320/2328,Y176 and empty enemy stream, then buttons only apart from following camera and servicing actual VRAM consumer. Two coldSmall cases and one actual mature mushroom/60-growth earned tier1 case; no acquired state seeds. Review-mirror source polling is not a reconstruction of unlogged native private fractions, a real NMI/PPU, Lua VM execution or physical-poll replay. The original-controller typed source control crosses; it does not reproduce the native failing phase and is not presented as a failure reproduction.',
        bindings={str(p):sha(p)for p in[Path(__file__),POLICY,OLD,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),PARENT/'ready.json',PARENT/'trace.csv',PARENT/'inputs.csv',PARENT/'result.json',ROOT/'src/roster.s',ROOT/'tools/audit/current_darkwing_stairs_prepare_v1.py',ROOT/'tools/audit/current_darkwing_arrow_route_source_v1.py',ROOT/'tools/audit/current_link_simon_powerups_prepare_v1.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py',ROOT/'build/current_link_final_stair_v2_first-oracle-negative.json']})
    if not proof['passed']:
        put(ROOT/'build/current_link_final_stair_v2_trial-negative.json',proof)
        raise AssertionError([(x['start_x'],x['terminal'],x['transitions'])for x in sources])
    assert all(x['landing']and x['fresh_launch']and x['landing']['y']==x['fresh_launch']['before']['y']==112 and x['fresh_launch']['before']['state']==0 and not x['fresh_launch']['before']['previous']&128 for x in sources)
    trace=list(csv.DictReader((PARENT/'trace.csv').open()));at=lambda f:next(r for r in trace if int(r['frame'])==f)
    proof['original_native_FALSE']=dict(result_sha256=sha(PARENT/'result.json'),brake_start=at(4301),horizontal_stop=at(4318),terminal=at(4347),cause='Late airborne brake above final support/gap, not a proven collision/physics defect.')
    put(PROOF,proof)
    patch=ROOT/'build/current_link_final_stair_v2_policy.patch';patch.write_text(''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile=str(OLD),tofile=str(POLICY))),newline='\n')
    prepare(Namespace(identity='link',mode='easy',rom=ROM,expected_sha256=EXPECTED,output=OUT,frames=8000,policy=POLICY,replay=None))
    rp=OUT/'ready.json';z=json.loads(rp.read_text());cmd=OUT/'command.json';put(cmd,z['command'])
    for p in[Path(__file__),PROOF,patch,PARENT/'result.json',PARENT/'trace.csv',PARENT/'inputs.csv',cmd]:z['bindings'][str(p.resolve())]=sha(p)
    z.update(native_run=False,input_only=True,source_proof=dict(path=str(PROOF),sha256=sha(PROOF)),original_v1_FALSE_preserved=True,scope='Original Link Easy only: earlier airborne brake, genuine native last-top landing and fresh ground runup/jump. All old route/hardware/zero-death/finite caps unchanged; source CPU cases are not a native clear.')
    put(rp,z);assert all(sha(Path(p))==h for p,h in z['bindings'].items())
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(rp),sha256=sha(rp),bindings=len(z['bindings']),command=str(cmd),source=str(PROOF),source_sha256=sha(PROOF),calls=[x['GameLoop_calls']for x in sources],original_source_control=oldcase['passed'])))

if __name__=='__main__':main()
