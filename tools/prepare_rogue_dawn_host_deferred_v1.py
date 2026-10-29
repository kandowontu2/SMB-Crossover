"""Separate private deferred-world-effect successor; immutable v3 retained."""
from pathlib import Path
import hashlib,json,runpy,sys
R=Path(__file__).resolve().parents[1];O=R/'build/rogue-dawn-host-deferred-v1'
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 old=R/'build/rogue-dawn-host-transactions-v3';h=json.loads((old/'handoff.json').read_text())
 assert hashlib.sha256((old/'handoff.json').read_bytes()).hexdigest()=='2b599acf5fdecec07b91c9e1eaef5a89767d9dd2591908e3a669972fe9c76fd5'
 for row in h['bindings']:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
 text=(old/'frozen-rogue_dawn_host_transactions.s').read_text()
 text=once(text,'.export RdTxStart,RdTxEnd','.export RdTxStart,RdTxEnd,RdTxMovementBegin\nRdHeadCell=$5c0b ; unconsumed original player offscreen projection; approved transient\nRdHeadPage=$5c3b ; bomb phase is dead until the later weapon update')
 # All original source state/register/blocked-pixel semantics survive. Native
 # block effects execute once at the shallow after-Main call, never in bridge.
 text=once(text,' RdHsSave\n RdTxSaveNative\n lda Player_Y_HighPos',' RdHsSave\n lda Player_Y_HighPos')
 text=once(text,' jsr RdTxNativeCell\n jsr PlayerHeadCollision\nDone:\n RdTxRestoreNative\n sec\n jmp RdHsRestoreC', ''' ; At most one BLOCKED up callback in the sole Physics invocation per
 ; admitted source ControlStep. That structural obligation is source-tested.
 lda Rh4
 lsr
 lsr
 lsr
 lsr
 sta Rh7
 lda Rh3
 and #$f0
 sec
 sbc #32
 ora Rh7
 sta RdHeadCell
 lda Rh2
 sta RdHeadPage
Done:
 sec
 jmp RdHsRestoreC''')
 marker='; Call ONCE after real ControlStep+Export, before native scrolling/enemies.'
 begin='''; Clear only at an exact-owner movement boundary. Preserve incoming AXYP.
.proc RdTxMovementBegin
 php
 pha
 jsr RdHostEnabled
 bcc Done
 lda #$ff
 sta RdHeadCell
 lda #0
 sta RdHeadPage
Done:pla
 plp
 rts
.endproc

'''
 text=once(text,marker,begin+marker)
 text=once(text,' lda #0\n sta Rh6\nCoinLoop:', ''' ; Flush before any actor/weapon update. Restore source-published Y speed
 ; after the genuine BumpBlock writes its native0, as the original immediate
 ; callback was followed by the exact same source ExportPosition publication.
 lda RdHeadCell
 cmp #$ff
 beq NoHead
 and #$f0
 clc
 adc #32
 sta Rh3
 lda RdHeadCell
 asl
 asl
 asl
 asl
 sta Rh4
 lda RdHeadPage
 sta Rh2
 lda #$ff
 sta RdHeadCell
 lda #0
 sta RdHeadPage
 jsr RdTxNativeCell
 jsr PlayerHeadCollision
 lda RdVY
 sta Player_Y_Speed
NoHead:
 lda #0
 sta Rh6
CoinLoop:''')
 text=once(text,'Done:RdTxRestoreNative\n sec', 'Done:lda #$ff\n sta RdHeadCell\n lda #0\n sta RdHeadPage\n RdTxRestoreNative\n sec')
 text=text.replace('Private successor to frozen services9dc533.', 'Private DEFERRED successor to unsafe transaction25f5 and frozen services9dc533.')
 path=R/'src/rogue_dawn_host_deferred.s'
 if path.exists():assert path.read_text()==text
 else:path.write_text(text,newline='\n')
 # Consume the preserved real assembler recipe, using a new component source
 # and output. All generated DBG/LBL and preimage checks remain genuine.
 builder=(old/'frozen-prepare_rogue_dawn_host_transactions_v1.py').read_text()
 builder=once(builder,"R=Path(__file__).resolve().parents[1]",'R=Path('+repr(R.as_posix())+')')
 builder=builder.replace("R/'build/rogue-dawn-host-transactions-v1'","R/'build/rogue-dawn-host-deferred-v1'")
 builder=builder.replace('rogue_dawn_host_transactions.s','rogue_dawn_host_deferred.s')
 O.mkdir(exist_ok=True);p=O/'build-private.py'
 assert not(O/'build.json').exists(),'Frozen successor cannot regenerate'
 p.write_text(builder,newline='\n')
 sys.argv=[str(p),'--output',str(O)]
 runpy.run_path(str(p),run_name='__main__')
if __name__=='__main__':main()
