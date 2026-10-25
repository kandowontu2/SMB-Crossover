"""Publish source-authenticated SMB3 Mario and Luigi with honest port limits."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
V=R/'build/verification/smb3-adoption-mu'
O=R/'build/checkpoints/smb3-roster-mu'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/cv3-blocks-mt/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text())
    native=json.loads((V/'native-results.json').read_text())
    proof={k:json.loads((V/(k+'-proof.json')).read_text()) for k in ('core','render','native-bank-and-CHR')}
    assert len(native)==9 and all(x==0 for x in native.values()) and all(p['passed'] for p in proof.values())
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'smb3-final.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    assert sha(paths['mmc5-expanded'])==proof['core']['candidate_SHA256']==proof['render']['candidate_SHA256']==proof['native-bank-and-CHR']['sha256']
    # Only publication prose changes after the hash-bound ROM verification.
    readme=(R/'README.md').read_text().replace('**28 playable characters and alternates**','**30 playable characters and alternates**').replace('and Grant/Sypha/Alucard to the original roster.','Grant/Sypha/Alucard, and SMB3 Mario/Luigi to the original roster.').replace('SMB3 Mario/Luigi, Little Mac, and Mike Jones are still being integrated.','Little Mac and Mike Jones are still being integrated.').replace('build/checkpoints/cv3-roster-mr','build/checkpoints/smb3-roster-mu')
    (R/'README.md').write_text(readme)
    names=set(parent['source_files'])|set(adoption['after'])|set(adoption['owned'])|{'chr/characters/smb3-mario.chr','tools/audit/adopt_smb3_mu.py','tools/audit/check_smb3_mu.py','tools/audit/freeze_smb3_mu.py','docs/qa/smb3-mario-private-implementation-2026-10-23.md'}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ADOPTED_SMB3_MARIO_LUIGI',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='cv3-blocks-mt',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),implemented_identities=30,remaining_profiles=['Little Mac','Mike Jones'],native_results=native,smb3_core_proofs=proof)
    report['limitations']=parent['limitations']+['SMB3 inherits Pit music/provisional SMB SFX; Fire pickup flash and projectile contact poofs are pending.','SMB3 normal six upgrade types are implemented; Kuribo shoe, P-Wing inventory, held shells and original map objects remain outside this normal-form port.']
    report['scope']='30 playable identities/alternates with authenticated source components and declared SMB adaptations. No full campaign or video claim.'
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current56-progress-mu.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'],identities=30)))

if __name__=='__main__':main()
