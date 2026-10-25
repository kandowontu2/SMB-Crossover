"""Bind the CHR/OAM repair evidence to its private candidate; retain failures."""
from pathlib import Path
import csv, hashlib, json, zipfile
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT/'build/verification/chr-publication-np'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
ROUTES = [('kirby','easy'), ('meta','hard'), ('leonardo','easy'),
          ('raphael','easy'), ('michelangelo','easy'), ('donatello','easy'),
          ('octopus','easy'), ('twinbee','easy'), ('pentarou','easy')]
SOURCE = ['src/kirby_core.s','src/meta_knight.s','src/tmnt_draw.s','src/parodius_render.s']
PUBLIC = {'mmc3-oversized':'a03284f691e32be333976806462a5f65ee2d70e0659d0e404a6347b5a0d7bae7',
          'mmc5-expanded':'58e44b4ef7324bf1bd093b92738a35d38df6aba55315133d410b444ad7f09c6e'}


def main():
    rom = QA/'candidate-v2.nes'
    digest = sha(rom)
    assert digest == 'a21df869bdfa8d66c6a8ce3ea83b87e83e82afd0206b5f539c49703479ee3549'
    routes = {}
    for name, mode in ROUTES:
        discovery = QA/f'discover-{name}-{mode}-v2'
        replay = QA/f'replay-{name}-{mode}-v2-fresh'
        pair = {}
        for label, folder in [('discovery',discovery), ('replay',replay)]:
            m, proof = read(folder/'manifest.json'), read(folder/'chr-commit.json')
            assert m['ROM_sha256']==digest and m['exit']==0 and m['result']['cleared']
            assert m['result']['deaths']==0 and m['result']['failure']is None
            assert set(m['result']['stage_entries'])=={'0-0','0-1'}
            assert m['controller_only']and not m['memory_writes']and m['fixed_replay']==(label=='replay')
            assert m['inputs_sha256']==sha(folder/'inputs.csv')
            assert proof['passed']and proof['mismatched_frames']==0 and proof['frames']>1000
            rows = list(csv.DictReader((folder/'chr-commit.csv').open()))
            assert len(rows)==proof['frames']and all(row['bad']=='0'for row in rows)
            assert (ROOT/'tools/audit/chr_commit_observer.lua').read_text()in(folder/'audit.lua').read_text()
            pair[label] = dict(manifest_sha256=sha(folder/'manifest.json'),
                inputs_sha256=sha(folder/'inputs.csv'), trace_sha256=sha(folder/'chr-commit.csv'),
                frame_count=m['result']['frames'], graphics=proof)
        assert (discovery/'inputs.csv').read_bytes()==(replay/'inputs.csv').read_bytes()
        routes[name] = dict(mode=mode, **pair)
    before = {}
    for name,mode in [('kirby','easy'),('meta','hard'),('leonardo','easy'),('octopus','easy')]:
        folder = QA/f'before-route-{name}-{mode}'
        m, proof = read(folder/'manifest.json'), read(folder/'chr-commit.json')
        assert m['ROM_sha256']==sha(ROOT/'build/checkpoints/roll-performance-no/candidate.nes')
        assert not proof['passed']and proof['mismatched_frames']>0
        # The earlier discovery harness failed to propagate observer failures.
        # These native clears are explicitly failed graphics evidence.
        before[name] = dict(graphics=proof, trace_sha256=sha(folder/'chr-commit.csv'),
                            original_manifest_exit=m['exit'], graphics_admission=False)
    entries = read(QA/'entry-v2/results.json')
    assert entries['rom_sha256']==digest and entries['identities']==37 and len(entries['results'])==37
    assert all(r['exit']==0 for r in entries['results'].values())
    arenas = read(QA/'turtle-arenas-v2/results.json')
    assert arenas['passed']and arenas['rom_sha256']==digest
    meta = read(QA/'components-v2/results.json')['results']['meta']
    assert meta['exit']==0
    regressions = {}
    for suite in ('components','bells','pickups'):
        result = read(QA/f'parodius-{suite}-v2/results.json')
        assert result['ROM_sha256']==digest and set(result['results'])=={'1','2','3'}
        assert all(row['exit']==0 for row in result['results'].values())
        if suite=='pickups':assert sum(r['rendered_source_pixel_cases']for r in result['results'].values())==45
        regressions['parodius_'+suite] = result
    roll = read(QA/'roll-components-easy-v2/results.json')
    assert roll['ROM_sha256']==digest and roll['exit']==0
    regressions['roll_components_easy'] = roll
    standards = {}
    for mapper,wanted in [('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),
                          ('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')]:
        assert sha(QA/f'standard-{mapper}.nes')==wanted
        standards[mapper] = wanted
    for name,wanted in PUBLIC.items():assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==wanted
    old, control = read(QA/'components-v2/results.json'), read(QA/'old-fixtures-parent-control/results.json')
    failures = {}
    for name in ('turtle-health','turtle-attacks','turtle-natural','kirby-food'):
        assert old['results'][name]['exit']!=0 and control['results'][name]['exit']!=0
        def failure(folder):
            logs=list((folder/name/'build/verification').glob('*.log'))
            assert len(logs)==1
            return next(line for line in logs[0].read_text().splitlines()if line.startswith('FAIL '))
        assert failure(QA/'components-v2')==failure(QA/'old-fixtures-parent-control')
        failures[name] = dict(baseline_and_candidate_failure=failure(QA/'components-v2'),
            retimed_current_arena_pass=name in ('turtle-health','turtle-attacks'),
            original_fixture_sha256=old['results'][name]['fixture_sha256'])
    parent = read(ROOT/'build/checkpoints/roll-performance-no/manifest.json')
    changed = []
    for name, wanted in parent['source_files'].items():
        if name.startswith(('src/','chr/','audio/','inc/'))and sha(ROOT/name)!=wanted:changed.append(name)
    assert set(changed)==set(SOURCE), changed
    image = Image.new('RGB',(4*512,3*510),'#111c29')
    draw = ImageDraw.Draw(image)
    for i,(name,mode) in enumerate(ROUTES):
        folder=QA/f'replay-{name}-{mode}-v2-fresh'
        frames=sorted((folder/'frames').glob('*.png'))
        frame=frames[len(frames)//2]
        x,y=(i%4)*512,(i//4)*510
        draw.text((x+12,y+8),name.upper()+' / '+mode+' / frame '+frame.stem,fill='white')
        image.paste(Image.open(frame).convert('RGB').resize((512,480),Image.Resampling.NEAREST),(x,y+30))
    image.save(QA/'replay-contact.png')
    report = dict(passed=True, rom_sha256=digest, parent='roll-performance-no',
        source_changes={n:sha(ROOT/n)for n in SOURCE}, before=before, routes=routes,
        independent_replay_video_frames=sum(p['replay']['frame_count']for p in routes.values()),
        independent_replay_observed_graphics_frames=sum(p['replay']['graphics']['frames']for p in routes.values()),
        entries=entries, meta_components=meta, turtle_components=arenas,
        regressions=regressions, unchanged_standard_roms=standards,
        unchanged_public_roms=PUBLIC, retained_stale_fixture_failures=failures,
        scope='Private MMC5 CHR publication repair;9 independent1-1 replays, read-only actual OAM/CHR ownership. No all-pixel/full-roster/powerup/60Hz/audio/MMC3 completion claim.')
    (QA/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in ('passed','rom_sha256','independent_replay_video_frames','independent_replay_observed_graphics_frames')}))


if __name__=='__main__':main()
