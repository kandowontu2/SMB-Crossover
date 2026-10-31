"""Actual Bowser menu/native-host source plus shared27/33 service target resolver."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load
P=R/'build/bowser-gameplay-component-v3';B=R/'build/battletoads-current-host-v4'
O=R/'build/bowser-functional-host-v1';J=O/'joint';D=J/'bowser';BT=J/'bt'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def main():
 assert not O.exists();oldstage=json.loads((P/'source-stage.json').read_text())
 for p,v in oldstage['bindings'].items():assert sha(p)==v,p
 shutil.copytree(P/'joint',J);shutil.copytree(B/'joint/bt',BT)
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in ['.s','.inc','.cfg']:
   s=p.read_text();s=s.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix()).replace(str(B/'joint'),str(J)).replace((B/'joint').as_posix(),J.as_posix());write(p,s)
 # Real shared table remains36 JSRs at B020; resolver returns addresses only.
 s=(BT/'router.s').read_text();s=s.replace('.import BtCheck,BtCacheServices,FarCallCommon,FarcallJmpTarget_SMC','.import BwBtResolve,BtCacheServices,FarCallCommon,FarcallJmpTarget_SMC')
 s=s.replace('BtServiceVeneers:','BwServiceVeneers:\nBtServiceVeneers:',1).replace('.export BtServiceVeneers,','.export BwServiceVeneers,BtServiceVeneers,')
 a=s.index(' BtFar BtCheck,jsr');z=s.index(' pla\n tay',a)
 s=s[:a]+''' tsx
 lda $0105,x
 sec
 sbc #<(BtServiceVeneers+2)
 BtFar BwBtResolve,jsr
 bcc BtRouterBad
 sta NextBank_SMC+1
'''+s[z:];write(BT/'router.s',s)
 s=(R/'tools/reference/bowser_mixed_resolver_v1.s').read_text().replace('BwColdDraw,BwFresh,CmHostFresh','BwColdDraw,CmHostFresh')
 s+='''
.import FmAlts,FmGroups
.export BwStartFlags
BwStartFlags:
 php
 lda #$80
 cpx #31
 beq BwStartAlts
 lsr
 lsr
 cpx #9
 beq BwStartAlts
 lsr
 lsr
 cpx #26
 beq BwStartAlts
 lda #0
BwStartAlts:
 and FmAlts
 sta FmAlts
 lda #$20
 cpx #23
 beq BwStartGroups
 lda #$18
 cpx #30
 beq BwStartGroups
 lda #0
BwStartGroups:
 and FmGroups
 sta FmGroups
 plp
 lda #0
 rts
.assert *<=$b300,lderror,"A67 resolver+shared Start helper213B"
''';write(D/'router.s',s)
 write(D/'cold.s',(R/'tools/reference/bowser_cold_host_v1.s').read_text())
 # Only two complete RIGHT standing records are needed before verified load.
 s=(D/'preview.s').read_text();s=re.sub(r'^BwPortrait[13]Left:.*\n','',s,flags=re.M)
 s=s.replace('.export BwPortrait1Right,BwPortrait1Left,BwPortrait3Right,BwPortrait3Left','.export BwPortrait1Right,BwPortrait3Right')
 lines=[]
 for line in s.splitlines():
  if line.startswith(('BwPortrait1Right:','BwPortrait3Right:')):
   name,nums=line.split('.byte');v=[int(x)for x in nums.split(',')];dy=8 if '1Right'in name else 16;dx=8 if '1Right'in name else 0
   for i in range(1,len(v),4):v[i+2]=(v[i+2]-dy)&255;v[i+3]=(v[i+3]-dx)&255
   line=name+'.byte '+','.join(map(str,v))
  lines.append(line)
 write(D/'preview.s','\n'.join(lines)+'\n')
 # Own original-state internal predicate: ROL gets the same0/1 A without V
 # normalization; public loader restores original P and consumes only C/Z.
 s=(D/'check.s').read_text().replace(' lda #0\n adc #0\n sec',' lda #0\n rol\n sec',1)
 s=s.replace('.import VRAM_Buffer1_Offset,VRAM_Buffer1','.import VRAM_Buffer1_Offset,VRAM_Buffer1,OperMode_Task,X5QueueAreaBackdrop')
 s=s.replace('BwColors:\n','BwColors:\n lda OperMode_Task\n cmp #3\n bne BwColorsBody\n BwFar X5QueueAreaBackdrop,jsr\nBwColorsBody:\n')
 write(D/'check.s',s)
 # Correct busy retry and source flame facing; full native callback output ABI
 # is validated at actual callers, not claimed from the private projections.
 s=(D/'host.s').read_text().replace(' BwFar BwColors\n lda #0',' BwFar BwColors\n cpx #78\n bcs BwUiDone\n lda #0')
 s=s.replace(' lda #<(BwFireRecord+$2000)\n sta R0\n lda #>(BwFireRecord+$2000)\n sta R1',''' lda #<(BwFireRecord+$2000)
 ldy BwShots+1,x
 cpy #1
 bne BwFireRecordReady
 lda #<(BwFireRecordRight+$2000)
BwFireRecordReady:sta R0
 lda #>(BwFireRecord+$2000)
 sta R1''')
 s=s.replace('BwFireRecord:.byte 12,56,0,0,0,58,0,0,8,60,0,0,16','BwFireRecord:.byte 12,56,0,0,0,58,0,0,8,60,0,0,16\nBwFireRecordRight:.byte 12,60,64,0,0,58,64,0,8,56,64,0,16\n.assert >BwFireRecord=>BwFireRecordRight,lderror,"Flame records same source page"')
 write(D/'host.s',s)
 # Genuine shared common source, compressed metadata with every original
 # address+bank linked assertion. Remove only two proven redundant CLCs.
 s=(R/'build/battletoads-transport-proposal-v2/joint/union.s').read_text()
 s=s.replace(' cmp #33\n jeq HuExtendedBT',' cmp #27\n jeq HuExtendedBT\n cmp #33\n jeq HuExtendedBT',1)
 a=s.index('HuExtendedBT:');z=s.index('.assert .lobyte(BtServiceVeneers)',a)
 s=s[:a]+s[a:z].replace(' asl\n clc\n adc',' asl\n adc').replace(' clc\n adc #<BtServiceVeneers',' adc #<BtServiceVeneers')+s[z:]
 write(J/'union.s',s)
 # The exact Only classifier changes just two bytes relative to siblingv2:
 # own26, explicit28,22, bounded32/33, and masked24/25/27.
 s=(R/'build/battletoads-only-transport-v2/joint/src/new_roster_dispatch.s').read_text()
 a=s.index('::GmOnlyCommon:');z=s.index('::GmOnlyLegacy:',a)
 t=s[a:z].replace('cmp #25','cmp #28').replace('and #$fb','and #$fc');s=s[:a]+t+s[z:]
 write(J/'src/new_roster_dispatch.s',s)
 # Concrete own cold chains and selected raw3 metadata producer.
 s=(J/'src/character_select.s').read_text().replace('.import FwMuxMenuResolve','.import BwMenuResolve').replace('farcall FwMuxMenuResolve,jmp','farcall BwMenuResolve,jmp');write(J/'src/character_select.s',s)
 s=(J/'screen_render.s').read_text().replace('farcall S2InitScreenPrepare','farcall BwScene');write(J/'screen_render.s',s)
 s=(J/'src/mmc5.s').read_text().replace('.bank(DpArtStart)|$80),$ff,$c9,$ff,$8c','.bank(DpArtStart)|$80),$ff,$c9,3,$8c');write(J/'src/mmc5.s',s)
 s=(J/'src/full_roster_menu.s').read_text().replace('lda #16\n bne Pending\nBowser3:lda #15\n bne Pending','lda #16\n clc\n rts\nBowser3:lda #15\n clc\n rts')
 a=s.index('.proc FmStartFlags');z=s.index('.endproc',a)
 s=s[:a]+'.proc FmStartFlags\n farcall BwStartFlags,jmp\n .res 10,$ea\n'+s[z:];write(J/'src/full_roster_menu.s',s)
 s=(J/'src/full_roster_menu_art.inc').read_text().replace('*SMB3 BOWSER',' SMB3 BOWSER').replace('*SMB1 BOWSER',' SMB1 BOWSER');write(J/'src/full_roster_menu_art.inc',s)
 # Adopt only genuine BT source producers/config partitions already granted.
 s=(J/'private.cfg').read_text()
 changes={
 'X5_NEW_5D:start=$a000,size=$fa7,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;':'X5_NEW_5D:start=$a000,size=$dc0,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;\nBT_ROM_LOADER_MEM:start=$adc0,size=$1e7,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5d;',
 'X5_NEW_57: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;':'X5_NEW_57:start=$a000,size=$1020,type=ro,file=%O,fill=yes,fillval=$ff,bank=$57;\nBT_ROM_ROUTER_MEM:start=$b020,size=$e0,type=ro,file=%O,fill=yes,fillval=$ff,bank=$57;\nBT_57_TAIL:start=$b100,size=$f00,type=ro,file=%O,fill=yes,fillval=$ff,bank=$57;',
 'X5_NEW_48: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$48;':'X5_NEW_48:start=$a000,size=$1011,type=ro,file=%O,fill=yes,fillval=$ff,bank=$48;\nBT_ROM_PREVIEW_MEM:start=$b011,size=$ef,type=ro,file=%O,fill=yes,fillval=$ff,bank=$48;\nBT_48_TAIL:start=$b100,size=$f00,type=ro,file=%O,fill=yes,fillval=$ff,bank=$48;',
 'ROGUE_AUDIO_PAGES_8: load=X5_NEW_57,':'ROGUE_AUDIO_PAGES_8: load=BT_57_TAIL,',
 'ROGUE_AUDIO_PAGES_9: load=X5_NEW_48,':'ROGUE_AUDIO_PAGES_9: load=BT_48_TAIL,',
 'UNALLOCATED_CHR_MEM:start=$e1400,size=$6800,type=ro,fill=yes,file=%O,fillval=$00;':'BENJ_RETAINED_CHR_MEM:start=$e1400,size=$3800,type=ro,fill=yes,file=%O,fillval=$00;\nBT_CHR_MEM:start=$e4c00,size=$1000,type=ro,fill=yes,file=%O,fillval=$00;\nBT_STREAM_MEM:start=$e5c00,size=$2000,type=ro,fill=yes,file=%O,fillval=$00;'
 }
 for a,z in changes.items():assert s.count(a)==1,a;s=s.replace(a,z)
 s=s.replace('MEMORY {','MEMORY {\nBT_CACHE_MEM:start=$a000,size=$2000,bank=3,type=ro,file="'+(BT/'cache.bin').as_posix()+'",fill=yes,fillval=$ff;\n',1)
 bt_cfg=(B/'joint/private.cfg').read_text();a=bt_cfg.index(' BT_ROM_LOADER:');z=bt_cfg.index(' BT_CACHE_INVALID_COOKIE:',a);z=bt_cfg.index(';',z)+1
 s=s.replace('SEGMENTS {','SEGMENTS {\n'+bt_cfg[a:z]+'\n',1);write(J/'private.cfg',s)
 # All actual output paths validated before every producer invocation.
 cc=R/'tools/Windows/cc65/bin';commands=[]
 def run(n,c):
  guard=validate(c,J,cwd=R);r=subprocess.run(c,cwd=R,text=True,capture_output=True);write(O/(n+'.json'),json.dumps(dict(command=c,validation=guard,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2)+'\n');assert r.returncode==0,(n,r.stderr);commands.append(n)
 def asm(folder,n):run(folder.name+'-'+n+'-build',[str(cc/'ca65.exe'),'--cpu','6502x','-g','-I',str(D),'-I',str(J),'-I',str(J/'src'),'--create-full-dep',str(folder/(n+'.dep')),'-o',str(folder/(n+'.o')),str(folder/(n+'.s'))])
 for n in ['host','core','art','image-tail','load','copy','check','retire','router','preview','cold','stream']:asm(D,n)
 for n in ['core','art','api','loader','router','preview','stream']:asm(BT,n)
 entry=(J/'entrypoint.s').read_text();extra=['BwScene','BwMenuResolve','BwStartFlags'];write(J/'entrypoint.s','.import '+','.join(extra)+'\n.export FmGroups,CmHostFresh,FmQueueName,JnResetDispatch,DrawMetasprite,WriteGameText\n'+entry)
 for n in ['main','union']:
  c=json.loads((J/(n+'-build.json')).read_text())['command'][:];c[1:1]=['-I',str(J),'-I',str(J/'src')]
  for flag in ['-o','--create-full-dep','--create-dep']:
   if flag in c:c[c.index(flag)+1]=str(J/(n+'.o'if flag=='-o'else n+'.dep'))
  c[-1]=str(J/('entrypoint.s'if n=='main'else'union.s'));run(n+'-build',c)
 c=json.loads((P/'final-link.json').read_text())['command'][:]
 for i,x in enumerate(c):
  if x.startswith(str(P/'joint')):c[i]=x.replace(str(P/'joint'),str(J))
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in c:c[c.index(flag)+1]=str(J/Path(c[c.index(flag)+1]).name)
 if '--ld-args'in c:
  i=c.index('--ld-args')+1;v=c[i].split(',')
  for k in range(1,len(v),2):v[k]=str(J/Path(v[k]).name)
  c[i]=','.join(v)
 # Only the actual main and union source importers are replaced.
 for i,x in enumerate(c):
  if x.endswith(('\\union.o','/union.o')):c[i]=str(J/'union.o')
 c += [str(D/'cold.o')]+[str(BT/(n+'.o'))for n in ['core','art','api','loader','router','preview','stream']]
 run('initial-link',c)
 image=(J/'bowser.bin').read_bytes();assert len(image)==8192
 (D/'cookie.bin').write_bytes(bytes([167,27,0,3])+hashlib.sha256(image).digest()[:12]);asm(D,'check');asm(D,'stream');run('final-link',c)
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes')
 b=load(J/'candidate.nes');old=load(P/'joint/candidate.nes')
 moves=[n for n,z in old['syms'].items()if not n.startswith('Bw')and n in b['syms']and b['syms'][n]['val']!=z['val']]
 assert not moves,moves[:20]
 for n in ['ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n)
 q=dict(source=True,candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),native=False,admitted=False,source_callbacks='Actual menu resolve before selected publication; native scene first, load+constructor verified; all36 workers genuine; raw27 pending root native qualification',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'private.cfg',J/'bowser.bin',D/'cookie.bin']})
 write(O/'source-stage.json',json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
