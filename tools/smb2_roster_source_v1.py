"""Read-only local original SMB2 authority/source/CPU/art audit, no port/build."""
from pathlib import Path
import hashlib,json,re,subprocess
from py65.devices.mpu6502 import MPU
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent/'mario in kid icarus/vendor/smb2'
ROM=Path('C:/NES/Super Mario Bros. 2 (USA).nes')
COMMIT='b73415e1953d7fdffd4957d5fb43fa7a13844c1c'
SHA='41300bc4942a8a4f9b53148b404dd5cae3dd708ebdd9b617888d290a51a83e43'
OUT=ROOT/'build/smb2-roster-source-v1'
def digest(b):return hashlib.sha256(b).hexdigest()
def binding(p):p=Path(p);b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),sha256=digest(b))
def main():
 raw=ROM.read_bytes();assert digest(raw)==SHA
 native=REPO/'bin/native.nes';assert native.read_bytes()[16:]==raw[16:]
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==COMMIT
 assert not subprocess.check_output(['git','status','--short'],cwd=REPO,text=True).strip()
 labels={};nls=sorted((REPO/'bin').glob('native.nes.*.nl'))
 for p in nls:
  for line in p.read_text().splitlines():
   m=re.match(r'\$([0-9a-fA-F]+)#([^#]+)#',line)
   if m:labels[m[2]]=int(m[1],16)
 def at(pair,pc,n=1):
  base=0xc000 if pair==7 else 0x8000;start=16+pair*16384+pc-base
  assert 0<=pc-base<16384
  return raw[start:start+n]
 class Memory:
  def __init__(self,pair=0):
   self.m=bytearray(65536);self.m[0x8000:0xc000]=raw[16+pair*16384:16+(pair+1)*16384]
   self.m[0xc000:]=raw[16+7*16384:16+8*16384];self.writes=[]
  def __getitem__(self,a):return self.m[a]
  def __setitem__(self,a,v):self.m[a]=v&255;self.writes.append((a,v&255))
 def call(m,name,a=0,x=0,y=0):
  c=MPU(memory=m,pc=labels[name]);c.a=a;c.x=x;c.y=y;c.p=0x24;c.sp=0xfd
  m.m[0x1fe]=0xfe;m.m[0x1ff]=0x7f
  for _ in range(30000):
   if c.pc==0x7fff:assert c.sp==255;return c
   assert m.m[c.pc]!=0,('BRK',name,hex(c.pc));c.step()
  raise AssertionError(('noRTS',name,hex(c.pc)))
 names=['Mario','Princess','Toad','Luigi'];stats=[]
 for char,name in enumerate(names):
  ptr=labels[name+'Stats'];values=list(at(5,ptr,23));stats.append(dict(native_id=char,name=name,source=f'A/B:{ptr:04X}',bytes=values,
   lift_delays=values[:6],jump_stand_charged_running=values[6:12],quicksand_launch=values[12],float_updates=values[13],
   gravity=values[14:17],run_right=values[17:20],run_left=values[20:23],
   palette=list(at(5,labels['CharacterPalette']+char*4,4))))
 jump=[]
 for char,info in enumerate(stats):
  for bits in range(8):
   for hold in [1,180]:
    m=Memory();m.m[labels['CharacterStatsRAM']:labels['CharacterStatsRAM']+23]=bytes(info['bytes'])
    for n,v in dict(CurrentCharacter=char,PlayerYLo=180,PlayerXVelocity=8 if bits&4 else 0,
     HoldingItem=bits&1,CrouchJumpTimer=60 if bits&2 else 0,Player1JoypadHeld=128).items():m.m[labels[n]]=v
    c=call(m,'PlayerStartJump');launch=m.m[labels['PlayerYVelocity']];index=c.y;trail=[]
    assert index==((2 if bits&2 else(4 if bits&4 else 0))+(bits&1))
    assert launch==info['bytes'][6+index]
    for tick in range(180):
     m.m[labels['Player1JoypadHeld']]=128 if tick<hold else 0
     m.m[labels['byte_RAM_10']]=tick&255
     if tick:call(m,'PlayerGravity')
     call(m,'ApplyPlayerPhysicsY')
     y=m.m[labels['PlayerYLo']]+256*m.m[labels['PlayerYHi']]
     if y>=32768:y-=65536
     trail.append([tick,y,m.m[labels['PlayerYVelocity']],m.m[labels['JumpFloatTimer']]])
     if tick>1 and y>=180:break
    jump.append(dict(native_id=char,input_RCI=bits,actual_source_index=index,hold=hold,source_launch=launch,
     apex_rise=180-min(r[1]for r in trail),return_crossing_updates=len(trail),final=trail[-1],
     trace_sha256=digest(json.dumps(trail,separators=(',',':')).encode())))
 # Execute the actual original renderer with real CHR-bank selection. No host
 # poses or guessed sprite assembly. RGB is a conventional palette preview.
 records=[];used_pages=set();preview=Image.new('RGB',(8*74,4*76),(44,54,68));draw=ImageDraw.Draw(preview)
 colors={0x0f:(0,0,0),1:(0,30,116),0x16:(152,34,32),0x27:(228,196,144),
  6:(84,4,0),0x25:(212,136,228),0x36:(236,180,176),0x30:(236,238,236),0x2a:(152,226,180)}
 for char,info in enumerate(stats):
  for size in [0,1]:
   for direction in [0,1]:
    for pose in [0,1,2,3,4,6,7,8,9,10]:
     m=Memory();m.m[0x200:0x300]=bytes([0xf8])*256
     for n,v in dict(CurrentCharacter=char,PlayerCurrentSize=size,PlayerAnimationFrame=pose,PlayerDirection=direction,
      PlayerScreenX=80,PlayerScreenYLo=80).items():m.m[labels[n]]=v
     call(m,'LoadWorldCHRBanks');c=call(m,'RenderPlayer')
     o=[list(m.m[p:p+4])for p in range(0x200,0x300,4)if m.m[p]<240]
     banks=[m.m[labels['SpriteCHR1']+i]for i in range(4)];px={}
     for y,t,attribute,x in reversed(o):
      # Inverted MMC3 maps four1KB sprite banks at0000..0FFF, and two2KB
      # background banks at1000..1FFF. Native odd eye tiles really use the
      # second pattern table; don't mistake them for character-page pixels.
      start=(t&1)*4096+(t&0xfe)*16
      if start<4096:page=banks[start//1024]
      else:
       latch=m.m[labels['BackgroundCHR1']+(start-4096)//2048]
       page=(latch&254)+(start%2048)//1024
      used_pages.add(page)
      tile=raw[16+131072+page*1024+(start&1023):16+131072+page*1024+(start&1023)+32]
      for yy in range(16):
       for xx in range(8):
        sy=15-yy if attribute&128 else yy;sx=7-xx if attribute&64 else xx;a=sy//8*16+sy%8
        value=(tile[a]>>(7-sx)&1)|((tile[a+8]>>(7-sx)&1)<<1)
        if value:px[x+xx-80,y+yy-79]=(value,attribute&3)
     records.append(dict(native_id=char,size=size,face=direction,pose=pose,sourceOAM=o,
      spriteCHR=banks,opaque=len(px),cycles=c.processorCycles,pixel_roles_sha256=digest(json.dumps(sorted(px.items())).encode())))
     selected={2:0,3:1,6:2,9:3}
     if direction==1 and pose in selected:
      column=size*4+selected[pose];image=Image.new('RGB',(64,60),(107,116,130))
      for (x,y),(value,pal)in px.items():
       # Source bodyP0 character palette, eyesP1 world1overworld30/16/0F.
       role=info['palette'] if pal==0 else[15,48,22,15]
       if 0<=x+24<64 and 0<=y+14<60:image.putpixel((x+24,y+14),colors[role[value]])
      preview.paste(image,(column*74+5,char*76+13));draw.text((column*74+4,char*76+1),f'{names[char]} {size}/{pose}',fill='white')
 OUT.mkdir(exist_ok=True);picture=OUT/'original-player-preview.png';preview.save(picture)
 requests={
  0:['HandlePlayerState','HandlePlayerState_Normal','sub_BANK0_8C1A','PlayerStartJump','PlayerGravity',
   'sub_BANK0_8D2C','sub_BANK0_8DC0','ApplyPlayerPhysics','ApplyPlayerPhysicsY','PlayerTileCollision',
   'TileBehavior_CheckPickUp','HandlePlayerState_Lifting','PlayerLiftTimer','ThrowXVelocity','ThrowYVelocity'],
  1:['DamagePlayer','CheckCollisionWithPlayer','EnemyBehavior_PickUpMushroom','EnemyBehavior_PickUpStopwatch'],
  2:['StartProcessingSoundQueue','ProcessMusicAndSfxQueues','ProcessDPCMQueue','ProcessMusicQueue','NoteFrequencyData','InstrumentSoundData'],
  5:['StatOffsets','CharacterStats','CharacterPalette','CopyCharacterStatsAndStuff'],
  7:['RenderPlayer','CharacterTiles_Walk1','CharacterTiles_PrincessJumpBody','LoadCharacterCHRBanks','RestorePlayerToFullHealth','DPCMSampleData','DPCMSampleDataEnd_DrumSample']}
 routines=[]
 for pair,ns in requests.items():
  for name in ns:
   p=labels[name];base=0xc000 if pair==7 else 0x8000
   routines.append(dict(name=name,pair=pair,original8KBbank=pair*2+(p-base)//8192,CPU=f'{p:04X}',first12=at(pair,p,12).hex()))
 fields='PlayerXHi PlayerYHi PlayerXLo PlayerYLo PlayerXVelocity PlayerYVelocity PlayerXSubpixel PlayerYSubpixel PlayerState PlayerInAir HoldingItem ObjectBeingCarriedIndex PlayerCurrentSize PlayerHealth PlayerMaxHealth CrouchJumpTimer JumpFloatTimer CharacterStatsRAM CurrentCharacter Player1JoypadHeld Player1JoypadPress CurrentMusicPointer SoundEffectQueue1 SoundEffectQueue2 SoundEffectQueue3 DPCMQueue'.split()
 audio=at(2,0x8000,16384);audio_end=0x8000+len(audio.rstrip(bytes([255])))
 assert at(2,0x875f,0x8f00-0x875f)==bytes([255])*(0x8f00-0x875f)
 assert at(2,0x8fb3,0x9000-0x8fb3)==bytes([255])*(0x9000-0x8fb3)
 packed_audio=(0x875f-0x8000)+(0x8fb3-0x8f00)+(audio_end-0x9000)
 result=dict(status='AUTHENTIC_ORIGINAL_READONLY_SOURCE_AUDIT_NO_HOST_ALLOCATION_OR_PORT',ROM=binding(ROM),
  original_header=raw[:16].hex(),existing_reference=binding(native),all_PRG_CHR_payload_bytes_exact=True,
  source_revision=COMMIT,tracked_worktree_clean=True,source_repo='https://github.com/Xkeeper0/smb2',
  original_mapping='MMC3 physical8KB0..15; variable pairs0/1..C/D at8000..BFFF; fixedE/F atC000..FFFF',
  requested_variant_to_native_id=[0,3,2,1],character_stats=stats,original_entries=routines,
  RAM={n:f'{labels[n]:04X}'for n in fields},source_jump_primitive_cases=jump,
  jump_scope='Original StartJump plus original Gravity/Integrator, real signed fractions and inputs; no terrain/fullnormalwrapper/NMI/PPU; return means ground-height crossing, not native landing',
  source_renderer_cases=records,preview=binding(picture),
  observed_player_CHR_pages=sorted(used_pages),
  art_scope='Actual RenderPlayer/LoadWorldCHR; source palette roles; preview world1overworld RGB only, not PPU/native/allareas. Odd eye tiles use actual inverted-MMC3 background pattern latches.',
  audio_storage=dict(source_bank4_5_end=f'{audio_end:04X}',packable_code_data_bytes=packed_audio,
   known_fill_hole_bytes=audio_end-0x8000-packed_audio,
   original_DPCM_bounding_bytes=7168,projection_adapter_not_included=True),
  audio_scope='Original bank4/5 complete engine+data plus fixedE C000..DC00 DPCM bounding region; exact packing and all RAM/host/DMC lifecycle still need closure audit',
  immutable_inputs=[binding(REPO/p)for p in ['README.md','config.asm','smb2.asm','src/ram.asm','src/defs.asm',
   'src/prg-0-1.asm','src/prg-2-3.asm','src/prg-4-5.asm','src/prg-6-7.asm','src/prg-a-b.asm','src/prg-e-f.asm','smb2.chr',
   'src/music/instruments.asm','src/music/dpcm-samples.asm','src/music/music-data.asm']]+[binding(p)for p in nls],
  tool=binding(__file__),limits=['No source/game edits, fresh build, cloned trees, RAM/PRG/CHR reservation or Mesen',
   'Earlier SMB1-in-SMB2 port is provenance aid only; its replacement physics and fireballs are not original SMB2 authority'])
 p=OUT/'audit.json';p.write_text(json.dumps(result,indent=2)+'\n')
 report=ROOT/'docs/qa/smb2-roster-source-2026-10-28.txt'
 handoff=dict(status='FROZEN_READONLY_ORIGINAL_SMB2_AUDIT_NO_RESERVATION_OR_IMPLEMENTATION',
  owned_files=[binding(__file__),binding(report)],outputs=[binding(p),binding(picture)],
  original_ROM=binding(ROM),original_existing_build=binding(native),original_payload_exact=True,
  source_revision=COMMIT,compiled_source_jump_primitive_cases=len(jump),compiled_source_render_cases=len(records),
  requested_variant_map=[0,3,2,1],original_player_chr_pages=sorted(used_pages),
  proposed_envelopes_only=dict(CORE=6144,ART=2048,CHR=12288,AUDIO_code_data_adapter=8192,DPCM_plan=8192,
   active_RAM=128,persistent_owner_gated_RAM=8),
  proposal_limits='No actual spans reserved; size estimates need complete translated caller/asset recipe and allocator review before implementation',
  parser_findings=['Actual native odd eye tileD5 uses background pattern-latch page25; initial class-page-only assumption rejected',
   'Actual charged branch overrides running before jump index; six launch entries plus separate quicksand and float bytes, not eight launch entries'],
  ROOT_next='Review source-supported gameplay/adaptations and actual bank/RAM proposal before any leaf implementation; native remains ROOT-owned')
 q=OUT/'handoff.json';q.write_text(json.dumps(handoff,indent=2)+'\n')
 print(json.dumps(dict(handoff=binding(q),audit=binding(p),preview=binding(picture),source_jumps=len(jump),render_cases=len(records)),indent=2))
if __name__=='__main__':main()
