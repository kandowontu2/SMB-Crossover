"""Original Bowser art and executable source-native SMB3 movement/control leaf.

Abstract arena only: no host PRG/CHR/RAM placement, shared hooks or menu write.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,location
O=R/'build/bowser-source-core-v1';P=R/'build/coherent62-lives-fixes-v1/joint';S=R/'build/smb3-bowser-source-assets-v1';D=R/'build/source-acquisition/dk-bowser-2026-10-29/smb3/source/PRG'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def main():
 assert not O.exists();O.mkdir()
 assert sha(S/'handoff.json')=='8fdc8351cd53f6e90ef47dc5ccb489d904744f43b19dc2f17c1d4dd2728033b7'
 b=load(P/'candidate.nes');original=Path('C:/NES/Super Mario Bros. (World).nes');rom=original.read_bytes();originalchr=rom[32784:];native=(R/'chr/mmc5/sprites_enemies.chr').read_bytes()
 records={};pairs=[];origins=[]
 for side in ['RIGHT','LEFT']:
  for mouth,feet in [(m,f)for m in ['OPEN','CLOSED']for f in [1,2]]:
   record=[]
   for label,dx,dy in [('FRONT_MOUTH_'+mouth,16 if side=='RIGHT'else 0,0),('REAR_WALK_'+str(feet),0 if side=='RIGHT'else 16,8)]:
    at=location(b,'MetaspriteData_BOWSER_'+label+'_'+side);n=b['raw'][at];rec=b['raw'][at+1:at+1+n]
    for t,a,y,x in zip(rec[0::4],rec[1::4],rec[2::4],rec[3::4]):
     assert t&1 and t<64
     pat=native[2048+(t&62)*16:2048+(t&62)*16+32];assert len(pat)==32
     if pat not in pairs:pairs.append(pat)
     halves=[]
     for h in range(2):
      hits=[32784+i*16 for i in range(512)if originalchr[i*16:(i+1)*16]==pat[h*16:(h+1)*16]];assert hits,(label,t,h)
      halves.append(hits)
     origins.append(dict(label=label,side=side,tile=t,original_8x8_ROM_offsets=halves))
     record += [pairs.index(pat)*2,a&0xc0,(y+dy)&255,(x+dx)&255]
   records[f'Bw1{mouth}{feet}{side}']=[len(record)]+record
 assert len(pairs)<=32
 art1=b''.join(pairs)+bytes(1024-32*len(pairs));(O/'bowser1.chr').write_bytes(art1)
 source3=json.loads((S/'handoff.json').read_text());assert source3['used_1KB_pages']==2
 (O/'bowser3.chr').write_bytes((S/'bowser3.chr').read_bytes()[:2048])
 art=['; Authenticated native SMB1 full body: front + rear with original Y+8.', '.segment "BW_ART"','.export BwArtStart,BwArtEnd','BwArtStart:']
 for n,r in records.items():art +=[n+': .byte '+','.join(map(str,r))]
 art+=['Bw1Palette: .byte $0f,$1a,$30,$27']
 # Reuse original SMB3 descriptors, never regenerate geometry from the PNG.
 s=(S/'bowser3-art.inc').read_text();s=s.replace('.segment "BOWSER_ART"','.segment "BW_ART"');art +=[s,'BwArtEnd:'];write(O/'art.s','\n'.join(art)+'\n')
 # Literal original Object_AddVelFrac instruction stream. Only names and
 # absolute indexed data operands are projected; original math/flags intact.
 text=(D/'prg000.asm').read_text();start=text.index('Object_AddVelFrac:\n');end=text.index('\n\tRTS',start)+len('\n\tRTS');originalblock=text[start:end]
 transformed=[]
 names={'Object_AddVelFrac':'Bw3AddVelFrac','Objects_XVelFrac':'BwFrac','Objects_XVel':'BwVel','Objects_XHi':'BwPage','Objects_X':'BwPos','Object_VelCarry':'BwCarry'}
 for line in originalblock.splitlines():
  line=line.split(';',1)[0].strip()
  if not line:continue
  for old,new in names.items():line=re.sub(r'\b'+old+r'\b',new,line)
  line=line.replace('<','')
  if line.startswith('ADD '):transformed+=[' clc',' adc '+line[4:]]
  elif line.startswith('BLT '):transformed+=[' bcc '+line[4:]]
  else:transformed.append(' '+line if not line.endswith(':')else line)
 write(O/'source-addvel-original.asm',originalblock+'\n')
 state='''; ABSTRACT ARENA ONLY. These are not granted host RAM addresses.
BwVel=$6000
BwFrac=$6004
BwPos=$6008
BwPage=$600c
BwCarry=$6010
BwPrevious=$6011
BwFresh=$6012
BwInput=$6013
BwGrounded=$6014
BwFacing=$6015
BwPose=$6016
BwBreath=$6017
BwSlam=$6018
BwEmit=$6019
BwImpact=$601a
BwFrame=$601b
BwStateEnd=$601c
'''
 write(O/'state.inc',state)
 core='''; Playable input adaptation around original SMB3 object motion.
; A is real NES controller bits. Host import/export uses top-left source
; coordinates; BwWorldResolve must settle native feet/head/sides BEFORE
; gravity. It owns BwGrounded and clamps fractions/velocities on contact.
; Only the caller decides pause/death/foreign dispatch and commits state.
.setcpu "6502"
.include "state.inc"
.import BwWorldResolve
.export Bw3Step,Bw3AddVelFrac,BwCoreStart,BwCoreEnd,Bw3Fresh
.segment "BW_CORE"
BwCoreStart:
Bw3Fresh:
 lda #0
 ldx #27
:sta $6000,x
 dex
 bpl :-
 lda #1
 sta BwFacing
 rts
Bw3Step:
 sta BwInput
 eor BwPrevious
 and BwInput
 sta BwFresh
 lda BwInput
 sta BwPrevious
 lda #0
 sta BwEmit
 sta BwImpact
 sta BwVel
 lda BwInput
 and #3
 cmp #1
 beq Right
 cmp #2
 bne HorizontalDone
 lda #2
 sta BwFacing
 lda #$e8                   ; authored left control: source velocity -$18
 bne SetX
Right:
 lda #1
 sta BwFacing
 lda #$18                   ; source Bowser_XVelByDist entry2, 1.5px/update
SetX:sta BwVel
HorizontalDone:
 lda BwGrounded
 beq Air
 lda BwFresh
 and #$80
 beq JumpDone
 lda #$a0                   ; original Bowser jump velocity -$60 in4.4FP
 sta BwVel+1
 lda #0
 sta BwGrounded
JumpDone:
 jmp FireInput
Air:
 lda BwFresh
 and #$80
 beq FireInput
 lda BwInput
 and #4
 beq FireInput
 lda #10                    ; original AlignAndFall wait
 sta BwSlam
 lda #$e0                   ; original AlignAndFall hop -$20
 sta BwVel+1
 lda #0
 sta BwVel
FireInput:
 lda BwBreath
 bne Breathe
 lda BwFresh
 and #$40
 beq Motion
 lda #$3f                   ; original Bowser_Counter1 timeline
 sta BwBreath
Breathe:
 dec BwBreath
 lda BwBreath
 lsr
 lsr
 lsr
 lsr
 and #7
 tay
 lda HopFrames,y
 sta BwPose
 lda BwBreath
 cmp #$10                   ; original single BreatheFire call point
 bne Motion
 inc BwEmit                 ; caller spawns actual source fire in owner pool
Motion:
 ldx #0
 jsr Bw3AddVelFrac
 ldx #1
 jsr Bw3AddVelFrac
 jsr BwWorldResolve          ; actual original order: integrate, detect, gravity
 lda BwGrounded
 beq Falling
 lda BwSlam
 beq Landed
 inc BwImpact               ; caller consumes genuine floor-smash contact
 lda #0
 sta BwSlam
Landed:
 lda #0
 sta BwVel+1
 sta BwFrac+1
 jmp Pose
Falling:
 lda BwSlam
 beq Gravity
 dec BwSlam
 lda #0
 sta BwVel
Gravity:
 lda BwVel+1
 bmi AddGravity
 cmp #$50                   ; original jumping terminal threshold
 bcs Pose
AddGravity:
 inc BwVel+1                ; literal original Bowser jumping gravity +3
 inc BwVel+1
 inc BwVel+1
Pose:
 lda BwBreath
 bne Done
 lda #0
 sta BwPose
 lda BwGrounded
 beq Done
 lda BwFrame
 and #$10
 beq Done
 lda #5                     ; original look/walk frame, no fabricated art
 sta BwPose
Done:
 inc BwFrame
 rts
HopFrames:.byte $00,$00,$03,$02,$00,$00,$00,$00
'''
 write(O/'core.s',core+'\n'+'\n'.join(transformed)+'\nBwCoreEnd:\n')
 write(O/'arena.s','''; Isolated callback ABI bench, never a host implementation.
.setcpu "6502"
.include "state.inc"
.export BwWorldResolve
.segment "BW_CALLBACK"
BwWorldResolve:
 lda BwPage+1
 bne :+
 lda BwPos+1
 cmp #176
 bcc :+
 lda BwVel+1
 bmi :+
 lda #176
 sta BwPos+1
 lda #1
 sta BwGrounded
:rts
''')
 write(O/'arena.cfg','''MEMORY { CODE:start=$8000,size=$2000,type=ro,file=%O,fill=yes; }
SEGMENTS { BW_CORE:load=CODE,type=ro; BW_ART:load=CODE,type=ro; BW_CALLBACK:load=CODE,type=ro; }
''')
 compiler=R/'tools/Windows/cc65/bin/ca65.exe';commands=[]
 for name in ['core','art','arena']:
  commands.append((name+'-build',[str(compiler),'-g','-I',str(O),'--create-full-dep',str(O/(name+'.dep')),'-o',str(O/(name+'.o')),str(O/(name+'.s'))]))
 commands.append(('arena-link',[str(compiler.with_name('ld65.exe')),'-C',str(O/'arena.cfg'),'-o',str(O/'arena.bin'),'-Ln',str(O/'arena.lbl'),'--dbgfile',str(O/'arena.dbg'),'-m',str(O/'arena.map')]+[str(O/(n+'.o'))for n in ['core','art','arena']]))
 write(O/'output-preflight.json',json.dumps([dict(name=n,validation=validate(c,O,cwd=R))for n,c in commands],indent=2)+'\n')
 for n,c in commands:
  validate(c,O,cwd=R);z=subprocess.run(c,cwd=R,capture_output=True,text=True);write(O/(n+'.json'),json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr)
 q=dict(source=True,host=False,native=False,status='SOURCE_NATIVE_SMB3_INTEGRATOR_WITH_AUTHORED_PLAYER_CONTROL_ABSTRACT_CALLBACK_ONLY',SMB1_original_ROM=dict(path=str(original),sha256=sha(original)),SMB1_original_tile_half_matches=origins,SMB1_packed_pairs=len(pairs),SMB1_packed_pages=1,SMB3_original_source=sha(S/'handoff.json'),SMB3_packed_pages=2,total_body_CHR_pages=3,scope='SMB1 original art only, no SMB1 physics yet. SMB3 original velocity semantics/control kernel compiled; real host terrain/fire/hit/progression/render/lifecycle remain integration boundaries. No lease/native/admission.',bindings={str(p.resolve()):sha(p)for p in [Path(__file__),S/'handoff.json',D/'prg000.asm',D/'prg001.asm',P/'candidate.nes',P/'candidate.dbg']+list(O.glob('*'))if p.is_file()})
 write(O/'source-stage.json',json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','SMB1_original_tile_half_matches']}),flush=True)
if __name__=='__main__':main()
