"""Project the frozen Bowser kernel into real selected RAM3 host services."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load
P=R/'build/bowser-split-workers-v2';K=R/'build/bowser-source-core-v5'
O=R/'build/bowser-gameplay-component-v3';J=O/'joint';D=J/'bowser'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')

def main():
 assert not O.exists();h=json.loads((P/'handoff.json').read_text())
 for p,v in h['bindings'].items():assert sha(p)==v,p
 shutil.copytree(P/'joint',J)
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in['.s','.inc','.cfg']:write(p,p.read_text().replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()))
 state=(K/'state.inc').read_text().replace('; ABSTRACT ARENA ONLY. These are not granted host RAM addresses.','; Selected family27 RAM3 A-view only, original whole source fields retained.')
 state=re.sub(r'\$60([0-9a-f]{2})',lambda m:'$be'+m[1],state,flags=re.I)
 state+='''
BwPending=$be22
BwNativeY=$be23
BwOldX=$be24
BwPaletteAck=$be25
BwReady=$be26
BwPlayerKey=$be27
BwTier=$be28
BwHP=$be29
BwTemp=$be2a
BwShotSlot=$be2b
BwDrawY=$be2c
BwDrawX=$be2d
BwDrawFlip=$be2e
BwDrawPage=$be2f
BwPartBytes=$be30
BwRenderBuffer=$be40
BwShots=$be80
BwPersistent=$bf80
'''
 write(D/'state.inc',state)
 core=(K/'core.s').read_text().replace('.import BwWorldResolve','.export BwCoreFinish')
 core=core.replace('.segment "BW_CORE"','.segment "BW_IMAGE"').replace('sta $6000,x','sta BwVel,x')
 core=core.replace(' jsr BwWorldResolve          ; actual original order: integrate, detect, gravity',' lda #1\n sta BwPending\n rts\nBwCoreFinish:                ; resumed AFTER actual native terrain once')
 private=set(re.findall(r'(?m)^(\w+):',core));private={n for n in private if not n.startswith('Bw')}
 for n in sorted(private,key=len,reverse=True):core=re.sub(r'\b'+n+r'\b','BwCore_'+n,core)
 write(D/'core.s',core)
 host=(R/'tools/reference/bowser_host_cache_v2.s').read_text()
 targets=['BwMovement','BwGraphics','BwDrawShots','BwGraphics','BwNoop','BwInjury','BwStatus','BwDeathStart','BwDeath','BwVisible','BwHead','BwBody','BwAdder','BwBoxProfile','BwSide','BwConstruct','BwFullBox','BwGraphics','BwNoop','BwConstruct','BwPrepare','BwCacheDecline','BwCacheDecline','BwMature','BwPickup','BwFullPower','BwUi','BwBounce','BwHeadWithin','BwUi','BwNoop','BwBounce','BwNoop','BwPowerupTick','BwWeaponTail','BwCacheDecline']
 host=host.replace(' .word 0 ; builder replaces this two-byte marker with the real36JMP table','\n'.join(' jmp '+n for n in targets))
 host=host.replace(' sec\n sbc #8\n sta BwShots+4,x',' sta BwShots+4,x')
 host=host.replace(' sta BwShots+7,x\n lda BwShots+4,x\n sta BwShots+8,x',''' sta BwShots+7,x
 lda PseudoRandomBitReg,x
 and #3
 tay
 lda BwFlameTargetY,y
 sta BwShots+8,x''')
 host=host.replace('BwSpawnDone:rts','BwSpawnDone:rts\nBwFlameTargetY:.byte $90,$80,$70,$90')
 # Source3 flame has initial +$10 Yvelocity; the native-world support event
 # stops it after the original first floor landing. Both cases are literal
 # source state choices, not native Mario bouncing-fireball substitution.
 host=host.replace(' lda BwVariant\n bne BwFireOne',''' lda BwVariant
 bne BwFireOne
 lda BwShots+6,x
 bne BwFireThreeX
 inc BwShots+4,x
 jsr BwFireFloor
BwFireThreeX:''')
 host=host.replace('BwFireContact:\n jsr BwFireActors','''BwFireContact:
 lda BwVariant
 beq BwFireActorsNow
 lda BwShots+4,x
 cmp BwShots+8,x
 beq BwFireActorsNow
 bcs BwFireTargetUp
 inc BwShots+4,x
 bne BwFireActorsNow
BwFireTargetUp:dec BwShots+4,x
BwFireActorsNow:
 jsr BwFireActors''')
 host=host.replace(' stx R1\n jsr HandleEnemyFBallCol',''' stx R1
 lda ObjectOffset
 pha
 stx ObjectOffset
 jsr HandleEnemyFBallCol''').replace(' ldx BwShotSlot\n lda #0\n sta BwShots,x\n rts',' pla\n sta ObjectOffset\n ldx BwShotSlot\n lda #0\n sta BwShots,x\n rts')
 host+='''
; Actual current16x13 native block buffer, absolute world/page lookup. The
; projectile's own center/bottom is used; player coordinates are untouched.
BwFireFloor:
 lda BwShots+2,x
 clc
 adc #8
 sta R5
 lda BwShots+3,x
 adc #0
 and #1
 tay
 lda #>Block_Buffer_1
 sta R7
 lda R5
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 lda BwShots+4,x
 clc
 adc #16
 bcs BwFireFloorDone
 cmp #32
 bcc BwFireFloorDone
 cmp #240
 bcs BwFireFloorDone
 and #$f0
 sec
 sbc #32
 tay
 lda (R6),y
 tay
 lda MTileAttribute,y
 and #$80
 beq BwFireFloorDone
 lda BwShots+4,x
 and #$f0
 sta BwShots+4,x
 inc BwShots+6,x
BwFireFloorDone:rts
'''
 write(D/'host.s',host)
 shutil.copyfile(K/'art.s',D/'art.s');write(D/'art.s',(D/'art.s').read_text().replace('.segment "BW_ART"','.segment "BW_IMAGE"'))
 native=['AreaType','SelectedCharacter','OperMode','OperMode_Task','FamilyMainCommit','GamePauseStatus','TimerControl','FmAlts','CurrentPlayer','NumberofLives','PlayerStatus','PlayerSize','CrouchingFlag','PlayerFacingDir','Player_XSpeedAbsolute','Player_X_Scroll','Player_Y_MoveForce','Player_Rel_XPos','Player_Rel_YPos','InjuryTimer','GuestBodyStompAllowed','GuestBodyNoStomp','GuestPowerupOld','GuestPowerupDisplay','GuestPowerupTarget','GuestPowerupUpdate','MarioSourceBeginFreeze','MarioSourcePowerupCollision','Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue','MmDeathFlag','KillPlayer','EraseEnemyObject','SetupFloateyNumber','NativePlayerDeath','BlockBufferColli_Head','BlockBufferColli_Side','BoundingBox_UL_Corner','BoundingBox_LR_Corner','PowerUpType','ScreenLeft_X_Pos','ScreenLeft_PageLoc','SecondaryHardMode','PseudoRandomBitReg','HandleEnemyFBallCol','MetaspriteRenderLoop','ObjectMetasprite','Player_SprAttrib','SmPosePtr','SmChrBank','CurrentCHRBank','X5ChrMode','CurrentBankC','X5SetPhysicalChr','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','BwColors','METASPRITE_SAMUS_BODY','BlockBufferAddr','Block_Buffer_1','MTileAttribute','StarInvincibleTimer']
 zp=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_X_Speed','Player_Y_Speed','Player_State','SavedJoypadBits','GameEngineSubroutine','FrameCounter','Enemy_Flag','Enemy_State','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','ObjectOffset','R0','R1','R2','R3','R4','R5','R6','R7']
 write(D/'host-imports.inc','.import '+','.join(native)+'\n.importzp '+','.join(zp)+'\n.import Bw1Step,Bw3Step,BwCoreFinish\n.import Bw1OPEN1RIGHT,Bw1OPEN2RIGHT,Bw1CLOSED1RIGHT,Bw1CLOSED2RIGHT,Bw3PoseLo,Bw3PoseHi,Bw3PosePages\n')
 # Export genuine source metadata symbols, not numeric DBG aliases.
 art=(D/'art.s').read_text();write(D/'art.s','.export Bw1OPEN1RIGHT,Bw1OPEN2RIGHT,Bw1CLOSED1RIGHT,Bw1CLOSED2RIGHT,Bw3PoseLo,Bw3PoseHi,Bw3PosePages\n'+art)
 # Standalone typed rows remain the v2 guarded transport while the sibling
 # prepares the jointly funded common selector. This worker is real in ROM.
 with (D/'check.s').open('a')as f:f.write('''
.import VRAM_Buffer1_Offset,VRAM_Buffer1
.export BwColors
BwColors:
 ldx VRAM_Buffer1_Offset
 cpx #78
 bcs BwColorsDone
 ldy #0
BwColorsCopy:
 lda BwColorPacket,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #6
 bcc BwColorsCopy
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
BwColorsDone:rts
BwColorPacket:.byte $3f,$11,3,$1a,$30,$27
.assert *<=$b600,lderror,"Exact A84 Bowser partition with body palette"
''')
 cfg=(D/'image.cfg').read_text();write(D/'image.cfg',cfg)
 # RAM3 source/cache image has a dedicated selected-owner state slab and
 # two4B player records. It never overlaps code or the16B cookie.
 write(D/'image-tail.s','''.segment "BW_IMAGE"
.import BwCacheServices
.res $be00-*, $ff
.res $180,$ff
.res 8,$ff
.res $58,$ff
.res 16,0
.res 16,$ff
.assert *=$c000,lderror,"Exact8KB code/state/cookie image"
''')
 ca=str(R/'tools/Windows/cc65/bin/ca65.exe');ld=str(R/'tools/Windows/cc65/bin/ld65.exe')
 recipes=[]
 def run(n,c):
  v=validate(c,J,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True);write(O/(n+'.json'),json.dumps(dict(command=c,validation=v,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr);recipes.append(n)
 def asm(n):run(n+'-build',[ca,'-g','-I',str(D),'--create-full-dep',str(D/(n+'.dep')),'-o',str(D/(n+'.o')),str(D/(n+'.s'))])
 for n in ['host','core','art']:asm(n)
 # Tail length is resolved by a genuine linker start, not guessed assembly
 # location: make it one object with includes so the reservation is absolute.
 merged='.include "host.s"\n.include "core.s"\n.include "art.s"\n.include "image-tail.s"\n'
 # Separate objects avoid redefining each shared field; linker BSS reservations
 # are placed explicitly instead of textual inclusion.
 write(D/'image-tail.s','.segment "BW_STATE"\n.res $1e0,$ff\n.segment "BW_COOKIE_GAP"\n.res 16,0\n.res 16,$ff\n')
 cfg='MEMORY { M:start=$a000,size=$2000,type=ro,bank=3,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { BW_IMAGE:load=M,type=ro; BW_STATE:load=M,type=ro,start=$be00; BW_COOKIE_GAP:load=M,type=ro,start=$bfe0; }\n'
 write(D/'image.cfg',cfg);asm('image-tail')
 # For this independent cache link, borrow only actual exported native
 # producers from the parent full link; no synthetic PC aliases are used.
 # The current full source will be recompiled with any missing zero-byte
 # exports and all real native object imports rebound below.
 exports=[n for n in native+zp if n!='BwColors']
 entry=(J/'entrypoint.s').read_text();write(J/'entrypoint.s','.export '+','.join(exports)+'\n'+entry)
 cmd=json.loads((J/'main-build.json').read_text())['command'][:]
 cmd[1:1]=['-I',str(J),'-I',str(J/'src')]
 for flag in ['-o','--create-full-dep','--create-dep']:
  if flag in cmd:cmd[cmd.index(flag)+1]=str(J/('main.o'if flag=='-o'else'main.dep'))
 cmd[-1]=str(J/'entrypoint.s');run('main-build',cmd)
 # Current main opcode bytes are unchanged by the genuine export addition.
 # The complete native objects are linked once, with a private RAM3 image
 # file distinct from the unchanged FF ram3.bin output.
 private=(J/'private.cfg').read_text()
 private=private.replace('BW_IMAGE:load=BW_IMAGE_MEM,type=ro;','BW_IMAGE:load=BW_IMAGE_MEM,type=ro;\nBW_STATE:load=BW_IMAGE_MEM,type=ro,start=$be00;\nBW_COOKIE_GAP:load=BW_IMAGE_MEM,type=ro,start=$bfe0;')
 write(J/'private.cfg',private)
 # The old image is replaced by real host+kernel+all originalbody metadata.
 # Rebuild the palette source first, then source-image fingerprint, stream.
 for n in ['check','load','copy','retire','router','preview']:asm(n)
 link=json.loads((P/'actual-host-link.json').read_text())['command'][:]
 oldmain=[x for x in link if x.endswith('/main.o')or x.endswith('\\main.o')];assert len(oldmain)==1
 link[link.index(oldmain[0])]=str(J/'main.o')
 for i,x in enumerate(link):
  if x.startswith(str(P/'joint')):link[i]=str(J/Path(x).name)if Path(x).parent==P/'joint'else x.replace(str(P/'joint'),str(J))
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
 if '--ld-args'in link:
  i=link.index('--ld-args')+1;a=link[i].split(',')
  for k in range(1,len(a),2):a[k]=str(J/Path(a[k]).name)
  link[i]=','.join(a)
 oldimage=str(D/'image.o');assert oldimage in link;link.remove(oldimage)
 link += [str(D/(n+'.o'))for n in ['host','core','art','image-tail']]
 run('initial-link',link)
 image=(J/'bowser.bin').read_bytes();assert len(image)==8192
 (D/'cookie.bin').write_bytes(bytes([167,27,0,2])+hashlib.sha256(image).digest()[:12])
 # Keep source-built body pages and add original nativeflame patterns in the
 # three spare pairs28..30 of every body page. Original body pixels unchanged.
 b=load(P/'joint/candidate.nes');pos=16+128*8192+0
 rec=b['syms']['MetaspriteBowserFlame'];seg=b['segs'][rec['seg']];off=int(seg['ooffs'],0)+int(rec['val'],0)-int(seg['start'],0);record=b['raw'][off:off+13]
 body=bytearray((D/'body.chr').read_bytes())
 enemy=(R/'chr/mmc5/sprites_enemies.chr').read_bytes()
 for i in range(3):
  tile=record[1+i*4]&0x3e;pair=enemy[2048+tile*16:2048+tile*16+32];assert len(pair)==32
  for page in range(3):assert not any(body[page*1024+(28+i)*32:page*1024+(29+i)*32]);body[page*1024+(28+i)*32:page*1024+(29+i)*32]=pair
 (D/'body.chr').write_bytes(body)
 for n in ['check','stream']:asm(n)
 run('final-link',link)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes')
 out=load(J/'candidate.nes');old=load(P/'joint/candidate.nes')
 assert all(out['syms'][n]['val']==z['val']for n,z in old['syms'].items()if not n.startswith('Bw'))
 for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n)
 report=dict(status='REAL_BOWSER_GAMEPLAY_COMPONENT_UPSTREAM_INGRESS_PENDING',source=True,candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),native=False,admitted=False,
  kernel='Frozen source instruction projection; split at original World callback. Native terrain then source continuation at genuine weapon-tail34.',
  source_file=str(D/'host.s'),cache_bytes=8192,source_state=['BE00','BFE0'],cookie=list((D/'cookie.bin').read_bytes()),
  WIP_adaptations=['Native big-player16x32 contact geometry with complete40/48px body artwork overhang','2friendly original-speed flames using original nativeSMB flame art/P2','Original34/5bossHP adapted to1HP nativecontact; native mushroom/flower tiers/healing'],
  pending=['Actual mixedROMcold/service ingress, scene/menu chain, Startmask','NaturalMain/terrain/render/control/ISR proof before rootnative'],
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/reference/bowser_host_cache_v2.s',P/'handoff.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'bowser.bin',D/'cookie.bin',J/'private.cfg']})
 write(O/'source-stage.json',json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
