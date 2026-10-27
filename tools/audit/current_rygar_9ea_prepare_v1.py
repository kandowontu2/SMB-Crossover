"""Fresh accepted9ea Rygar preparations via the immutable6be source preparer.

Only the loaded preparer's EXPECTED identity changes. It executes its whole
actual CPU campaigns against the explicitly supplied9ea ROM. No native run.
"""
from pathlib import Path
import contextlib
import hashlib
import importlib.util
import io
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
OLD = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
NEW = '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
SOURCE = '63789904a5e617967fa4d0e7a126444e7e0a71ce8cf2c47a01e5806d2a44bc66'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
bind = lambda p: dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))


def main():
    original = ROOT/'tools/audit/current_rygar_powerups_prepare_v1.py'
    fixture = ROOT/'tools/audit/current_rygar_powerups_v1.lua'
    assert sha(original) == '6988f2a5d7371b6d2340e248e6fbb1e7722778110c6a061045e7eabae2a6f512'
    assert sha(fixture) == '14ccdcfd388e3fdf65697d5d0d4dee3d1c26daeeec192522462007c759e1e5a8'
    assert '--rom' in sys.argv and '--mode' in sys.argv and '--output' in sys.argv
    target = Path(sys.argv[sys.argv.index('--rom')+1]).resolve()
    assert target == (ROOT/'build/bill_early_cache.nes').resolve()
    output = Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    mode = sys.argv[sys.argv.index('--mode')+1]
    assert mode in ['easy','hard'] and not output.exists()
    parent = ROOT/'build/samus_fixed_hud_current4a.nes'
    assert sha(parent) == OLD and sha(target) == NEW
    assert sha(ROOT/'src/remaining_weapons.s') == SOURCE
    old_ready = ROOT/f'build/current-6be-rygar-{mode}-items-v1/prepared-not-run.json'
    old = json.loads(old_ready.read_text())
    assert old['status'] == 'PREPARED_DO_NOT_RUN' and not old['native_run']
    assert not (old_ready.parent/'native').exists(), 'Keep old6be profile unrun'
    for item in old['bindings']:
        path = Path(item['path'])
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    spec = importlib.util.spec_from_file_location('rygar_immutable_preparer',original)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    a,b = parent.read_bytes(),target.read_bytes()
    assert len(a) == len(b) == 2097168
    diffs = [i for i,(x,y) in enumerate(zip(a,b)) if x != y]
    assert len(diffs) == 43 and {(i-16)//8192 for i in diffs} == {6}
    assert a[:16] == b[:16] and a[16+128*8192:] == b[16+128*8192:]
    before,after = m.scoped_load(parent),m.scoped_load(target)
    spans=[]
    for name in ['GameLoop','HpProcessFireballsBridge','ProcFireball_Bubble',
                 'ExpandedWeapons','ExpandedMovement','ExpandedDrawShots',
                 'ExpandedWeaponPointer','MegaManWeapons','MarioSourcePowerupCollision',
                 'GuestBeginPowerup','GuestPowerupUpdate','InventorySupported',
                 'NonMaskableInterrupt','IrqScrollSplit','OAMandReadJoypad','PostDmaMaskEnable']:
        x,y = m.address(before,name),m.address(after,name)
        n = int(before['syms'][name].get('size','0'),0)
        assert x == y and n == int(after['syms'][name].get('size','0'),0)
        p,q = m.location(before,name),m.location(after,name)
        bank = (p-16)//8192
        assert p == q and bank != 6
        if n:
            assert a[p:p+n] == b[q:q+n]
        else:
            # These are genuine labels inside a larger owner, not empty code.
            lo=16+bank*8192;assert a[lo:lo+8192] == b[lo:lo+8192]
        spans.append(dict(symbol=name,PC=x,bank=bank,declared_size=n,
                          comparison='whole symbol' if n else 'whole enclosing unchanged physical bank'))
    tables=[]
    for name,index,count in [('ExpandedWeapons::DiskReach',0,3),('InvItemCount',7,1),
                             ('InvSelectable',112,16),('InvInitialAmmo',112,16),('InvMaxAmmo',112,16)]:
        p,q = m.location(before,name)+index,m.location(after,name)+index
        assert p == q and a[p:p+count] == b[q:q+count]
        tables.append(dict(symbol=name,index=index,count=count,bytes=list(b[q:q+count])))
    m.EXPECTED = NEW
    with contextlib.redirect_stdout(io.StringIO()):
        m.main()  # Fresh8-case/668-GameLoop campaign on actual9ea, not copied controls.
    ready_path=output/'prepared-not-run.json';ready=json.loads(ready_path.read_text())
    old_cfg=json.loads((old_ready.parent/'config.json').read_text())
    cfg=json.loads((output/'config.json').read_text())
    assert {k for k in cfg if cfg[k] != old_cfg[k]} == {'ROM_sha256'}
    assert cfg['ROM_sha256'] == ready['ROM_sha256'] == NEW
    assert (output/'source-controls.json').read_bytes() == (old_ready.parent/'source-controls.json').read_bytes()
    source=json.loads((output/'source-controls.json').read_text())
    assert source['passed'] and source['GameLoop_calls'] == 668 and len(source['cases']) == 8
    proof=output/'retarget-proof.json'
    proof.write_text(json.dumps(dict(passed=True,source_only=True,native_run=False,
        parent_ROM_sha256=OLD,ROM_sha256=NEW,accepted_ROOT_source_sha256=SOURCE,
        changed_ROM_bytes=43,changed_banks=[6],diff_file_offsets=diffs,header_CHR_exact=True,
        unchanged_compiled_owners=spans,unchanged_tables=tables,
        old6be_ready=bind(old_ready),old6be_remains_unrun=True,
        fixture_byte_exact=True,fixture_sha256=sha(fixture),
        only_loaded_preparer_setting_changed='EXPECTED=9ea; explicit --rom bill_early_cache.nes',
        all_other_config_fields_exact=True,fresh_CPU_campaign_execution=True,
        fresh_CPU_campaign_ROM_sha256=NEW,fresh_GameLoop_calls=668,
        fresh_controls=bind(output/'source-controls.json'),
        fresh_controls_byte_equal_old_is_deterministic_output_not_reuse=True),indent=2)+'\n',newline='\n')
    extra=[Path(__file__),old_ready,proof,ROOT/'src/remaining_weapons.s']
    extra += [Path(item['path']) for item in old['bindings']]
    seen={x['path'] for x in ready['bindings']}
    for path in extra:
        item=bind(path)
        if item['path'] not in seen:
            ready['bindings'].append(item);seen.add(item['path'])
    ready['source_retarget']='Fresh actual accepted9ea source campaigns; old6be preparations remain unrun and immutable.'
    ready['unchanged_controller_mechanics_hardware_plan']=True
    ready_path.write_text(json.dumps(ready,indent=2)+'\n',newline='\n')
    for item in ready['bindings']:
        path=Path(item['path'])
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    print(json.dumps(dict(status='PREPARED_DO_NOT_RUN',output=str(output),
        ready_sha256=sha(ready_path),bindings=len(ready['bindings']),
        retarget_proof_sha256=sha(proof),fresh_GameLoop_calls=668,native_run=False)))


if __name__=='__main__':
    main()
