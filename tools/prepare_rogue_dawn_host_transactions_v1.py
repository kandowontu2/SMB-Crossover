"""Sparse real-assembler Rogue transaction component on reviewed 4cbd.

No admission/menu hooks, native launch, source tree clone or canonical writes.
"""
from pathlib import Path
import configparser,difflib,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
from check_tmnt_audio_fallback_oc import qualified
import rogue_dawn_map_v1 as ref
BASE=R/'build/roster-shared-rcr-adopted-v8.nes'
EXPECTED='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
O=R/'build/rogue-dawn-host-transactions-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a))
 return s.replace(a,b)

def main():
 global O
 if '--output' in sys.argv:O=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
 assert sha(BASE)==EXPECTED
 freeze=R/'build/rogue-dawn-host-services-v1/handoff.json'
 assert sha(freeze)=='9dc533c5b59145c095e8d16f81965fcf05726c922607e7e731fb7895cd760f61'
 for b in json.loads(freeze.read_text())['bindings']:
  assert sha(b['path'])==b['sha256'],b['path']
 if O.exists():
  assert not (O/'build.json').exists(),'Frozen output cannot be regenerated'
  if (O/'build.log').exists()and not(O/'initial-link-negative.log').exists():
   (O/'initial-link-negative.log').write_bytes((O/'build.log').read_bytes())
 else:O.mkdir()
 ep=(R/'src/entrypoint.s').read_text();weapons=(R/'src/megaman_weapons.s').read_text();objects=(R/'src/object.s').read_text();gates=(R/'src/new_roster_dispatch.s').read_text()
 begin=weapons.index('.proc CrossoverBlockSize\n');end=weapons.index('.endproc',begin)+len('.endproc')
 old=weapons[begin:end]
 new=once(old,'  cmp #CHARACTER_MEGAMAN\n  beq MegaManHead\n','')
 new=once(new,'  lda CrossoverBehaviorVersion\n  bne SmallHead\n  lda SmBall\n  bne SmallHead\n',
  '  lda RdVariant\n  cmp #1\n  beq SmallHead               ; actual Rogue never reads legacy SmBall\n  lda CrossoverBehaviorVersion\n  ora SmBall                  ; legal old Samus bool0/1; complete caller proof\n  bne SmallHead\n')
 new=once(new,'.if ::ENABLE_MMC5_EXPANDED\n  nop\n.endif\n','')
 # Seven new bytes, four removed comparisons and two-byte legal OR folding,
 # one original NOP: actual proc end and all subsequent old PCs stay fixed.
 new=new.replace('.proc CrossoverBlockSize\n','.proc CrossoverBlockSize\n.if ::ENABLE_MMC5_EXPANDED\n')
 new=new[:-len('.endproc')]+'.else\n'+old.split('\n',1)[1][:-len('.endproc')]+'.endif\n.endproc'
 weapons=weapons[:begin]+new+weapons[end:]
 objects=once(objects,'  farcall Z2PositionOnPlatform\n','  farcall RdTxPositionPlatform\n')
 overlays={}
 gates=once(gates,'.proc NrPrepare\n php\n pha\n lda SelectedCharacter\n', '.proc NrPrepare\n jmp RdNrPrepare\n nop\n nop\n::RdNrPrepareLegacy:\n')
 for name,text in [('megaman_weapons.s',weapons),('object.s',objects),('new_roster_dispatch.s',gates)]:
  p=O/name;p.write_text(text,newline='\n');overlays[name]=p
  ep=once(ep,'.include "'+name+'"','.include "'+p.name+'"')
 # Component-only sources deliberately redeclare local constants/macpacks.
 # This private include-only derivative adds guards, never changes instructions.
 # Keep immutable source and its assembled A600 prefix byte-exact.
 ctl=(R/'src/rogue_dawn_control.s').read_text().replace('.macpack longbranch\n','')
 svc=(R/'src/rogue_dawn_host_services.s').read_text().replace('.macpack longbranch\n','')
 declared=set(re.findall(r'^(Rd\w+)=',ctl,re.M))|set(re.findall(r'^(Rd\w+)=',(R/'src/rogue_dawn_weapons.s').read_text(),re.M))
 svc=re.sub(r'^(Rd\w+)=(\$[0-9a-fA-F]+)([^\n]*)$',lambda m:('.assert '+m[1]+'='+m[2]+',error,"same immutable component constant"'+m[3])if m[1]in declared else m[0],svc,flags=re.M)
 ctlp=O/'control-include.s';ctlp.write_text(ctl,newline='\n')
 svcp=O/'services-include.s';svcp.write_text(svc,newline='\n')
 # ca65 has a real256-segment ceiling (shared image already252). Reuse the
 # existing C94 segment without changing its old bytes/addresses: Sunny ends
 # D25F; approved Rogue art starts D300, then bridge DF50. Exactly four NEW
 # segment names remain: CORE/AUX/HOST/CHR. No new physical allocation.
 art=(R/'src/rogue_dawn_art.inc').read_text().replace('.segment "ROGUE_DAWN_ART"','.segment "SUNNY_ART"')
 art='.pushseg\n.segment "SUNNY_ART"\n.res $500-(*-SunnyArtBegin),$ff\n.popseg\n'+art
 artp=O/'art-include.inc';artp.write_text(art,newline='\n')
 bridge=(R/'src/rogue_dawn_host_bridge.s').read_text().replace('.segment "ROGUE_DAWN_HOST_BRIDGE"','.segment "SUNNY_ART"\n.res $1150-(*-SunnyArtBegin),$ff')
 bridgep=O/'bridge-include.s';bridgep.write_text(bridge,newline='\n')
 include='''
.if ::ENABLE_MMC5_EXPANDED
RD_FIRST_CHR=680
RD_LEAF_RENDER_PLAYER=RdRenderPlayer
RD_LEAF_ADD_MISSILE_TANK=RdAddMissileTank
RD_LEAF_DAMAGE_COMPLETE=RdControlDamageComplete
.include "art-include.inc"
.include "rogue_dawn.s"
.include "rogue_dawn_weapons.s"
.include "rogue_dawn_render.s"
.include "control-include.s"
.define RdHostDispatch RdHsFrozenDispatch
.include "services-include.s"
.undefine RdHostDispatch
.include "rogue_dawn_host.s"
.include "rogue_dawn_host_transactions.s"
.include "bridge-include.s"
.include "rogue_dawn_host_integration.s"
.pushseg
.segment "ROGUE_DAWN_CHR"
.incbin "chr/characters/rogue-dawn.chr"
.popseg
.endif
'''
 ep+=include
 entry=O/'entrypoint.s';entry.write_text(ep,newline='\n')
 mainc=O/'main.c';mainc.write_bytes((R/'src/main.c').read_bytes())
 cfg=(R/'smb1base-mmc5-expanded.cfg').read_text()
 marker='    CELESTE_MARIO_CHR: load=CELESTE_MARIO_CHR_MEM,type=ro,optional=yes;'
 cfg=once(cfg,marker,marker+'''
    ROGUE_DAWN_CONTROL_AUX:load=X5_NEW_7C,type=ro,start=$ae00,optional=yes;
    ROGUE_DAWN_CORE:load=X5_NEW_7C,type=ro,start=$b000,optional=yes;
    ROGUE_DAWN_HOST:load=X5_NEW_5F,type=ro,start=$a600,optional=yes;
''')
 cf=O/'private.cfg';cf.write_text(cfg,newline='\n')
 options=configparser.ConfigParser();options.optionxform=str;options.read(R/'build_options.ini')
 defs={k:v for s in options.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 out=O/'candidate.nes'
 cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(cf),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(O),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
 for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd += [str(mainc),str(entry)]
 if '--qualify-existing'not in sys.argv:
  z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'build.log').write_text(z.stdout+z.stderr)
  assert z.returncode==0,'See private build.log: '+(z.stdout+z.stderr)[:3000]
  prepare(R,out)
 else:assert out.exists()and out.with_suffix('.dbg').exists()
 a,b=scoped_load(BASE),scoped_load(out)
 # The frozen services+helper prefix is never rewritten. Only the bridge's
 # genuine dispatcher operand changes; all actual symbols come from this link.
 p=location(b,'RdHsFrozenDispatch');prefix=(R/'build/rogue-dawn-host-services-v1/services.bin').read_bytes()
 assert b['raw'][p:p+len(prefix)]==prefix
 assert address(b,'RdTxStart')==0xb004 and address(b,'RdTxEnd')<=0xc000
 assert address(a,'CrossoverBlockSize')==address(b,'CrossoverBlockSize')
 assert int(a['syms']['CrossoverBlockSize']['size'],0)==int(b['syms']['CrossoverBlockSize']['size'],0)
 oldsym,newsym=qualified(BASE),qualified(out)
 moved={str(n):[v,newsym.get(n)]for n,v in oldsym.items()if newsym.get(n)!=v and 'LOCAL-MACRO_SYMBOL-'not in str(n)}
 # Internal implementation labels deliberately change within the fixed proc.
 assert all('CrossoverBlockSize'in k or '_FARCALL_COUNT'in k for k in moved),moved
 diff=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 assert len(a['raw'])==len(b['raw'])
 # Existing bytes only change in the block-size proc and the actual platform
 # farcall. All new bodies/CHR occupy exact previously FF/zero reservations.
 head=range(location(a,'CrossoverBlockSize'),location(a,'CrossoverBlockSize')+int(a['syms']['CrossoverBlockSize']['size'],0))
 plat=range(location(a,'PositionPlayerOnVPlat'),location(a,'PositionPlayerOnVPlat')+32)
 pickup=range(location(a,'NrPrepare'),location(a,'NrPrepare')+5)
 for i in diff:
  if i in head or i in plat or i in pickup:continue
  bank=(i-16)//8192;pc=i-16-bank*8192
  if bank<128:
   allowed=(bank==95 and 0x600<=pc<0x2000)or(bank==94 and 0x1300<=pc<0x2000)or(bank==124 and 0xc53<=pc<0x2000)
   assert allowed and a['raw'][i]==255,(i,bank,hex(pc))
  else:
   assert 16+1048576+680*1024<=i<16+1048576+696*1024 and a['raw'][i]==0,i
 patch=O/'source.patch';patch.write_text(''.join(''.join(difflib.unified_diff((R/'src'/n).read_text().splitlines(True),p.read_text().splitlines(True),fromfile='current4cbd/src/'+n,tofile='private/'+n))for n,p in overlays.items()),newline='\n')
 paths=[Path(__file__),R/'src/rogue_dawn_host_transactions.s',R/'src/rogue_dawn_host_integration.s',BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),freeze,entry,mainc,cf,patch,ctlp,svcp,artp,bridgep,*overlays.values()]+[R/'src'/n for n in ['megaman_weapons.s','object.s','new_roster_dispatch.s','entrypoint.s']]
 proof=dict(passed=True,source_only=True,native_run=False,playable_admission=False,ROM_sha256=sha(out),parent_sha256=EXPECTED,bytes_changed=len(diff),PRG_changed_banks=sorted({(i-16)//8192 for i in diff if i<16+1048576}),service_prefix_byteexact=True,host_end=hex(address(b,'RdTxEnd')),host_bytes=address(b,'RdTxEnd')-0xa600,frozen_services_sound_endpoint_negative='bridge7 Health/8 Low; v1 dispatcher reverses; new dispatcher repairs without changing frozen bytes',old_symbols_moved=moved,commands=[cmd],bindings=[ref.binding(p)for p in paths])
 (O/'build.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps({k:proof[k]for k in ['ROM_sha256','bytes_changed','host_end','host_bytes']}))
if __name__=='__main__':main()
