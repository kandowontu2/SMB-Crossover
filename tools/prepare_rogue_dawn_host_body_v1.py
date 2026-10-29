"""Private f56a body successor. Real assembler closure; no shared/native writes."""
from pathlib import Path
import hashlib,json,re,runpy,sys
R=Path(__file__).resolve().parents[1]
O=R/'build/rogue-dawn-host-body-v1'
P=R/'build/roster-shared-celeste-small-chr-v1.nes'
EXPECTED='f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)

def main():
 assert sha(P)==EXPECTED
 prior=R/'build/rogue-dawn-host-pipeline-v2'
 assert sha(prior/'candidate.nes')=='e4b788fe7426c9fb1e9b2b5ff9d116420d8adee0a383bb0298adb31ec900c333'
 assert not(O/'build.json').exists(),'Frozen output'
 O.mkdir(exist_ok=True)
 (O/'movement-flush.s').write_bytes((prior/'movement-flush.s').read_bytes())
 t=(prior/'build-private.py').read_text()
 t=once(t,"R/'build/roster-shared-celeste-small-v1.nes'","R/'build/roster-shared-celeste-small-chr-v1.nes'")
 t=once(t,'d52eeefe78c5f050d276a833c651456b717157856d1783b98c131f9da29f8a60',EXPECTED)
 t=once(t,"R/'build/rogue-dawn-host-pipeline-v2'","R/'build/rogue-dawn-host-body-v1'")
 t=once(t," overlays={}\n",''' # Preserve the genuine old44B implementation as an A95 foreign leaf.
 begin=weapons.index('.proc MmDynamicPlayerPrgOwner\\n');end=weapons.index('.endproc',begin)+len('.endproc')
 legacy=weapons[begin:end].replace('.proc MmDynamicPlayerPrgOwner','.proc RdBodyLegacyDynamicPrg')
 legacy=once(legacy,'jmp HpNativePointerEnd','rts')
 (O/'legacy-player-prg.s').write_text(legacy,newline='\\n')
 shim=""".proc MmDynamicPlayerPrgOwner
 cpy #0
 bne Done
 farcall RdBodyDynamicPrg
Done:jmp HpNativePointerEnd
 .res 19,$ea
 .assert *-::MmDynamicPlayerPrgOwner=44,lderror,"old44B owner span"
.endproc"""
 weapons=weapons[:begin]+shim+weapons[end:]
 objects=once(objects,'  farcall RdTxPositionPlatform\\n','  farcall RdBodyPositionPlatform\\n')
 overlays={}
''')
 t=once(t," for name,text in [('player.s',player)",''' player=once(player,'  jsr MegaManCollisionBox','.if ::ENABLE_MMC5_EXPANDED\\n  jsr RdBodyBoxSelectBridge\\n.else\\n  jsr MegaManCollisionBox\\n.endif')
 player=once(player,'  farcall LmBoundingBoxGate','  farcall RdBodyBox')
 player=once(player,'  farcall SamusGraphics','.if ::ENABLE_MMC5_EXPANDED\\n  farcall RdBodyGraphics\\n.else\\n  farcall SamusGraphics\\n.endif')
 luigi=once(luigi,'  .res 83-(*-::LuigiNativeTraction),$ea',\"\"\"::RdBodyBoxSelectBridge:
  .assert RdBodyBoxSelectBridge=$b970,error,"Approved remaining B1 padding"
  lda #<RdBodySelectBox
  sta FarcallJmpTarget_SMC+1
  lda #>RdBodySelectBox
  sta FarcallJmpTarget_SMC+2
  lda #($80|95)
  jmp FarCallCommon
  .assert *-RdBodyBoxSelectBridge=15,error,"Single exact selector target"
  .res 83-(*-::LuigiNativeTraction),$ea\"\"\")
 colors=gates.index('.proc NrColors');colorsend=gates.index('.endproc',colors)
 colorleaf=once(gates[colors:colorsend],'farcall X5GetPlayerColors','farcall RdBodyColors')
 gates=gates[:colors]+colorleaf+gates[colorsend:]
 post=(R/'src/zelda2_link_platform.s').read_text()
 p0=post.index('.proc Z2PostBGBodyBridge');p1=post.index('.endproc',p0)+len('.endproc')
 post=post[:p0]+\"\"\".proc Z2PostBGBodyBridge
 php
 pha
 lda SelectedCharacter
 cmp #2
 bne Foreign
 lda RdVariant
 cmp #1
 bne Foreign
 pla
 plp
 rts
Foreign:pla
 plp
 jmp BassPostBGDispatch
 .assert *-::Z2PostBGBodyBridge=24,lderror,"Owned inline gate"
 .res 14,$ea
.endproc\"\"\"+post[p1:]
 for name,text in [('zelda2_link_platform.s',post),('player.s',player)''')
 t=once(t,'.include "rogue_dawn_host_pipeline.s"\n','.include "rogue_dawn_host_pipeline.s"\n.include "rogue_dawn_host_body.s"\n')
 t=once(t," cmd += [str(mainc),str(entry)]"," cmd += ['--create-full-dep',str(O/'assembler-full.dep'),str(mainc),str(entry)]")
 cut=t.index(' a,b=scoped_load(BASE),scoped_load(out)')
 t=t[:cut]+''' from prepare_rogue_dawn_host_body_v1 import qualify
 qualify(O,BASE,out,cmd,overlays)
if __name__=='__main__':main()
'''
 p=O/'build-private.py';p.write_text(t,newline='\n')
 sys.argv=[str(p),'--output',str(O)];runpy.run_path(str(p),run_name='__main__')

