"""Install independently qualified Mac native music once, retaining rollback."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT='52918588bab0eec3f3a1f857bf084d2d799e88a5c781c75233c098ccc5f54f3f'
FINAL='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    prepared=D/'mac-native-current529-v1'
    out=prepared/'adoption-v1'
    assert not out.exists(),'One-shot adoption already started; inspect its retained state.'
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    alias=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert sha(installed)==sha(alias)==PARENT and sha(prepared/'candidate.nes')==FINAL
    qualification=prepared/'root-qualification-v1/proof.json'
    q=json.loads(qualification.read_text(encoding='utf-8'))
    assert q['passed'] and q['ROM_sha256']==FINAL and q['original_source_CPU_calls']==162009
    assert q['native_music']['source_calls']==9306 and q['native_music']['ordered_source_APU_writes']==81157
    assert q['full_ordinary_AudioUpdate']['full_AudioUpdate_cases']==5856
    for path,expected in (q['tools']|q['receipts']).items():
        assert sha(Path(path))==expected,path
    roster_path=prepared/'roster-audio-cpu-v1/proof.json'
    roster=json.loads(roster_path.read_text(encoding='utf-8'))
    assert roster['passed'] and roster['ROM_sha256']==FINAL and roster['identities']==36 and roster['full_AudioUpdate_calls']==9216
    assert roster['tool_sha256']==sha(ROOT/'tools/audit/check_mac_music_roster_cpu.py')
    composition=json.loads((prepared/'proof.json').read_text(encoding='utf-8'))
    files=composition['source_files']
    for name,row in files.items():
        current=ROOT/name
        if row['before_sha256'] is None:
            assert not current.exists(),name
        else:
            assert sha(current)==row['before_sha256'],name
        assert sha(prepared/'source'/name)==row['after_sha256'],name
    out.mkdir()
    shutil.copy2(installed,out/'previous-MMC5.nes')
    previous=out/'previous-source'
    suffixes=['.nes','.dbg','.lbl','.map','.build.json','.build.log']
    for suffix in suffixes:
        old=alias.with_suffix(suffix)
        if old.exists():
            saved=out/'previous-default'/old.name
            saved.parent.mkdir(exist_ok=True)
            shutil.copy2(old,saved)
    for name,row in files.items():
        if row['before_sha256'] is not None:
            saved=previous/name
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/name,saved)
    try:
        for name in files:
            shutil.copy2(prepared/'source'/name,ROOT/name)
        with (out/'fresh-build.log').open('w',encoding='utf-8') as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                            '--output',str(out/'candidate.nes')],cwd=ROOT,check=True,
                           stdout=log,stderr=subprocess.STDOUT)
        assert sha(out/'candidate.nes')==FINAL,'Fresh canonical ROOT build differs'
    except BaseException:
        for name,row in files.items():
            if row['before_sha256'] is None:
                (ROOT/name).unlink(missing_ok=True)
            else:
                shutil.copy2(previous/name,ROOT/name)
        raise
    staged=installed.with_name(installed.stem+'.staging-'+FINAL[:8]+'.nes')
    assert not staged.exists()
    shutil.copy2(out/'candidate.nes',staged)
    assert sha(staged)==FINAL
    staged.replace(installed)
    for suffix in suffixes:
        shutil.copy2((out/'candidate.nes').with_suffix(suffix),alias.with_suffix(suffix))
    assert sha(alias)==sha(installed)==FINAL
    proof=dict(adopted=True,goal_complete=False,ROM_sha256=FINAL,parent_ROM_sha256=PARENT,
               fresh_canonical_ROOT_compile_exact=True,source_files=files,
               changed_ROM_bytes=7959,changed_PRG_banks=[38,123,126],
               retained_PC_RAM_CHR_fixed_DPCM_exact=True,new_RAM_bytes=0,new_CHR_bytes=0,
               original_source_CPU_calls=162009,original_source_CPU_APU_writes=700355,
               actual_dispatch_source_CPU_calls=48570,actual_dispatch_source_CPU_APU_writes=414342,
               native_music=q['native_music'],matched_performance=q['matched_performance'],
               full_ordinary_AudioUpdate=q['full_ordinary_AudioUpdate'],
               other36_identity_CPU_calls=9216,
               non_Mac_cycle_costs=roster['rows'],
               qualification=str(qualification),qualification_sha256=sha(qualification),
               roster_CPU_proof=str(roster_path),roster_CPU_proof_sha256=sha(roster_path),
               ordinary_target_hashes=composition['ordinary_target_hashes'],
               installed=str(installed),Downloads_and_default_build_current=True,
               backup_directory=str(out),
               scope='Authentic nine-track Punch-Out music and14 area/event selections, current-hash source/native/hardware/cadence qualified.36 other identities retain exact CPU audio/state outcomes; expanded fallback identities add12 dispatcher CPU cycles, explicitly disclosed. No new full-level/natural-item/whole-roster or universal60fps claim.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    receipt=ROOT/'build/verification/mac-native-music'
    receipt.mkdir(exist_ok=True)
    shutil.copy2(out/'proof.json',receipt/'proof.json')
    print(json.dumps({k:v for k,v in proof.items()if k not in ['source_files','native_music','matched_performance','non_Mac_cycle_costs']},indent=2))


if __name__=='__main__':
    main()
