"""Exact post-owner-return native death hook and transport-operand proposal."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import measure_prince_deferred_death_1102_v75 as V
O=V.O


def transform(services,public,audio,native,base):
 services,public,audio=V.transform(services,public,audio,native,base)
 old='''PpNativeDeferredKill:
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
 rts'''
 new='''PpNativeDeferredKill:
 lda $c0ac
 cmp #2
 bne DeferredNo
 dec $c0ac
 lda GameEngineSubroutine
 cmp #8
 bne DeferredNo
 sec
 rts
DeferredNo:clc
 rts'''
 assert old in audio;audio=audio.replace(old,new)
 assert public.count('PpServiceTag=$c09e')==1
 public=public.replace('PpServiceTag=$c09e ; Source world SavedY; overwritten before its only read.','PpServiceTag=$0179 ; Saved transport result-A operand, consumed before nested native calls.')
 return services,public,audio


def main():
 source=Path(V.__file__);text=source.read_text().replace('v75','v78').replace("q['audio_code_bytes']==151","q['audio_code_bytes']==146")
 env=dict(__file__=str(Path(__file__)),__name__='prince_postreturn_measure_v78');exec(compile(text,str(source),'exec'),env);env['transform']=transform;env['main']()
 hook='''.setcpu "6502"
.segment "FIRST"
.export PrPostWeapon,PrPostWeaponEnd,PrPostClassify,PrPostClassifyEnd
PrPostWeapon:
 sta $016a
 .byte $90,<(Done-(*+1)) ; BCC to the linked second fragment, same bank.
 php
 lda $6002
 cmp #38
 jmp PrPostClassify
PrPostWeaponEnd:
.segment "SECOND"
PrPostClassify:
 beq Own
 lda $016a
 plp
Done:rts
Own:plp
 jmp $97d6
PrPostClassifyEnd:
'''
 cfg=f'MEMORY{{F:start=$a760,size=$f,file=%O;S:start=$a795,size=$f,file="{(O/"post-return-second-v78.bin").as_posix()}";}}SEGMENTS{{FIRST:load=F,type=ro;SECOND:load=S,type=ro;}}'
 blob,lab=V.A.A.assemble('post-return-v78',hook,cfg);second=(O/'post-return-second-v78.bin').read_bytes();assert len(blob)==14 and len(second)==11
 q=dict(measured=True,qualified=False,ROM_written=False,shared_grant=False,first=[0xa760,0xa76e],second=[0xa795,0xa7a0],used_bytes=25,source_padding_bytes=30,entry_patch=[0xad75,'8d6a01','2060a7'],native_fixed_KillPlayer=0x97d6,transport_tag_operand=0x0179,selector_growth=0,source_request='Original fatal/pit epoch sets pending2. Actual public row34 consumes2→1 and returnsC1 only for queued native-engine8 death. The new hook runs after that complete resident callback returns, restoring foreign A/P before tail return; exact owned queued C1 tail-jumps genuine KillPlayer at native caller depth.',required='Root review of exact current preimages/source-declared padding/direct/indirect closure; actual fullGameCore and deepest IRQ; allforeign AXYP/SP and full cold/retire/tag-operand lifetime proof.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,O/'deferred-death-measurement-v78.json',O/'post-return-v78.s',O/'post-return-v78.bin',O/'post-return-second-v78.bin']})
 (O/'post-return-measurement-v78.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
