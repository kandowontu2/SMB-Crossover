"""Compile only owned Gimmick leaves, optionally link against immutable ac126 objects."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,collections
R=Path(__file__).resolve().parents[1];O=R/'build/gimmick-component-v2';P=R/'build/pit-retold-host-v3'
sys.path[:0]=[str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 global O
 a=argparse.ArgumentParser();a.add_argument('--link',action='store_true');a.add_argument('--fixture',action='store_true')
 a.add_argument('--output',type=Path,default=O);a.add_argument('--source-dir',type=Path,default=R/'src');a.add_argument('--chr-file',type=Path,default=R/'chr/characters/gimmick-source-v2.chr');a.add_argument('--lease-proof',type=Path,default=O/'lease-closure.json');a=a.parse_args()
 O=a.output.resolve();O.mkdir(parents=True,exist_ok=True)
 assert not(O/'handoff.json').exists(),'Frozen unit must remain unchanged'
 b=scoped_load(P/'candidate.nes');assert sha(P/'candidate.nes')=='ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
 host='''SelectedCharacter NumberofLives AreaPointer WorldNumber SavedJoypadBits GamePauseStatus GameEngineSubroutine
 TimerControl Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_X_Speed Player_Y_Speed
 Player_State PlayerFacingDir Player_X_Scroll Player_XSpeedAbsolute PlayerSize PlayerStatus ObjectMetasprite
 Player_Rel_XPos Player_Pos_ForScroll ScreenLeft_X_Pos ScreenLeft_PageLoc R0 R1 R2 R3 R4 R5 R6 R7
 GetBlockBufferAddr BlockBufferAddr Block_Buffer_1 MTileAttribute MTILE_SOLID FarCallCommon SafecallA_SMC FarcallJmpTarget_SMC
 SafereturnA_SMC NextBank_SMC CurrentBank CurrentBankC CrossoverBehaviorVersion CurrentOAMOffset
 GuestOamRotationActive RgOamRotation Sprite_Y_Position Sprite_Tilenumber Sprite_Attributes Sprite_X_Position
 VRAM_Buffer1 VRAM_Buffer1_Offset VRAM_Buffer_AddrCtrl StarInvincibleTimer GuestPowerupActive
 MmXFraction MmYFraction SmPosePtr SmChrBank Player_SprAttrib X5SetPhysicalChr
 BoundingBox_UL_Corner BoundingBox_LR_Corner ObjectOffset Enemy_X_Position Enemy_PageLoc Enemy_ID
 Enemy_Y_Position Enemy_Y_HighPos Enemy_Flag Enemy_State MmDeathFlag KillPlayer
 MmSlot MmEnemySlot SmSlot SmBombHits MmBulletType BeginEnemyLoop'''.split()
 lines=['; Literal genuine ac126 DBG bindings, macro substitutions create NO fake exported aliases.','.macpack longbranch']
 for n in host:
  assert n in b['syms'],n
  lines.append('.define '+n+' $%04x'%address(b,n))
 lines+=['.macro GmSaveScratch']
 for n in ['R0','R1','R2','R3','R4','R5','R6','R7','NextBank_SMC+1','SafecallA_SMC+1','FarcallJmpTarget_SMC+1','FarcallJmpTarget_SMC+2','SafereturnA_SMC+1','CurrentBankC']:
  lines+=[' lda '+n,' pha']
 lines+=['.endmacro','.macro GmRestoreScratch',' pla',' sta CurrentBankC',' sta $5116']
 for n in reversed(['R0','R1','R2','R3','R4','R5','R6','R7','NextBank_SMC+1','SafecallA_SMC+1','FarcallJmpTarget_SMC+1','FarcallJmpTarget_SMC+2','SafereturnA_SMC+1']):
  lines+=[' pla',' sta '+n]
 lines+=['.endmacro','.macro GmFar Target,Bank',' sta SafecallA_SMC+1',' lda #<Target',' sta FarcallJmpTarget_SMC+1',
  ' lda #>Target',' sta FarcallJmpTarget_SMC+2',' lda #(Bank|$80)',' jsr FarCallCommon','.endmacro',
  '.include "gimmick.s"']
 (O/'component.s').write_text('\n'.join(lines)+'\n')
 cc=R/'tools/Windows/cc65/bin'
 cmd=[str(cc/'ca65.exe'),'--cpu','6502x','-g','-I',str(a.source_dir.resolve()),'-I',str(R),str(O/'component.s'),'-o',str(O/'component.o')]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'assemble.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0,p.stderr
 p=subprocess.run([str(cc/'od65.exe'),'--dump-segments',str(O/'component.o')],capture_output=True,text=True)
 (O/'size.txt').write_text(p.stdout);sizes={}
 for m in re.finditer(r'Name:\s+"([^"]+)".*?Size:\s+(\d+)',p.stdout,re.S):sizes[m[1]]=int(m[2])
 print(json.dumps(dict(size_only=not a.link,sizes=sizes)))
 if a.fixture:
  cfg='MEMORY { A:start=$ae80,size=$d80,file=%O,fill=yes,fillval=$ff,bank=$18; B:start=$b740,size=$8c0,file=%O,fill=yes,fillval=$ff,bank=$7a; C:start=$b9c0,size=$640,file=%O,fill=yes,fillval=$ff,bank=$4b; D:start=$d920,size=$6e0,file=%O,fill=yes,fillval=$ff,bank=$49; }\nSEGMENTS{ GIMMICK_CORE:load=A,type=ro;GIMMICK_MOVE:load=B,type=ro;GIMMICK_COLD:load=C,type=ro;GIMMICK_ART:load=D,type=ro; }\n'
  (O/'fixture.cfg').write_text(cfg)
  cmd=[str(cc/'ld65.exe'),'-C',str(O/'fixture.cfg'),'-o',str(O/'leaf.bin'),'--dbgfile',str(O/'leaf.dbg'),'-Ln',str(O/'leaf.lbl'),'-m',str(O/'leaf.map'),str(O/'component.o')]
  p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'fixture-link.log').write_text(p.stdout+p.stderr);assert not p.returncode,p.stderr
  print(json.dumps(dict(isolated_leaf=sha(O/'leaf.bin'),limits='Isolated compiled section fixture only. Not a parent ROM/candidate; old-owner allocation is still conditional.')))
 if not a.link:return
 lease=json.loads(a.lease_proof.read_text())
 assert lease['status']=='PRIVATE_SOURCE_OWNER_LEASE_CLOSED','Complete actual source/consumer closure before using conditional spans'
 cfg=(P/'smb1base-mmc5-expanded.cfg').read_text()
 # These formal MEMORY splits retain exact total PRG and all old segment PCs.
 replacements=[
 ('CONTRA_MEM',0x3c00,0x2e80,'GIMMICK_CORE_MEM: start=$ae80,size=$d80,type=ro,file=%O,fill=yes,fillval=$ff,bank=$18;'),
 ('X5_NEW_7A',0x2000,0x1740,'GIMMICK_MOVE_MEM: start=$b740,size=$8c0,type=ro,file=%O,fill=yes,fillval=$ff,bank=$7a;'),
 ('X5_NEW_4B',0x2000,0x19c0,'GIMMICK_COLD_MEM: start=$b9c0,size=$640,type=ro,file=%O,fill=yes,fillval=$ff,bank=$4b;'),
 ('X5_NEW_49',0x2000,0x1920,'GIMMICK_ART_MEM: start=$d920,size=$6e0,type=ro,file=%O,fill=yes,fillval=$ff,bank=$49;')]
 for name,old,new,extra in replacements:
  pat=r'(?m)^\s*'+name+r':.*$';m=re.search(pat,cfg);assert m,name
  line=m[0];changed,n=re.subn(r'size\s*=\s*\$'+format(old,'x'),r'size=$'+format(new,'x'),line,flags=re.I);assert n==1,name
  cfg=cfg[:m.start()]+changed+'\n    '+extra+cfg[m.end():]
 # Formal asset-memory split preserves physical length/order and all old
 # owners. Inserting a later-address segment before GB_PIT in one ld65 area
 # would advance its cursor and reject the genuine earlier Pit address.
 m=re.search(r'(?m)^\s*TMNT_CHR_TAIL:.*$',cfg);assert m
 line=m[0];assert 'size=$13000'in line
 cfg=cfg[:m.start()]+line.replace('size=$13000','size=$f000')+'\n GIMMICK_CHR_MEM:start=$cc000,size=$1000,type=ro,fill=yes,file=%O,fillval=$00;\n TMNT_CHR_AFTER_GM:start=$cd000,size=$3000,type=ro,fill=yes,file=%O,fillval=$00;'+cfg[m.end():]
 cfg=cfg.replace('SEGMENTS {','SEGMENTS {\n GIMMICK_CORE:load=GIMMICK_CORE_MEM,type=ro;\n GIMMICK_MOVE:load=GIMMICK_MOVE_MEM,type=ro;\n GIMMICK_COLD:load=GIMMICK_COLD_MEM,type=ro;\n GIMMICK_ART:load=GIMMICK_ART_MEM,type=ro;\n GIMMICK_CHR:load=GIMMICK_CHR_MEM,type=ro;\n',1)
 (O/'smb1base-mmc5-expanded.cfg').write_text(cfg)
 (O/'chr.s').write_text('.segment "GIMMICK_CHR"\n.incbin "'+a.chr_file.resolve().as_posix()+'"\n')
 p=subprocess.run([str(cc/'ca65.exe'),'-g',str(O/'chr.s'),'-o',str(O/'chr.o')],cwd=R,capture_output=True,text=True);assert not p.returncode,p.stderr
 old=json.loads((P/'build-proof.json').read_text())['commands'][-1]
 cmd=[v.replace(str(P/'smb1base-mmc5-expanded.cfg'),str(O/'smb1base-mmc5-expanded.cfg')).replace(str(P/'candidate.'),str(O/'candidate.'))for v in old]
 cmd+=[str(O/'component.o'),str(O/'chr.o'),'-m',str(O/'candidate.map')]
 p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(O/'link.log').write_text(p.stdout+p.stderr)
 assert p.returncode==0,p.stderr
 # Exact ordinary E clone refresh from final127; no stale code sample overlay.
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare
 prepare(R,O/'candidate.nes')
 raw=(O/'candidate.nes').read_bytes();diff=[i for i,(x,y)in enumerate(zip(b['raw'],raw))if x!=y]
 allowed=[(16+bank*8192+lo,16+bank*8192+hi)for bank,lo,hi in[(24,0xe80,0x1c00),(122,0x1740,0x2000),(75,0x19c0,0x2000),(73,0x1920,0x2000)]]+[(1048592+816*1024,1048592+820*1024)]
 assert len(raw)==len(b['raw'])and all(any(lo<=i<hi for lo,hi in allowed)for i in diff)
 def symbols(p):
  scopes={};syms=[];segs={}
  for line in p.read_text().splitlines():
   if not line.startswith(('scope\t','sym\t','seg\t')):continue
   z=dict(v.split('=',1)for v in line[4 if line.startswith(('sym\t','seg\t'))else 6:].split(',')if '='in v)
   if line.startswith('scope\t'):scopes[z['id']]=z
   elif line.startswith('seg\t'):segs[z['id']]=z
   elif 'val'in z:syms.append(z)
  def path(k):
   if k not in scopes:return ''
   s=scopes[k];return path(s.get('parent'))+'::'+s['name']
  return collections.Counter((z['name'],z['val'],path(z.get('scope')),segs.get(z.get('seg'),{}).get('name'))for z in syms)
 oldsym=symbols(P/'candidate.dbg');newsym=symbols(O/'candidate.dbg');assert not(oldsym-newsym),'An original genuine qualified symbol moved/disappeared'
 proof=dict(status='PRIVATE_LINK_UNQUALIFIED',parent=sha(P/'candidate.nes'),candidate=sha(O/'candidate.nes'),changed_bytes=len(diff),all_old_qualified_symbols_exact=sum(oldsym.values()),sizes=sizes,commands=[cmd],native=False)
 (O/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
if __name__=='__main__':main()
