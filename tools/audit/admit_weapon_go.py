"""Admit source-backed Arm/Rush mechanics, landing audio and MM closure savings."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
C=V/'weapons-current-gf/source';O=V/'weapons-admission-go';CP=R/'build/checkpoints/weapons-source-go'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())


def main():
    assert not O.exists()and not CP.exists();O.mkdir()
    prep=read(C.parent/'preparation.json');build=read(C.parent/'build.json')
    assert build['passed']
    parent=R/'build/checkpoints/rygar-world-palette-ga/manifest.json'
    assert sha(parent)==prep['parent_manifest_sha256']
    assert all(sha(R/f'build/smb-crossover-{m}.nes')==h for m,h in prep['parent_ROMs'].items())
    for n,h in prep['parent_source_hashes'].items():assert sha(R/n)==h,n
    verification={}
    for folder,name in [('weapons-regressions-gh','summary.json'),('weapons-mechanics-gi','summary.json'),('weapons-audio-cost-gk','summary.json'),('weapons-broad-gn','summary.json')]:
        p=V/folder/name;j=read(p);assert j['passed'];verification[p.relative_to(R).as_posix()]=sha(p)
    land=V/'weapons-land-gg/review.json';j=read(land);assert j['status'].startswith('PASS_CURRENT_GF')and j['total_calls']==516
    verification[land.relative_to(R).as_posix()]=sha(land)
    route=R/'build/roster-through-2-2/root-rygar-weapon-gm-7-v0-mmc3/manifest.json';j=read(route)
    assert j['verified_through_2_2']and j['result']['deaths']==0
    verification[route.relative_to(R).as_posix()]=sha(route)
    # Old Bass tape fails identically on both GA and GF, not a new weapon regression.
    bass=[R/'build/roster-through-2-2'/n for n in ('root-bass-parent-gl-9-v0-mmc3','root-bass-current-gj-9-v0-mmc3')]
    for folder in bass:
        j=read(folder/'manifest.json');assert not j['verified_through_2_2']and j['result']['failure']=='death'and j['result']['frames']==2251
    same=[]
    for p in bass[0].iterdir():
        q=bass[1]/p.name
        if p.suffix in('.csv','.jsonl')and q.exists():assert p.read_bytes()==q.read_bytes();same.append(p.name)
    assert 'trace.csv'in same and 'oam.csv'in same
    for n,h in prep['modified_files'].items():assert sha(C/n)==h
    assert set(prep['modified_files'])=={'src/entrypoint.s','src/guest_audio.s','src/megaman_audio.s','src/special_weapons.s','src/megaman_rush.s','src/megaman_rush_land.s','src/megaman_super_arm.s'}
    expected={m:sha(C/f'build/smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
    (O/'preparation.json').write_text(json.dumps(dict(parent_manifest_sha256=sha(parent),expected_ROMs=expected,verification=verification,Bass_unchanged_negative_files=same,goal_complete=False),indent=2)+'\n')
    for n in prep['modified_files']:shutil.copyfile(C/n,R/n)
    shutil.copyfile(V/'weapons-broad-gn/bass-special-weapons.lua',R/'tests/bass-special-weapons.lua')
    for mapper in expected:
        with(O/(mapper+'-build.log')).open('wb')as f:z=subprocess.run([sys.executable,str(R/'tools/build.py'),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT)
        assert z.returncode==0
        assert sha(R/f'build/smb-crossover-{mapper}.nes')==expected[mapper]
        print('MAIN',mapper,'literal reviewed GF',flush=True)
    names=set(prep['parent_source_hashes'])|set(prep['modified_files'])|{'tests/bass-special-weapons.lua'}
    for mapper in expected:
        for base in ('','-baseline'):
            for ext in ('nes','lbl','dbg','map'):names.add(f'build/smb-crossover-{mapper}{base}.{ext}')
    for n in names:
        d=CP/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,d)
    manifest=dict(status='ARM_RUSH_SOURCE_RULES_LANDING_SFX_AND_AUDIO_OPTIMIZATION_ADMITTED_FULL_GOAL_ACTIVE',utc=datetime.now(timezone.utc).isoformat(),parent_checkpoint=parent.relative_to(R).as_posix(),parent_checkpoint_sha256=sha(parent),ROMs=expected,hashes={n:sha(CP/n)for n in sorted(names)},verification=verification,source_overlay=prep['modified_files'],goal_complete=False)
    (CP/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (O/'summary.json').write_text(json.dumps(dict(passed=True,checkpoint_sha256=sha(CP/'manifest.json'),ROMs=expected,verification=verification,whole_goal_complete=False),indent=2)+'\n')


if __name__=='__main__':main()
