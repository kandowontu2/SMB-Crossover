"""Root-only fresh I native runs; preserve all earlier F component negatives."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'build/verification/ryu49o2-head-components-i'
OUT = ROOT / 'build/verification/root49o2-head-i-native-a'
P = ROOT / 'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode = True
    assert not OUT.exists()
    assert sha(PACKET/'freeze.json') == '30c5760403dad228affa9c7779b845c346ded5aadf3a8bbb2e567bd8408a908d'
    assert sha(PACKET/'bindings-host-report.json') == '17923b94a7b528b2d2ff2831fb69d9a1f9bb4e7ab31e53640b647bb9c021d5e7'
    freeze = json.loads((PACKET/'freeze.json').read_text())
    for n, r in freeze['files'].items():
        assert sha(PACKET/n) == r['sha256'], n
    for n, h in freeze['dependencies'].items():
        assert sha(ROOT/n) == h, n
    assert sha(P/'manifest.json') == 'be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    current = json.loads((P/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n) == h for n,h in current.items())
    sys.path.insert(0, str(ROOT/'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 20_000_000 + 225_000_000 < 50_000_000_000
    parser = ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance = json.loads((parser/'provenance.json').read_text())
    for r in [provenance['wheel']] + provenance['extracted']:
        assert sha(Path(r['path'])) == r['sha256']
    sys.path.insert(0, str(parser/'runtime'))
    from lupa.lua54 import LuaRuntime
    parse = LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    ok, error = parse((PACKET/'component.lua').read_text(), 'I-component')
    assert ok, error
    cases = []
    for name, r in json.loads((PACKET/'bindings-host-report.json').read_text())['bindings'].items():
        binding = ROOT/name
        assert sha(binding) == r['sha256']
        b = json.loads(binding.read_text())
        script = ROOT/r['argv'][2]
        rom = ROOT/r['argv'][3]
        assert sha(script) == r['wrapper_sha256']
        assert sha(rom) == b['rom_sha256']
        assert sha(rom.with_suffix('.dbg')) == b['dbg_sha256']
        assert sha(rom.with_suffix('.lbl')) == b['lbl_sha256']
        ok, error = parse(script.read_text(), str(script))
        assert ok, error
        output = binding.parent/'native-output'
        assert output.is_dir() and not any(output.iterdir())
        cases.append(dict(mapper=r['mapper'], role=r['role'], binding=str(binding), binding_sha256=sha(binding),
                          script=str(script), script_sha256=sha(script), rom=str(rom), rom_sha256=sha(rom)))
    OUT.mkdir()
    report = dict(status='RUNNING_FRESH_I_COMPONENTS', cases=cases, script_sha256=sha(Path(__file__)),
                  current_P_manifest_sha256=sha(P/'manifest.json'), workspace_before=used,
                  own_future_reserve=20_000_000, other_future_reserve=225_000_000,
                  accepted_release=False, goal_complete=False)
    def save():
        (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    sys.path.insert(0, str(ROOT/'tools'))
    import run_mesen
    for c in cases:
        code = run_mesen.run(Path(c['script']), Path(c['rom']), timeout=300,
                             emulator_options=['--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
                                               '--nes.randomizeMapperPowerOnState=false'])
        output = Path(c['binding']).parent/'native-output'
        log = ROOT/'build/verification'/(Path(c['rom']).stem+'-'+Path(c['script']).stem+'.log')
        c.update(native_exit=code, log_sha256=sha(log))
        if (output/'result.json').exists():
            c.update(result=json.loads((output/'result.json').read_text()), result_sha256=sha(output/'result.json'))
        save()
    for n,r in freeze['files'].items():
        assert sha(PACKET/n) == r['sha256']
    assert all(sha(ROOT/n) == h for n,h in current.items())
    report.update(status='COMPLETE_FRESH_I_NATIVE_ALL_NEGATIVES_RETAINED_STRICT_REVIEW_PENDING',
                  workspace_after=workspace_bytes(ROOT),
                  qualification='Seeded actual components; fresh release setup only. O2 source diagnostics remain controls. Native reexecution, full end effects, full source lifecycle and ordinary route proof are separate.')
    save()
    print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'),
                          native_exits=[(c['mapper'],c['role'],c['native_exit']) for c in cases])))

if __name__ == '__main__':
    main()
