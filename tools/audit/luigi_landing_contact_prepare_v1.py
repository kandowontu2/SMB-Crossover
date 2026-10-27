"""Prepare one passive exact-input Luigi failure diagnostic; never launch."""
from pathlib import Path
from types import SimpleNamespace
import csv, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from current_roster_compact_11_v1 import prepare,lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

SHA='6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def main():
 old=ROOT/'build/verification/compact-next-luigi-6be-easy-v1'
 out=ROOT/'build/verification/compact-next-luigi-6be-easy-contact-v1'
 receipt=ROOT/'docs/qa/luigi-easy-6be-native-failure-2026-10-27.json'
 rom=ROOT/'build/samus_fixed_hud_current4a.nes'
 assert not out.exists()and not receipt.exists()and sha(rom)==SHA
 z=json.loads((old/'result.json').read_text());prior=json.loads((old/'ready.json').read_text())
 assert z['ROM_sha256']==prior['ROM_sha256']==SHA and z['actual_mode']==0 and not z['passed']and z['frames']==1250 and z['reason']=='Zero-death 1-1 route'
 assert sha(old/'review.json')=='5fc46279ff60ac3ce8857cc4df16107949b99780e14e5521e07ea1b9a0c3a811'
 assert sha(old/'selected-whole-frames.png')=='e00ac4c755ba88b96e17977963d7c103ec9a17e79338044659dfedc62899fbff'
 t=list(csv.DictReader((old/'trace.csv').open(newline='')));assert len(t)==1250
 for frame,x,y,vy in [(1247,1951,165,5),(1248,1954,170,5),(1249,1956,175,5),(1250,1959,176,252)]:
  a=t[frame-1];assert all(int(a[n])==v for n,v in dict(frame=frame,x=x,y=y,vy=vy,power=0).items())
 inputs=list(csv.DictReader((old/'inputs.csv').open(newline='')));assert len(inputs)==1249
 assert all(int(a['poll'])==i for i,a in enumerate(inputs,1))
 policy=ROOT/'tools/playthroughs/mario_luigi_scrooge_policy.lua'
 nav=ROOT/'tools/playthroughs/mario_luigi_scrooge_nav.lua'
 assert sha(policy)==prior['bindings'][str(policy)]and sha(nav)==prior['bindings'][str(nav)]
 b=scoped_load(rom)
 def h(n,d=0):
  at=location(b,n)+d;pc=address(b,n)+d;bank=(at-16)//8192;bs=b['raw'][at:at+3];banks=[bank]
  if bank==127:
   clone=16+125*8192+(pc&8191);assert b['raw'][clone:clone+3]==bs;banks=[125,127]
  return dict(symbol=n,delta=d,pc=pc,banks=banks,bytes=list(bs))
 def unique_call(start,end,target):
  at=location(b,start);span=b['raw'][at:location(b,end)];a=address(b,target);needle=bytes([0x20,a&255,a>>8]);assert span.count(needle)==1
  return span.index(needle)+3
 bg_delta=unique_call('PlayerCtrlRoutine','PlayerMovementSubs','PlayerBGCollision')
 core_delta=unique_call('PlayerEnemyCollision','CheckForPUpCollision','PlayerCollisionCore')
 hooks=dict(bg=h('PlayerBGCollision'),after_bg=h('PlayerCtrlRoutine',bg_delta),core=h('PlayerCollisionCore'),after_core=h('PlayerEnemyCollision',core_delta),
            player_enemy=h('PlayerEnemyCollision'),contact=h('CheckForPUpCollision'),handle=h('HandlePECollisions'),body_after=h('HandlePECollisions',3),
            water=h('GuestWaterStompPolicy'),injury_check=h('ChkForPlayerInjury'),injury=h('InjurePlayer'),force_injury=h('ForceInjury'),kill=h('KillPlayer'),stomp=h('EnemyStomped'),set_engine=h('SetPRout'))
 assert hooks['after_bg']['bytes'][0]==0xad and hooks['after_bg']['bytes'][1:]==[address(b,'SmCeilingHit')&255,address(b,'SmCeilingHit')>>8]
 assert hooks['after_core']['bytes'][:2]==[0xa6,address(b,'ObjectOffset')]
 assert hooks['body_after']['bytes'][0]==0x90
 names='ObjectOffset SelectedCharacter MarioVariant CrossoverBehaviorVersion GameEngineSubroutine Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State Player_X_Speed Player_Y_Speed PlayerSize CrouchingFlag Player_BoundBoxCtrl PlayerStatus StompTimer InjuryTimer GuestBodyNoStomp GuestBodyStompAllowed FrameCounter Player_Rel_XPos Enemy_Rel_XPos BoundingBox_UL_Corner Enemy_Flag Enemy_ID Enemy_State Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_MovingDir Enemy_CollisionBits EnemyOffscrBitsMasked'.split()
 cfg=dict(ROM_sha256=SHA,first=1171,last=1250,ram={n:address(b,n)for n in names},hooks=hooks)
 # Same controller, saved real menu/gameplay masks and all original mechanics guards.
 prepare(SimpleNamespace(rom=rom,expected_sha256=SHA,output=out,identity='luigi',mode='easy',frames=8000,policy=policy,replay=old/'inputs.csv'))
 module=ROOT/'tools/audit/luigi_landing_contact_probe_v1.lua'
 body=module.read_text();assert 'removeMemoryCallback'not in body and 'emu.write'not in body and 'setInput'not in body
 put(out/'contact-config.json',cfg)
 run=out/'run.lua';text=run.read_text();needle='dofile('+lua((ROOT/'tools/audit/current_roster_compact_11_v1.lua').as_posix())+')';assert text.count(needle)==1
 append='LUIGI_LANDING_CONTACT_PROBE='+lua(cfg)+'\nlocal priorClose=ROSTER_CONFIG.bass_close\nlocal contactClose=dofile('+lua(module.as_posix())+')\nROSTER_CONFIG.bass_close=function()local q=priorClose and priorClose()or{};q.luigi_contact=contactClose();return q end\n'
 run.write_text(text.replace(needle,append+needle),newline='\n')
 ledger=dict(identity='luigi',mode=0,ROM_sha256=SHA,component='controller-only1-1',outcome='FALSE',frame=1250,x=1959,y=176,
             failure='Zero-death guard near three ground Goombas after descent',remaining='Exact source injury/stomp owner and pre/post-floor velocity require passive fixed-input diagnostic; no source hitbox defect established.')
 evidence=[old/n for n in ['ready.json','result.json','review.json','trace.csv','inputs.csv','selected-whole-frames.png']]
 put(receipt,dict(status='NATIVE_FALSE',ROM_sha256=SHA,actual_numeric_mode=0,identity='luigi',frame=1250,whole_PPU_frames_valid=1027,
                  actual256_DMAs=z['completed_DMAS'],completed_GameLoops=z['completed_loops'],zero_death=False,route_clear=False,selected_frames_ROOT_viewed=5,
                  trajectory='1247 X1951/Y165/vy5;1248 X1954/Y170/vy5;1249 X1956/Y175/vy5;1250 X1959/Y176 with death changing velocity toFC. Final screenshot is adjacent to three ground Goombas; exact actor and first injury branch are not logged.',
                  source_cause_limit='PlayerCtrl calls PlayerBGCollision before the enemy pass. The native enemy path admits positive Y velocity to stomp; landing can change the actual velocity before that test. EndFrame velocity and image alone cannot prove whether this was a valid descending overlap or a grounded side contact.',
                  next_step='One passive exact1249-input replay; no policy or game change. If no failure recurs, original replay-exhaustion guard stops without inventing a tail.',ledger_entry=ledger,
                  external_evidence=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in evidence]))
 put(out/'negative-ledger-entry.json',ledger)
 report=dict(PREPARED_DO_NOT_RUN=True,native_run=False,ROM_sha256=SHA,physical_window=[1171,1250],window_frames=80,
             source_hooks=hooks,only_added_outputs='One bounded CSV2500rows/1MiB; close statistics merge into existing result. No added screenshots or container.',
             all_callbacks_registered_at_startup=True,shared_harness_and_controller_unchanged=True,exact_original1249_inputs=True,
             owner_contract='Each real hook checks physical bank+compiled3bytes. Pre/postBG and PlayerCollisionCore verify the actual return PC and SP only for these specific compiled callers; collision result carry is captured before LDX. No runtime callback registration or return-address synthesis.',
             data_contract='Actual ObjectOffset, six live enemy slots with flags/IDs/states/world positions/directions/collision/offscreen bits, actual player/enemy bounding boxes, PlayerSize/crouch/control and velocities; branch PC/AXYP/SP and velocity/state/engine bus stores.',
             remaining_limits='Read-only prospective diagnostic, not a route retry or hitbox fix. Internal stackReturn is only a raw word, not a claimed caller. No no-contact/pass decision is synthesized. All original mode/zero-death/input/motion/NMI/IRQ/SMC/CHR/E008/full256DMA/render-enable guards remain literal.',public_failure_receipt=str(receipt))
 put(out/'contact-review.json',report)
 ready=out/'ready.json';z=json.loads(ready.read_text());z['bindings'][str(run)]=sha(run)
 z['PREPARED_DO_NOT_RUN']=True;z['contact_probe']=dict(read_only=True,first=1171,last=1250,rows_cap=2500,CSV_bytes_cap=1048576,report=str(out/'contact-review.json'))
 for p in [Path(__file__).resolve(),module,receipt,out/'contact-config.json',out/'contact-review.json',out/'negative-ledger-entry.json']+evidence+[ROOT/n for n in ['src/collision.s','src/player.s','src/guest_body_contact.s','src/guest_source_stomp.s']]:z['bindings'][str(p)]=sha(p)
 put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,requires_ROOT_native_lease=True,argv=z['command']));z['bindings'][str(out/'command.json')]=sha(out/'command.json')
 for p,d in z['bindings'].items():assert sha(p)==d,p
 put(ready,z)
 print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),failure_receipt=str(receipt),receipt_sha256=sha(receipt))))

if __name__=='__main__':main()
