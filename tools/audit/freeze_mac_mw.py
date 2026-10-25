"""Publish all32 requested identities, retaining explicit integration limits."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
V=R/'build/verification/mac-adoption-mw'
O=R/'build/checkpoints/mac-roster-mw'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/mike-roster-mv/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text());native=json.loads((V/'native-results.json').read_text())
    assert native==dict(mac=0)
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')};paths['mmc5-expanded']=V/'mac-final.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    proof={n:json.loads((V/(n+'.json')).read_text()) for n in ('native-bank-and-CHR-proof','component-proof','art-proof')}
    assert all(p['passed'] for p in proof.values())
    assert sha(paths['mmc5-expanded'])==proof['native-bank-and-CHR-proof']['sha256']==proof['component-proof']['sha256']
    text=(R/'README.md').read_text().replace('**31 playable characters and alternates**','**32 playable characters and alternates**').replace('and Mike Jones to the original roster.','Mike Jones, and Little Mac to the original roster.').replace(' Little Mac is still being integrated.','').replace('build/checkpoints/mike-roster-mv','build/checkpoints/mac-roster-mw')
    anchor='| Mike Jones |'
    at=text.index(anchor)
    text=text[:at]+'| Little Mac | A jumps, B punches, Up+B spends one star for a super punch. Down ducks; duck and rest to recover exhausted hearts. Flowers become physical star pickups, capped at three; mushrooms heal. Uses his original pink tracksuit running animation with authored source-pixel attack compositions. |\n'+text[at:]
    (R/'README.md').write_text(text)
    doc='docs/qa/little-mac-implementation-2026-10-23.md';shutil.copyfile(R/'build/player-guide-agent/little-mac-private/adoption-packet/CONTRACT.md',R/doc)
    names=set(parent['source_files'])|set(adoption['after'])|set(adoption['owned'])|{'chr/characters/little-mac.chr','tools/audit/adopt_mac_mw.py','tools/audit/check_mac_mw.py','tools/audit/freeze_mac_mw.py',doc}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True);shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ADOPTED_ALL32_IDENTITIES_PENDING_FINAL_INTEGRATION',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='mike-roster-mv',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),implemented_identities=32,portraits=19,remaining_profiles=[],native_results=native,mac_proofs=proof)
    report['limitations']=parent['limitations']+['Mac uses Mario platform/swim adapters, authored original-pixel attack compositions and existing Pit/SMB audio. No original boxing arena or Punch-Out music engine port.','New-profile spring/stomp and native level-helper integration are still pending in this checkpoint.']
    report['scope']='All32 requested playable identities; focused source/native component checks. No full campaign or video claim.'
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');(R/'build/verification/root-current58-progress-mw.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'],identities=32)))

if __name__=='__main__':main()
