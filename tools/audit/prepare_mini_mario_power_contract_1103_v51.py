"""Tiny pinned-source Mini power contract and current-kernel legal CPU fixtures."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import base64,hashlib,json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
import check_mini_mario_step_1103_v18 as T
W,R=H.W,H.R
O=R/'build/mini-mario-power-contract-1103-v51'
HOST=R/'build/mini-mario-native-end-1103-v48'
ROM=R/'build/mini-mario-end-candidate-root-1103-v49/mini-end.nes'
PIN='ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'
TREE='56d5a30ff8f58096c074ca59656efc5f787d0edb'
INPUTS={
 'project/prefabs/actors/powerup.gbsres':'0dd6985330c6b6edbf91a12a7293f8ef83c62762',
 'project/scripts/setmariopalette.gbsres':'5285a89ebe90595389f38aaea0a3d6ca289b1fde',
 'project/scenes/1-1/actors/powerup.gbsres':'097e4a5a155fe8cb1ee60fec4a65844b23a0c595',
}
def events(value):
 if isinstance(value,dict):
  if 'command'in value:yield value
  for x in value.values():yield from events(x)
 elif isinstance(value,list):
  for x in value:yield from events(x)
def main():
 O.mkdir(exist_ok=True);chosen={};provenance={}
 for path,blob in INPUTS.items():
  q=json.loads(subprocess.check_output(['gh','api','repos/Mico27/SuperMarioBrosMini/git/blobs/'+blob]));data=base64.b64decode(q['content'])
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob
  chosen[path]=data;provenance[path]=dict(tree=TREE,git_blob=blob,SHA256=W.sha(data),bytes=len(data))
 archive=O/'power-inputs-v51.zip'
 with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
  for name,b in chosen.items():z.writestr(name,b)
 power=json.loads(chosen['project/prefabs/actors/powerup.gbsres']);switch=power['script'][0]
 assert switch['command']=='EVENT_SWITCH'and switch['args']['value0']['value']==1 and switch['args']['value1']['value']==2
 branches={}
 for name,key,expected in[('mushroom','true0',1),('flower','true1',2)]:
  branch=switch['children'][key][0]['children']['true'][1]
  assert branch['command']=='EVENT_IF';body=branch['children']['true'];flat=list(events(body))
  writes=[e['args']for e in flat if e['command']=='EVENT_SET_VALUE'and e['args'].get('variable')=='24']
  assert len(writes)==1 and writes[0]['value']['value']==expected
  waits=[e['args']['frames']for e in flat if e['command']=='EVENT_WAIT'];assert waits==([15,15]if name=='mushroom'else[5]*7)
  branches[name]=dict(item_value=switch['args']['value0'if key=='true0'else'value1']['value'],condition=branch['args']['condition'],target_status=expected,wait_frames=waits,total_locked_frames=sum(waits),sprite_changes=[e['args']['spriteSheetId']for e in flat if e['command']=='EVENT_PLAYER_SET_SPRITE'],animation_states=[e['args']['spriteStateId']for e in flat if e['command']=='EVENT_ACTOR_SET_STATE'])
 kernel=(HOST/'mini-host-v48.bin').read_bytes();q=json.loads((HOST/'mini-host-v48.json').read_text());L=q['labels'];S=H.symbols();raw=ROM.read_bytes();assert W.sha(raw)==PIN and raw[1048592+962*1024:1048592+962*1024+len(kernel)]==kernel
 def fresh(tier=0):
  m=T.memory(kernel,L,0)
  for addr,path in[(0xd300,R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin'),(0xd000,R/'build/mini-mario-art-1103-v12/engine-animation-index.bin'),(0xd160,R/'build/mini-mario-art-1103-v12/engine-animation-frames.bin')]:
   b=path.read_bytes();m.memory[addr:addr+len(b)]=b
  for n,v in dict(GameEngineSubroutine=8,Player_X_Position=40,Player_Y_Position=176,Player_Y_HighPos=1,PlayerStatus=tier,AreaType=1).items():m.memory[S[n]]=v
  T.call(m,L['MiniHostFresh']);return m
 def step(m,epoch,held):
  m.memory[S['FrameCounter']]=epoch&255;m.memory[S['SavedJoypadBits']]=held;T.call(m,L['MiniHostMain'])
 def word(m,at):return m.memory[at]|m.memory[at+1]<<8
 forms=[]
 for tier in[0,1,2]:
  for crouch in[0,1]:
   m=fresh(tier)
   for epoch in range(8):step(m,epoch,4 if crouch else 0)
   top=1 if tier==0 or crouch else 249;assert m.memory[0xc244]==tier and m.memory[0xc256]==top
   assert (m.memory[0xc310]>=39)==(tier>0)
   T.call(m,L['MiniHostBox']);bounds=m.memory[S['BoundingBox_UL_Corner']:S['BoundingBox_UL_Corner']+4];assert(bounds[3]-bounds[1]+1)&255==(7 if top==1 else 15)
   m.memory[S['VRAM_Buffer1_Offset']]=0;T.call(m,L['MiniHostColors']);rgb=m.memory[S['VRAM_Buffer1']+4:S['VRAM_Buffer1']+7];assert rgb==([0x27,0x37,0x16]if tier==2 else[0x27,0x16,0x18])
   forms.append(dict(native_status_fixture=tier,crouched=crouch,source_top=1 if top==1 else-7,bbox=bounds,pose=m.memory[0xc310],opaque_RGB=rgb))
 # One geometric source/controller fixture, no enemies/parser/nativeheadwork.
 # The first Q spans336..351, queryrow144 (underside160). Original runjump
 # must reach the Q; standing37.5px does not reach that source head height.
 m=fresh();m.memory[S['Player_X_Position']]=250;m.memory[S['ScreenLeft_X_Pos']]=144
 solid=m.memory[0x300+176];m.memory[0x3d0+112+5]=solid;launch=None;contact=None
 for epoch in range(330):
  x=word(m,0xc250)/16;held=0x41
  if launch is None and x>=304 and m.memory[0xc24c]&1:launch=epoch
  if launch is not None and epoch-launch<40:held|=128
  step(m,epoch,held)
  if m.memory[0xc25c]:
   contact=dict(update=epoch,takeoff_update=launch,x16=word(m,0xc250),y16=word(m,0xc252),headX=word(m,0xc25d),headY=word(m,0xc25f),rawtile=m.memory[0xc261]);break
 assert contact and contact['headX']//16==21 and contact['headY']//16==9,contact
 out=dict(passed=True,source_CPU_only=True,ROM_written=False,native_earned=False,parent_ROM_SHA256=PIN,kernel_SHA256=q['SHA256'],source_tree=TREE,archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=W.sha(archive.read_bytes()),provenance=provenance,original_power_branches=branches,existing_active_form_fixtures=forms,first_power_block_source_geometry=contact,first_actionable_contract='Original mushroom only0->1; flower directly anynon2->2. Script wait arguments total30/35 frames; exact GBVM elapsed timing not asserted. Native GuestBeginPowerup targets old+1 with60update freeze. Existing private row24Pickup is CLC, row33Powerup CLC. Earned native first mushroom observation is next; no source change yet.',existing_power_gaps=['No original ChangeSize animation during nativefreeze: MiniAnimate only runs on actual8Step.','No original flower projectile/attack lifecycle: rows4 and34 intentionally handled without source projectile.','Actual native pickup/headtransaction and maturecollection remain unqualified until root earned replay; CPU statusfixtures are not earned pickups.'],bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),HOST/'mini-host-v48.bin',HOST/'mini-host-v48.json',R/'src/guest_powerups.s',R/'src/new_roster_dispatch.s',R/'tools/reference/mini_mario_world_1103_v16.inc',R/'build/mini-mario-animation-1103-v20/animate.s']})
 (O/'power-contract-v51.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','archive_bytes','original_power_branches','first_power_block_source_geometry']}))
if __name__=='__main__':main()
