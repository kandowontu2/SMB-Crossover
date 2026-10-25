"""Add read-only six-slot enemy telemetry to the existing failed-prefix observer."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
FIELDS = ('Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position',
          'Enemy_PageLoc', 'Enemy_Y_Position')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / 'tools/audit/observe_failed_route_oy.py'
    spec = importlib.util.spec_from_file_location('failed_prefix_oy', base)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = module.OBSERVER
    before = "f:write('frame,cycle,'..table.concat(FAILED_OBS_FIELDS,',')..'\\n')"
    extra = [name + '_' + str(i) for i in range(6) for name in FIELDS]
    after = "f:write('frame,cycle,'..table.concat(FAILED_OBS_FIELDS,',')..','.." + json.dumps(','.join(extra)) + "..'\\n')"
    assert source.count(before) == 1
    source = source.replace(before, after)
    before = "   for _,name in ipairs(FAILED_OBS_FIELDS)do row[#row+1]=r(name)end"
    after = before + '\n   for slot=0,5 do\n'
    for name in FIELDS:
        after += "    row[#row+1]=emu.read(assert(L['" + name + "'])+slot,emu.memType.nesDebug)\n"
    after += '   end'
    assert source.count(before) == 1
    module.OBSERVER = source.replace(before, after)
    args = sys.argv[1:]
    out = Path(args[args.index('--output') + 1])
    assert '--fields' in args and all(name in args[args.index('--fields') + 1:] for name in FIELDS)
    module.main()
    proof = dict(passed=True, base_driver_sha256=sha(base), wrapper_sha256=sha(Path(__file__)),
                 extended_observer_sha256=sha(out / 'observer.lua'),
                 original_proof_sha256=sha(out / 'proof.json'), memory_writes=False,
                 scope='Exact original failed-prefix replay with completed-loop scalar fields and six full read-only enemy slots. This is diagnosis; the original discovery remains failed.')
    (out / 'slot-proof.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__':
    main()
