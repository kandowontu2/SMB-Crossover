"""One direct-input v29-v34 supplement; only explicitly terminal captures."""
import argparse,hashlib,json,zipfile
from pathlib import Path

R=Path(__file__).resolve().parents[2];O=R/'build/bub-menu-candidate-1102-v2'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capture',action='append',required=True,choices=[
        'native-landing-bub-stair-diagnostic','native-landing-bub-full11-stepback',
        'native-current-landing-bub-full11-final-pit','native-current-landing-bob-full11-final-pit'])
    args=ap.parse_args();captures=list(dict.fromkeys(args.capture))
    assert sha(O/'combined-current-landing.nes')==PIN
    sources=['check_bub_stair_wall_contact_1102_v29.py','check_bub_actual_stair_route_1102_v30.py',
        'prepare_bub_stair_stepback_native_1102_v31.py','compose_bub_current_landing_1102_v32.py',
        'check_bub_final_pit_ingress_1102_v33.py','prepare_bub_final_pit_native_1102_v34.py',Path(__file__).name]
    paths=[R/'tools/audit'/name for name in sources]
    names=['stair-wall-contact-v29-CPU.json','actual-stair-route-v30-CPU.json',
        'landing-current-v32-check.json','final-pit-ingress-v33-CPU.json','combined-current-landing.json']
    paths += [O/name for name in names]
    checkpoint=R/'docs/qa/checkpoints/2026-11-02/bub-landing-v27/receipt.json';paths.append(checkpoint)
    for name in['native-landing-bub-full11-stepback','native-landing-bob-full11-stepback',
                 'native-current-landing-bub-full11-final-pit','native-current-landing-bob-full11-final-pit']:
        p=O/name
        paths += [p/n for n in['controller.lua','ready.json','run.py']]
        ready=json.loads((p/'ready.json').read_text())
        assert all(sha(Path(k))==v for k,v in ready['bindings'].items()),name
    terminal=[];safe=[]
    for name in captures:
        p=O/name/'capture';binding=json.loads((p/'binding.json').read_text())
        assert isinstance(binding['exit_code'],int),name
        files=sorted(p.iterdir());assert all(f.is_file()and not f.is_symlink()for f in files)
        assert len(files)<=64 and sum(f.stat().st_size for f in files)<=128_000_000
        assert sum(f.suffix.lower()=='.png'for f in files)<=4
        full=p/'full11.json';result=json.loads(full.read_text())if full.is_file()else{}
        terminal.append(dict(path=p.relative_to(R).as_posix(),ROM_sha256=binding['ROM_sha256'],
            exit_code=binding['exit_code'],passed=result.get('passed',False),reason=result.get('why'),
            x=result.get('current_x'),y=result.get('current_y'),maximum_x=result.get('maximum_x')))
        paths+=files;safe+=files
    paths=list(dict.fromkeys(paths));assert all(p.is_file()for p in paths)
    assert len(paths)<128 and sum(p.stat().st_size for p in paths)<8_000_000
    before={p:sha(p)for p in paths};archive=O/'landing-current-supplement-v35.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in paths:z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(paths)
        for p,h in before.items():assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==h==sha(p)
    receipt=O/'landing-current-supplement-v35.json';assert not receipt.exists()
    out=dict(passed=True,source_and_native_checkpoint=True,installed=False,ROM_sha256=PIN,
        archive=archive.relative_to(R).as_posix(),archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,
        previous_source_checkpoint=checkpoint.relative_to(R).as_posix(),previous_source_checkpoint_SHA256=sha(checkpoint),
        scope='Direct source/CPU/current9cf composition inputs plus explicit terminal native runs. Previousv27 source remains one read-only checkpoint; no recursive archive extraction, ROM copy or cleanup by producer. Actualv31 missing edge predicate is not inferred from sparse CSV.',
        terminal_runs=terminal,files={p.relative_to(R).as_posix():dict(SHA256=h,bytes=p.stat().st_size)for p,h in before.items()},
        exact_capture_files_safe_to_remove_only_after_root_archive_bytecomparison=[p.relative_to(R).as_posix()for p in safe])
    receipt.write_text(json.dumps(out,indent=2)+'\n')
    stage=O/'landing-current-commit-files-v35.txt';assert not stage.exists()
    stage.write_text('\n'.join([('tools/audit/'+s)for s in sources]+[archive.relative_to(R).as_posix(),receipt.relative_to(R).as_posix(),stage.relative_to(R).as_posix()])+'\n')
    print(json.dumps(dict(passed=True,archive=str(archive),archive_SHA256=sha(archive),files=len(paths),archive_bytes=archive.stat().st_size,terminal_runs=terminal)))


if __name__=='__main__':main()
