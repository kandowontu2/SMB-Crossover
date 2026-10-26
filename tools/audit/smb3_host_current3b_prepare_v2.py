"""Private source integration of authenticated SMB3 music on frozen adopted3b."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'root-current-roster-composition-v1';CORE=D/'smb3-native-readers-opt-v2';OLD=D/'smb3-native-core-v5'
PARENT='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

ADAPTER=r'''
B3SourceImage=XgLzHistory
B3SourceTimers=XgLzHistory+$40
B3SourceZp=XgAudioPtr
B3Pending=XgAudioSelection
; Owned shared DMC value4 uses the existing priority byte only as lease marker.
; It is mutually exclusive with active CV3. Existing owners0..3 are unchanged.
.segment "SMB3_NATIVE_CORE"
.proc B3ExpandedRoutes
 cmp #18
 bcs ShipOrOther
 BankPRGA #86
 jmp B3MusicUpdate
ShipOrOther:
 bne Legacy
 lda VvVariant
 bne Legacy
 BankPRGA #.bank(GradiusAudioUpdate)
 jmp GradiusAudioUpdate
Legacy:jmp LmNativeMusicGate
.endproc
.proc B3HostMute
 lda #0
 sta GuestNativeEnable
 sta GuestCombinedEnable
 sta $4015
 sta BassDmcActive
 sta Cv3DmcPriority
 lda #$ff
 sta $5117
 rts
.endproc
.proc B3ResetImage
 jsr B3HostMute
 lda #0
 ldx #47
ClearImage:sta B3SourceImage,x
 dex
 bpl ClearImage
 ldx #10
ClearTimers:sta B3SourceTimers,x
 dex
 bpl ClearTimers
 ldx #31
ClearScratch:sta XgLzHistory+$6e0,x
 dex
 bpl ClearScratch
 ldx #5
ClearZp:sta B3SourceZp,x
 dex
 bpl ClearZp
 ldx #15
ClearApu:sta GuestNativeApu,x
 lda #1
 sta GuestNativeDirty,x
 lda #0
 dex
 bpl ClearApu
 rts
.endproc
; Same-bank software cleanup before genuine vanilla SoundEngine.
.segment "SMB3_VANILLA_GATE"
.proc B3VanillaMusicGate
 php
 lda XgAudioCharacter
 cmp #$fa
 bne CheckOwner
 lda #$ff
 sta XgAudioCharacter
CheckOwner:lda BassDmcActive
 cmp #4
 bne Done
 lda #0
 sta $4015
 sta BassDmcActive
 sta Cv3DmcPriority
 sta $4011
 lda #$ff
 sta $5117
Done:plp
 jmp SoundEngine
.endproc
.assert *<=$c000,lderror,"Only verified bank5 tail after Sophia cold"
.segment "SMB3_NATIVE_COLD"
.proc B3MusicUpdate
 lda #0
 sta RgAudioRequest
 lda XgAudioCharacter
 cmp #$fa
 beq Initialized
 lda #$fa
 sta XgAudioCharacter
 lda #0
 sta RgAudioSilenced
 lda #9
 sta B3Pending
Initialized:
 lda AreaMusicQueue
 ora EventMusicQueue
 and #Silence
 beq Area
 lda #1
 sta RgAudioSilenced
Area:lda AreaMusicQueue
 and #$7f
 beq Event
 ldx #0
FindArea:lsr
 bcs AreaFound
 inx
 bne FindArea
AreaFound:lda Areas,x
 sta B3Pending
 lda #0
 sta RgAudioSilenced
Event:lda EventMusicQueue
 and #$7f
 beq Pause
 ldx #0
FindEvent:lsr
 bcs EventFound
 inx
 bne FindEvent
EventFound:lda Events,x
 sta B3Pending
 lda #0
 sta RgAudioSilenced
Pause:lda GamePauseStatus
 and #1
 bne Mute
 lda RgAudioSilenced
 bne Mute
 lda B3Pending
 bne Restart
 ; Restore held ordinary voices after pause; never fabricate a DMC retrigger.
 lda B3Source4015
 and #15
 sta GuestNativeEnable
 lda #0
 ldx #0
 ldy #0
 jsr B3SourceA000
 jmp Queues
Restart:sta RgAudioSong
 inc XgAudioSong
 jsr B3ResetImage
 lda RgAudioSong
 sec
 sbc #1
 ldx #0
 ldy #0
 jsr B3StandaloneCold
 lda #0
 sta B3Pending
 jmp Queues
Mute:jsr B3HostMute
Queues:lda #0
 sta AreaMusicQueue
 sta EventMusicQueue
 sta Square1SoundQueue
 sta Square2SoundQueue
 sta NoiseSoundQueue
 rts
Areas:.byte 9,11,12,23,14,1,13
Events:.byte 43,42,39,39,42,38,27
.endproc
'''
STATUS=r'''
.proc B3Write4015
 php
 pha
 sta B3Source4015
 sta GuestNativeEnable
 and #16
 beq Disable
 lda B3PendingClone
 sta B3ActiveClone
 sta $5117
 lda #4
 sta BassDmcActive
 lda #$80
 sta Cv3DmcPriority
 pla
 pha
 jsr Publish
 jmp Done
Disable:
 pla
 pha
 jsr Publish ; ORIGINAL disable precedes any E-bank restoration.
 lda #0
 sta BassDmcActive
 sta Cv3DmcPriority
 lda #$ff
 sta $5117
Done:pla
 plp
 rts
Publish:sta GuestCombinedEnable
 lda GuestMixMask
 and #8
 ora GuestCombinedEnable
 sta GuestCombinedEnable
 sta $4015
 rts
.endproc
'''

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();o=a.output.resolve();assert not o.is_relative_to(R);o.mkdir(parents=True,exist_ok=False)
 assert sha(BASE/'candidate.nes')==PARENT;assert sha(CORE/'candidate.nes')=='e578d0de91b0613ccfd6907467109c7c30dabd3fa69dcbefb4fe68c4ed4e2eff'
 manifest=json.loads((BASE/'source-manifest.json').read_text());src=o/'source';src.mkdir()
 for n,h in manifest.items():
  assert sha(BASE/'source'/n)==h,n;f=src/n;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/'source'/n,f)
 def editfile(n,edits):
  f=src/n;b=f.read_bytes();nl=b'\r\n'if b'\r\n'in b else b'\n'
  for old,new in edits:
   old=old.replace('\n',nl.decode()).encode();new=new.replace('\n',nl.decode()).encode();assert b.count(old)==1,(n,old,b.count(old));b=b.replace(old,new)
  f.write_bytes(b)
 cfg='smb1base-mmc5-expanded.cfg'
 editfile(cfg,[('X5_NEW_5F: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5f;','X5_NEW_5F: start=$a000,size=$0340,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5f;\n    SMB3_ASSET_Z2_C95:start=$c340,size=$0380,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5f;\n    SMB3_ASSET_MIKE_C95:start=$c6c0,size=$0940,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5f;\n    B3_PAYLOAD95:start=$d000,size=$1000,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5f;'),('MIKE_GFX:load=X5_NEW_61,type=ro;','MIKE_GFX:load=SMB3_ASSET_MIKE_C95,type=ro,start=$c6c0;'),('Z2_GFX: load=X5_NEW_46,type=ro,optional=yes;','Z2_GFX:load=SMB3_ASSET_Z2_C95,type=ro,start=$c340,optional=yes;'),('BILL_ORBIT_2: load=XG_AUDIO_MEM, type=ro, optional=yes; # Existing C000 FF tail; all prior data fixed.','BILL_ORBIT_2:load=X5_NEW_55,type=ro,start=$cbe8,optional=yes;'),('VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro;','SMB3_NATIVE_CORE:load=XG_AUDIO_MEM,type=ro,start=$cbe8;\n    VG_AUDIO_DISPATCH:load=XG_AUDIO_MEM,type=ro,start=$dfe8;')])
 for bank in [78,86,90,93,96,98,118,119]:
  old=f'X5_NEW_{bank:02X}: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=${bank:02x};'
  prefix=old.replace('size=$2000','size=$1000')if bank!=86 else old.replace('size=$2000','size=$0800')+'\n    B3_COLD86:start=$a800,size=$0200,type=ro,file=%O,fill=yes,fillval=$ff,bank=$56;\n    B3_GAP86:start=$aa00,size=$0600,type=ro,file=%O,fill=yes,fillval=$ff,bank=$56;'
  editfile(cfg,[(old,prefix+f'\n    B3_PAYLOAD{bank}:start=$b000,size=$1000,type=ro,file=%O,fill=yes,fillval=$ff,bank=${bank:02x};')])
 for bank in [70,97]:editfile(cfg,[(f'X5_NEW_{bank:02X}: start=$c000, size=$2000',f'X5_NEW_{bank:02X}: start=$e000, size=$2000')])
 extra='\n    SMB3_NATIVE_COLD:load=B3_COLD86,type=ro;\n    SMB3_DMC_CLONE70:load=X5_NEW_46,type=ro;\n    SMB3_DMC_CLONE97:load=X5_NEW_61,type=ro;\n    SMB3_VANILLA_GATE:load=PRGA_05,type=ro,start=$beec;\n'
 for page,bank in enumerate([78,86,90,93,95,96,98,118,119]):extra+=f'    SMB3_SOURCE_PAGE{page}:load=B3_PAYLOAD{bank},type=ro;\n'
 editfile(cfg,[('SEGMENTS {','SEGMENTS {'+extra)])
 raw=(CORE/'source/src/smb3_native_standalone.s').read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';text=raw.decode();rows=json.loads((OLD/'preparation.json').read_text())['emitted_original_instruction_rows'];projection={}
 for r in rows:
  old=r['linked_instruction'];m=re.search(r'\$([0-9a-f]{2,4})(?:[,)]|$)',old,re.I)
  if not m or 'B3Read'in old or '#$'in old:continue
  at=int(m[1],16);expr=None
  if 0x4d0<=at<=0x4ff:expr=f'B3SourceImage+${at-0x4d0:02x}'
  elif 0x7f0<=at<=0x7fa:expr=f'B3SourceTimers+${at-0x7f0:02x}'
  elif at in [0x6b,0x6c,0x6d,0x6e,0x71,0x72]:expr=f'z:B3SourceZp+{[0x6b,0x6c,0x6d,0x6e,0x71,0x72].index(at)}'
  if expr:
   before=f"B3Source{r['source_PC']:04X}:\n "+old;after=before.replace(m[0].rstrip(',)'),m[0].rstrip(',)').replace('$'+m[1],expr))
   before,after=(v.replace('\n',nl)for v in [before,after]);assert text.count(before)==1,(r,before);text=text.replace(before,after);projection[at]=expr
 text=text.replace(' lda $6b',' lda z:B3SourceZp').replace(' lda $6c',' lda z:B3SourceZp+1').replace(' lda $71',' lda z:B3SourceZp+4').replace(' lda $72',' lda z:B3SourceZp+5')
 # A86 is the explicit adapter lease, never the foreground CurrentBank shadow.
 assert text.count(' lda CurrentBank')==2;text=text.replace(' lda CurrentBank',' lda #86|MMC5_PRG_ROM'+nl+' nop')
 start=text.index('B3Write4015:');end=text.index('B3Write4015X:');text=text[:start]+STATUS.strip().replace('\n',nl)+nl+text[end:]
 writers=[]
 for r in rows:
  m=re.fullmatch(r'(STA|STX) \$(40[0-9a-f]{2})(?:,([XY]))?',r['source_instruction'],re.I)
  if not m:continue
  op,at,reg=m[1].upper(),int(m[2],16),(m[3]or'').upper()
  if at>=0x4010:continue
  offset=at-0x4000;name=f'B3Image{op}{offset:02X}{reg}';old=f"B3Source{r['source_PC']:04X}:\n "+r['linked_instruction'];new=f"B3Source{r['source_PC']:04X}:\n jsr {name}"
  old,new=(s.replace('\n',nl)for s in [old,new]);assert text.count(old)==1,(r,old);text=text.replace(old,new);writers.append((name,op,offset,reg))
 direct=[]
 for name,op,offset,reg in sorted(set(writers)):
  suffix=','+reg.lower()if reg else'';direct +=[name+':',f' {op.lower()} GuestNativeApu+{offset}{suffix}',' php',f' inc GuestNativeDirty+{offset}{suffix}',' plp',' rts']
 # Put core helpers before real core end; put A86 updater before real cold end.
 adapter=ADAPTER.strip();cpart,apart=adapter.split('.segment "SMB3_NATIVE_COLD"',1)
 text=text.replace('B3CoreEnd:',(nl.join(direct)+nl+cpart.replace('\n',nl)+nl+'.segment "SMB3_NATIVE_CORE"'+nl)+'B3CoreEnd:')
 text=text.replace('B3ColdEnd:','.segment "SMB3_NATIVE_COLD"'+nl+apart.replace('\n',nl)+nl+'B3ColdEnd:')
 target=src/'src/smb3_native_standalone.s';target.write_bytes(text.encode())
 payload=(CORE/'source/audio/smb3-native/source-payload.bin').read_bytes();assets=src/'audio/smb3-native';assets.mkdir(parents=True);(assets/'source-payload.bin').write_bytes(payload)
 raw=(CORE/'source/src/smb3_native_payload.s').read_text();raw=re.sub(r'\.incbin "audio/smb3-native/clone(?:70|97)\.bin"','.res 8192,$ff',raw);(src/'src/smb3_native_payload.s').write_bytes(raw.replace('\n','\r\n').encode())
 f=src/'src/entrypoint.s';b=f.read_bytes();eol=b'\r\n'if b'\r\n'in b else b'\n';f.write_bytes(b+eol+b'.if ::ENABLE_MMC5_EXPANDED'+eol+b'.include "smb3_native_standalone.s"'+eol+b'.include "smb3_native_payload.s"'+eol+b'.endif'+eol)
 editfile('src/gradius_audio.s',[('  cmp #18\n  bne Legacy\n  lda VvVariant\n  bne Legacy\n  BankPRGA #.bank(GradiusAudioUpdate)\n  jmp GradiusAudioUpdate\nLegacy:', '  cmp #17\n  bcc Legacy\n  jmp B3ExpandedRoutes\n  .res 10,$ea\nLegacy:')])
 editfile('src/cv3_dmc_complete.s',[('  PLACEHOLDER','')])if False else None
 # Exact old source uses one-space instructions; only owner4 gets new behavior.
 editfile('src/cv3_dmc_complete.s',[(' cmp #3\n beq Owned\n lda #0\n sta Cv3DmcPriority\nOwned:',' cmp #3\n bcs Owned\n lda #0\n sta Cv3DmcPriority\nOwned:')])
 editfile('src/cv3_dmc_completion.inc',[(' cmp #3\n beq SourceCompletion',' cmp #3\n bcs SourceCompletion')])
 editfile('src/music_drivers/audio.s',[('      MusicPlayback\n  .endif','      MusicPlayback\n  .endif')])if False else None
 # Change only the original same-A5-bank call operand, retaining all fixed PCs.
 editfile('src/music_drivers/vanilla_music.s',[('  jsr SoundEngine\n.endmacro',' .if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr B3VanillaMusicGate\n .else\n  jsr SoundEngine\n .endif\n.endmacro')])
 put(o/'source-projection.json',projection);put(o/'source-manifest.json',{str(f.relative_to(src)).replace('\\','/'):sha(f)for f in src.rglob('*')if f.is_file()})
 cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(o/'candidate.nes')];run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/'build-command.json',dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stdout+run.stderr
 print(json.dumps(dict(linked=True,NOT_yet_postlink_mirrored=True,ROM_sha256=sha(o/'candidate.nes'),parent=PARENT),indent=2))
if __name__=='__main__':main()
