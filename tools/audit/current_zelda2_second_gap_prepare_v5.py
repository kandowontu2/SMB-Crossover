"""Typed complete-GameLoop second-gap controller controls and one unrun ready.

No Mesen launch, production change, native RAM reconstruction, or physics seed
in the prepared route. Source arenas disclose initial position/map/camera;
Jump is acquired from a real prepared mature actor and paid with Select.
"""
from argparse import Namespace
from pathlib import Path
import csv,json
from current_roster_compact_11_v1 import ROOT,prepare,sha
from current_darkwing_stairs_prepare_v1 import compiled_map
from current_zelda2_earned_cpu_v1 import scene,actor,snapshot
from current_darkwing_arrow_route_source_v1 import world,block
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address

ROM=ROOT/'build/zelda2_easy_glove.nes'
EXPECTED='32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
POLICY=ROOT/'tools/playthroughs/current_roster_zelda2_11_v5.lua'
PARENT=ROOT/'build/verification/compact-326942-zelda2-easy-v2'
OUT=ROOT/'build/verification/compact-326942-zelda2-easy-v3'
PROOF=ROOT/'build/zelda2_easy_route_diagnosis_v1/source-controls.json'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def consume(q,b):
    ptr=address(b,'VRAM_Buffer1')
    q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0)
    q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)

def initial(b,mode,cols,start):
    q=Arena(b,4);q.put(Z2Variant=1,CrossoverBehaviorVersion=mode,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    scene(q);q.array('GameTimerDisplay',[3,9,9])
    end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
    def update(bits=0):
        q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits);q.invoke('GameLoop');consume(q,b)
    for _ in range(4):update()
    assert q.get('Z2LearnedSpells')==0 and q.get('Z2Mp')==127
    scene(q);actor(q,46,112,184,5);q.set('PowerUpType',0,5);q.invoke('Z2PreparePickupGate',x=5)
    assert q.get('InvPickup',5)==192
    for tick in range(100):
        update()
        if not q.get('Enemy_Flag',5) and not q.get('GuestPowerupActive'):break
    else:raise AssertionError('Source mature C0 contact did not finish')
    assert q.get('Z2LearnedSpells')==2 and q.get('Z2Selection')==1
    update(32);update()
    assert q.get('Z2Mp')==31 and q.get('Z2ActiveSpells')==2
    earned=snapshot(q)
    # Disclosed typed scene: cold horizontal velocity after the earned prefix,
    # actual parser cells, no actors. No private movement/resource outcome is set.
    scene(q);q.put(Player_X_Position=start&255,Player_PageLoc=start>>8,MmOldX=start&255)
    return q,earned

def terrain(q,cols):
    x=world(q)
    for page in [x//256,x//256+1]:
        for col in range(page*16,page*16+16):
            for row,t in enumerate(cols[col]):q.set('Block_Buffer_1',t,page%2*208+row*16+col%16)
    cam=max(1200,x-112)
    q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)

class Controller:
    """Exact review mirror of the new local override; Lua/poll lag excluded."""
    def __init__(self):self.phase='land'
    def buttons(self,q):
        x,y=world(q),q.get('Player_Y_Position');ground=q.get('Player_State')==0
        if self.phase=='land':
            if ground and y==176:self.phase='runup'
            else:return 1 if x<1344 else 2
        if self.phase=='runup':
            if ground and y==176 and 1360<=x<=1366 and 0<q.get('Player_X_Speed')<128 and not q.get('Z2PreviousButtons')&128:
                self.phase='cross';return 129
            return 1 if x<=1366 else 2
        if self.phase=='cross':
            if ground and x>=1424:self.phase='done';return 1
            return 129
        return 1

def campaign(b,cols,mode,start,old=False):
    q,earned=initial(b,mode,cols,start);ctl=Controller();rows=[];launch=None;landing=None
    for tick in range(200):
        terrain(q,cols);before=dict(x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vx=q.get('Player_X_Speed'),previous=q.get('Z2PreviousButtons'))
        bits=(129 if tick<35 else 1)if old else ctl.buttons(q)
        q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits);q.invoke('GameLoop');consume(q,b)
        r=dict(update=tick+1,x=world(q),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vx=q.get('Player_X_Speed'),vy=q.get('Player_Y_Speed'),buttons=bits,engine=q.get('GameEngineSubroutine'),phase=ctl.phase)
        rows.append(r)
        if r['engine']==8 and r['y']<240:
            assert q.get('Z2ActiveSpells')==2 and q.get('Z2Mp')==31
        if before['state']==0 and r['state']==1 and r['vy']>=128 and launch is None:launch=dict(before=before,after=r.copy())
        if launch and r['state']==0 and r['x']>=1424:landing=r.copy();break
        if r['y']>=240 or r['engine']!=8:break
    if old:
        assert launch and not landing and rows[-1]['y']>=240,('Early standing launch must fail this real gap',rows[-4:])
    else:
        assert landing and 1360<=launch['before']['x']<=1366 and launch['before']['vx']>0 and not launch['before']['previous']&128,(launch,rows[-6:])
    return dict(mode=mode,initial_x=start,early_standing_launch=old,earned=earned,actual_GameLoops=len(rows),launch=launch,landing=landing,minimum_y=min(r['y']for r in rows),rows=rows)

