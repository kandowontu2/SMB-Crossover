"""Private source-built guarded TMNT expansion sweep; immutable parser parent.

No source song/store/tick changes, native launch, production edits or adoption.
"""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT, sha

PARENT = '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'

GATE = '''; Enter only from GuestAudioFinish, whose consumed A/N/Z are dead.
; The original public flush remains the fallback for all foreign owners.
.pushseg
.segment "TN_SWEEP_GATE"
.proc TnExpansionSweepGate
 lda SelectedCharacter
 cmp #CHARACTER_TMNT
 bne Original
 lda BassDmcActive
 beq Idle
 cmp #4                       ; original TMNT E-window owner4 only
 bne Original
 beq CheckMask
Idle:
 lda $4015                    ; unowned active DMC takes literal original
 and #$10
 bne Original
CheckMask:
 lda GuestMixMask
 and #1
 beq Original
 jmp TnExpansionSweepCall
Original:
 jmp GuestExpansionFlush
.endproc
.assert TnExpansionSweepGate=$bfda,lderror,"Declared A29 free tail"
.assert *=$c000,lderror,"Exact38-byte gate in A29 tail"
.popseg
'''

FAST = '''; New private C87 run alias. A29 remains mapped for literal fallback
; clock/target calls. Only owner0/4 is admitted; TMNT samples reside in E.
.pushseg
.segment "TN_SWEEP_C87"
.proc TnExpansionFlushFast
 lda GuestMixMask
 and #3
 sta $5015
.repeat 8,I
 lda GuestFxApu+7-I
 sta GuestExpansionApu+7-I
.endrepeat
 ; Gate already proves pulse1. Dirty images, nonzero divider
 ; or reload, and values outside18..2047 retain literal source halfclocks.
 lda GuestSweepControl
 cmp #$99
 jne Original
 lda GuestFxDirty+1
 ora GuestFxDirty+2
 ora GuestFxDirty+3
 jne Original
 lda GuestSweepDivider
 ora GuestSweepReload
 bne Original
 lda GuestSweepPeriod+1
 cmp #8
 bcs Original
 cmp #0
 bne Wide
 lda GuestSweepPeriod
 cmp #18
 bcc Original
 ; Exact8-bit specialization. Last SBC cannot overflow for P>=18.
 sec
 sbc #1
 lsr
 sta GuestSweepPeriod
 sta GuestExpansionApu+2
 sec
 sbc #1
 lsr
 sta GuestSweepDelta
 lda #0
 sta GuestSweepPeriod+1
 sta GuestSweepDelta+1
 sta GuestSweepTicks
 lda GuestFxApu+3
 and #$f8
 sta GuestExpansionApu+3
 jmp Output
Wide:
 sec
 lda GuestSweepPeriod
 sbc #1
 sta GuestSweepPeriod
 lda GuestSweepPeriod+1
 sbc #0
 lsr
 sta GuestSweepPeriod+1
 ror GuestSweepPeriod
 sec
 lda GuestSweepPeriod
 sbc #1
 sta GuestSweepDelta
 lda GuestSweepPeriod+1
 sbc #0
 lsr
 sta GuestSweepDelta+1
 ror GuestSweepDelta
 lda #0
 sta GuestSweepTicks
 lda GuestSweepPeriod
 sta GuestExpansionApu+2
 lda GuestFxApu+3
 and #$f8
 ora GuestSweepPeriod+1
 sta GuestExpansionApu+3
 jmp Output
Original:
'''

CALL = '''::TnExpansionSweepCall:
 lda CurrentBankC
 pha
 lda #$d7
 sta CurrentBankC
 sta $5116
 jsr TnExpansionFlushFast
 ; Private helper returns Y=original final A. Original public X=8 and
 ; final CPX#8 flags are independent of final A. LDA/STA retain V/D/I.
 pla
 sta CurrentBankC
 sta $5116
 tya
 ldy #1
 cpx #8
 rts
'''


