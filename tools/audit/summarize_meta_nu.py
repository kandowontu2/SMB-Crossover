"""Bind the grounded Meta repair to exact ROM, native proofs and fixed replays."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/meta-knight-source-nu'
LIVE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-meta-knight-nu-live')
NATIVE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-meta-knight-native-audit')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())


def main():
    rom=LIVE/'candidate-v7.nes';wanted=sha(rom)
    assert wanted=='b90ede8fa3afaceefe3ef3090424f4d6b6662c139a1a3d6df52e64b7ec00b240'
    components={}
    for name in('moves-easy-v9','moves-hard-v9','physical-easy-v3','physical-hard-v3'):
        p=QA/name/'result.json';r=read(p)
        assert r['passed']and r['rom_sha256']==wanted and r['exit']==0
        assert r['proof']['passed']
        components[name]=dict(path=str(p),sha256=sha(p),proof=r['proof'])
    entry=read(QA/'entry-v7/results.json')
    assert entry['rom_sha256']==wanted and entry['identities']==37 and len(entry['results'])==37
    assert all(r['exit']==0 for r in entry['results'].values())
    art=read(QA/'art-independent-v7.json');assert art['passed']and art['rom_sha256']==wanted
    assert len(art['linked_poses'])==90 and art['native_visible_parts']==136
    rotor=read(QA/'rotor-v7/proof.json');assert rotor['passed']and rotor['after_sha256']==wanted
    native=read(NATIVE/'v7/check/proof.json');assert native['passed']and native['ROM_sha256']==wanted
    assert all(c['priority_mismatch_frames']==0 for c in native['cases'].values())
    negative=read(NATIVE/'v5-negative-proof.json');assert not negative['passed']
    routes={}
    for mode in('easy','hard'):
        row={}
        for kind in('discover','replay'):
            d=LIVE/f'{kind}-{mode}-v3';m=read(d/'manifest.json')
            assert m['ROM_sha256']==wanted and m['exit']==0 and m['controller_only']and not m['memory_writes']
            assert m['result']['cleared']and m['result']['deaths']==0 and m['chr_commit']['passed']
            assert sha(d/'inputs.csv')==m['inputs_sha256']
            row[kind]=dict(path=str(d),manifest_sha256=sha(d/'manifest.json'),inputs_sha256=sha(d/'inputs.csv'),
                           trace_sha256=sha(d/'trace.csv'),frames=m['result']['frames'],chr=m['chr_commit'])
        assert row['discover']['inputs_sha256']==row['replay']['inputs_sha256']
        assert row['discover']['trace_sha256']==row['replay']['trace_sha256']
        routes[mode]=row
    public={
        'mmc3':'97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
        'mmc5':'7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128',
        'mmc3-oversized':'a03284f691e32be333976806462a5f65ee2d70e0659d0e404a6347b5a0d7bae7',
        'mmc5-expanded':'58e44b4ef7324bf1bd093b92738a35d38df6aba55315133d410b444ad7f09c6e'}
    for name,h in public.items():assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==h
    parent=read(ROOT/'build/checkpoints/little-mac-star-nt/manifest.json')
    changed={n:sha(ROOT/n)for n,h in parent['source_files'].items()if sha(ROOT/n)!=h}
    report=dict(passed=True,status='PRIVATE_GROUNDED_META_REPAIR_WITH_OPEN_FULL_GOAL',rom=str(rom),rom_sha256=wanted,
                parent_checkpoint='little-mac-star-nt',source_changes=changed,components=components,identities_cold_entered=37,
                source_art=dict(path=str(QA/'art-independent-v7.json'),sha256=sha(QA/'art-independent-v7.json')),
                native_hardware=dict(path=str(NATIVE/'v7/check/proof.json'),sha256=sha(NATIVE/'v7/check/proof.json'),proof=native),
                priority_negative=dict(path=str(NATIVE/'v5-negative-proof.json'),sha256=sha(NATIVE/'v5-negative-proof.json')),
                boundary_jump=dict(path=str(NATIVE/'v7/boundary-jump-proof.json'),sha256=sha(NATIVE/'v7/boundary-jump-proof.json')),
                independent_audit_report=dict(path=str(ROOT/'build/verification/meta-knight-native-audit/manifest.json'),
                                              sha256=sha(ROOT/'build/verification/meta-knight-native-audit/manifest.json')),
                rotor_differential=rotor,routes=routes,unchanged_public_roms=public,
                limitations=['Sword hues explicitly remapped30/37/17 to30/27/16; source sword audio usesSMB fallback.',
                             'Player input, recovery/spin bounds and stronger jump are explicit playable-boss adaptations.',
                             'Full37identity every-item/campaign/performance/audio matrix and fullMMC3port remain open.',
                             'Original boss/food/move/rotor fixtures are explicitly seeded native-boundary components, not campaigns.'],goal_complete=False)
    (QA/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,rom_sha256=wanted,source_changes=list(changed),routes={k:v['replay']['frames']for k,v in routes.items()},goal_complete=False)))


if __name__=='__main__':main()
