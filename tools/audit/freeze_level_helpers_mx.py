"""Publish32 identities with native level accommodations on all mapper builds."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2];V=R/'build/verification/level-platform-adoption-mx';O=R/'build/checkpoints/level-roster-mx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/mac-roster-mw/manifest.json').read_text());adoption=json.loads((V/'adoption.json').read_text())
    native=json.loads((V/'native-results.json').read_text());proof={n:json.loads((V/(n+'.json')).read_text()) for n in ('static-final-component-proof','helper-final-component-proof')}
    assert len(native)==12 and all(x==0 for x in native.values()) and all(p['passed'] for p in proof.values())
    paths={m:V/f'level-platform-{m}-final.nes' for m in ('mmc3','mmc5','expanded')}
    assert all(sha(p)==proof['static-final-component-proof']['ROMs'][m] for m,p in paths.items())
    text=(R/'README.md').read_text().replace('those level accommodations have not yet been installed.','the definite static changes and native moving-platform accommodations are now installed. Unproved maze/camera/generator differences remain listed in the implementation report.').replace('build/checkpoints/mac-roster-mw','build/checkpoints/level-roster-mx').replace('Native level-helper integration is pending.','[Native level helpers and definite terrain changes](docs/qa/level-platform-mr-private-implementation-2026-10-23.md) are integrated using the original platform actors, graphics, collision and carry routines.')
    (R/'README.md').write_text(text)
    names=set(parent['source_files'])|set(adoption['after'])|{'tools/audit/adopt_level_helpers_mx.py','tools/audit/check_level_helpers_mx.py','tools/audit/freeze_level_helpers_mx.py'}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for key,path in paths.items():
        mapper='mmc5-expanded' if key=='expanded' else key
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True);shutil.copyfile(path.with_suffix(ext),dest);shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ADOPTED_NATIVE_LEVEL_HELPERS_ALL32',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='mac-roster-mw',ROMs={('mmc5-expanded' if m=='expanded' else m):sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),native_results=native,level_proofs=proof)
    report['limitations']=[x for x in parent['limitations'] if not x.startswith('New-profile spring/stomp and native level-helper')]+['New-profile spring/stomp adapter correction is pending at this checkpoint.','Level packet leaves literal maze lengths/checkpoints, water-fish generators and ambiguous class/anchor equivalences unresolved.']
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');(R/'build/verification/root-current59-progress-mx.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'],identities=32)))

if __name__=='__main__':main()
