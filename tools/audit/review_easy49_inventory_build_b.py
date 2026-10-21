"""Retain the final catalog negative and classify generated-file normalization."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49-easy-inventory-base-a'
S=H/'source'
B=R/'build/verification/root49-easy-hard-user-baseline-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=H/'build-review-b.json'
    assert not out.exists()
    original=H/'report.json';a=json.loads(original.read_text())
    assert a['status']=='BUILDING_PRIVATE_LEGACY_INVENTORY_BOUNDARY'
    assert len(a['builds'])==2 and all(q['exit']==0 and q['RAM_exact'] and q['CHR_exact'] and q['DPCM_exact'] for q in a['builds'])
    baseline=json.loads((B/'baseline.json').read_text())
    assert all(sha(R/n)==h for n,h in baseline['current_source_hashes'].items())
    actual={n:sha(S/n)for n in a['candidate_source_hashes']}
    changed={n:dict(before=h,after=actual[n])for n,h in a['candidate_source_hashes'].items()if actual[n]!=h}
    expected={'src/bass_metasprites.inc','src/chr_map_mmc3.inc','src/chr_map_mmc5.inc',
        'src/megaman_injury_art.inc','src/megaman_metasprites.inc','src/ordinary_body_layout_art.inc','src/player_outline_flags.inc'}
    assert set(changed)==expected
    t_archive=R/'build/checkpoints/roster-audit-v49-ryu-head-t/source-v49-ryu-head-t.zip'
    with zipfile.ZipFile(t_archive)as z:
        for n,row in changed.items():
            before=R/n;after=S/n
            row['same_after_CRLF_normalization']=before.read_bytes().replace(b'\r\n',b'\n')==after.read_bytes().replace(b'\r\n',b'\n')
            row['generated_bytes_equal_T_source']=after.read_bytes()==z.read(n)
            assert row['same_after_CRLF_normalization'] and row['generated_bytes_equal_T_source'],n
    for q in a['builds']:
        for p in q['artifacts'].values():assert sha(R/p['path'])==p['sha256']
    result=dict(status='PASS_PRIVATE_LEGACY_INVENTORY_BOUNDARY_LAYOUT_ONLY',
        script_sha256=sha(__file__),retained_original_host_negative=dict(path=str(original.relative_to(R)),sha256=sha(original),
            cause='Both native links/layout checks passed; final literal input catalog assertion found seven regenerated includes normalized fromCRLF toLF. No gameplay execution failure.'),
        frozen_user_baseline_sha256=sha(B/'baseline.json'),actual_source_hashes=actual,
        generator_normalization=changed,builds=a['builds'],mode_contract=a['mode_contract'],
        RAM_exact=True,CHR_exact=True,DPCM_exact=True,user_main_source_and_ROMs_unchanged=True,
        complete_Easy_behavior=False,native_or_CPU_execution=False,accepted_release=False,goal_complete=False,
        remaining='Execute shared-mode/pickup/drop boundary checks; integrate the audited per-characterEasy gates and shared injury/power transitions before publication.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],sha(out),flush=True)


if __name__=='__main__':main()