def sword_stop(b,cols,mode):
    q,_=initial(b,mode,cols,1320)
    for _ in range(30):
        terrain(q,cols);q.put(SavedJoypadBits=1,SavedJoypad1Bits=1);q.invoke('GameLoop');consume(q,b)
    before=dict(x=world(q),vx=q.get('Player_X_Speed'),native_vx=q.get('Z2NativeVX'),state=q.get('Player_State'))
    assert before['vx']==24 and before['state']==0
    q.put(SavedJoypadBits=65,SavedJoypad1Bits=65);q.invoke('GameLoop');consume(q,b)
    after=dict(x=world(q),vx=q.get('Player_X_Speed'),native_vx=q.get('Z2NativeVX'),attack=q.get('Z2AttackStage'))
    assert after['vx']==after['native_vx']==0 and after['attack']>0
    return dict(mode=mode,before=before,after=after)

def main():
    assert sha(ROM)==EXPECTED and not PROOF.exists() and not OUT.exists()
    b=scoped_load(ROM);cols=compiled_map(b)
    assert all(cols[c][11:]==[0,0]for c in range(86,89))
    assert cols[85][11:]==cols[89][11:]==[84,84]
    actual=list(csv.DictReader((PARENT/'trace.csv').open(newline='')))
    r=lambda f:actual[f-1]
    assert(r(2267)['x'],r(2267)['vx'],r(2331)['engine'])==('1329','0','11')
    cases=[campaign(b,cols,m,start)for m in [0,1]for start in [1296,1329,1344]]
    negatives=[campaign(b,cols,m,1329,True)for m in [0,1]]
    stops=[sword_stop(b,cols,m)for m in [0,1]]
    inputs=[ROOT/'tools/audit/current_roster_compact_11_v1.py',ROOT/'tools/audit/current_roster_compact_11_v1.lua',
        Path(__file__),POLICY,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'src/level_tiles.s',
        ROOT/'src/zelda2_link_motion.s',ROOT/'src/zelda2_native_motion.inc',PARENT/'ready.json',PARENT/'trace.csv',PARENT/'inputs.csv',PARENT/'result.json',
        ROOT/'tools/audit/current_darkwing_stairs_prepare_v1.py',ROOT/'tools/audit/current_zelda2_earned_cpu_v1.py',
        ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py']
    put(PROOF,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,
        actual_negative=dict(frame=2331,reason='Zero-death 1-1 route',second_gap=[1376,1424],early_ground_launch=r(2267),death=r(2331)),
        compiled_parser_columns={str(c):cols[c]for c in range(81,93)},positive_cases=cases,standing_early_negatives=negatives,real_ground_sword_stops=stops,
        scope='Typed full GameLoop controls with actual parser cells and physically collected C0/paid Jump. One input per Main; not actual native RAM/poll timing or a native route pass. Prepared route has only controller input, no scene or resource writes.',
        bindings={str(p.resolve()):sha(p)for p in inputs}))
    prepare(Namespace(identity='zelda2',mode='easy',rom=ROM,expected_sha256=EXPECTED,output=OUT,frames=8000,policy=POLICY,replay=None))
    ready=OUT/'ready.json';z=json.loads(ready.read_text());old=json.loads((PARENT/'ready.json').read_text())
    for key in old['config']:
        if key not in ['out','prefix','policy']:assert z['config'][key]==old['config'][key],key
    for p in [Path(__file__),PROOF]:z['bindings'][str(p.resolve())]=sha(p)
    put(OUT/'command.json',z['command']);z['bindings'][str((OUT/'command.json').resolve())]=sha(OUT/'command.json')
    z['source_control']=str(PROOF.resolve());z['preserved_original_FALSE']=str((PARENT/'result.json').resolve());put(ready,z)
    print(json.dumps(dict(ready=str(ready),ready_sha256=sha(ready),source_proof=str(PROOF),source_sha256=sha(PROOF),bindings=len(z['bindings']),native_run=False),indent=2))

if __name__=='__main__':main()
