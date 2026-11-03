"""Measure same-Main deferred death on the existing actual row34 host seam."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import measure_prince_native_lifecycle_1102_v70 as V
import measure_prince_collision_services_1102_v49 as A
O=A.O


def transform(services,public,audio,native,base):
 services,public,audio=V.transform(services,public,audio,native,base)
 native['GameEngineSubroutine']=A.address(base,'GameEngineSubroutine')
 assert services.count(' lda PpDead\n bne DeathDone')==1
 services=services.replace(' lda PpDead\n bne DeathDone','')
 old='Kill:\n lda #1\n sta PpDead\n ldx #0\n ldy #0\n jmp PpNativeCall'
 assert old in services
 services=services.replace(old,'Kill:\n lda #2\n sta PpDead\n sec\n rts')
 services=services.replace(' .byte $ea,$ea\nPpNativeServicesEnd:', 'NativeBank:.byte Bank_KillPlayer,NativeDefeatBank,NativeDefaultBank,NativeDeathBank\n.export NativeBank\nPpNativeServicesEnd:')
 public=public.replace(' bcs Scalar\n clc\n adc #<NativeVector',' bcs Scalar\n adc #<NativeVector')
 public=public.replace(' cmp #78\n beq Colors',' cmp #78\n beq Colors\n cmp #102\n beq Late')
 public=public.replace('Yes:pla','Late:pla\n jmp PpNativeDeferredKill\nYes:pla')
 public=public.replace(' ldx #0\nFreshLastPage:', ' ldx #$65\nFreshLastPage:').replace(' inx\n bpl FreshLastPage',' dex\n bpl FreshLastPage')
 audio=audio.replace('.export NativeLo,NativeHi,NativeBank,PpNativeDeathUpdate','.export NativeLo,NativeHi,PpNativeDeathUpdate,PpNativeDeferredKill')
 audio=audio.replace(' sta $c780,y\n cmp $c780,y',' sta $c766,y\n cmp $c766,y').replace(' iny\n bpl ColdCopy',' iny\n cpy #154\n bne ColdCopy')
 deferred='''PpNativeDeferredKill:
 lda $c0ac
 cmp #2
 bne DeferredDone
 dec $c0ac
 lda GameEngineSubroutine
 cmp #8
 bne DeferredDone
 ldx #0
 ldy #0
 jmp PpNativeCall
DeferredDone:sec
 rts
'''
 audio=audio.replace('; Native X=0',deferred+'; Native X=0')
 line='NativeBank:.byte Bank_KillPlayer,NativeDefeatBank,NativeDefaultBank,NativeDeathBank\n'
 assert audio.count(line)==1;audio=audio.replace(line,'')
 return services,public,audio


def main():
 source=Path(A.__file__);text=source.read_text();marker=" battle=clean((O/'native-battle-v42.s')"
 text=text.replace(marker," services,public,audio=transform(services,public,audio,native,base)\n"+marker)
 text=text.replace("'PpNativePickup':0xc7b5,", "'PpNativePickup':0xc7b5,'PpNativeDeathUpdate':0xc7ef,'PpNativeDeferredKill':0xc781,")
 text=text.replace("'PpNativeVerticalExport','NativeLo','NativeHi','NativeBank'", "'PpNativeVerticalExport','NativeLo','NativeHi'")
 text=text.replace("local={**native,'PpColdContinue'", "local={**native,'PpNativeCall':refs['PpNativeCall'],'PpColdContinue'")
 # NativeBank now resides in the measured private service tail, freeing
 # four audio bytes. Every target is an exact native symbol/bank pair.
 text=text.replace("['PpNativeProxyIn','PpNativeProxyOut','NativeDefeat','NativeDefeatBank']", "['PpNativeProxyIn','PpNativeProxyOut','NativeDefeat','NativeDefeatBank']")
 text=text.replace("start=0xc780 if name=='audio'", "start=0xc766 if name=='audio'")
 text=text.replace("if name=='services':local=", "if name=='services':local=")
 # All native table values were already exact-bound in the original recipe.
 text=text.replace("elif name=='battle':local=", "if name=='services':local.update({n:native[n]for n in ['NativeDefeatBank','NativeDefaultBank','NativeDeathBank']})\n   elif name=='battle':local=")
 text=text.replace("elif name=='audio':local={**native,", "elif name=='audio':local={**native,")
 text=text.replace('len(images[\'audio\'])<=128','len(images[\'audio\'])<=154').replace('bytes(128-len(images[\'audio\']))','bytes(154-len(images[\'audio\']))')
 old="off=life['ColdLastPage']-0xa000;assert runtime[off:off+6]==bytes.fromhex('9900c7c8d0fa');runtime[off+4]=0x10"
 new="off=life['ColdLastPage']-0xa000;assert runtime[off:off+6]==bytes.fromhex('9900c7c8d0fa');runtime[off:off+9]=bytes([0x4c])+labels['public']['PpNativeResetTail'].to_bytes(2,'little')+bytes([0xea])*6"
 assert old in text;text=text.replace(old,new).replace('v49','v75')
 env=dict(__file__=str(Path(__file__)),__name__='prince_deferred_measure_v75',transform=transform);exec(compile(text,str(source),'exec'),env);env['main']()
 q=json.loads((O/'collision-services-measurement-v75.json').read_text());lab=json.loads((O/'native-labels-v75.json').read_text())
 assert q['metadata_end']==0xdfcf and q['audio_code_bytes']==151 and q['state_stream_bytes']==1529
 q.update(qualified=False,private_proposal=True,requested_new_audio_half_open=[0xc766,0xc780],packet_scratch_half_open=[0xc200,0xc20d],audio_backing_bytes=154,source_request_dead_value=2,delivered_dead_value=1,native_route=lab['PpNativeRoute'],old_native_route=0xdf26,scope='Original source request is queued at its genuine source death epoch. Actual Main row34 after GameRoutines fully returns services it before enemies/draw. Native pit may already have delivered genuine death; deferred leaf consumes pending state but does not invoke Kill again unless native engine is still8. Original native Kill/UnionDeathStart/MegaManDeathUpdate remain intact. Extended source-dead C766..C780, packet scratch and shared two route operands require reviewed amendment; no cold/auth/native qualification or ROM mutation.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(V.__file__),O/'native-stack-negative-v72.json',O/'death-ack-stack-negative-v74.json']})
 (O/'deferred-death-measurement-v75.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
