"""Current-parent foreign Main and focused Samus/FF native DrawAll pairs."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import cf_bt_shared_foreign_main_v1 as FM
import ff_joint_native_flash_controls_1030_v3 as D
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address

OLD = R / 'build/bt-ready-menu-1031-v2/joint'
NEW = R / 'build/contra-force-p1-coherent-cart-v2/joint'
OUT = R / 'build/contra-force-p1-coherent-foreign-v1'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def focused_drawall(old, new):
    bases = [D.seed(b) for b in [old, new]]
    rows = []
    # No selected31 in this FOREIGN suite. BT invalid-cache remains an exact
    # ROM fallback pair; root owns its separate real ready-cache/native proof.
    for selected, freeze, offset in itertools.product([0, 2, 22, 33], [0, 1], [0, 64]):
        if freeze and selected != 2:
            continue
        pair, costs = [], []
        for b, base in zip([old, new], bases):
            m = D.P.duplicate(base)
            D.H.put(m, SelectedCharacter=selected, SmFreezeRenderState=freeze,
                    CurrentOAMOffset=offset, SpriteShuffleOffset=1)
            meta = D.enemy(m, 0, 12)
            m[address(b, 'ObjectMetasprite') + 1] = meta
            m.writes.clear()
            m.ram_writes.clear()
            c, minimum = D.invoke_drawall(m)
            pair.append(D.signature(m, c))
            costs.append(c.processorCycles)
        assert pair[0] == pair[1], ('Focused genuine foreign DrawAll', selected, freeze, offset)
        rows.append(dict(selected=selected, freeze=freeze, offset=offset,
                         parentCPU=costs[0], currentCPU=costs[1], delta=costs[1] - costs[0]))
    return dict(passed=True, cases=len(rows), rows=rows,
                AXYP_SP_application_ordered_writes_OAM_rawmaps_and_FFcache_exact=True,
                BT_invalid_cache_fallback_only=True)


def main():
    assert not OUT.exists()
    OUT.mkdir()
    result = dict(passed=False, source_CPU=True, native=False, admitted=False, checks={})
    try:
        stage = json.loads((NEW.parent / 'source-stage.json').read_text())
        for name, digest in stage['bindings'].items():
            assert sha(name) == digest, name
        # Existing legal47-identity/282-Main suite receives the actual current
        # BT source as oracle, not its historical pit-retold source baseline.
        FM.J, FM.P, FM.O = NEW, OLD, OUT / 'legacy-main'
        FM.main()
        result['checks']['established_47_identity_282_Main'] = json.loads((FM.O / 'controls.json').read_text())
        result['checks']['focused_native_Samus_FF_DrawAll'] = focused_drawall(qualified(OLD / 'candidate.nes'),
                                                                               qualified(NEW / 'candidate.nes'))
        result['passed'] = True
    except Exception as error:
        result.update(error=repr(error), traceback=traceback.format_exc())
        raise
    finally:
        files = [Path(__file__), Path(FM.__file__), Path(FM.U.__file__), Path(D.__file__), Path(D.P.__file__),
                 Path(D.H.__file__), OLD / 'candidate.nes', OLD / 'candidate.dbg',
                 NEW / 'candidate.nes', NEW / 'candidate.dbg', NEW.parent / 'source-stage.json']
        result['bindings'] = {str(p.resolve()): sha(p) for p in files}
        target = OUT / 'controls.json'
        target.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(dict(path=str(target), sha256=sha(target), passed=result['passed'], error=result.get('error'))))


if __name__ == '__main__':
    main()
