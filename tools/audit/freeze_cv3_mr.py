"""Publish three verified CV3 alternates while retaining documented limits."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
V=R/'build/verification/cv3-adoption-mr'
O=R/'build/checkpoints/cv3-roster-mr'
D=R/'build/player-guide-agent/cv3-private/adoption-packet'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    parent=json.loads((R/'build/checkpoints/palette-roster-mq/manifest.json').read_text())
    adoption=json.loads((V/'adoption.json').read_text())
    evidence=V/'final-v2'
    native=json.loads((evidence/'native-results.json').read_text())
    component=json.loads((evidence/'component-proof.json').read_text())
    integration=json.loads((evidence/'integration-proof.json').read_text())
    assert len(native)==10 and all(x==0 for x in native.values()) and component['passed'] and integration['passed']
    paths={m:V/f'standard-{m}'/f'smb-crossover-{m}.nes' for m in ('mmc3','mmc5')}
    paths['mmc5-expanded']=V/'cv3-final-v2.nes'
    assert all(sha(paths[m])==parent['ROMs'][m] for m in ('mmc3','mmc5'))
    assert sha(paths['mmc5-expanded'])==component['candidate_sha256']==integration['sha256']
    adoption['after']={n:sha(R/n) for n in adoption['after']}
    adoption['bank4_tail_growth_bytes']=19
    adoption['bank4_gate_size']=50
    adoption['negative_first_guard_candidate_sha256']=sha(V/'cv3-final.nes')
    adoption['negative_scope']='First combined farcall chain could miss a one-update upgrade input at full ship ensemble; separate resident targets avoid the extra per-frame ship farcall.'
    (V/'adoption.json').write_text(json.dumps(adoption,indent=2)+'\n')
    doc='docs/qa/cv3-alternates-implementation-2026-10-23.md'
    shutil.copyfile(D/'CONTRACT.md',R/doc)
    names=set(parent['source_files'])|set(adoption['after'])|set(adoption['owned'])|{doc,'tools/audit/adopt_cv3_mr.py','tools/audit/check_cv3_mr.py','tools/audit/freeze_cv3_mr.py'}
    O.mkdir(parents=True)
    with zipfile.ZipFile(O/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names):z.write(R/n,n)
    for mapper,path in paths.items():
        for ext in ('.nes','.lbl','.dbg','.map'):
            dest=O/'build'/('smb-crossover-'+mapper+ext);dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(path.with_suffix(ext),dest)
            if mapper=='mmc5-expanded':shutil.copyfile(dest,R/'build'/dest.name)
    report=dict(parent,status='ADOPTED_CV3_ALTERNATES',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_checkpoint='palette-roster-mq',ROMs={m:sha(p) for m,p in paths.items()},source_files={n:sha(R/n) for n in sorted(names)},source_zip_sha256=sha(O/'source.zip'),implemented_identities=28,remaining_profiles=['SMB3 Mario/Luigi','Little Mac','Mike Jones'],native_results=native,cv3_component_proof=component,cv3_integration_proof=integration)
    report['limitations']=parent['limitations']+['CV3 inherited Simon music/SFX; attack-based SMB brick/question-block activation and blue Ice tint remain pending.','CV3 original36px Sypha/Alucard jumps need the pending audited native platform helpers for full campaign traversal.']
    report['scope']='28 playable identities/alternates with authentic source artwork and movement/weapon components plus explicitly documented NES/SMB adaptations. No full campaign or video claim.'
    (O/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (R/'build/verification/root-current54-progress-mr.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(O),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'],identities=28)))

if __name__=='__main__':main()