def grouped_output(private=False):
    # Grouping only removes repeated mask tests. Hardware and image stores
    # remain in their original ascending order; each emitted register retains
    # exactly the same dirty/change predicate.
    return '''Output:
.repeat 2,C
.scope
 lda #(1<<C)
 and GuestMixMask
 beq NextChannel
.repeat 4,R
.scope
 I=C*4+R
.if R<>1
 lda GuestExpansionApu+I
 cmp GuestExpansionLast+I
 bne Write
 lda #(1<<C)
 and GuestMixChanged
 bne Write
 lda GuestFxDirty+I
 beq Next
Write:
 lda GuestExpansionApu+I
 sta $5000+I
 sta GuestExpansionLast+I
Next:
.endif
.endscope
.endrepeat
NextChannel:
.endscope
.endrepeat
 ldx #8
''' + (' tay\n' if private else ' ldy #1\n') + ' cpx #8\n rts\n'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists() and not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.ready/'candidate.nes')==PARENT
    a.output.mkdir(parents=True);s=a.output/'source'
    shutil.copytree(a.ready/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    path=s/'src/mmc5_sfx.s';original=path.read_text()
    prefix,tail=original.split('Output:\n',1);oldout,remainder=tail.split('.endproc',1)
    fallback=prefix.split('  ; MMC5 has no sweep registers.',1)[1]
    fallback='  ; MMC5 has no sweep registers.'+fallback
    # Repeated branch scope names remain local in the copied source.
    fast=FAST+fallback+grouped_output(True)+'.endproc\n.popseg\n'
    path.write_text(prefix+'.if ::ENABLE_MMC5_EXPANDED\n'+grouped_output()+CALL+'.assert *-GuestExpansionFlush=371,lderror,"Public flush span"\n.else\nOutput:\n'+oldout+'.endif\n.endproc'+remainder)
    (s/'src/tmnt_sweep_fast.s').write_text(GATE+fast)
    path=s/'src/guest_audio.s';text=path.read_text();old='  jsr GuestExpansionFlush\n';assert text.count(old)==1
    text=text.replace(old,'.if ::ENABLE_MMC5_EXPANDED\n  jsr TnExpansionSweepGate\n.else\n'+old+'.endif\n')
    old='  cmp #CHARACTER_BASS\n  beq :+\n    jsr BassAudioBegin\n'
    assert text.count(old)==1
    text=text.replace(old,'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  cmp #CHARACTER_PIT\n  bcs :+\n.else\n  cmp #CHARACTER_BASS\n  beq :+\n.endif\n    jsr BassAudioBegin\n')
    old='  jsr BassAudioBegin\n  rts\nNativeQueues:';assert text.count(old)==1
    text=text.replace(old,'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jmp BassAudioBegin\n  nop\n.else\n  jsr BassAudioBegin\n  rts\n.endif\nNativeQueues:')
    path.write_text(text)
    path=s/'src/entrypoint.s';path.write_text(path.read_text()+'\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "tmnt_sweep_fast.s"\n.endif\n')
    path=s/'smb1base-mmc5-expanded.cfg';text=path.read_text()
    old='X5_NEW_57: start=$a000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;'
    assert text.count(old)==1
    text=text.replace(old,'X5_NEW_57: start=$a000, size=$1500, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;\n    TN_SWEEP_C87_MEM: start=$d500, size=$0b00, type=ro, file=%O, fill=yes, fillval=$ff, bank=$57;')
    old='TMNT_CORE:load=X5_NEW_57,type=ro;';assert text.count(old)==1
    text=text.replace(old,old+'\n    TN_SWEEP_C87:load=TN_SWEEP_C87_MEM,type=ro;')
    anchor='X5_AUDIO_MIX: load=PRG_EXTRA,type=ro,optional=yes;'
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+'\n    TN_SWEEP_GATE:load=PRG_EXTRA,start=$bfda,type=ro;')
    path.write_text(text)
    command=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    result=subprocess.run(command,cwd=s,capture_output=True,text=True)
    (a.output/'build.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,(result.stdout+result.stderr)[-4000:]
    before,after=(a.ready/'candidate.nes').read_bytes(),(a.output/'candidate.nes').read_bytes()
    changes={n:sum(x!=y for x,y in zip(before[16+n*8192:16+(n+1)*8192],after[16+n*8192:16+(n+1)*8192])) for n in range(128)}
    changes={n:c for n,c in changes.items()if c};assert set(changes)=={29,87}
    qb,qa=qualified(a.ready/'candidate.nes'),qualified(a.output/'candidate.nes')
    moved={str(k):[v,qa.get(k)]for k,v in qb.items()if qa.get(k)!=v}
    assert not moved,moved
    assert before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert before[16+87*8192+0x1500:16+88*8192]==bytes([255])*0xb00
    manifest={};patch=''
    for n in ['src/mmc5_sfx.s','src/guest_audio.s','src/entrypoint.s','src/tmnt_sweep_fast.s','smb1base-mmc5-expanded.cfg']:
        old,new=a.ready/'source'/n,s/n
        manifest[n]=dict(before=sha(old)if old.exists()else None,after=sha(new))
        patch+=''.join(difflib.unified_diff(old.read_text().splitlines(True)if old.exists()else [],new.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    proof=dict(prepared=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
               changed_PRG_bytes=changes,source_changes=manifest,all_existing_qualified_symbols_exact=True,
               original_sweep_public_entry_span_clock_target_unchanged=True,source_audio_and_CHR_unchanged=True,
               bounded_period_range=[18,2047],timer_range_bits=11,lower_guard_literal_fallback=True,
               C87_mapping_only_owner0_or4=True,temporary_C_bank_restored=True,new_RAM_or_SMC_borrow=False,
               old_lead_erratum='Periods18..2047 are the bounded11-bit timer range, not the entire13-bit domain.',
               checker_sha256=sha(Path(__file__)))
    metadata=json.loads((a.ready/'preparation.json').read_text())
    metadata.update(proof)
    (a.output/'preparation.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
