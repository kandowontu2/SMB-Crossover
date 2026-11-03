"""Measure a private source-owned stack/lifecycle successor; no ROM writes.

The saved native-call ABI bytes occupy the already disposable draw packet only
during synchronous foreground native calls. This lifetime amendment is a
proposal until its finite consumer and interrupt checks have been reviewed.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import measure_prince_collision_services_1102_v49 as A
O=A.O


def transform(services,public,audio,native,base):
 old=' jsr PpNativePitDeath\n sec\n rts'
 assert services.count(old)==1
 services=services.replace(old,' jmp PpNativePitDeath')
 assert services.count('DeathDone:\n clc\n rts')==1
 services=services.replace('DeathDone:\n clc\n rts','DeathDone:\n sec\n rts')
 old=''' ldx #0
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
 bne SaveSmc'''
 new=''' ldx #7
SaveZp:
 lda R0,x
 sta $c200,x
 dex
 bpl SaveZp
 ldx #4
SaveSmc:
 ldy SmcOffsets,x
 lda $0100,y
 sta $c208,x
 dex
 bpl SaveSmc'''
 assert old in services;services=services.replace(old,new)
 services=services.replace('RestoreSmc:\n pla','RestoreSmc:\n lda $c208,x').replace('RestoreZp:\n pla','RestoreZp:\n lda $c200,x')
 old=''' lda $c615
 beq FaceLeft
 lda #1
 bne FaceReady
FaceLeft:
 lda #2
FaceReady:
 sta PlayerFacingDir'''
 assert old in services
 services=services.replace(old,' lda #1\n cmp $c615\n adc #0\n sta PlayerFacingDir')
 # Keep the original public entry and all shared operands at DF26. Two bytes
 # are explicit owned padding, rather than shifting resident caller targets.
 services=services.replace('PpNativeServicesEnd:', ' .byte $ea,$ea\nPpNativeServicesEnd:')
 public=public.replace(' sbc #30',' sbc #24').replace(' cmp #21',' cmp #27')
 assert public.count(' cmp #27\n beq Yes')==1
 public=public.replace(' cmp #27\n beq Yes','')
 public=public.replace('NativeVector:\n','NativeVector:\n jmp PpNativeDeathUpdate\n sec\n rts\n nop\n')
 public=public.replace('(NativeVector+20)','(NativeVector+26)').replace('Native seven-row','Native nine-row')
 audio=audio.replace('.export NativeLo,NativeHi,NativeBank','.export NativeLo,NativeHi,NativeBank,PpNativeDeathUpdate')
 assert audio.count(' sta BoundingBox_UL_XPos\n clc')==1
 audio=audio.replace(' sta BoundingBox_UL_XPos\n clc',' sta BoundingBox_UL_XPos')
 assert audio.count(' lda #91\n ldy #0\n jsr PpSetAction')==1
 audio=audio.replace(' lda #91\n ldy #0\n jsr PpSetAction',' lda #91\n jsr PpSetAction')
 audio=audio.replace('NativePickup:\n ldy #2\n jmp PpNativeCall','PpNativeDeathUpdate:\n ldy #3\n bne NativeGo\nNativePickup:\n ldy #2\nNativeGo:\n jmp PpNativeCall')
 audio=audio.replace('<NativeDefaultPickup\n','<NativeDefaultPickup,<NativeDeathUpdate\n').replace('>NativeDefaultPickup\n','>NativeDefaultPickup,>NativeDeathUpdate\n').replace('NativeDefeatBank,NativeDefaultBank\n','NativeDefeatBank,NativeDefaultBank,NativeDeathBank\n')
 native['NativeDeathUpdate']=A.address(base,'MegaManDeathUpdate')
 native['NativeDeathBank']=((A.location(base,'MegaManDeathUpdate')-16)//8192)|128
 assert native['NativeDeathUpdate']==0xaf3a and native['NativeDeathBank']==0x88
 return services,public,audio


def main():
 source=Path(A.__file__);text=source.read_text()
 marker=" battle=clean((O/'native-battle-v42.s')"
 assert text.count(marker)==1
 text=text.replace(marker," services,public,audio=transform(services,public,audio,native,base)\n"+marker)
 text=text.replace("'PpNativePickup':0xc7b5,", "'PpNativePickup':0xc7b5,'PpNativeDeathUpdate':0xc7ef,")
 text=text.replace('v49','v70')
 env=dict(__file__=str(Path(__file__)),__name__='prince_lifecycle_measure_v70',transform=transform)
 exec(compile(text,str(source),'exec'),env);env['main']()
 q=json.loads((O/'collision-services-measurement-v70.json').read_text())
 lab=json.loads((O/'native-labels-v70.json').read_text());old=json.loads((O/'native-labels-v49.json').read_text())
 assert q['audio_code_bytes']==128 and q['metadata_end']==0xdfd0
 assert lab['PpNativeRoute']==old['PpNativeRoute']==0xdf26
 assert lab['PpNativeRetire']==old['PpNativeRetire']==0xd98f
 q.update(qualified=False,private_source_proposal=True,packet_scratch_half_open=[0xc200,0xc20d],packet_scratch_lifetime='Synchronous PpNativeCall only, outside original source update and draw. No authorization to consume until exact reader/reentry/IRQ closure is reviewed.',row8='Real bank88 MegaManDeathUpdate, no timer/engine outcome writes',metadata_clock_boundary=0xdfd0,shared_route_operands_unchanged=True,required='Actual GameRoutines death/life/respawn, every native-call stack/SMC/IRQ path, full cold/warm current-owner regression, and packet scratch lifetime approval before composition.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [source,Path(__file__),O/'native-lifecycle-negative-v69.json']})
 (O/'native-lifecycle-measurement-v70.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
