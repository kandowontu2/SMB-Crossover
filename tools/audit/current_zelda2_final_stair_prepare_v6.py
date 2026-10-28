"""Finite full-GameLoop final-stair controller controls; never launches Mesen."""
from argparse import Namespace
from pathlib import Path
import csv,json
from current_roster_compact_11_v1 import ROOT,prepare,sha
from current_zelda2_second_gap_prepare_v5 import ROM,EXPECTED,initial,consume,compiled_map,scoped_load,world

POLICY=ROOT/'tools/playthroughs/current_roster_zelda2_11_v6.lua'
PARENT=ROOT/'build/verification/compact-326942-zelda2-easy-v3'
OUT=ROOT/'build/verification/compact-326942-zelda2-easy-v4'
DIR=ROOT/'build/zelda2_easy_final_stair_v6'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

class Controller:
    """Review mirror of the new local override. Lua VM is not executed."""
    def __init__(self):self.phase='approach'
    def buttons(self,q):
        x,y=world(q),q.get('Player_Y_Position');g=q.get('Player_State')==0;vx=q.get('Player_X_Speed');a=q.get('Z2PreviousButtons')&128
        if self.phase=='approach':
            if g and y<=112:self.phase='runup'
            elif x>=2410 and y<=112:self.phase='brake'
            else:return 1|(128 if(g and not a)or not g else 0)
        if self.phase=='brake':
            if 0<vx<128:return 2
            self.phase='land'
        if self.phase=='land':
            if g:
                if y<=112:self.phase='runup'
                else:self.phase='approach';return 1
            else:return(1 if x<2418 else 0)|(2 if x>2436 else 0)
        if self.phase=='runup':
            if g and x>=2432 and 0<vx<128 and not a:self.phase='cross';return 129
            return 1
        if self.phase=='cross':
            if g and x>=2480:self.phase='done';return 1
            return 129
        return 1

def campaign(b,cols,mode,start,y,poll_updates,old=False):
    q,earned=initial(b,mode,cols,start);q.put(Player_Y_Position=y)
    for col in range(128,160):
        for row,t in enumerate(cols[col]):q.set('Block_Buffer_1',t,col%32//16*208+row*16+col%16)
    ctl=Controller();rows=[];events=[];lastphase='';bits=1;landing=None;launch=None
    for tick in range(310):
        x=world(q);cam=max(2278,x-112)
        q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)
        if tick%poll_updates==0:bits=1 if old else ctl.buttons(q)
        before=dict(x=x,y=q.get('Player_Y_Position'),state=q.get('Player_State'),vx=q.get('Player_X_Speed'),previous=q.get('Z2PreviousButtons'))
        if lastphase!=ctl.phase:events.append(dict(update=tick,phase=ctl.phase,before=before));lastphase=ctl.phase
        q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits);q.invoke('GameLoop');consume(q,b)
        r=dict(update=tick+1,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vx=q.get('Player_X_Speed'),vy=q.get('Player_Y_Speed'),phase=ctl.phase,buttons=bits);rows.append(r)
        assert q.get('GameEngineSubroutine')==8 and q.get('Z2ActiveSpells')==2 and q.get('Z2Mp')==31,rows[-5:]
        if ctl.phase=='cross'and before['state']==0 and r['state']==1 and launch is None:launch=dict(before=before,after=r.copy())
        if launch and r['state']==0 and r['x']>=2480:landing=r.copy();break
    if old:assert len(rows)==310 and all(r['x']==2400 and r['y']==128 and r['state']==0 for r in rows)
    else:assert launch and landing and launch['before']['y']<=112 and not launch['before']['previous']&128,(mode,start,y,poll_updates,events,rows[-8:])
    return dict(mode=mode,typed_initial=dict(x=start,y=y),inputs_per_poll=poll_updates,held_Right_only_old_hop_tail=old,earned=earned,actual_GameLoops=len(rows),phase_changes=events,launch=launch,landing=landing,rows=rows)

def main():
    assert sha(ROM)==EXPECTED and not(OUT/'ready.json').exists()
    b=scoped_load(ROM);cols=compiled_map(b);proof=DIR/'source-controls.json';assert not proof.exists()
    assert cols[151][7]==cols[152][7]==cols[155][7]==97 and cols[153][7]==cols[154][7]==0
    positives=[campaign(b,cols,m,x,y,p)for m in[0,1]for x,y in[(2390,144),(2400,128),(2422,112)]for p in[1,2]]
    negatives=[campaign(b,cols,m,2400,128,1,True)for m in[0,1]]
    r=list(csv.DictReader((PARENT/'trace.csv').open(newline='')))
    final=r[-1];assert(final['x'],final['y'],final['mask'],final['state'])==('2400','128','1','0')
    files=[Path(__file__),POLICY,ROOT/'tools/playthroughs/current_roster_zelda2_11_v1.lua',ROOT/'tools/audit/current_zelda2_second_gap_prepare_v5.py',
        ROOT/'tools/audit/current_darkwing_stairs_prepare_v1.py',ROOT/'tools/audit/current_zelda2_earned_cpu_v1.py',ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),
        ROOT/'src/zelda2_link_motion.s',ROOT/'src/zelda2_native_motion.inc',PARENT/'ready.json',PARENT/'trace.csv',PARENT/'inputs.csv',PARENT/'result.json']
    put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,positive_cases=positives,old_tail_negatives=negatives,
        compiled_parser_stairs={str(c):cols[c]for c in range(148,160)},actual_native_FALSE=final,
        cause='Retained v1 hop has10-poll A window; below-top landingY128 never satisfies its Y<=112 exit and cannot reset held counter. ConstantRight then stalls at the next real step.',
        scope='Typed legal initial position/map/camera, complete GameLoop, physically earned C0 and paid Jump; no native RAM reconstruction. One or two Main calls per controller poll, not actual Lua/PPU/native scheduler proof. Prepared run has only buttons and no emulated writes.',
        bindings={str(p.resolve()):sha(p)for p in files}))
    prepare(Namespace(identity='zelda2',mode='easy',rom=ROM,expected_sha256=EXPECTED,output=OUT,frames=8000,policy=POLICY,replay=None))
    ready=OUT/'ready.json';z=json.loads(ready.read_text());parent=json.loads((PARENT/'ready.json').read_text())
    for k,v in parent['config'].items():
        if k not in['out','prefix','policy']:assert z['config'][k]==v,k
    for p in[Path(__file__),proof]:z['bindings'][str(p.resolve())]=sha(p)
    put(OUT/'command.json',z['command']);z['bindings'][str((OUT/'command.json').resolve())]=sha(OUT/'command.json')
    z['source_controls']=str(proof.resolve());z['original_FALSE_preserved']=str((PARENT/'result.json').resolve());put(ready,z)
    assert all(sha(Path(p))==h for p,h in z['bindings'].items())
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready),ready_sha256=sha(ready),bindings=len(z['bindings']),source_proof=str(proof),source_sha256=sha(proof)),indent=2))

if __name__=='__main__':main()