def qualify(o,parent,out,cmd,overlays):
 sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
 from link_pit_rygar_sophia_audit_cpu import scoped_load
 from check_tmnt_render_oa import address,location
 from check_tmnt_audio_fallback_oc import qualified
 import rogue_dawn_map_v1 as ref
 import difflib
 a,b=scoped_load(parent),scoped_load(out)
 old=scoped_load(R/'build/rogue-dawn-host-pipeline-v2/candidate.nes')
 spans=[]
 for name,size in [('RdHsFrozenDispatch',2564),('RdTxStart',address(old,'RdTxMovementEnd')-address(old,'RdTxStart')),('CORE124B000',4090),('AUX124AE00',508),('RdArtStart',3150),('RdHostBridgeStart',175)]:
  if name.startswith('CORE'):x=y=16+124*8192+0x1000
  elif name.startswith('AUX'):x=y=16+124*8192+0xe00
  else:x,y=location(old,name),location(b,name)
  assert old['raw'][x:x+size]==b['raw'][y:y+size],name
  spans.append(dict(symbol=name,bytes=size,sha256=hashlib.sha256(b['raw'][y:y+size]).hexdigest()))
 assert address(b,'RdBodyStart')==0xb5d2 and address(b,'RdBodyEnd')<=0xc000
 assert b['raw'][16+8192+0x197f]==234 and b['raw'][16+8192+0x1980]==96
 assert a['raw'][16+8192+0x192d:16+8192+0x1958]==b['raw'][16+8192+0x192d:16+8192+0x1958]
 diff=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 # Old hook extents have genuine symbol/assembler lengths, not a whole-bank waiver.
 allowed=[]
 def span(n,length):
  x=location(a,n);allowed.append((x,x+length,n))
 for n,l in [('CrossoverBlockSize',int(a['syms']['CrossoverBlockSize']['size'],0)),('PositionPlayerOnVPlat',32),('NrPrepare',5),('NrColors',int(a['syms']['NrColors']['size'],0)),('MmDynamicPlayerPrgOwner',44),('Z2PostBGBodyBridge',38)]:span(n,l)
 # The four real player farcall/call operands are located by exact old bytes.
 raw=bytes(a['raw'])
 def farpre(n):
  return bytes([0x8d])+(address(a,'SafecallA_SMC')+1).to_bytes(2,'little')+bytes([0xa9,address(a,n)&255,0x8d])+(address(a,'FarcallJmpTarget_SMC')+1).to_bytes(2,'little')+bytes([0xa9,address(a,n)>>8,0x8d])+(address(a,'FarcallJmpTarget_SMC')+2).to_bytes(2,'little')+bytes([0xa9,128|(location(a,n)-16)//8192,0x20])+address(a,'FarCallCommon').to_bytes(2,'little')
 for n,owner in [('SamusMovement','PlayerMovementSubs'),('LmBoundingBoxGate','PlayerCtrlRoutine'),('SamusGraphics','PlayerGfxHandler')]:
  x=raw.find(farpre(n),location(a,owner),location(a,owner)+500);assert x>=0,n
  allowed.append((x,x+18,owner+'->'+n))
 for n in ['PlayerBGCollision','MegaManCollisionBox']:
  seq=bytes([32])+address(a,n).to_bytes(2,'little');x=raw.find(seq,location(a,'PlayerCtrlRoutine'),location(a,'PlayerCtrlRoutine')+500);assert x>=0,n
  allowed.append((x,x+3,'PlayerCtrl->'+n))
 allowed.append((16+8192+0x1958,16+8192+0x197f,'B1 exact39B padding'))
 for i in diff:
  if any(x<=i<y for x,y,_ in allowed):continue
  bank=(i-16)//8192;off=(i-16)%8192
  if bank<128:
   ok=(bank==95 and 0x600<=off<0x2000)or(bank==94 and 0x1300<=off<0x2000)or(bank==124 and 0xc53<=off<0x2000)
   assert ok and a['raw'][i]==255,(i,bank,hex(off))
  else:assert 16+1048576+680*1024<=i<16+1048576+696*1024 and a['raw'][i]==0,i
 oldsyms,newsyms=qualified(parent),qualified(out)
 moved={str(k):[v,newsyms.get(k)]for k,v in oldsyms.items()if newsyms.get(k)!=v and 'LOCAL-MACRO_SYMBOL-'not in str(k)}
 assert all(any(z in k for z in ['CrossoverBlockSize','_FARCALL_COUNT',"('MmDynamicPlayerPrgOwner', '"])for k in moved),moved
 dep=o/'assembler-full.dep';text=dep.read_text();assert ':\t'in text,text[:300]
 # Genuine ca65 dependency list includes unused phony targets after main line.
 first=text.split(':\t',1)[1].split('\n\n',1)[0].replace('\\\n',' ').strip()
 paths=[]
 for word in re.split(r'(?<!\\)\s+',first):
  if not word:continue
  p=Path(word.replace('\\ ',' '));p=(p if p.is_absolute()else R/p).resolve();assert p.is_file(),str(p)
  if p not in paths:paths.append(p)
 assert len(paths)>450,len(paths)
 patch=o/'source.patch';patch.write_text(''.join(''.join(difflib.unified_diff((R/'src'/n).read_text().splitlines(True),p.read_text().splitlines(True),fromfile='f56a/src/'+n,tofile='private/'+n))for n,p in overlays.items()),newline='\n')
 extras=[Path(__file__),o/'build-private.py',o/'private.cfg',R/'build_options.ini',R/'tools/Windows/cc65/bin/cl65.exe',R/'tools/Windows/cc65/bin/ca65.exe',R/'tools/Windows/cc65/bin/ld65.exe',R/'src/rogue_dawn_host_body.s',o/'legacy-player-prg.s',o/'movement-flush.s',patch,dep,parent,parent.with_suffix('.dbg'),parent.with_suffix('.lbl'),out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map')]
 bindings=[ref.binding(p)for p in dict.fromkeys(paths+extras)]
 result=dict(passed=True,source_only=True,native_run=False,playable_admission=False,ROM_sha256=sha(out),parent_sha256=EXPECTED,previous_pipeline_sha256=sha(R/'build/rogue-dawn-host-pipeline-v2/candidate.nes'),host_start=0xa600,body_start=address(b,'RdBodyStart'),host_end=address(b,'RdBodyEnd'),body_bytes=address(b,'RdBodyEnd')-address(b,'RdBodyStart'),frozen_literal_spans=spans,bytes_changed=len(diff),PRG_changed_banks=sorted({(i-16)//8192 for i in diff if i<16+1048576}),old_hook_extents=[dict(start=x,end=y,name=n)for x,y,n in allowed],old_symbols_moved=moved,assembler_full_dependency_count=len(paths),dependency_scope='Actual cl65 --create-full-dep output; full consumed ASM/incbin plus explicit linker/config/build tools. No claim that handwritten owned-file list establishes closure.',commands=[cmd],bindings=bindings,open=['typed lifecycle/injury/visibility shared gates','native hardware/pixels/deadline','gear world contact/art and source audio closure','menu/playable admission'])
 (o/'build.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['ROM_sha256','body_bytes','host_end','assembler_full_dependency_count']}))

if __name__=='__main__':main()
