"""Freeze the real6be contact cause and prepare ONE controller-only9ea route."""
from pathlib import Path
from types import SimpleNamespace
import csv,hashlib,json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from luigi_mario_profile731_cpu_v1 import full,tick
from mario_luigi731_coefficients_v1 import seed_vx,coord

OLD='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
NEW='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def scope_controls():
 base=dict(name='luigi',mode=0,char=8,variant=1,world=0,level=0,area=1,yhigh=1,ground=False,vy=5,y=125,id=6,state=0,ey=184,dx=43,slot=1,flag=1,bbox=9,corridor=True)
 def admit(s):
  return s['name']=='luigi'and s['mode']==0 and s['char']==8 and s['variant']==1 and s['world']==s['level']==0 and s['area']==s['yhigh']==1 and not s['ground']and 0<s['vy']<128 and s['id']==6 and s['state']<2 and s['ey']==184 and 20<s['dx']<100 and s['y']>=104 and s['y']+32<198 and s['slot']in range(6)and 0<s['flag']<128 and s['bbox']==9 and s['corridor']
 rows=[dict(changes={},expected=True,literal_result=admit(base))];assert admit(base)
 for k,v in [('name','mario'),('mode',1),('char',0),('variant',0),('world',1),('level',1),('area',2),('yhigh',0),('ground',True),('vy',0),('vy',252),('id',13),('state',2),('ey',168),('dx',20),('dx',100),('y',103),('y',166),('slot',6),('flag',0),('flag',128),('bbox',0),('corridor',False)]:
  actual=admit({**base,k:v});assert not actual;rows.append(dict(changes={k:v},expected=False,literal_result=actual))
 return dict(scope='Literal read-only scope model, not executed Lua',cases=rows)

def cpu_controls(b):
 rows=[]
 bbox=location(b,'BoundBoxCtrlData');assert list(b['raw'][bbox+4:bbox+8])==[3,20,13,32]
 assert list(b['raw'][bbox+36:bbox+40])==[3,14,13,20]
 for fraction in [0,65535]:
  for enemy_fraction in [0,255]:
   pair=[]
   for corrected in [False,True]:
    q=full(b,0,0)
    q.put(MarioSourceActive=1,Player_X_Position=132,Player_PageLoc=7,Player_Y_Position=110,Player_Y_HighPos=1,
          Player_State=1,Player_Y_Speed=5,PlayerSize=1,Player_Y_MoveForce=0,VerticalForce=112,VerticalForceDown=112,
          ScreenLeft_PageLoc=7,ScreenLeft_X_Pos=1,ScreenRight_PageLoc=8,ScreenRight_X_Pos=0,Player_Rel_XPos=131,Player_Pos_ForScroll=131)
    q.array('MmVY',[0,0,5]);seed_vx(q,0,2.5);q.array('MmXFraction',[fraction&255,fraction>>8])
    q.invoke('InitGoomba')
    q.put(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_Y_HighPos=1,Enemy_Y_Position=184,
          Enemy_X_Position=183,Enemy_PageLoc=7,ObjectOffset=0,Enemy_X_MoveForce=enemy_fraction)
    braking=0;land=None;launched=False;path=[]
    for age in range(35):
     x=coord(q,'X');y=q.get('Player_Y_Position');ex=q.get('Enemy_X_Position')+256*q.get('Enemy_PageLoc');dx=ex-x;g=q.get('Player_State')==0
     # Literal active descent branch; this legal model has a clear supported lane.
     brake=corrected and 20<dx<100 and not g and 0<q.get('Player_Y_Speed')<128 and y>=104 and y+32<198
     if brake:bits=2;braking+=1
     elif land is not None:
      # Exact ordinary flat-lane base trigger: fresh A when grounded enemy<45.
      bits=65+(128 if g and 0<dx<45 else 0)
     else:bits=65
     tick(q,bits);q.set('ObjectOffset',0);q.invoke('MoveNormalEnemy')
     s=dict(update=age+1,x=coord(q,'X'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),enemy_x=q.get('Enemy_X_Position')+256*q.get('Enemy_PageLoc'),input=bits)
     path.append(s)
     if land is None and s['state']==0:
      land=s.copy();land['gap']=s['enemy_x']-s['x']
      if not corrected:break
     elif land is not None and s['state']!=0 and bits&128:
      launched=True;break
    assert land is not None
    if corrected:assert land['gap']>10 and launched and braking>0,(fraction,enemy_fraction,land)
    else:assert land['gap']<=10,(fraction,enemy_fraction,land)
    pair.append(dict(corrected=corrected,first_landing=land,brake_updates=braking,next_fresh_native_jump=launched,updates=len(path),last=path[-1]))
   rows.append(dict(player_fraction=fraction,enemy_fraction=enemy_fraction,paired_result=pair))
 return dict(passed=True,actual_full_PlayerCtrl_and_native_Goomba_calls=True,cases=rows,
             scope='Four paired isolated legal flat-floor arenas reconstructed from observed X1924/Y110/vx2.5/vy5 and Goomba1975/184/-0.5. Both horizontal fractional endpoints. Literal branch model, not executed Lua or exact full failed RAM. No native enemy collision, NMI/IRQ/PPU, source audio or whole-route proof. Model confirms floor-side-contact gap versus safe landing and a genuine next ordinary source jump only.')

