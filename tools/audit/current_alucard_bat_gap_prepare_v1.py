"""Prepare one source-qualified AlucardEasy native bat-gap controller; no launch."""
from pathlib import Path
from types import SimpleNamespace
import csv,hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from luigi_mario_profile731_cpu_v1 import full,tick
from mario_luigi731_coefficients_v1 import coord
from check_tmnt_render_oa import address,location
SHA='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def authored_model(q):
    # Explicit finite scene model, not a recovered native full-RAM snapshot.
    # Actual trace supplies launch2373/Y144; actual2594 image supplies the
    # near/far stairs and32px gap2448..2479. Native route rechecks live map.
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for wx in range(2304,2816,16):
        top=208
        if 2352<=wx<2368:top=192
        elif 2368<=wx<2384:top=176
        elif 2384<=wx<2400:top=160
        elif 2400<=wx<2448:top=144
        elif 2448<=wx<2480:continue
        elif 2480<=wx<2496:top=144
        elif 2496<=wx<2512:top=160
        elif 2512<=wx<2528:top=176
        elif 2528<=wx<2544:top=192
        for y in range(top,240,16):q.set('Block_Buffer_1',0x54,(wx//256%2)*208+(y-32)//16*16+(wx%256)//16)

def controls(b):
    rows=[]
    for launch,attack in [(x,a)for x in (2371,2373,2375)for a in (False,True)]:
        q=full(b,0,1);q.put(SelectedCharacter=5,Cv3Variant=3,MarioVariant=0,
            NumberofLives=2,AreaPointer=194,WorldNumber=0,LevelNumber=0,
            Player_X_Position=launch%256,Player_PageLoc=launch//256,
            Player_Y_Position=144,Player_Y_HighPos=1,Player_State=0,
            ScreenLeft_PageLoc=9,ScreenLeft_X_Pos=0,
            ScreenRight_PageLoc=9,ScreenRight_X_Pos=255,
            Player_Rel_XPos=launch-2304,Player_Pos_ForScroll=launch-2304)
        authored_model(q);phase='approach';path=[];entry_hearts=None;flight_hearts=[];seen=[]
        if attack:
            tick(q,64);q.invoke('Cv3WeaponsGate')
            assert q.get('Cv3AttackAge')>0
        initial_attack_age=q.get('Cv3AttackAge')
        for age in range(420):
            x=coord(q,'X');y=q.get('Player_Y_Position');bat=q.get('Cv3Bat')
            bits=129 if age==0 else 1
            if phase=='approach'and x>=2380 and y<=128:phase='release'
            if phase=='release':
                if bat:phase='cross'
                elif q.get('Cv3Previous')&128==0 and q.get('Cv3AttackAge')==q.get('Cv3HurtAge')==0 and q.get('Cv3Hearts',2)>0:
                    bits=132;entry_hearts=q.get('Cv3Hearts',2)
                else:bits=0
            if phase=='cross':
                if bat==1:bits=0
                elif bat==2:
                    floor=any(q.get('Block_Buffer_1',((x+8)//256%2)*208+(yy-32)//16*16+((x+8)%256)//16)not in [0,0x23,0x26,0xc2,0xc3] for yy in range(max(96,y+40),225,8))
                    if x>=2512 and y<=80 and floor:
                        bits=132 if q.get('Cv3Previous')&128==0 else 0
                        if bits:phase='land'
                    else:bits=1+(8 if y>64 else 0)+(4 if y<56 else 0)
                else:bits=0
            elif phase=='land':bits=0
            tick(q,bits)
            state=dict(update=age+1,input=bits,x=coord(q,'X'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),bat=q.get('Cv3Bat'),hearts=q.get('Cv3Hearts',2),airVX=q.get('Cv3AirVX'),phase=phase)
            path.append(state)
            if not seen or state['bat']!=seen[-1]:seen.append(state['bat'])
            if state['bat']==2:flight_hearts.append(state['hearts'])
            assert q.get('MmDeathFlag')==q.get('InjuryTimer')==q.get('GuestHurtTicks')==0
            if phase=='land'and state['bat']==0 and state['state']==0:break
        assert seen==[0,1,2,3,0],(launch,seen,path[-1])
        assert entry_hearts==10 and flight_hearts and min(flight_hearts)>0
        assert 2512<=path[-1]['x']<2544 and path[-1]['y']<=160 and path[-1]['state']==0,(launch,path[-1])
        rows.append(dict(launch_x=launch,actual_B_attack_before_jump=attack,actual_initial_attack_age=initial_attack_age,actual_Ensure_initialized_hearts=entry_hearts,
                         frames=age+1,bat_states=seen,minimum_flight_hearts=min(flight_hearts),
                         actual_final=path[-1],path=path))
    # Original fixed-air caller: source owns velocity; neither Left nor
    # neutral nor releasing A can brake a rightward committed Alucard jump.
    locked=[]
    for bits in [0,2,128,130]:
        q=full(b,0,1);q.put(SelectedCharacter=5,Cv3Variant=3,MarioVariant=0)
        tick(q,129)
        x=coord(q,'X');tick(q,bits)
        assert coord(q,'X')-x==2 and q.get('Cv3AirVX')==1
        locked.append(dict(input=bits,deltaX=2,source_Cv3AirVX=1))
    scope=dict(name='alucard',mode=0,char=5,variant=3,world=0,level=0,area=1,x=2380)
    def admitted(s):return s['name']=='alucard'and s['mode']==0 and s['char']==5 and s['variant']==3 and s['world']==s['level']==0 and s['area']==1 and 2336<=s['x']<2592
    negative=[]
    for key,value in [('name','simon'),('mode',1),('char',4),('variant',0),('world',1),('level',1),('area',0),('x',2335),('x',2592)]:
        assert not admitted(scope|{key:value});negative.append(dict(change={key:value},admitted=False))
    assert admitted(scope)
    return dict(passed=True,actual_full_PlayerCtrl=True,cases=rows,fixed_air_controls=locked,foreign_scope_negatives=negative,
        model='Literal controller translation over a disclosed finite stair/gap scene using actual current PlayerCtrl/background/CV3 ability/import/export calls. Cv3Ensure initializes10 hearts; no heart/bat/velocity/form/timer/outcome seeds after initialization.',
        limits='Not Lua execution, exact failed RAM, full level parser, native hardware/audio/cadence, dynamic enemies or campaign proof. Native controller queries genuine far support/head clearance; source model stair coordinates beyond exact trace launch and visible gap are declared geometry, not claimed recovered NT bytes. Model viewport2304..2559 intentionally covers both stairs; it is not the failed native camera2259.',
        retained_draft_negatives=['Initial240/420-update model could not passX2498 because its static ScrollLock viewport ended2511; extending duration alone correctly did not repair that fixture clamp. Source model viewport now covers the complete crossing; native controller does not write/lock camera.', 'The first successful205-update model was rejected by a unique-state accumulator expecting a repeated final0. Corrected to consecutive transition history0→1→2→3→0; original assertion retained in this note, no gameplay changed.'])

def main():
    rom=ROOT/'build/bill_early_cache.nes';assert sha(rom)==SHA
    draft=ROOT/'build/alucard-stair-source-v1';draft.mkdir(exist_ok=True)
    b=scoped_load(rom);cpu=controls(b);put(draft/'source-controls.json',cpu)
    if '--source-only'in sys.argv:print(json.dumps(dict(passed=True,cases=len(cpu['cases']),output=str(draft))));return
    out=ROOT/'build/verification/compact-next-alucard-9ea-easy-v3'
    assert not out.exists()
    old=ROOT/'build/verification/compact-next-alucard-9ea-easy-v2'
    prior=json.loads((old/'ready.json').read_text());result=json.loads((old/'result.json').read_text())
    assert prior['ROM_sha256']==result['ROM_sha256']==SHA and not result['passed']and result['frames']==2629
    trace=list(csv.DictReader((old/'trace.csv').open(newline='')))
    continued=[z for z in trace if 2594<=int(z['frame'])<=2621]
    assert continued[0]['x']=='2411'and continued[-1]['x']=='2465'and all(z['vx']=='32'for z in continued)
    policy=ROOT/'tools/playthroughs/current_roster_alucard_bat_gap_v2.lua'
    text=policy.read_text();assert not re.search(r'emu\.(?:write\w*|setState|setInput|loadSavestate|reset)\s*\(',text)and'io.open'not in text
    prepare(SimpleNamespace(rom=rom,expected_sha256=SHA,output=out,identity='alucard',mode='easy',frames=8000,policy=policy,replay=None))
    receipt=ROOT/'docs/qa/alucard-easy-9ea-stair-controller-failures-2026-10-27.json'
    first=ROOT/'build/verification/compact-next-alucard-9ea-easy-v1';v1=json.loads((first/'result.json').read_text());v1trace=list(csv.DictReader((first/'trace.csv').open(newline='')))
    assert not v1['passed']and v1['ROM_sha256']==SHA and v1['frames']==2667
    put(receipt,dict(status='NATIVE_FALSES_PRESERVED',ROM_sha256=SHA,v1=dict(frame=2667,final_trace=v1trace[-1],reason=v1['reason']),
        v2=dict(frame=2629,final_trace=trace[-1],reason=result['reason'],countersteer_input_masks=sorted({int(z['mask'])for z in continued}),
                actual='X2411→2465 continues+2/update after Right/A release and later Left. Near-stair top is passed before descendingY112; fixed source air velocity makes the Roll landing maneuver ineffective.'),
        source='Cv3StartJump stores direction in Cv3AirVX; FixedAir reuses it until landing. Alucard bat is Down+freshA, not Select; Cv3AttackAge/HurtAge must be0 and actual hearts>0. Cold source Ensure initializes10; actual2594 HUD also displays HEART10. Native transform takes36 updates each way, flight drains1 heart per60 updates.',
        selected_image=dict(path=str(draft/'actual2594.png'),sha256=sha(draft/'actual2594.png'),ppu_frame=2594,scope='One decoded original whole PPU frame, not a new native capture or whole-container review. Near stair,32px gap and far descending stair visible; exact hidden RAM/NT not recovered.'),
        ledger_fields=dict(identity='alucard',mode=0,ROM_sha256=SHA,outcome='FALSE',frame=2629,route_clear=False,remaining='New source-qualified native bat-gap controller clear and independent replay; no ROM defect demonstrated.'),
        external_evidence=[dict(path=str(d/n),sha256=sha(d/n))for d in [first,old]for n in ['ready.json','result.json','trace.csv','inputs.csv','captures.nesppuv1','captures-index.jsonl']]))
    ready=out/'ready.json';z=json.loads(ready.read_text());put(out/'source-controller-controls.json',cpu)
    review=dict(PREPARED_DO_NOT_RUN=True,native_run=False,controller_only=True,scope='AlucardEasy/world0level0/outdoor2336<=X<2592 only; early B suppression, actual Cv3Previous/attack/hurt/hearts/bat readbacks and live map support/clearance; no writes or cap changes.',
        change='Release A once; native Down+freshA enters bat above near stair. Fly right at source acceleration while maintainingY56..64. AtX>=2512 with actual far support/head clearance, native Down+freshA restores human; neutral until real landing, then unchanged base controller resumes.',
        source_limits=cpu['limits'],original_failures_preserved=True,actual_art_ability_cost_cadence_clear_replay_unproved=True)
    put(out/'controller-review.json',review)
    paths=[Path(__file__).resolve(),receipt,out/'source-controller-controls.json',out/'controller-review.json',draft/'actual2594.png']
    paths += [ROOT/'src'/n for n in ['cv3_core.s','cv3_abilities.s','cv3_combat.s','cv3_pickups.s','cv3_remaining_source_fx.s']]
    paths += [ROOT/'tools/audit'/n for n in ['luigi_mario_profile731_cpu_v1.py','mario_luigi731_coefficients_v1.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','robots_weapon_cpu_v1.py']]
    for p in paths:z['bindings'][str(p)]=sha(p)
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
    for p,h in z['bindings'].items():assert sha(p)==h,p
    z['PREPARED_DO_NOT_RUN']=True;z['controller_revision']=review;put(ready,z)
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),receipt=str(receipt))))

if __name__=='__main__':main()
