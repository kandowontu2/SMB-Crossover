"""Run unchanged Sophia regressions against the isolated friction C2b ROMs.

The normal runner's differential postchecks remain intact. Only its ROOT and
output-directory literals change in a retained private copy.
"""
from pathlib import Path
import concurrent.futures,difflib,hashlib,importlib.util,json,sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49o2-sophia-friction-c2b-native-h'
BUILD=ROOT/'build/verification/root49o2-sophia-friction-private-build-c2b'
CURRENT=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+150_000_000<50_000_000_000
    current=json.loads((CURRENT/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in current.items())
    built=json.loads((BUILD/'report.json').read_text())
    assert sha(BUILD/'report.json')=='21403475826c250ab8222e28ce108f53990eee82a2d01cc22e8cf130dd32cfd3'
    targets=[(row['mapper'],row['outputs'])for row in built['builds']]
    for _,outputs in targets:
        for p in outputs.values():assert sha(Path(p['path']))==p['sha256']
    fixtures={p.relative_to(ROOT).as_posix():sha(p)for p in (ROOT/'tests').rglob('*')if p.is_file()}
    fixtures['tools/run_mesen.py']=sha(ROOT/'tools/run_mesen.py')
    OUT.mkdir();native=OUT/'native-output';native.mkdir()
    original=(ROOT/'tools/run_mesen.py').read_text()
    marker="ROOT = Path(__file__).resolve().parents[1]"
    output_marker="    output = ROOT / 'build/verification'"
    assert original.count(marker)==original.count(output_marker)==1
    derived=original.replace(marker,'ROOT = Path('+repr(str(ROOT))+')')
    derived=derived.replace(output_marker,'    output = Path('+repr(str(native))+')')
    driver=OUT/'private-run-mesen.py';driver.write_text(derived)
    (OUT/'runner-path-only.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),derived.splitlines(True),fromfile='original-runner',tofile='private-output-runner')))
    spec=importlib.util.spec_from_file_location('private_sophia_native_runner',driver)
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    names=('sophia-homing-vector','sophia-homing-nearest','sophia-homing-targets',
           'sophia-homing-terrain','sophia-homing-lifetime','sophia-native-products',
           'sophia-independent-weapons','sophia-impact-sequence','sophia-missile-impact-art',
           'sophia-collision-equivalence','sophia-missile-collision-equivalence',
           'sophia-enemy-explosion-art','sophia-enemy-explosion','sophia-inventory-202',
           'sophia-energy-drops-202','sophia-attached-fire','sophia-cannon-upgrade-snapshot',
           'sophia-empty-candidates','sophia-late-input-candidates')
    report={'status':'running-private-friction-C2b-native-regressions','accepted_release':False,'goal_complete':False,
            'script_sha256':sha(Path(__file__)),'original_runner_sha256':fixtures['tools/run_mesen.py'],
            'private_runner_sha256':sha(driver),'target_build_report_sha256':sha(BUILD/'report.json'),
            'fixture_hashes_before':fixtures,'cases':[]}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def run(mapper,outputs,name):
        rom=Path(outputs['nes']['path']);script=ROOT/'tests'/(name+'.lua')
        code=runner.run(script,rom,timeout=150 if name=='sophia-native-products'else 90,
                        emulator_options=['--nes.ramPowerOnState=AllZeros',
                                          '--nes.randomizeCpuPpuAlignment=false',
                                          '--nes.randomizeMapperPowerOnState=false'])
        log=native/(rom.stem+'-'+name+'.log')
        return {'mapper':mapper,'test':name,'native_and_host_exit':code,'log_sha256':sha(log),
                'has_PASS': 'PASS 'in log.read_text(),'original_fixture_sha256':sha(script)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        futures=[pool.submit(run,mapper,outputs,name)for mapper,outputs in targets for name in names]
        for future in concurrent.futures.as_completed(futures):
            report['cases'].append(future.result());save()
    report['cases'].sort(key=lambda c:(c['mapper'],c['test']))
    assert all(sha(ROOT/n)==h for n,h in fixtures.items())
    assert all(sha(ROOT/n)==h for n,h in current.items())
    for _,outputs in targets:
        for p in outputs.values():assert sha(Path(p['path']))==p['sha256']
    failed=[c for c in report['cases']if c['native_and_host_exit']!=0 or not c['has_PASS']]
    report.update(status='FAIL_PRIVATE_NATIVE_REGRESSIONS'if failed else 'PASS_38_UNCHANGED_SOPHIA_NATIVE_AND_HOST_REGRESSIONS',
                  failures=failed,workspace_bytes=workspace_bytes(ROOT),
                  qualification='Seeded unchanged component fixtures. Includes original host differential postchecks and independent native product oracle. No ordinary playthrough, hardware or release acceptance claim.')
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json'),'failures':failed}))
    assert not failed

if __name__=='__main__':main()
