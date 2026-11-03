"""Measured full battle/proxy/services relink, private image only, no ROM."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import prepare_prince_successor_manifest_1102_v26 as M
from check_tmnt_render_oa import address,location
P,O=A.L.P,A.O


def clean(text,names):
 return '\n'.join(line for line in text.splitlines()if not any(re.match(re.escape(n)+r'=\$',line)for n in names))+'\n'


def defs(values):return ''.join(f'{n}=${v:04x}\n'for n,v in values.items())


def main():
 base,_,_,_=M.bundle();old=P.T.labels(O/'host-services-v18.lbl');life=P.T.labels(O/'host-life-v12.lbl');grid=P.T.labels(O/'pose-grid-helper-v37.lbl')
 services=(O/'host-services-v18.s').read_text().replace('.segment "SERVICES"','.macpack longbranch\n.segment "SERVICES"')
 services=services.replace(' jsr PpHostInit\n',' jsr PpHostInit\n lda $c084\n sta $c07f\n lda $c085\n sta $c080\n',1)
 services=services.replace(' ldx #0                 ; original F158 consumes X=actor slot',' jsr PpNativeProxyIn\n ldx #0                 ; original F158 consumes X=actor slot')
 services=services.replace(' jsr PpNativeMotionExport\n',' jsr PpNativeProxyOut\n jsr PpNativeMotionExport\n',1)
 # The real original environmental fall sets4CE=2. Combat death retains its
 # complete original85 animation until185; no fabricated timer/grace.
 services=services.replace('PpNativePitDeath:\n lda PpDead\n bne Rejected\n','''PpNativePitDeath:
 lda PpDead
 bne DeathDone
 lda $c6cf
 bne NativePit
 lda $c4ce
 cmp #2
 beq Kill
 lda $c616
 cmp #85
 bne NativePit
 lda $c617
 cmp #185
 beq Kill
NativePit:
''')
 services=services.replace(' bcc Rejected\n',' bcc DeathDone\n').replace(' bne CheckHigh\n',' bne CheckHigh\n')
 start=services.index(' ; FarCallCommon owns five');end=services.index('; Quiet event boundary',start)
 services=services[:start]+''' ldx #0
 ldy #0
 jmp PpNativeCall
DeathDone:
 clc
 rts
; Both genuine host services share exactly the same13-byte foreground lease.
; Slot/kind are synchronous owned instruction operands, never shared RAM.
.export PpNativeCall,PpNativeCallSlot,PpNativeCallKind,SmcOffsets
PpNativeCall:
 stx PpNativeCallSlot+1
 sty PpNativeCallKind+1
 ldx #0
SaveZp:
 lda R0,x
 pha
 inx
 cpx #8
 bne SaveZp
 ldx #0
SaveSmc:
 ldy SmcOffsets,x
 lda $0100,y
 pha
 inx
 cpx #5
 bne SaveSmc
PpNativeCallKind:ldy #0
 lda NativeLo,y
 sta FarcallJmpTarget_SMC+1
 lda NativeHi,y
 sta FarcallJmpTarget_SMC+2
 lda NativeBank,y
PpNativeCallSlot:ldx #0
 jsr FarCallCommon
 ldx #4
RestoreSmc:
 pla
 ldy SmcOffsets,x
 sta $0100,y
 dex
 bpl RestoreSmc
 ldx #7
RestoreZp:
 pla
 sta R0,x
 dex
 bpl RestoreZp
 sec
 rts
SmcOffsets:
 .byte <(SafecallA_SMC+1),<(FarcallJmpTarget_SMC+1),<(FarcallJmpTarget_SMC+2),<(NextBank_SMC+1),<(SafereturnA_SMC+1)
NativeLo:.byte <KillPlayer,<NativeDefeat
NativeHi:.byte >KillPlayer,>NativeDefeat
NativeBank:.byte Bank_KillPlayer,NativeDefeatBank
'''+services[end:]
 proxy=(O/'native-proxy-v40.s').read_text();a=proxy.index(' ldx #0\nSaveZp:',proxy.index('PpNativeProxyOut:'));z=proxy.index(' lda #0\n sta $c61c',a)
 proxy=proxy[:a]+''' ldy #1
 jsr PpNativeCall
'''+proxy[z:]
 proxy=clean(proxy,['SmcOffsets']);proxy=proxy.replace('.segment "PROXY"','.segment "PROXY"')
 battle=(O/'native-battle-v40.s').read_text();battle=clean(battle,['PpNativeSfx','PpNativeRawSfx'])
 public=(O/'public-private-v24.s').read_text();public=clean(public,[n for n in old if n.startswith('PpNative')])
 public=public.replace(' cmp #3\n beq PublicGraphics\n',''' cmp #3
 beq PublicGraphics
 cmp #15
 beq PublicContact
 cmp #33
 beq PublicContact
 cmp #18
 beq PublicStatus
 cmp #27
 beq PublicGraphics
 cmp #78
 beq PublicColors
''')
 public=public.replace('PublicGraphics:\n','''PublicContact:
 pla
 jmp PpNativeContact
PublicStatus:
 pla
 jmp PpNativeHealthStatus
PublicColors:
 pla
 jmp PpNativeColors
PublicGraphics:
''')
 # Original v37 jumps over the now-dead44B pointer body. Its exact41B tail
 # is source-funded again, without moving any renderer/world public address.
 renderlab=P.T.labels(O/'grid-render-labels-v37.lbl');contact_at=renderlab['PpPosePointer']+3;contact_limit=renderlab['PpReadProjection']
 policy='''.setcpu "6502"
.segment "CONTACT"
.export PpNativeContact,PpNativeHealthStatus,PpContactEnd
PpNativeContact:
 php
 pha
 txa
 pha
 tya
 pha
 lda $c6cf
 beq ContactDone
 ldy #0
 jsr PpOriginalDefenderContact
ContactDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
PpNativeHealthStatus:
 lda #1
 sec
 rts
PpContactEnd:
.segment "COLORS"
.export PpNativeColors,PpColorsEnd
PpNativeColors:
 php
 pha
 txa
 pha
 tya
 pha
 ldx VRAM_Buffer1_Offset
 cpx #$4e
 bcs ColorsDone
 ldy #0
ColorsCopy:
 lda ColorsPacket,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #6
 bne ColorsCopy
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
ColorsDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
ColorsPacket:.byte $3f,$11,3,$27,$16,$20
PpColorsEnd:
'''
 refs={**{n:old[n]for n in old if n.startswith('PpNative')},'PpNativeProxyIn':0x4400,'PpNativeProxyOut':0x44db,'PpNativeCall':0xdc27,'PpNativeContact':contact_at,'PpNativeHealthStatus':contact_at+32,'PpNativeColors':0xdf80,'PpOriginalDefenderContact':0x4020}
 native={'NativeDefeat':address(base,'ShellOrBlockDefeat'),'NativeDefeatBank':((location(base,'ShellOrBlockDefeat')-16)//8192)|128}
 images={};labels={};ends={};previous=None
 for iteration in range(6):
  refs.update({n:v for lab in labels.values()for n,v in lab.items()if n.startswith('PpNative')})
  if 'battle'in labels:refs['PpOriginalDefenderContact']=labels['battle']['PpBattle_4_ACEC']
  at=grid['PpGridEnd']
  for name,source,segment in [('services',services,'SERVICES'),('battle',battle,'BATTLE'),('proxy',proxy,'PROXY'),('public',public,'PUBLIC'),('policies',policy,'COLORS')]:
   local={}
   if name=='services':local={**native,**{n:refs[n]for n in ['PpNativeProxyIn','PpNativeProxyOut']}}
   elif name=='battle':local={'PpNativeSfx':refs['PpNativeQuietSfx'],'PpNativeRawSfx':refs['PpNativeQuietSfx']}
   elif name=='proxy':local={'PpNativeCall':refs['PpNativeCall']}
   elif name=='public':local={n:refs[n]for n in refs if n.startswith('PpNative')and n not in ['PpNativeFresh','PpNativeFreshEnd','PpNativeResetTail','PpNativeRoute','PpNativePublicEnd']}
   else:local={'PpOriginalDefenderContact':refs['PpOriginalDefenderContact'],**{n:address(base,n)for n in ['VRAM_Buffer1','VRAM_Buffer1_Offset']}}
   extra=''
   if name=='public':extra=f'F:start=$b3ef,size=$11,file="{(O/"native-fresh-v42.bin").as_posix()}";'
   if name=='policies':extra=f'C:start=${contact_at:04x},size=${contact_limit-contact_at:x},file="{(O/"native-contact-v42.bin").as_posix()}";'
   segments='FRESH_PREFIX:load=F,type=ro;'if name=='public'else'CONTACT:load=C,type=ro;'if name=='policies'else''
   images[name],labels[name]=A.assemble('native-'+name+'-v42',defs(local)+source,f'MEMORY{{M:start=${at:04x},size=$800,file=%O;{extra}}}SEGMENTS{{{segment}:load=M,type=ro;{segments}}}')
   ends[name]=[at,at+len(images[name])];at+=len(images[name])
  signature=json.dumps([ends,labels],sort_keys=True)
  if previous==signature:break
  previous=signature
 else:raise AssertionError('Private service references failed to converge')
 metadata=(O/'prince-pose-grid-v37.bin').read_bytes()+(O/'pose-grid-helper-v37.bin').read_bytes()+b''.join(images.values());assert len(metadata)==at-0xc800
 renderer=bytearray((O/'grid-render-v37.bin').read_bytes());contact=(O/'native-contact-v42.bin').read_bytes();pos=contact_at-0xbbc1;assert all(v==0xea for v in renderer[pos:pos+len(contact)]);renderer[pos:pos+len(contact)]=contact
 # Source palette1 selects native player slot0. Keep source hues27/16/20.
 needle=bytes([0xa9,1,0xae,0x15,0xc6,0xf0,2,0xa9,0x41]);sites=[i for i in range(len(renderer))if renderer[i:i+len(needle)]==needle];assert len(sites)==1
 pos=sites[0];renderer[pos+1]=0;renderer[pos+8]=0x40
 runtime=bytearray((O/'public-runtime-v24.bin').read_bytes());runtime[0xbbc1-0xa000:0xbbc1-0xa000+len(renderer)]=renderer;runtime[0xb3ef-0xa000:0xb3ef-0xa000+(O/'native-fresh-v42.bin').stat().st_size]=(O/'native-fresh-v42.bin').read_bytes()
 assert runtime[-3]==0x4c and int.from_bytes(runtime[-2:],'little')==old['PpNativeInit'];runtime[-2:]=labels['services']['PpNativeInit'].to_bytes(2,'little')
 # Only source-declared environment calls are relocated to the new services.
 recovery=json.loads((O/'contact-recovery.json').read_text());core=P.T.labels(O/'contact-core.lbl');old_targets={old[n]:labels['services'][n]for n in ['PpNativeQuietSfx','PpNativeQuietMusic','PpNativeUnpublishedMaterial']}
 fix=[]
 for tag,ins in recovery['instructions'].items():
  if ins['mn']not in ['JSR','JMP']:continue
  bank,pc=tag.split(':');cpu=core[f'PpN_{bank}_{pc}'];off=cpu-0xa000;target=int.from_bytes(runtime[off+1:off+3],'little')
  if target in old_targets:runtime[off+1:off+3]=old_targets[target].to_bytes(2,'little');fix.append([cpu,target,old_targets[target]])
 for name,delta in [('PpN_7_F044',2),('PpN_7_F08D',3)]:
  off=core[name]-0xa000+delta;assert runtime[off]==0x4c;runtime[off+1:off+3]=labels['battle']['PpCombatControls'].to_bytes(2,'little')
 all_labels={n:v for lab in labels.values()for n,v in lab.items()if n.startswith('Pp')};all_labels.update({n:renderlab[n]for n in renderlab if n.startswith('Pp')});all_labels.update(grid)
 (O/'native-runtime-v42.bin').write_bytes(runtime);(O/'native-metadata-v42.bin').write_bytes(metadata);(O/'native-labels-v42.json').write_text(json.dumps(all_labels,indent=2)+'\n')
 q=dict(measured=True,qualified=False,ROM_written=False,base_SHA256=M.A.PIN,component_half_open=ends,metadata_bytes=len(metadata),metadata_end=at,RAM2_capacity_before_clock=0xdfd0-0xc800,remaining_before_shared_clock=0xdfd0-at,renderer_pointer_tail_reclaimed=[contact_at,contact_at+len(contact)],renderer_tail_original_bytes=contact_limit-contact_at,exact_original_environment_operand_relocations=fix,source_combat_control_edges_retargeted=2,common_native_service_gateway=True,constructor_floor_reference='Before sourceReady, nativeInit initializes existing WorldSurface16 from genuine computedWorldFoot16. First controls cannot align to zero before first phase3; this reference preserves current physical anchor, and actual terrain queries replace it.',implemented_public_rows=[0,1,2,5,6,9,11,15,19,26,36],unimplemented_policies='Native full collision box/profile/head/side/pickup/bounce/death-loop policies remain explicit fallback; not a playable/native-ready image.',new_execution_scope_required=[grid['PpGridLookup'],at],bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-runtime-v42.bin',O/'native-metadata-v42.bin',O/'native-labels-v42.json',O/'native-contact-v42.bin',O/'native-proxy-CPU-v41.json',M.A.BASE]})
 (O/'native-link-measurement-v42.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','exact_original_environment_operand_relocations']}))


if __name__=='__main__':main()
