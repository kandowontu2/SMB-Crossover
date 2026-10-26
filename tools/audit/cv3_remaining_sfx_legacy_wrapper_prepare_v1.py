"""Private27-cycle legacy wrapper source proposal; no native launch/adoption."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PARENT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-remaining-steady-v3')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):assert b'\r'not in p.read_bytes();p.write_bytes(s.encode())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(PARENT/'candidate.nes')=='eaa36e56c09e87f58a85db312894f14bfd7fb5838be139fc508ae6121c9e0732';source=a.output/'source';shutil.copytree(PARENT/'source',source);oldhash={}
 f=source/'src/roster_audio.s';oldhash[str(f.relative_to(source))]=sha(f);s=f.read_text();assert s.count('  beq AlreadyInit\n')==1;s=s.replace('  beq AlreadyInit\n',''' .if Kind=2 .and ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  beq Save ; actual unrolled Save never reads inputY; hot LDY23 was dead
 .else
  beq AlreadyInit
 .endif
''',1);assert s.count('  jsr Cv3MusicAndNoiseTick\n')==1;s=s.replace('  jsr Cv3MusicAndNoiseTick\n',''' .if ::MAPPER_MMC5
  jsr Cv3FxNativeTick ; real private caller; compatibility entry remains callable
 .else
  jsr Cv3MusicAndNoiseTick
 .endif
''',1);write(f,s)
 f=source/'src/cv3_remaining_source_fx.s';oldhash[str(f.relative_to(source))]=sha(f);s=f.read_text();needle=' jmp Cv3FxResidentDispatch::Generic\n .assert *-::Cv3FxResidentNoise';assert s.count(needle)==1;body=''' jmp Cv3FxResidentDispatch::Generic
 ; Genuine sole roster-wrapper caller, in the original unreachable tail.
 ; Original public Tick compatibility entry remains byte-exact.
::Cv3FxNativeTick:
 lda Cv3DmcPending
 ora Cv3DmcPriority
 bne NativeDmcWork
 jsr CvAudioPlay ; its first LDA overwrites A/NZ, all other flags unchanged
NativePlayed:
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq NativeEmpty
 jsr Cv3FxDrainGate
NativeEmpty:lda Cv3NoiseActive
 beq NativeInactive
 bmi NativeSteady
 jmp Cv3MusicAndNoiseTick::KnownActive
NativeInactive:lda Cv3FxOwned
 bne NativeFull
 lda AvAudioRequest
 cmp #26
 beq NativeLegacyCold
 lda #0
 rts
NativeLegacyCold:jmp Cv3MusicAndNoiseTick+3
NativeFull:jmp Cv3FxResidentDispatch
NativeSteady:jmp Cv3FxSteadyTry
NativeDmcWork:
 jsr Cv3DmcBeforeCv1
 jmp NativePlayed
 .assert *-::Cv3FxResidentNoise''';s=s.replace(needle,body,1);write(f,s)
 f=source/'src/cv3_source_audio.s';oldhash[str(f.relative_to(source))]=sha(f);s=f.read_text();needle=' lda Cv3NoiseActive\n beq Request\n lda GuestNativeDirty+12';assert s.count(needle)==1;s=s.replace(needle,' lda Cv3NoiseActive\n beq Request\nKnownActive:lda GuestNativeDirty+12',1)
 needle='Request:lda Cv3NoiseActive\n bmi End\n lda AvAudioRequest';assert s.count(needle)==1;s=s.replace(needle,'''Request:
 .if !::MAPPER_MMC5
 lda Cv3NoiseActive
 bmi End
 .endif
 ; Both MMC5 Tick callers enter only with a nonnegative Active value.
 lda AvAudioRequest''',1)
 needle='Continue:lda Cv3NoiseActive\n beq Done\n ldy Cv3NoiseIndex';assert s.count(needle)==1;s=s.replace(needle,'''Continue:
 .if !::MAPPER_MMC5
 lda Cv3NoiseActive
 beq Done
 .endif
 ; Entry is positive, or cold Av26 has just set Active=1. No phase is omitted.
 ldy Cv3NoiseIndex''',1)
 start=s.index('.proc Cv3MusicAndNoiseTick\n');end=s.index('.endproc',start);s=s[:end]+''' .if ::MAPPER_MMC5
 .assert *-::Cv3MusicAndNoiseTick<=221,error,"Retained genuine public legacy span"
 .res 221-(*-::Cv3MusicAndNoiseTick),$ea
 .endif
'''+s[end:];write(f,s)
 for ext in['.nes','.dbg','.lbl']:shutil.copyfile(PARENT/('candidate'+ext),a.output/('baseline'+ext))
 cmd=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
 with(a.output/'build.host.log').open('w')as log:z=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
 assert not z.returncode,(a.output/'build.host.log').read_text()[-6000:]
 r=dict(prepared=True,native_executed=False,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(a.output/'baseline.nes'),changed_source={n:dict(parent_sha256=h,candidate_sha256=sha(source/n))for n,h in oldhash.items()},source=str(source),retained_public_Tick67B_byteexact=True,expected_legacy_emptyqueue_idleDMC_saving_cycles=27,legacy_phase_counter_source_loop_unchanged=True,no_new_RAM_CHR_sample_or_tick_changes=True,scope='Private source proposal, not qualification. Need exact actual caller liveness, exhaustive legal/allphase compatibility, state/APU, IRQ, ordinary audio and whole AudioUpdate cost proofs before any native readiness.',tool_sha256=sha(__file__));(a.output/'prepared.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
