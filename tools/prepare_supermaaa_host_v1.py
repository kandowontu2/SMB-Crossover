"""Private full-source ac126 successor. Frozen source audit remains unchanged."""
from pathlib import Path
import hashlib,json,random,re,subprocess,sys,difflib,math
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools/audit')]
from sunny_integrated_controls_v1 import *
P=R/'build/pit-retold-host-v3';O=R/'build/supermaaa-host-v1'
SOURCE=R/'build/source-acquisition/super-maaa-author-2026-10-29/source'

def once(s,a,z):
 assert s.count(a)==1,(a[:120],s.count(a));return s.replace(a,z)

def asset_data(b):
 raw=(SOURCE/'chr/lanky_mario.chr').read_bytes()
 labels={m[2]:int(m[1],16)for l in(R/'build/supermaaa-neck-audit-v1/body-native.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([\da-fA-F]+) \.(\S+)',l))}
 source=(R/'build/supermaaa-neck-audit-v1/body-native.bin').read_bytes()
 at=labels['PlayerGraphicsTable']-labels['RenderPlayerSub'];tiles=source[at:at+208]
 heads=list((R/'build/supermaaa-neck-audit-v1/draw-native.bin').read_bytes()[-26:])
 frames=[(tuple(tiles[i*8:i*8+8]),heads[i]//4,i)for i in range(26)]
 native=[23]*63
 def frame(v,head,base):
  q=(tuple(v),head,base)
  if q not in frames:frames.append(q)
  return frames.index(q)
 for name,s in b['syms'].items():
  if not name.startswith('METASPRITE_')or'MARIO'not in name and'SMALL_FIRE'not in name:continue
  ident=address(b,name)
  if not 1<=ident<63:continue
  small='SMALL_'in name
  base=23 if small else 25
  for word,index in [('WALKING_1',0),('WALKING_2',1),('WALKING_3',2),('SKIDDING',3),('JUMPING',4),('CROUCHING',10),('SWIMMING_1',5),('SWIMMING_2',6),('SWIMMING_3',7),('CLIMBING_1',8),('CLIMBING_2',9)]:
   if word in name:base=index+12 if small and index<10 else index
  if 'DEATH'in name:base=22
  if 'GROW_INTERMEDIATE'in name:base=24
  v=list(tiles[base*8:base*8+8]);head=heads[base]//4;source_base=base
  if 'FIRE_'in name and'CLIMBING'not in name:
   # Original throw replaces three rows while moving, four when standing.
   throw=list(tiles[11*8:12*8]);moving=any(t in name for t in['WALKING','SKIDDING','JUMPING','SWIMMING'])and'STILL'not in name
   v=throw[:6]+v[6:]if moving else throw
   head=0;source_base=11
  if '_HOLD'in name and'SWIMMING'in name:
   # Native host HOLD is selected on original FrameCounter bit2==0.
   v[6]=70 if small else 49
  native[ident]=frame(v,head,source_base)
 def pattern(tile,flip=False):
  v=raw[tile*16:tile*16+16]
  return bytes(int(f'{x:08b}'[::-1],2)for x in v)if flip else v
 def pair(a,z,ha=False,hz=False):
  # Source ChkForPlayerAttrib mirrors the right bottom tile in its
  # standing/crouch/death records. A 16-high pair with different half-flips
  # must carry that exact transformed pattern; no whole-pair substitute.
  if a==252:ha=False
  if z==252:hz=False
  flag=64 if ha and(hz or z==252)else 0
  return (pattern(a,ha and not flag)+pattern(z,hz and not flag),flag)
 neck={pair(16,16)[0],pair(16,252)[0]}
 parts=[];requirements=[]
 for v,head,base in frames:
  def p(row,col,following=None):
   mirror=lambda r:col==1 and(r==3 and base in[10,22,23,24,25]or r==2 and base==22)
   return pair(v[row*2+col],v[following*2+col]if following is not None else 252,mirror(row),mirror(following)if following is not None else False)
  hr=head//2
  pairs=[p(hr,0),p(hr,1)]
  mid=head+2
  for col in range(2):pairs.append(p(mid//2,col,mid//2+1 if mid+2<8 else None)if mid<8 else None)
  for col in range(2):pairs.append(p(3,col)if head==0 else None)
  parts.append(pairs);requirements.append(set(x[0]for x in pairs if x is not None)|neck)
 best=None;rng=random.Random(0x4d414141)
 for attempt in range(1500):
  order=list(range(len(frames)))
  if attempt:rng.shuffle(order)
  order.sort(key=lambda i:-len(requirements[i]))
  bins=[];groups=[]
  for i in order:
   choices=[(len(requirements[i]-v),j)for j,v in enumerate(bins)if len(v|requirements[i])<=32]
   if choices:_,j=min(choices);bins[j]|=requirements[i];groups[j].append(i)
   else:bins.append(set(requirements[i]));groups.append([i])
  score=(len(bins),sum(map(len,bins)))
  if best is None or score<best[0]:best=(score,bins,groups)
  if score[0]<=3:break
 if best[0][0]>3:
  universe=sorted(set().union(*requirements));masks=[sum(1<<universe.index(p)for p in v)for v in requirements]
  unique=list(dict.fromkeys(masks));found=None
  def unions(a):
   v=[0,0,0]
   for i,k in enumerate(a):v[k]|=unique[i]
   return v
  def energy(v):
   sizes=[m.bit_count()for m in v]
   return sum(sizes)+100*sum(max(0,n-32)**2 for n in sizes)
  for restart in range(12):
   a=[rng.randrange(3)for _ in unique];v=unions(a);cost=energy(v)
   for it in range(25000):
    i=rng.randrange(len(a));old=a[i];a[i]=rng.randrange(3)
    new=unions(a);value=energy(new);temp=max(.1,60*(1-it/25000))
    if value<=cost or rng.random()<math.exp(min(0,(cost-value)/temp)):v,cost=new,value
    else:a[i]=old
    if all(m.bit_count()<=32 for m in v):found=(a[:],v);break
   if found:break
  if found:
   a,v=found;bins=[{universe[i]for i in range(len(universe))if m>>i&1}for m in v]
   groups=[[i for i,m in enumerate(masks)if a[unique.index(m)]==k]for k in range(3)]
   best=((3,sum(map(len,bins))),bins,groups)
 score,bins,groups=best
 proof=dict(original_frames=26,total_exact_combinations=len(frames),pages=len(bins),pair_counts=list(map(len,bins)),native_map=native,source_frames=frames,groups=groups,minimum_found_not_global_optimum=True)
 (O/'asset-layout.json').write_text(json.dumps(proof,indent=2)+'\n')
 assert len(bins)<=3,('Measured art does not fit approved3pages',score)
 banks=[sorted(v)for v in bins];page={i:j for j,g in enumerate(groups)for i in g}
 pixels=b''.join(b''.join(v).ljust(1024,b'\0')for v in banks).ljust(3072,b'\0')
 rows=[]
 def table(name,values):rows.extend([name+':',' .byte '+','.join(str(x)for x in values)])
 table('MaaFrameMap',native);table('MaaHeads',[h*4 for _,h,_ in frames]);table('MaaPages',[45+page[i]for i in range(len(frames))])
 table('MaaTiles',[255 if p is None else(2*banks[page[i]].index(p[0]))|p[1]for i,partsrow in enumerate(parts)for p in partsrow])
 table('MaaNeckRepeat',[2*v.index(pair(16,16)[0])for v in banks]);table('MaaNeckOdd',[2*v.index(pair(16,252)[0])for v in banks])
 return pixels,'\n'.join(rows)+'\n',proof

def main():
 assert not(O/'handoff.json').exists(),'Frozen means immutable'
 (O/'src').mkdir(parents=True,exist_ok=True)
 parent=json.loads((P/'closure.json').read_text())
 for p,h in parent['actual_dependencies'].items():assert sha(p)==h,p
 b=scoped_load(P/'candidate.nes');assert sha(P/'candidate.nes')=='ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
 assert b['raw'][16+68*8192+0x1b20:16+68*8192+0x1f20]==bytes([255])*1024
 assert b['raw'][16+66*8192+0x1680:16+66*8192+0x19a8]==bytes([255])*808
 assert b['raw'][16+9*8192+0x1fe1:16+9*8192+0x1fef]==bytes([255])*14, 'Approved BILL_BODY_COLD growth must be real FF'
 assert b['raw'][1048592+813*1024:1048592+816*1024]==bytes(3072)
 pixels,data,art=asset_data(b);(O/'maaa.chr').write_bytes(pixels)
 overlays={};preimages={}
 def change(name,path,fn):
  before=Path(path).read_text();after=fn(before)
  preimages[name]=dict(path=str(Path(path).resolve()),sha256=sha(path),text=before)
  overlays[name]=after;(O/'src'/name).write_text(after)
 timer_source=(R/'src/game.s').read_text();timer=timer_source[timer_source.index('RunGameTimer:'):timer_source.index('ProcessWhirlpools:')]
 timer=once(timer,'RunGameTimer:','.proc MaaTimer')
 timer=once(timer,'  sta GameTimerCtrlTimer\n','''  sta GameTimerCtrlTimer
  jsr MaaOwner
  bne MaaTimerUnchanged
  lda MaaaLength
  cmp #160
  bcs MaaTimerUnchanged
  adc #1
  sta MaaaLength
MaaTimerUnchanged:
''')+'.endproc\n'
 engine=(R/'src/metasprite_engine.s').read_text()
 reservation=engine[engine.index('.proc PlayerOAMReservation'):engine.index('.endproc',engine.index('.proc PlayerOAMReservation'))+len('.endproc')]
 reservation=reservation.replace('.proc PlayerOAMReservation','''.proc MaaReservation
 php
 pha
 jsr MaaOwner
 bne Legacy
 pla
 plp
 lda #24
 ldx #0
 rts
Legacy:pla
 plp''')
 collision=(R/'src/collision.s').read_text();sa=collision.index('HandleStompedShellE:');sz=collision.index('SBnce:',sa)
 stomp_prefix=collision[sa:sz]
 body=stomp_prefix[stomp_prefix.index('       lda #$04'):]
 stomp='''.proc MaaStomp
 php
 pha
 jsr MaaOwner
 bne Native
 lsr MaaaLength
Native:pla
 plp
 jsr InventoryStompDropHook
'''+body+' jmp SBnce\n.endproc\n'
 core=(R/'tools/reference/supermaaa_host_core_v1.s').read_text().replace('__TIMER__',timer).replace('__STOMP__',stomp).replace('__RESERVATION__',reservation).replace('__ART_DATA__',data).replace('__CHR__',(O/'maaa.chr').as_posix())
 # Imported names are actual linked parent symbols; never guessed addresses.
 defs=set(re.findall(r'^\s*(?:\.proc\s+)?([A-Za-z_]\w*)\s*:',core,re.M))|set(re.findall(r'^\.proc\s+(\w+)',core,re.M))|{'MaaaLength'}
 asm_only='\n'.join(line.split(';',1)[0]for line in core.splitlines())
 asm_only=re.sub(r'"[^"\n]*"','',asm_only)
 tokens=set(re.findall(r'\b[A-Za-z_]\w*\b',asm_only));imports=sorted(n for n in tokens if n in b['syms']and n not in defs and n not in {'Target','Bank','Tail','ENABLE_CROSSOVER','MOUSE_DISPLAY_CURSOR'}and not n.startswith('LOCAL-MACRO'))
 external=[]
 for n in imports:external.append(('.importzp 'if address(b,n)<256 else'.import ')+n)
 core=core.replace('__IMPORTS__','\n'.join(external)+'\n.import MaaOwner\n')
 (O/'component.s').write_text(core)
 resident='''
; Reclaimed original88B timer span; all external resident entries remain.
.proc MaaRenderGate
 tya
 bne Legacy
 jsr MaaOwner
 bne Legacy
 lda #68|$80
 sta CurrentBankC
 sta $5116
 jmp MaaBodyDraw
Legacy:jmp RlNativeRenderDispatch
.endproc
.proc MaaLagChrGuard
 lda SelectedCharacter
 bne Skip
 lda MarioVariant
 cmp #2
 bne Native
Skip:sec
 rts
Native:clc
 rts
.endproc
.proc MaaTail
 jsr MaaIndirect
 jsr MaaOwner
 bne Legacy
 lda ObjectMetasprite
 beq Legacy
 lda #68|$80
 sta CurrentBankC
 sta $5116
 jmp MaaDrawNeck
Legacy:lda #$f8
 rts
.endproc
MaaIndirect:jmp (M0)
'''
 old_timer_bytes=address(b,'ProcessWhirlpools')-address(b,'RunGameTimer')
 def game_edit(s):
  a=s.index('RunGameTimer:');z=s.index('ProcessWhirlpools:')
  return s[:a]+'.if ::ENABLE_MMC5_EXPANDED\nRunGameTimer:\n farcall MaaTimer,jmp\n'+resident+' .res '+str(old_timer_bytes)+'-(*-RunGameTimer),$ea\n.else\n'+s[a:z]+'.endif\n'+s[z:]
 change('game.s',R/'src/game.s',game_edit)
 # Real post-feet hook, approved15B PLAYER growth; native inputs unchanged.
 def player_edit(s):
  s=once(s,'  jsr PlayerBGCollision       ;do collision detection and process',''' .if ::ENABLE_MMC5_EXPANDED
  farcall MaaAfterBG
 .else
  jsr PlayerBGCollision
 .endif ; genuine post-feet neck coin producer''')
  a=s.index('.proc PlayerLoseLife');z=s.index('  bpl StillInGame',a)
  old=s[a:z]
  prefix=old[old.index('\n')+1:]
  assert address(b,'PlayerLoseLife::StillInGame')>address(b,'PlayerLoseLife')
  # Genuine16B prologue ->18B farcall; record this additional2B PLAYER move.
  assert address(b,'PlayerLoseLife::StillInGame')-address(b,'PlayerLoseLife')==29
  s=s[:a]+'.proc PlayerLoseLife\n.if ::ENABLE_MMC5_EXPANDED\n farcall MaaLifePrefix\n.else\n'+prefix+'.endif\n'+s[z:]
  s=once(s,'  farcall LmBoundingBoxGate','  farcall MaaBox')
  return s
 change('player.s',R/'build/kamikaze-mario-host-v4/overlay/src/player.s',player_edit)
 def engine_edit(s):
  a=s.index('.proc PlayerOAMReservation');z=s.index('.endproc',a)+len('.endproc')
  old=s[a:z]
  new='''.proc PlayerOAMReservation
.if ::ENABLE_MMC5_EXPANDED
 farcall MaaReservation,jmp
::MaaOwner:
 lda MarioVariant
 eor #2
 ora SelectedCharacter
 rts
 .res 2,$ea
 .assert *-PlayerOAMReservation=29,error,"Original reservation span"
.else
'''+old.split('\n',1)[1].rsplit('.endproc',1)[0]+'.endif\n.endproc'
  s=s[:a]+new+s[z:]
  s=once(s,'  jmp (M0)\n',' .if ::ENABLE_MMC5_EXPANDED\n  jmp MaaTail\n .else\n  jmp (M0)\n .endif\n')
  s=once(s,'  jsr RlNativeRenderDispatch','  jsr MaaRenderGate')
  return s
 change('metasprite_engine.s',R/'src/metasprite_engine.s',engine_edit)
 def collision_edit(s):
  size=address(b,'SBnce')-address(b,'HandleStompedShellE')
  return once(s,stomp_prefix,'HandleStompedShellE:\n.if ::ENABLE_MMC5_EXPANDED\n farcall MaaStomp,jmp\n .res '+str(size)+'-(*-HandleStompedShellE),$ea\n.else\n'+stomp_prefix.split('\n',1)[1]+'.endif\n')
 change('collision.s',R/'src/collision.s',collision_edit)
 def reset_edit(s):
  return once(s,'    lda SelectedCharacter\n    bne KeepLagChr',''' .if ::ENABLE_MMC5_EXPANDED
    jsr MaaLagChrGuard
    bcs KeepLagChr
 .else
    lda SelectedCharacter
    bne KeepLagChr
 .endif''')
 change('reset.s',R/'src/reset.s',reset_edit)
 def head_edit(s):
  a=s.index('.proc BillBGHeadConsumer');z=s.index('.endproc',a)+len('.endproc');old=s[a:z]
  return s[:a]+'.proc BillBGHeadConsumer\n.if ::ENABLE_MMC5_EXPANDED\n farcall MaaHead,jmp\n nop\n.else\n'+old.split('\n',1)[1].rsplit('.endproc',1)[0]+'.endif\n.endproc'+s[z:]
 change('bill_bg_empty.s',R/'src/bill_bg_empty.s',head_edit)
 def object_edit(s):
  a=s.index('  lda Player_X_Position',s.index('.proc FireballObjCore'));z=s.index('  ldy PlayerFacingDir',a);old=s[a:z]
  n=address(b,'FireballObjCore::RunFB') # validate actual declared procedure owner
  return s[:a]+'.if ::ENABLE_MMC5_EXPANDED\n farcall MaaFireInit\n bcc NoFBall\n .res '+str(0)+' ,$ea\n.else\n'+old+'.endif\n'+s[z:]
 change('object.s',R/'src/object.s',object_edit)
 # Restore the head-hit actor origin from the raised physical query. The
 # original block/score/erase routines remain the only writers.
 def rare_edit(s):
  a=s.index('.proc NativeRarePlayerHeadCollisionCore');z=s.index('.endproc',a)
  old=s[a:z]
  needle='  lda Player_Y_Position    ;get player\'s vertical coordinate'
  replacement='''.if ::ENABLE_MMC5_EXPANDED
  jsr MaaOwner
  bne MaaNativeBumpY
  lda Player_Y_Position
  sec
  sbc MaaaLength
  jmp MaaBumpYReady
MaaNativeBumpY:
  lda Player_Y_Position
MaaBumpYReady:
.else
'''+needle+'\n.endif'
  return s[:a]+once(old,needle,replacement)+s[z:]
 change('bill_native_rare.s',R/'src/bill_native_rare.s',rare_edit)
 def body_includes(s):
  for name in ['bill_native_rare.s','bill_bg_empty.s']:
   s=once(s,'.include "'+name+'"','.include "'+(O/'src'/name).relative_to(R).as_posix()+'"')
  return s
 change('bill_source_body.s',R/'src/bill_source_body.s',body_includes)
 def menu_edit(s):
  s=once(s,'jmp GbPitQueueName','jmp MaaQueueName')
  return once(s,'    farcall NrFreshGameInit','''    jsr MaaFresh
    .res 15,$ea''')
 change('character_select.s',P/'src/character_select.s',menu_edit)
 def km_edit(s):
  s=once(s,' cmp #1\n beq Skin',' cmp #1\n beq Maaa\n cmp #2\n beq Skin')
  return once(s,'Skin:lda #3','Maaa:lda #2\n rts\nSkin:lda #3')
 change('kamikaze_mario.s',R/'src/kamikaze_mario.s',km_edit)
 # Fully linked current source; no binary overlays or stale E-bank clone.
 funcs='MaaaLength MaaTimer MaaStomp MaaReservation MaaFresh MaaLifePrefix MaaBox MaaHead MaaAfterBG MaaFireInit MaaQueueName MaaBodyDraw MaaDrawNeck'.split()
 original_entry=(P/'entrypoint.s').read_text()
 existing_imports=set(re.findall(r'\b\w+\b','\n'.join(m[1]for m in re.finditer(r'^\s*\.import(?:zp)?\s+([^;\n]+)',original_entry,re.M))))
 entry=original_entry+'\n.if ::ENABLE_MMC5_EXPANDED\n.import '+','.join(funcs)+'\n.export MaaOwner\n'+''.join('.export '+n+'\n'for n in imports if n not in existing_imports)+'.endif\n'
 # ca65 searches cwd before -I. Explicit src/ includes must be rebound too;
 # declaring an overlay in a report is not evidence that it was consumed.
 for name in overlays:
  for prefix in ['', 'src/']:
   entry=entry.replace('.include "'+prefix+name+'"','.include "'+(O/'src'/name).relative_to(R).as_posix()+'"')
 (O/'entrypoint.s').write_text(entry)
 cfg=(P/'smb1base-mmc5-expanded.cfg').read_text()
 dark=re.search(r'^\s*DARKWING_GFX:\s*load\s*=\s*(\w+)',cfg,re.M).group(1)
 cfg=once(cfg,'}\nSYMBOLS {','    MAAA_CORE:load=X5_NEW_42,type=ro,start=$b680,optional=yes;\n    MAAA_ART:load='+dark+',type=ro,start=$db20,optional=yes;\n    MAAA_CHR:load=TMNT_CHR_TAIL,type=ro,start=$cb400,optional=yes;\n}\nSYMBOLS {')
 (O/'smb1base-mmc5-expanded.cfg').write_text(cfg)
 commands=[]
 template=parent['commands'][0]
 for name,source in [('main',O/'entrypoint.s'),('component',O/'component.s')]:
  cmd=template[:];cmd[cmd.index('-o')+1]=str(O/(name+'.o'));cmd[cmd.index('--create-full-dep')+1]=str(O/(name+'.d'));cmd[-1]=str(source)
  i=cmd.index('-I');cmd[i:i]=['-I',str(O/'src')]
  run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/(name+'.log')).write_text(run.stdout+run.stderr);assert not run.returncode,run.stderr[:4000]
  commands.append(cmd)
 actual_main=set()
 for word in re.split(r'(?<!\\)\s+',(O/'main.d').read_text().split(':\t',1)[1].strip().removesuffix(':')):
  p=Path(word.replace('\\ ',' '));actual_main.add((p if p.is_absolute()else R/p).resolve())
 assert all((O/'src'/n).resolve()in actual_main for n in overlays),('Unconsumed sparse leaf',[n for n in overlays if(O/'src'/n).resolve()not in actual_main])
 link=parent['commands'][3][:]
 for i,v in enumerate(link):
  for before,after in [(P/'smb1base-mmc5-expanded.cfg',O/'smb1base-mmc5-expanded.cfg'),(P/'main-independent.o',O/'main.o'),(P/'independent.nes',O/'candidate.nes'),(P/'independent.dbg',O/'candidate.dbg'),(P/'independent.lbl',O/'candidate.lbl')]:v=v.replace(str(before),str(after))
  link[i]=v
 link.append(str(O/'component.o'));run=subprocess.run(link,cwd=R,capture_output=True,text=True);(O/'link.log').write_text(run.stdout+run.stderr)
 (O/'draft-commands.json').write_text(json.dumps(commands+[link],indent=2)+'\n');assert not run.returncode,run.stderr
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes')
 new=scoped_load(O/'candidate.nes')
 (O/'draft-preimages.json').write_text(json.dumps(preimages,indent=2)+'\n')
 (O/'source.patch').write_text(''.join(''.join(difflib.unified_diff(preimages[n]['text'].splitlines(True),s.splitlines(True),fromfile='parent/'+n,tofile='private/'+n))for n,s in overlays.items()))
 print(json.dumps(dict(assembled=True,candidate=sha(O/'candidate.nes'),CORE_end=hex(address(new,'MaaCoreEnd')),ART_end=hex(address(new,'MaaArtEnd')),frames=art['total_exact_combinations'],pages=art['pages'],counts=art['pair_counts'])))

if __name__=='__main__':main()
