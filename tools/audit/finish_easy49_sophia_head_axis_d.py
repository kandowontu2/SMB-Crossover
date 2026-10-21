"""Complete C's unchanged96 fixtures against the actual current-C parent."""
from pathlib import Path
import hashlib
import json

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-sophia-head-axis-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parent=R/'tools/audit/check_easy49_sophia_head_axis_c.py'
    text=parent.read_text()
    a="    ns['main']()"
    assert text.count(a)==1
    text=text.replace(a,"    assert json.loads((D/'compiled-axis-c.json').read_text())['status']=='PASS_COMPILED_SOURCE_NORMAL_FLAT_CORNER_AXES_BOTH_MAPPERS'")
    a="    spec=importlib.util.spec_from_file_location('original_terrain_96',original)\n    mod=importlib.util.module_from_spec(spec)\n    spec.loader.exec_module(mod)"
    assert text.count(a)==1
    replacement='''    import types
    mod=types.ModuleType('original_terrain_96_current_parent')
    mod.__file__=str(original)
    original_text=original.read_text()
    old="V/'root49-sophia-source-body-hs/source/build'"
    assert original_text.count(old)==1
    original_text=original_text.replace(old,"V/'root49-combined-working-c/source/build'")
    original_text=original_text.replace("'compiled-ig.json'","'compiled-original96-d.json'")
    exec(compile(original_text,str(original),'exec'),mod.__dict__)'''
    text=text.replace(a,replacement)
    text=text.replace("sha(D/'compiled-ig.json')","sha(D/'compiled-original96-d.json')")
    ns={'__file__':__file__,'__name__':'source_head_axis_d_completion'}
    exec(compile(text,str(parent),'exec'),ns)
    ns['main']()
    (D/'host-parent-negative-d.json').write_text(json.dumps(dict(
        status='RETAINED_HOST_METADATA_PARENT_NEGATIVE_CORRECTED',
        original96_negative_sha256=sha(D/'compiled-ig.json'),
        parent_checker_sha256=sha(parent),completion_script_sha256=sha(__file__),
        reason='The original IG checker compared MegaManVineAnchor to the older HS build. Current C changed that resident span before this patch. Compare all unchanged96 assertions to the actual current-C parent, retaining all original assertions and the metadata equality gate.',
        unchanged_runtime_source=True,passing96=sha(D/'compiled-original96-d.json'),
        complete_head_span=sha(D/'complete-head-span-c.json')),indent=2)+'\n')


if __name__=='__main__':main()
