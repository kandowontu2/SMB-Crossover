"""Source-derived native contact/query/pickup successor, measured private only."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import prepare_prince_successor_manifest_1102_v26 as M
from check_tmnt_render_oa import address,location
P,O=A.L.P,A.O


def clean(text,names):return '\n'.join(line for line in text.splitlines()if not any(re.match(re.escape(n)+r'=\$',line)for n in names))+'\n'
def defs(values):return ''.join(f'{n}=${v:04x}\n'for n,v in values.items())


def main():
 base,_,_,_=M.bundle();lab=json.loads((O/'native-labels-v42.json').read_text());life=P.T.labels(O/'host-life-v12.lbl')
 native={n:address(base,n)for n in ['Player_Rel_XPos','Player_Rel_YPos','BoundingBox_UL_XPos','BoundingBox_UL_YPos','BoundingBox_LR_Corner','PowerUpType','Enemy_State','EraseEnemyObject','SetupFloateyNumber','BlockBufferColli_Head','BlockBufferColli_Side','Player_Y_Speed']}
 native['NativeDefaultPickup']=address(base,'MarioSourcePowerupCollision');native['NativeDefaultBank']=((location(base,'MarioSourcePowerupCollision')-16)//8192)|128
 native.update(NativeDefeat=address(base,'ShellOrBlockDefeat'),NativeDefeatBank=((location(base,'ShellOrBlockDefeat')-16)//8192)|128,KillPlayer=address(base,'KillPlayer'),Bank_KillPlayer=((location(base,'KillPlayer')-16)//8192)|128)
 core=P.T.labels(O/'contact-core.lbl');services=(O/'native-services-v42.s').read_text();services=clean(services,['PpNativeProxyIn','PpNativeProxyOut','NativeDefeat','NativeDefeatBank'])
 for name in ['NativeLo','NativeHi','NativeBank']:
  services=re.sub(r'(?m)^'+name+r':\.byte[^\n]+\n','',services)
 assert services.count(' sta PlayerFacingDir\n rts')==1;services=services.replace(' sta PlayerFacingDir\n rts',' sta PlayerFacingDir\n sec\n jmp PpNativeVerticalExport')
 services+='\n.export PpPendingSoundOpcode,PpPendingSoundID,PpPendingMusic\nPpPendingSoundOpcode=$c0ad\nPpPendingSoundID=$c0ae\nPpPendingMusic=$c0af\n'
 # Source state bank2 code image is still identical except native cold finalizer
 # and existing original-state last-page zero boundaries are rebound below.
 public=(O/'native-public-v42.s').read_text();prefix=public[:public.index('PpNativeRoute:')];prefix=clean(prefix,[n for n in lab if n.startswith('PpNative')and n not in ['PpNativeFresh','PpNativeResetTail','PpNativeRoute','PpNativePublicEnd','PpNativeFreshEnd']]);assert ' inx\n bne FreshLastPage' in prefix;prefix=prefix.replace(' inx\n bne FreshLastPage',' inx\n bpl FreshLastPage')
 public=prefix+'''
PpNativeRoute:
 pha
 lda PpServiceTag
 sec
 sbc #30
 bcc Scalar
 cmp #21
 bcs Scalar
 clc
 adc #<NativeVector
 sta VectorJump+1
 pla
VectorJump:jmp NativeVector
Scalar:
 lda PpServiceTag
 beq Tick
 cmp #6
 beq Draw
 cmp #108
 beq Fresh
 cmp #3
 beq Yes
 cmp #27
 beq Yes
 cmp #69
 beq Yes
 cmp #15
 beq Contact
 cmp #18
 beq Status
 cmp #72
 beq Pickup
 cmp #78
 beq Colors
 pla
 clc
 rts
Tick:pla
 jmp PpNativeTick
Draw:pla
 jmp PpHostDraw
Fresh:pla
 jmp PpNativeFresh
Contact:pla
 jmp PpNativeContact
Status:pla
 jmp PpNativeHealthStatus
Pickup:pla
 jmp PpNativePickup
Colors:pla
 jmp PpNativeColors
Yes:pla
 sec
 rts
NativeVector:
 jmp BlockBufferColli_Head
 jmp PpNativeContact
 jmp PpNativeAdder
 ldy #0
 rts
 jmp BlockBufferColli_Side
 jmp PpNativeFresh
 jmp PpNativeFullBox
.assert >NativeVector=>(NativeVector+20),error,"Native seven-row vector crosses page"
PpNativePublicEnd:
'''
 # Small direct resident leaves and native vertical sign transport occupy
 # exactly the last13B of the original dead pointer body. Current services
 # SEC before the tailcall; LDA/SBC transport changes no source physics.
 extra='''.setcpu "6502"
.segment "SMALL"
.export PpNativeAdder,PpNativeVerticalExport,PpSmallEnd
PpNativeAdder:
 ldy #6
 sec
 rts
PpNativeVerticalExport:
 lda $c084
 sbc $c086
 sta Player_Y_Speed
 rts
PpSmallEnd:
'''
 # The25B first leaf is position-independent while running from stagedC65F:
 # all internal branches are relative and its only JMP is resident RAM3.
 audio='''.setcpu "6502"
.segment "AUDIO"
.export PpNativeColdPrefix,PpNativeFullBox,PpNativePickup,PpAudioEnd
.export NativeLo,NativeHi,NativeBank
PpNativeColdPrefix:
 ldy #0
ColdCopy:
 lda $c65f,y
 sta $c780,y
 cmp $c780,y
 bne ColdFailed
 iny
 bpl ColdCopy
 ldy #0
 ldx #5
 jmp PpColdContinue
ColdFailed:clc
 rts
; Native X=0 is an actual sole-caller contract at PlayerSubs. Source center
; X=nativeX+8, explicit world-body probes span16px, foot=nativeY+32.
PpNativeFullBox:
 lda Player_Rel_XPos
 sta BoundingBox_UL_XPos
 clc
 adc #16
 sta BoundingBox_LR_Corner
 lda Player_Rel_YPos
 sta BoundingBox_UL_YPos
 clc
 adc #32
 sta BoundingBox_LR_Corner+1
 ldy #0
 sec
 rts
; Native collision has admitted the actual item overlap. Immature regular
; items remain in their block. Mushroom maps to the original small-heal
; effect bounded by the genuine initial5HP; flower maps to original sword
; effect6EE1/action91. Star/1up use the genuine native collector unchanged.
PpNativePickup:
 lda $c6cf
 beq PickupDone
 lda PowerUpType,x
 cmp #2
 bcs NativePickup
 lda Enemy_State,x
 bpl PickupDone
 lda PowerUpType,x
 bne Sword
 lda $c6cf
 cmp #5
 bcs Consume
 inc $c6cf
 bne Consume
Sword:
 txa
 pha
 lda #1
 sta $c6ee
 lda #91
 ldy #0
 jsr PpSetAction
 pla
 tax
Consume:
 jsr EraseEnemyObject
 lda #6
 jsr SetupFloateyNumber
PickupDone:sec
 rts
NativePickup:
 ldy #2
 jmp PpNativeCall
NativeLo:.byte <KillPlayer,<NativeDefeat,<NativeDefaultPickup
NativeHi:.byte >KillPlayer,>NativeDefeat,>NativeDefaultPickup
NativeBank:.byte Bank_KillPlayer,NativeDefeatBank,NativeDefaultBank
PpAudioEnd:
'''
 battle=clean((O/'native-battle-v42.s').read_text(),['PpNativeSfx','PpNativeRawSfx']);proxy=clean((O/'native-proxy-v42.s').read_text(),['PpNativeCall']);policies=clean((O/'native-policies-v42.s').read_text(),['PpOriginalDefenderContact'])
 refs={**lab,'PpOriginalDefenderContact':lab['PpBattle_4_ACEC'],'PpNativeAdder':0xbd3e,'PpNativeVerticalExport':0xbd42,'PpNativeFullBox':0xc799,'PpNativePickup':0xc7b5,'NativeLo':0xc7f7,'NativeHi':0xc7fa,'NativeBank':0xc7fd};images={};labels={};ends={};previous=None
 for iteration in range(8):
  refs.update({k:v for values in labels.values()for k,v in values.items()if k.startswith('Pp')or k in ['NativeLo','NativeHi','NativeBank']})
  if 'battle'in labels:refs['PpOriginalDefenderContact']=labels['battle']['PpBattle_4_ACEC']
  at=lab['PpGridEnd']
  for name,text,segment in [('services',services,'SERVICES'),('battle',battle,'BATTLE'),('proxy',proxy,'PROXY'),('public',public,'PUBLIC'),('policies',policies,'COLORS'),('audio',audio,'AUDIO'),('small',extra,'SMALL')]:
   local={};supplement='';segments=''
   if name=='services':local={n:refs[n]for n in ['PpNativeProxyIn','PpNativeProxyOut','PpNativeVerticalExport','NativeLo','NativeHi','NativeBank']}
   elif name=='battle':local={'PpNativeSfx':refs['PpNativeQuietSfx'],'PpNativeRawSfx':refs['PpNativeQuietSfx']}
   elif name=='proxy':local={'PpNativeCall':refs['PpNativeCall']}
   elif name=='public':
    defined=['PpNativeFresh','PpNativeFreshEnd','PpNativeResetTail','PpNativeRoute','PpNativePublicEnd'];local={n:v for n,v in refs.items()if n.startswith('PpNative')and n not in defined};local.update({n:native[n]for n in ['BlockBufferColli_Head','BlockBufferColli_Side']});supplement=f'F:start=$b3ef,size=$11,file="{(O/"native-fresh-v49.bin").as_posix()}";';segments='FRESH_PREFIX:load=F,type=ro;'
   elif name=='policies':local={'PpOriginalDefenderContact':refs['PpOriginalDefenderContact']};supplement=f'C:start=$bd22,size=$1c,file="{(O/"native-contact-v49.bin").as_posix()}";';segments='CONTACT:load=C,type=ro;'
   elif name=='audio':local={**native,'PpColdContinue':life['PpHostColdFinalize']+4,'PpSetAction':core['PpN_7_D6D8'],'PpNativeCall':refs['PpNativeCall']}
   else:local={'Player_Y_Speed':native['Player_Y_Speed']}
   start=0xc780 if name=='audio'else 0xbd3e if name=='small'else at
   images[name],labels[name]=A.assemble('native-'+name+'-v49',defs(local)+text,f'MEMORY{{M:start=${start:04x},size=$800,file=%O;{supplement}}}SEGMENTS{{{segment}:load=M,type=ro;{segments}}}')
   ends[name]=[start,start+len(images[name])]
   if name not in ['audio','small']:at+=len(images[name])
  signature=json.dumps(labels,sort_keys=True)
  if signature==previous:break
  previous=signature
 else:raise AssertionError('Native policy/source references failed to converge')
 meta=(O/'prince-pose-grid-v37.bin').read_bytes()+(O/'pose-grid-helper-v37.bin').read_bytes()+b''.join(images[k]for k in ['services','battle','proxy','public','policies']);assert len(meta)==at-0xc800
 runtime=bytearray((O/'native-runtime-v42.bin').read_bytes());oldlabels=json.loads((O/'native-labels-v42.json').read_text());oldservice=P.T.labels(O/'native-services-v42.lbl');newservice=labels['services'];fix=[]
 for tag,ins in json.loads((O/'contact-recovery.json').read_text())['instructions'].items():
  if ins['mn']not in ['JSR','JMP']:continue
  bank,pc=tag.split(':');off=core[f'PpN_{bank}_{pc}']-0xa000;target=int.from_bytes(runtime[off+1:off+3],'little');mapping={oldservice[n]:newservice[n]for n in ['PpNativeQuietSfx','PpNativeQuietMusic','PpNativeUnpublishedMaterial']}
  if target in mapping:runtime[off+1:off+3]=mapping[target].to_bytes(2,'little');fix.append([off+0xa000,target,mapping[target]])
 for name,delta in [('PpN_7_F044',2),('PpN_7_F08D',3)]:off=core[name]-0xa000+delta;runtime[off+1:off+3]=labels['battle']['PpCombatControls'].to_bytes(2,'little')
 runtime[-2:]=newservice['PpNativeInit'].to_bytes(2,'little')
 runtime[0xb3ef-0xa000:0xb3fc-0xa000]=(O/'native-fresh-v49.bin').read_bytes();runtime[0xbd22-0xa000:0xbd3e-0xa000]=(O/'native-contact-v49.bin').read_bytes();runtime[0xbd3e-0xa000:0xbd4b-0xa000]=images['small']
 # Preserve the cold finalizer's exact original remaining55B/address. Its
 # staged first audio leaf runs before code/source zeroing and returns to+4.
 off=life['PpHostColdFinalize']-0xa000;assert runtime[off:off+4]==bytes.fromhex('a000a205');runtime[off:off+4]=bytes.fromhex('4c5fc6ea')
 off=life['ColdLastPage']-0xa000;assert runtime[off:off+6]==bytes.fromhex('9900c7c8d0fa');runtime[off+4]=0x10
 assert len(images['audio'])<=128 and len(images['small'])==13 and at<=0xdfd0
 state=(O/'native-state_code-v18.bin').read_bytes()+images['audio']+bytes(128-len(images['audio']));alllabels={**oldlabels,**{n:v for values in labels.values()for n,v in values.items()if n.startswith('Pp')or n in ['NativeLo','NativeHi','NativeBank']}}
 (O/'native-runtime-v49.bin').write_bytes(runtime);(O/'native-metadata-v49.bin').write_bytes(meta);(O/'native-state-v49.bin').write_bytes(state);(O/'native-labels-v49.json').write_text(json.dumps(alllabels,indent=2)+'\n')
 q=dict(measured=True,qualified=False,ROM_written=False,base_SHA256=M.A.PIN,component_half_open=ends,metadata_bytes=len(meta),metadata_end=at,remaining_before_clock=0xdfd0-at,audio_code_bytes=len(images['audio']),audio_remaining=0xc800-ends['audio'][1],small_code_bytes=len(images['small']),small_remaining=0xbd4b-ends['small'][1],state_stream_bytes=len(state),state_staged_output_end=0xc100+len(state),source_dead_audio_execution_granted=False,box_contract='Native source-world adapter explicitly defines centerX=nativeX+8,16px query width, physicalfoot=nativeY+32. Native player/entity/item rectangle0..16×0..32 follows these anchors. This is the authored host rectangle derived from world query geometry, not an assertion the original sword-distance engine contains an SMB bbox.',head_side_contract='Typed direct forwards use genuine PRG126 BlockBufferColli_Head/Side and existing32px standing probe group6. Native Y-speed is current source physicalfoot minus previous sourcephysicsfoot; only native collision sign transport changes, authentic source movement remains original.',pickup_contract='Actual native overlap+maturestatebit7 gates regular items. Mushroom invokes original small-heal effect HP+1 bounded by genuine initial5HP. Flower invokes original6EE1/action91 effect through translated original SetAction. Native star/1up forward to genuine MarioSourcePowerupCollision via existing synchronous gateway. The item-kind mapping is the explicit host adaptation; original NES had potions/sword, not mushrooms/flowers.',cold_contract='New final state stream appends audio-code backing atC65F. First25B execute position-independently from C65F, copying/readback128B toC780 before source zeroing. Cold/fresh C700 zero loops stop atC780, preserving only source-dead audio-code. No code or outcome placed in native ROM.',implemented_rows=[0,1,2,5,6,9,10,11,12,13,14,15,16,19,23,24,26,36],required='Actual code/backing size fit, CPU source-item effects/native ingresses/bbox/queries/ISR/cold/fresh/foreign/auth closure; source-dead audio execution/stagedPC and exact shared rebind grant before root native queue.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'quiet-audio-code-proposal-v48.json',O/'native-runtime-v49.bin',O/'native-metadata-v49.bin',O/'native-state-v49.bin',O/'native-labels-v49.json',O/'native-link-measurement-v42.json',R/'docs/qa/allocations/prince-battle-lifetime-1102-v46.json']})
 (O/'collision-services-measurement-v49.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
