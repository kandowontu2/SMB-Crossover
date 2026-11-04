"""Compile isolated Mini fireball proposal and freeze only its direct originals."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, base64, hashlib, json, re, subprocess
import build_storage_guard_v1 as G
from py65.devices.mpu6502 import MPU

R=Path(__file__).resolve().parents[2]
TREE='56d5a30ff8f58096c074ca59656efc5f787d0edb'
INPUTS={
 'project/scripts/onattack.gbsres':'df3d99547a436a858ae1817f639f83a24b51045c',
 'project/prefabs/actors/fireball.gbsres':'35ababa5c48c537883b26246252eb33afa137064',
 'plugins/actorBehaviorPlugin/engine/src/actor_behavior.c':'31b05d03c3700bb23988a7734aa2bdb73ea05811',
 'project/scenes/1-1/scene.gbsres':'298beee054297e0c02f182dd8e074f9686d794f9',
}
sha=lambda b:hashlib.sha256(b).hexdigest()

def cpu_checks(o):
 labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(o/'worker.lbl').read_text(),re.M)}
 def fresh():
  mem=[0]*65536
  for name,at in [('attack',0xbcc0),('helpers',0xbd72)]:
   b=(o/(name+'.bin')).read_bytes();mem[at:at+len(b)]=b
  mem[0x15a]=0x60
  return MPU(memory=mem)
 def call(m,name):
  m.sp=0xfd;m.stPushWord(0x7eff);m.pc=labels[name];calls=0
  for _ in range(500):
   if m.pc==0x7f00:return calls
   if m.pc==0x15a:
    assert m.memory[0x16c:0x16e]==[0xa7,0xae]and m.a==0x80 and m.x==0
    calls+=1;m.memory[0x6e8]=0x34
   m.step()
  raise AssertionError('Worker did not return')
 spawn=0
 for x in range(256):
  for facing in [1,2]:
   for up in [0,8]:
    m=fresh();q=m.memory
    for at,value in {0x75b:2,0x558:0x40,0x75:x,0x5c:3,0xbd:176,0xa4:1,0x53e:facing,0xdc:up}.items():q[at]=value
    m.a,m.x,m.y,m.p=0xa5,0x37,0x49,0xe4
    assert call(m,'MiniFireballTail')==1
    assert q[0x7c]+256*q[0x63]==768+x+(2 if facing==1 else-6)
    assert q[0xc4]==196 and q[0xab]==1 and q[0x4d]==(0x20 if facing==1 else 0xe0)and q[0x95]==(0xff if up else 1)
    assert q[0x25]==1 and q[0x6e8]==0 and q[0x105]==0x20
    assert(m.a,m.x,m.y,m.p&0xcf)==(0xa5,0x37,0x49,(0xe4|1)&0xcf)
    spawn+=1
 admission=0
 for power in [0,1,2,3]:
  for held,old in [(0,0),(64,64),(64,0)]:
   for state in [0,1,0x80,0x81]:
    m=fresh();q=m.memory
    for at,value in {0x75b:power,0x558:held,0x55b:old,0x25:state,0x6e8:9,0xa4:1,0x53e:1}.items():q[at]=value
    calls=call(m,'MiniFireballTail')
    spawned=power==2 and held==64 and old==0 and state==0
    assert calls==(1 if power==2 and(state!=0 or spawned)else 0)
    if power!=2:assert q[0x25]==0 and q[0x6e8]==0
    elif state in [1,0x80]or spawned:assert q[0x6e8]==0
    elif state==0x81:assert q[0x6e8]==0x34
    admission+=1
 draws=0
 for logical in [0,4,248,252]:
  for rotation in [0,4,252]:
   m=fresh();q=m.memory
   for at,value in {0x25:1,0x7c:80,0x63:1,0x71f:32,0x71d:1,0xc4:196,0x6de:logical,0x6c0b:1,0x6c08:rotation}.items():q[at]=value
   call(m,'MiniFireballDraw')
   if logical<252:
    at=0x200+((logical+rotation)&255);assert q[at:at+4]==[199,0x6f,2,54]and q[0x6de]==logical+4
   else:assert q[0x6de]==252 and not any(q[0x200:0x300])
   draws+=1
 return dict(spawn_signed_page_and_up=spawn,admission_and_power_loss=admission,rotated_OAM_draws=draws,native_core='Native FarCall intercepted with genuine target/bank/slot checks; native body itself is not executed in these adapter fixtures.')

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--output',required=True,type=Path)
 a=ap.parse_args();o=a.output.resolve()
 G.preflight(private_root=o,reserved_bytes=100000,reserved_files=8,fresh=True)
 o.mkdir(exist_ok=True)
 chosen={}
 for path,blob in INPUTS.items():
  q=json.loads(subprocess.check_output(['gh','api','repos/Mico27/SuperMarioBrosMini/git/blobs/'+blob]))
  data=base64.b64decode(q['content'])
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob
  chosen[path]=data
 with ZipFile(o/'original-inputs.zip','w',ZIP_DEFLATED,compresslevel=9)as z:
  for path,data in chosen.items():z.writestr(path,data)
 scene=json.loads(chosen['project/scenes/1-1/scene.gbsres'])
 input_events=[e for e in scene['script']if e['command']=='EVENT_SET_INPUT_SCRIPT']
 assert any(e['args']['input']==['b']and e['children']['true'][0]['args']['customEventId']=='70c96f28-b99f-4a17-a885-b993c8676eb8' for e in input_events)
 src=R/'tools/reference/mini_mario_fireball_1103.s'
 cc=R/'tools/Windows/cc65/bin'
 cfg=o/'worker.cfg'
 cfg.write_text('MEMORY{ A:start=$bcc0,size=160,file="'+(o/'attack.bin').as_posix()+'"; H:start=$bd72,size=178,file="'+(o/'helpers.bin').as_posix()+'"; G:start=$d2e0,size=$20,file="'+(o/'art.bin').as_posix()+'";}SEGMENTS{MINI_FB_ATTACK:load=A,type=ro;MINI_FB_HELPERS:load=H,type=ro;MINI_FB_ART:load=G,type=ro;}')
 subprocess.run([cc/'ca65.exe',src,'-o',o/'worker.o'],check=True)
 subprocess.run([cc/'ld65.exe','-C',cfg,o/'worker.o','-o',o/'unused.bin','-Ln',o/'worker.lbl'],check=True)
 sizes={n:(o/(n+'.bin')).stat().st_size for n in ['attack','helpers','art']}
 art=(o/'art.bin').read_bytes()
 pixels=[(x,y)for y in range(16)for x in range(8)if (art[y//8*16+y%8]|art[y//8*16+8+y%8])&(128>>x)]
 assert len(pixels)==16 and (min(x for x,y in pixels),min(y for x,y in pixels),max(x for x,y in pixels),max(y for x,y in pixels))==(0,0,3,3)
 checks=cpu_checks(o)
 out=dict(source_CPU_only=True,ROM_written=False,native_run=False,bytes=sizes,total_PRG_bytes=sizes['attack']+sizes['helpers'],fits_reviewed_338B=sum(sizes[n]for n in ['attack','helpers'])<=338,
  funding=dict(bank=89,source='src/tmnt_mac_probes.inc',head_tail=['BCC0','BD60'],head_bytes=160,side_tail=['BD72','BE24'],side_bytes=178,reason='Both existing public endpoints end with genuine farcall...,jmp before .res.'),
  original_source_tree=TREE,original_input_blobs=INPUTS,
  original=dict(button='fresh B, nonoverride press input script',power='variable24==2',pool=1,spawn='X+8 right; X left; Y unchanged',horizontal_sixteenths=[32,-32],initial_vertical_sixteenths=[16,-16],up_held_selects_negative=True,gravity_sixteenths=4,down_cap_sixteenths=32,floor_bounce_sixteenths=-40,ceiling_velocity=0,wall='execute impact script then state255',original_effect_hitbox='8x8; requested4x4 is intentional adaptation'),
  adaptation=dict(physics='Actual native FireballObjCore gravity$50/256, fall cap3px, floor bounce-3px. Horizontal speed2px; initial nativeY speed±1. Same native terrain contact/impact/explosion/enemy outcomes.',shot_bbox='Unchanged canonical native control8 offsets6,4,10,8; native comparisons include equal edges. Visible graphic is exactly4x4 at base+[6,4].',art='metadata967 source-defined unused D2E0..D300; slot5 mapping967; tile$6F; atlas968 unchanged',pool='Only native shot0 used; source one-actor admission retained.'),
  integration_required=['Integrated source now lives in build_mini_empty_draw.py and mini_mario_empty_draw.s. No shared native fireball actor/bbox/initializer bytes change.','Public34 keeps a fast nonfire+empty shortcut; other calls reach the authenticated Mini actor worker.','Metadata D239 draw return calls the AXYP-preserving wrapper; native explosion metasprites states81+ remain in ordinary actor render; state80 initialhit frame is hidden.','Both original and fast Mini graphics set slot5 to967 before CHR publication.','Physical967+0x2E0 art and all metadata changes are included in the Mini payload cookie.','Actual Mini initializer through D2D0 clears both native fireball states/metasprites.','worker.cfg measures the exact source-declared160/178 pad bounds without emitting a ROM.','Native/controller-only earned flower, physical opaqueextent, enemydefeat/terrainimpact/explosion/pause/damage/foreign regression and Downloads qualification belong to root.'],
  source_SHA256=sha(src.read_bytes()),scope='Compiled proposal only. No ROM or emulator emitted. Temporary linker regions measure code, do not grant storage or install hooks.')
 out['adapter_CPU_checks']=checks
 (o/'contract.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:out[k]for k in ['bytes','total_PRG_bytes','fits_reviewed_338B','ROM_written']}))

if __name__=='__main__':main()
