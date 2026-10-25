"""Publish the composed31-identity roster and retain source-bound evidence."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
V=R/'build/verification/mike-adoption-mv'
O=R/'build/checkpoints/mike-roster-mv'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/smb3-roster-mu/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text())
    native=json.loads((V/'native-results.json').read_text())
    assert len(native)==5 and all(x==0 for x in native.values())
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'mike-final.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    proof={n:json.loads((V/(n+'.json')).read_text()) for n in ('native-bank-and-CHR-proof','native-owner-terrain','native-health-equivalence')}
    assert proof['native-bank-and-CHR-proof']['passed']
    assert sha(paths['mmc5-expanded'])==proof['native-bank-and-CHR-proof']['sha256']==proof['native-owner-terrain']['candidate_sha256']==proof['native-health-equivalence']['candidate_sha256']
    readme=(R/'README.md').read_text().replace('**30 playable characters and alternates**','**31 playable characters and alternates**').replace('and SMB3 Mario/Luigi to the original roster.','SMB3 Mario/Luigi, and Mike Jones to the original roster.').replace('Little Mac and Mike Jones are still being integrated.','Little Mac is still being integrated.').replace('build/checkpoints/smb3-roster-mu','build/checkpoints/mike-roster-mv')
    (R/'README.md').write_text(readme)
    doc='docs/qa/mike-jones-implementation-2026-10-23.md'
    shutil.copyfile(R/'build/mike-kd-private/handoff-Mike-core-m/README.md',R/doc)
    names=set(parent['source_files'])|set(adoption['after'])|set(adoption['owned'])|{'chr/characters/mike-jones.chr','tools/audit/adopt_mike_mv.py','tools/audit/check_mike_mv.py','tools/audit/freeze_mike_mv.py','tests/full-roster-entry.lua','tools/audit/check_full_roster_entry.py',doc}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ADOPTED_MIKE_JONES',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='smb3-roster-mu',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),implemented_identities=31,remaining_profiles=['Little Mac'],native_results=native,mike_proofs=proof)
    report['limitations']=parent['limitations']+['Mike uses existing Pit/SMB audio; native StarTropics music and utility inventory are not ported. His jump, trajectories and drops include declared SMB adaptations.']
    report['scope']='31 playable identities/alternates with authenticated source components and declared SMB adaptations. No full campaign or video claim.'
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current57-progress-mv.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'],identities=31)))

if __name__=='__main__':main()
