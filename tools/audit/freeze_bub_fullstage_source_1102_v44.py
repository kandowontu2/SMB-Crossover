"""Compact v36+ direct source/proof and three terminal native runs once."""
import hashlib,json,zipfile
from pathlib import Path

R=Path(__file__).resolve().parents[2];O=R/'build/bub-menu-candidate-1102-v2'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())


def main():
    assert sha(O/'combined-current-landing.nes')==PIN
    sources=['check_bub_reachable_pit_takeoff_1102_v36.py','prepare_bub_reachable_pit_native_1102_v37.py',
        'check_bub_castle_stairs_1102_v38.py','prepare_bub_castle_stairs_native_1102_v39.py',
        'check_bob_reachable_rearm_1102_v41.py','prepare_bob_reachable_rearm_native_1102_v42.py',Path(__file__).name]
    paths=[R/'tools/audit'/n for n in sources]
    # v40 is an unused immutable review recipe; root delivered with a separate
    # v43 source and actual Downloads replay. Retain it without staging it as
    # the successful installation recipe or changing its historical policy.
    paths.append(R/'tools/audit/deliver_bub_landing_full11_1102_v40.py')
    names=['reachable-pit-takeoff-v36-CPU.json','castle-stairs-v38-CPU.json','bob-reachable-rearm-v41-CPU.json',
        'combined-current-landing.json','landing-current-supplement-v35.json']
    paths += [O/n for n in names]+[R/'src/level_tiles.s']
    for n in names[:3]:assert read(O/n)['passed']and read(O/n)['ROM_sha256']==PIN
    native=['native-current-landing-bub-full11-reachable-pit','native-current-landing-bob-full11-reachable-pit',
        'native-current-landing-bub-full11-castle-stairs','native-current-landing-bob-full11-castle-stairs',
        'native-current-landing-bob-full11-source-wall']
    for name in native:
        p=O/name;q=read(p/'ready.json');assert q['ROM_sha256']==PIN
        assert all(sha(k)==v for k,v in q['bindings'].items()),name
        paths += [p/n for n in['controller.lua','ready.json','run.py']]
    terminals=[];safe=[]
    for name,expected in[(native[0],False),(native[2],True),(native[3],False)]:
        p=O/name/'capture';binding=read(p/'binding.json');full=read(p/'full11.json');obs=read(p/'bub-observer.json')
        assert binding['ROM_sha256']==PIN and binding['ready_sha256']==sha(p.parent/'ready.json')
        assert full['passed']==expected and(binding['exit_code']==0)==expected
        assert full['initial_lives']==full['final_lives']==2 and obs['failures']==0
        if expected:assert full['full_stage']and full['world']==0 and full['level']==1 and full['engine']==8 and len(full['clears'])==7
        files=sorted(p.iterdir());assert all(f.is_file()and not f.is_symlink()for f in files)
        assert len(files)<=64 and sum(f.stat().st_size for f in files)<=128_000_000 and sum(f.suffix.lower()=='.png'for f in files)<=4
        paths += files;safe += files
        terminals.append(dict(path=p.relative_to(R).as_posix(),ROM_sha256=PIN,passed=expected,
            full_stage=bool(full['full_stage']),reason=full['why'],x=full['current_x'],y=full['current_y'],maximum_x=full['maximum_x'],
            completed_Main=obs['completed_Main'],physical_frames=obs['physical_frames'],checks=obs['checks'],failures=obs['failures'],
            lives=[full['initial_lives'],full['final_lives']],pops=obs['pops'],original_rides=obs['source_bubble_ride_restarts']))
    paths=list(dict.fromkeys(paths));assert all(p.is_file()for p in paths)
    assert len(paths)<128 and sum(p.stat().st_size for p in paths)<8_000_000
    before={p:sha(p)for p in paths};archive=O/'landing-fullstage-source-v44.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in paths:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(paths)
        for p,h in before.items():assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==h==sha(p)
    previous=O/'landing-current-supplement-v35.zip';assert sha(previous)=='41ca85f81278f25fe33349193e196134456abd1617006caa11826625805fb857'
    out=dict(passed=True,source_and_native_checkpoint=True,ROM_sha256=PIN,ROM_copied=False,installed_by_producer=False,
        Bub_full1_1_passed=True,Bob_full1_1_passed=False,Bob_v42_native_pending=True,helpers_added=False,
        scope='One direct-input v36+ supplement, sourceCPU+actualBubfullstage/v37negative/Bobv39rearmnegative. Pendingv42 capture deliberately excluded. Original18Blanding/nativebinary exact source remains durablev27; v29-v35 inputs remainv35. No nested archives/fullROMs or historical source-tree rehydration. Root owns actualDownloadsdelivery/release proof separately.',
        archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        previous_source_archive=previous.relative_to(R).as_posix(),previous_source_archive_SHA256=sha(previous),
        terminal_runs=terminals,files={p.relative_to(R).as_posix():dict(SHA256=h,bytes=p.stat().st_size)for p,h in before.items()},
        exact_capture_files_safe_to_remove_only_after_root_archive_bytecomparison=[p.relative_to(R).as_posix()for p in safe])
    receipt=O/'landing-fullstage-source-v44.json';assert not receipt.exists();receipt.write_text(json.dumps(out,indent=2)+'\n')
    stage=O/'landing-fullstage-commit-files-v44.txt';assert not stage.exists()
    stage.write_text('\n'.join(['tools/audit/'+n for n in sources]+[archive.relative_to(R).as_posix(),receipt.relative_to(R).as_posix(),stage.relative_to(R).as_posix()])+'\n')
    print(json.dumps(dict(passed=True,archive=str(archive),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,files=len(paths),terminal_runs=terminals)))


if __name__=='__main__':main()
