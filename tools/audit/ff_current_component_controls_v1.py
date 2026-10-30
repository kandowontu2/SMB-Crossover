"""Run the complete frozen FF leaf assertions with the genuinely current host."""
from pathlib import Path
import json
import sys
import prepare_ff_current_component_v1 as C
from prepare_ff_current_component_v2 import qualified

O = C.R/'build/final-fantasy-current-component-v2/cpu-controls-v1'
LINKED = O.parent/'linked'
SOURCE = C.R/'tools/prepare_final_fantasy_controls_v1.py'


if __name__ == '__main__':
    assert not O.exists()
    proof = json.loads((O.parent/'build-proof.json').read_text())
    assert proof['passed'] and proof['original_component_CORE_ART_CHR_byte_exact']
    for path, digest in proof['bindings'].items():
        assert C.sha(path) == digest, path
    O.mkdir()
    source = SOURCE.read_text()
    old = "assert set(rom[16+62*8192+0xa00:16+63*8192])=={255},'Pinned CORE tail'"
    new = "assert set(rom[16+62*8192+0xa00:16+62*8192+0x1690])=={255},'Current FF CORE lease before Kamikaze'"
    assert source.count(old) == 1
    source = source.replace(old, new)
    old_outputs = "outputs=[bind(OUT/p)for p in ['component.bin','art.bin','component.lbl','component.dbg']]"
    new_outputs = "outputs=[bind(LINKED/p)for p in ['candidate.nes','candidate.lbl','candidate.dbg']]"
    assert source.count(old_outputs) == 1
    source = source.replace(old_outputs, new_outputs)
    C.write(O/'actual-controls-source.py', source)
    (O/'assets.json').write_bytes((C.OLD/'assets.json').read_bytes())
    namespace = dict(__name__='frozen_ff_leaf_assertions_current_host', __file__=str(O/'actual-controls-source.py'))
    exec(compile(source, str(O/'actual-controls-source.py'), 'exec'), namespace)
    current = qualified(LINKED/'candidate.nes')
    symbols = {name: int(value['val'], 0) for name, value in current['syms'].items()}
    raw = current['raw']
    code = raw[16+62*8192+0xa00:16+62*8192+0xa00+3211]
    art = raw[16+93*8192+0x1000:16+93*8192+0x1000+3410]
    namespace.update(OUT=O, HOST=C.P/'candidate', LINKED=LINKED,
                     EXPECTED={ext:C.sha((C.P/'candidate').with_suffix('.'+ext)) for ext in ['nes','dbg','lbl']},
                     build=lambda: (code, art, symbols))
    namespace['main']()
    assert (O/'candidate.nes').read_bytes() == (LINKED/'candidate.nes').read_bytes()
    result = json.loads((O/'controls.json').read_text())
    assert result['passed'] and not result['native'] and not result['host_integration']
    result.update(genuinely_linked_candidate_sha256=C.sha(LINKED/'candidate.nes'),
                  exact_qualified_linked_ROM_reconstruction=True,
                  all_original_semantic_assertions_retained=True,
                  fixture_changes=['Bind current genuine host and FF linked imports instead of rebuilding old absolute-address component.',
                                   'Pin only source-owned FF CORE AA00..<B690; following Kamikaze code is an existing different owner.',
                                   'Output provenance points to genuine linked candidate, not the old standalone component debug.'],
                  limits=['Source leaves and actual native draw/IRQ code only; no full host Main, NMI/raster, live terrain/combat integration or native route.'])
    bindings = dict(proof['bindings'])
    for path in [Path(__file__).resolve(), SOURCE, O.parent/'build-proof.json',
                 O/'actual-controls-source.py', O/'assets.json', O/'candidate.nes']:
        bindings[str(path)] = C.sha(path)
    result['bindings'] = bindings
    C.write(O/'controls.json', json.dumps(result, indent=2)+'\n')
    for path, digest in bindings.items():
        assert C.sha(path) == digest, path
    print(json.dumps(dict(passed=True, ROM_sha256=result['genuinely_linked_candidate_sha256'],
                         source_life_cases=result['source_life_cases'],
                         render_cases=result['rendered_entry_facing_shadow_cases'],
                         native=False, admitted=False)))
