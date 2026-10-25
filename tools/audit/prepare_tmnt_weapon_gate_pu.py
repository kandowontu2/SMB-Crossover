"""Bypass unrelated weapon banks at the single source-authenticated caller."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v5')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert sha(BASE/'candidate.nes')=='ed810ca2e2a131c83ad7f22ead9b7c854a8e1a35b94b0c4d2bdd83d9e3180898'
    source=a.output/'source';shutil.copytree(BASE/'source',source)
    path=source/'src/object.s';v=path.read_text();old='    farcall RlWeaponsDispatch\n';assert v.count(old)==1
    v=v.replace(old,'''::TnFastWeaponsSpan:
    jsr TnFastWeaponsGate
    jmp TnFastWeaponsResume
    .res 12,$ea
::TnFastWeaponsResume:
''');path.write_text(v)
    path=source/'src/tmnt_audio_resident.s';v=path.read_text();v+='''
; This one caller has just loaded SelectedCharacter and compared it to PIT.
; Repeat that comparison after admission so A and every P bit match the old
; farcall's input. No arbitrary function-entry A/P contract is assumed.
::TnFastWeaponsGate:
 cmp #19
 beq TnFastWeaponsNative
 cmp #CHARACTER_PIT
 farcall RlWeaponsDispatch,jmp
::TnFastWeaponsNative:
 cmp #CHARACTER_PIT
 farcall TnAllWeapons,jmp
.export TnFastWeaponsGate
''';path.write_text(v)
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
      '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=source,capture_output=True,text=True)
    (a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2300:]
    q=dict(prepared=True,accepted=False,goal_complete=False,parent_ROM_sha256=sha(BASE/'candidate.nes'),ROM_sha256=sha(a.output/'candidate.nes'),
      changed_sources=['src/object.s','src/tmnt_audio_resident.s'],native_target='TnAllWeapons',legacy_target='RlWeaponsDispatch',
      callsite_precondition='A=SelectedCharacter; live P from CMP#CHARACTER_PIT immediately before the patched span; helper repeats it exactly.')
    (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(q['ROM_sha256'],flush=True)
if __name__=='__main__':main()
