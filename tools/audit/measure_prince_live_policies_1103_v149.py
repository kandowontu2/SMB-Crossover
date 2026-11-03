"""Measure cold-to-live owned policies; no ROM, shared writes or new grant."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_strike_manifest_1103_v130 as C
O=C.O;A=C.M.A


def assemble(name,text,cfg):
 data,labels=A.assemble(name,text,cfg)
 # The object is an invocation-local linker intermediate, not a proof input.
 (O/(name+'.o')).unlink()
 return data,labels


def main():
 _,manifest=C.image();old=json.loads((O/'native-labels-v145.json').read_text());refs=dict(old)
 texts={n:(O/f'native-{n}-v145.s').read_text()for n in ['services','battle','proxy','public','policies','audio','small']}
 # Kind0's obsolete KillPlayer target has no live caller. Kind1/2/3 remain
 # the exact native defeat, star/1up collector and death updater respectively.
 texts['services']=texts['services'].replace('NativeBank:.byte Bank_KillPlayer,','NativeBank:.byte $cf,')
 for op in ['<','>']:
  needle=f'Native{"Lo"if op=="<"else"Hi"}:.byte {op}KillPlayer,'
  assert texts['audio'].count(needle)==1
  texts['audio']=texts['audio'].replace(needle,needle.replace(op+'KillPlayer',op+'$bae7'))
 texts['policies']='PpNativeCall=$da1b\n'+texts['policies']
 needle=' tya\n pha\n ldx VRAM_Buffer1_Offset'
 assert texts['policies'].count(needle)==1
 texts['policies']=texts['policies'].replace(needle,' tya\n pha\n ldy #0\n jsr PpNativeCall\n ldx VRAM_Buffer1_Offset')
 p=texts['public'];needle=' cmp #102\n beq Late\n pla\n clc\n rts'
 assert p.count(needle)==1 and p.count('Late:pla\n jmp PpNativeDeferredKill\n')==1
 p=p.replace(needle,' jmp PpLiveDispatch').replace('Late:pla\n jmp PpNativeDeferredKill\n','')
 texts['public']='PpLiveDispatch=$bfa3\n'+p
 live='''PpNativeDeferredKill=$c781
VRAM_Buffer1=$04af
.setcpu "6502"
.segment "LIVE"
.export PpLiveDispatch,PpLiveName,PpLiveEnd
PpLiveDispatch:
 cmp #102
 beq Late
 cmp #90
 beq PpLiveName
 pla
 clc
 rts
Late:
 pla
 jmp PpNativeDeferredKill
PpLiveName:
 pla
 cmp #0
 bne NameDone
 pha
 tya
 pha
 ldy #6
NameLoop:
 lda NameData,y
 sta VRAM_Buffer1+11,y
 dey
 bpl NameLoop
 pla
 tay
 pla
NameDone:
 sec
 rts
NameData:.byte 25,27,18,23,12,14,36
PpLiveEnd:
 .res 53-(*-PpLiveDispatch),$ea
'''
 livebytes,livelab=assemble('native-live-v149',live,'MEMORY{M:start=$bfa3,size=$35,file=%O;}SEGMENTS{LIVE:load=M,type=ro;}')
 assert len(livebytes)==53 and livelab['PpLiveEnd']<=0xbfd8
 images={};labels={};ends={};previous=None
 for iteration in range(8):
  refs.update({k:v for row in labels.values()for k,v in row.items()})
  if 'services'in labels:refs['PpNativeSfx']=refs['PpNativeRawSfx']=labels['services']['PpNativeQuietSfx']
  if 'battle'in labels:refs['PpOriginalDefenderContact']=labels['battle']['PpBattle_4_ACEC']
  at=old['PpNativeInit']
  for name,segment in [('services','SERVICES'),('battle','BATTLE'),('proxy','PROXY'),('public','PUBLIC'),('policies','COLORS'),('audio','AUDIO'),('small','SMALL')]:
   text=re.sub(r'(?m)^(\w+)=\$[0-9a-fA-F]+$',lambda m:f'{m[1]}=${refs[m[1]]:04x}'if m[1]in refs else m[0],texts[name])
   supplemental='';segments=''
   if name=='public':supplemental=f'F:start=$b3ef,size=$11,file="{(O/"native-fresh-v149.bin").as_posix()}";';segments='FRESH_PREFIX:load=F,type=ro;'
   if name=='policies':supplemental=f'C:start=$bd22,size=$1c,file="{(O/"native-contact-v149.bin").as_posix()}";';segments='CONTACT:load=C,type=ro;'
   start=0xc766 if name=='audio'else 0xbd3e if name=='small'else at
   cfg=f'MEMORY{{M:start=${start:04x},size=$800,file=%O;{supplemental}}}SEGMENTS{{{segment}:load=M,type=ro;{segments}}}'
   images[name],labels[name]=assemble('native-'+name+'-v149',text,cfg);refs.update(labels[name]);ends[name]=[start,start+len(images[name])]
   if name not in ['audio','small']:at+=len(images[name])
  signature=json.dumps(labels,sort_keys=True)
  if signature==previous:break
  previous=signature
 else:raise AssertionError('Live policy relink did not converge')
 meta=(O/'native-metadata-v145.bin').read_bytes()[:old['PpNativeInit']-0xc800]+b''.join(images[n]for n in ['services','battle','proxy','public','policies'])
 assert len(meta)==6092 and labels['public']['PpNativeRoute']==old['PpNativeRoute']and labels['services']['PpNativeRetire']==old['PpNativeRetire']
 runtime=bytearray((O/'native-runtime-v145.bin').read_bytes())
 # Every source/metadata entry keeps its prior address except this smaller
 # scalar resolver suffix and the adjacent five-byte-expanded colors leaf.
 runtime[0xb3ef-0xa000:0xb3fc-0xa000]=(O/'native-fresh-v149.bin').read_bytes()
 runtime[0xbd22-0xa000:0xbd3e-0xa000]=(O/'native-contact-v149.bin').read_bytes()
 runtime[0xbd3e-0xa000:0xbd4b-0xa000]=images['small']
 oldfinal=bytes(runtime[0xbfc4-0xa000:0xbfdf-0xa000])
 assert oldfinal[:4]==bytes.fromhex('8aa89900')and oldfinal[18:21]==bytes.fromhex('4ce7de'),oldfinal.hex()
 final='''PpNativeResetTail=$dee7
.setcpu "6502"
.segment "FINAL"
.export PpStageLive,PpStageLiveEnd
PpStageLive:
 ldy #52
Copy:
 lda $c6f9,y
 sta $c200,y
 dey
 bpl Copy
 txa
 jmp PpNativeResetTail
PpStageLiveEnd:
 .res 27-(*-PpStageLive),$ea
'''
 finalbytes,finallab=assemble('native-final-v149',final,'MEMORY{M:start=$bfc4,size=$1b,file=%O;}SEGMENTS{FINAL:load=M,type=ro;}')
 assert len(finalbytes)==27 and finallab['PpStageLiveEnd']<=0xbfdf
 runtime[0xbfc4-0xa000:0xbfdf-0xa000]=finalbytes
 code=(O/'native-state_code-v18.bin').read_bytes();assert len(code)==1375 and code[0xc200-0xc0b0:0xc235-0xc0b0]==bytes(53)
 assert len(images['audio'])<=154
 state=code+images['audio']+bytes(154-len(images['audio']))+livebytes
 assert len(runtime)==8159 and len(state)==1582
 combined=dict(old,**{n:v for row in labels.values()for n,v in row.items()if n.startswith('Pp')or n in ['NativeLo','NativeHi','NativeBank']},**livelab,**finallab)
 for n,data in [('runtime',runtime),('metadata',meta),('state',state)]:(O/f'native-{n}-v149.bin').write_bytes(data)
 (O/'native-labels-v149.json').write_text(json.dumps(combined,indent=2)+'\n')
 # Exact source-only shared alternative. No current resident file is edited.
 owner=(O/'post-owner-v130.s').read_text();needle=' jsr PrTypedWorker\n .res 15,$ea\n'
 assert owner.count(needle)==1
 owner=owner.replace(needle,''' jsr PrTypedWorker
 jmp PrAfterStageClear
PrClearStage:
 ldy #52
 lda #0
PrClearStageLoop:
 sta $c200,y
 dey
 bpl PrClearStageLoop
 sec
 rts
PrAfterStageClear:
''')
 needle=' cmp #38\n beq PrWorkerPrince\n sec ; Successful common Ex37/Bub39 cold must retain C1 after CMP.\n rts'
 assert owner.count(needle)==1
 owner=owner.replace(needle,' eor #38 ; Preserve the common worker success carry.\n beq PrWorkerPrince\n rts')
 needle='PrWorkerPrince:\n CoFar PrColdBoot,3\nPrWorkerDone:'
 assert owner.count(needle)==1
 owner=owner.replace(needle,'PrWorkerPrince:\n CoFar PrColdBoot,3\n bcc PrWorkerDone\n jmp PrCopyLive\nPrWorkerDone:')
 owner='PrCopyLive=$a7da\n'+owner
 cfg=(O/'post-owner-v130.cfg').read_text().replace('post-owner-extra-v130.bin','post-owner-extra-v149.bin')
 ownerbin,ownerlab=assemble('post-owner-v149',owner,cfg);extrabin=(O/'post-owner-extra-v149.bin').read_bytes()
 assert len(ownerbin)==531 and len(extrabin)==98
 for name in ['CoCold','CoRetire','CoCheckCode','CoCheckHeaders','CoOwnerEnd']:
  assert ownerlab[name]==A.L.P.T.labels(O/'post-owner-v130.lbl')[name]
 sel=(O/'post-selector-v130.s').read_text()+f'''\nPrClearStage=${ownerlab['PrClearStage']:04x}
PrCopyLive:
 ldy #52
PrCopyLiveLoop:
 lda $c200,y
 sta $bfa3,y
 cmp $bfa3,y
 bne PrCopyLiveFailed
 dey
 bpl PrCopyLiveLoop
 jmp PrClearStage
PrCopyLiveFailed:
 clc
 rts
'''
 selbin,sellab=assemble('post-selector-v149',sel,(O/'post-selector-v130.cfg').read_text())
 assert sellab['PrCopyLive']==0xa7dc,(sellab['PrCopyLive'],len(selbin))
 # ExForeignLo's two data bytes end at A7DC; the21-byte leaf follows there.
 # Resolve the one forward address after compilation, preserving selector.
 owner=owner.replace('PrCopyLive=$a7da',f'PrCopyLive=${sellab["PrCopyLive"]:04x}')
 ownerbin,ownerlab=assemble('post-owner-v149',owner,cfg)
 assert len(selbin)==177 and len(ownerbin)==531 and len(extrabin)==98
 q=dict(measured=True,qualified=False,ROM_written=False,shared_files_mutated=False,root_grant_required=True,parent_memory_SHA256=manifest['expected_memory_only_SHA256'],components=ends,runtime_bytes=len(runtime),metadata_bytes=len(meta),metadata_end=0xc800+len(meta),state_bytes=len(state),live_bytes=len(livebytes),live_half_open=[0xbfa3,0xbfd8],staged_live_half_open=[0xc6f9,0xc72e],cold_packet_half_open=[0xc200,0xc235],manager_bytes=len(ownerbin),extra_bytes=len(extrabin),selector_bytes=len(selbin),selector_spare=178-len(selbin),manager_executed_NOPs_replaced=15,native_kind0_target=['physicalPRG79',0xbae7],required='Exact original/private instruction and indirect constructor/call coverage, all NativeCallKind writers/value closure; complete new compressed backing/current cookie/fullcold, stage copy readback/zero-before-publish, foreign fullcold/retire ABI, warmFresh, actual palette/status ingress and IRQ/FF/nested. Proposed shared21-selector/4-extra/15-executedNOP funding conflicts with separate ungranted DK layout and needs root choice. No new candidate or admission.',bindings={p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),O/'native-labels-v145.json',O/'native-runtime-v145.bin',O/'native-metadata-v145.bin',O/'native-state-v145.bin',O/'post-owner-v130.s',O/'post-selector-v130.s',O/'strike-manifest-v130.json',*[O/f'native-{n}-v149.bin'for n in ['runtime','metadata','state','live','final']],O/'post-owner-v149.s',O/'post-owner-v149.bin',O/'post-owner-extra-v149.bin',O/'post-selector-v149.s',O/'post-selector-v149.bin']})
 (O/'live-policies-measurement-v149.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