def main():
 original=ROOT/'build/verification/compact-next-luigi-6be-easy-v1'
 probe=ROOT/'build/verification/compact-next-luigi-6be-easy-contact-v1'
 out=ROOT/'build/verification/compact-next-luigi-9ea-easy-v2'
 receipt=ROOT/'docs/qa/luigi-easy-6be-landing-contact-diagnostic-2026-10-27.json'
 policy=ROOT/'tools/playthroughs/current_roster_luigi_landing_brake_v2.lua'
 rom=ROOT/'build/bill_early_cache.nes'
 assert not out.exists()and not receipt.exists()and sha(rom)==NEW
 old=json.loads((original/'result.json').read_text());z=json.loads((probe/'result.json').read_text())
 assert z['ROM_sha256']==old['ROM_sha256']==OLD and not z['passed']and z['frames']==1250 and z['reason']=='Zero-death 1-1 route'
 equality={n:sha(original/n)==sha(probe/n)for n in ['inputs.csv','trace.csv','captures.nesppuv1','captures-index.jsonl']};assert all(equality.values())
 launch=json.loads((probe/'launch.json').read_text());assert launch['exit_code']==1 and launch['settings_before']==launch['settings_after']and not launch['changed_inputs']
 stats=z['bass_collision']['luigi_contact'];assert stats['rows']==710 and stats['BG_calls']==stats['BG_returns']==69 and stats['core_calls']==stats['core_returns']==76
 assert stats['injury_entries']==stats['kill_entries']==1 and stats['stomp_entries']==0 and not stats['clipped_BG']and not stats['clipped_core']
 rows=list(csv.DictReader((probe/'luigi-landing-contact.csv').open(newline='')))
 def one(event,frame=1250):
  a=[r for r in rows if r['event']==event and int(r['frame'])==frame];assert len(a)==1,(event,len(a));return a[0]
 pre=one('PlayerBGCollision-entry');post=one('PlayerCtrl-after-BG-before-guest-bridges');hit=one('ChkForPlayerInjury');inj=one('InjurePlayer');death=one('KillPlayer')
 assert pre['playerY']=='180'and pre['vy']=='5'and post['playerY']=='176'and post['vy']=='0'and post['playerState']=='0'
 assert hit['objectOffset']==inj['objectOffset']==death['objectOffset']=='1'and hit['vy']=='0'and hit['noStomp']=='0'and hit['stompAllowed']=='1'and hit['size']=='1'and hit['stompTimer']=='0'and hit['injuryTimer']=='0'
 e=hit['enemies'].split(';')[1].split(':');assert e[:8]==['1','1','6','0','1969','184','1','248']
 assert hit['playerBoxHex']=='86c890d4'and hit['allEnemyBoxesHex'][8:16]=='90c69acc'
 inputs=[original/n for n in ['ready.json','result.json','trace.csv','inputs.csv']]+[probe/n for n in ['ready.json','result.json','launch.json','luigi-landing-contact.csv']]
 put(receipt,dict(status='REPRODUCED_NATIVE_FALSE_WITH_CAUSAL_CONTACT',ROM_sha256=OLD,frame=1250,original_failure_unchanged=True,
                 exact_file_equalities=equality,observer_statistics=stats,settings_unchanged=True,
                 cause='Normal floor landing then Goomba side contact. PlayerBGCollision clamps Y180->176 and clears vy5->0/state1->0 before enemy pass. Actual slot1 Goomba1969/184 first reaches inclusive right-edge contact; stomp policy permits it, but native current vy0/StompTimer0 takes injury. Small form power0 then KillPlayer. No wrong hitbox or source state demonstrated.',
                 ordered_native_snapshots=[pre,post,hit,inj,death],
                 actual_screen_boxes=dict(player=[134,200,144,212],enemy1=[144,198,154,204],warning='Inclusive equality144 collides. The4px pre-floor vertical extent follows the native build-box-before-floor-clamp caller order. Native small bbox1 is [3,20,13,32], Goomba9 [3,14,13,20]; no hitbox mismatch demonstrated.'),
                 minimal_controller='Source-backed descent braking in a real clear supported lane, using actual ahead Goomba slot/box/position. Release A/B and countersteer Left before floor landing; unchanged base owns fresh subsequent jump. No power, invulnerability, actor or source changes.',
                 next_target_ROM=NEW,limits='This diagnostic stays exact6be. Byte-identical captured container/index establishes the saved full-PPU stream equality, not an additional every-pixel manual visual verdict.',
                 external_evidence=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in inputs]))
 b=scoped_load(rom);controls=cpu_controls(b);controls['scope_models']=scope_controls()
 prepare(SimpleNamespace(rom=rom,expected_sha256=NEW,output=out,identity='luigi',mode='easy',frames=8000,policy=policy,replay=None))
 put(out/'source-controller-controls.json',controls)
 report=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=NEW,controller_only=True,source_game_unchanged=True,
             policy='Unchanged current base called exactly once per poll. Only returned A/B/Left/Right change on selected LuigiEasy outdoor1-1, downward motion, live ahead ordinary Goomba with actual bbox9, and complete clear supported corridor. No latch, state/outcome write or cap increase.',
             scope='20<dx<100; native descent0<vy<128; enemy canonicalY184; playerY>=104/sole<enemyTop198. Every8px corridor column plus endpoint checks Y112..200 empty and ordinary solid support216. Blocking terrain, grounded/rising/near/foreign actors return original policy result.',
             previous_qualified_pattern='Same real landing-brake idea exists in surviving luigi_profile641_route_control_v7.lua. This is only a small current-base wrapper, not restored archived source or transfer of641 native result.',
             source_model=str(out/'source-controller-controls.json'),remaining_limits='Fresh9ea native route/replay and runtime lane admission remain unproved. No guaranteed stomp/fulllevel/pickup or universal collision fix is claimed.',
             draft_preflight='First source-only call rejected an incorrect expected small bbox [2,20,12,32] before executing CPU instructions or writing outputs. Actual linked bbox1 [3,20,13,32] and Goomba9 [3,14,13,20] are now asserted; safe gap threshold derives from their inclusive edges.',
             original6be_native_FALSE_preserved=True,diagnostic_receipt=str(receipt))
 put(out/'controller-review.json',report)
 ready=out/'ready.json';a=json.loads(ready.read_text());a['PREPARED_DO_NOT_RUN']=True;a['controller_revision']=report
 for p in [Path(__file__).resolve(),receipt,out/'source-controller-controls.json',out/'controller-review.json',ROOT/'tools/audit/luigi_profile641_route_control_v7.lua',ROOT/'tools/audit/luigi_mario_profile731_cpu_v1.py',ROOT/'tools/audit/mario_luigi731_coefficients_v1.py',ROOT/'src/collision.s',ROOT/'src/player.s']+inputs:a['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=a['command']));a['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,d in a['bindings'].items():assert sha(p)==d,p
 put(ready,a)
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(a['bindings']),diagnostic_receipt=str(receipt),diagnostic_sha256=sha(receipt))))

if __name__=='__main__':main()
