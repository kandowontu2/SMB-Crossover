"""Bind the existing passive whole-head observer to actual private D."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-head-axis-d'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    original=R/'tools/audit/capture_easy49_sophia_head_call_e.py'
    spec=importlib.util.spec_from_file_location('original_passive_head',original)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.D=D;m.main()
    (D/f'native-adapter-h-{sys.argv[1]}.json').write_text(json.dumps(dict(status='PREPARED_PASSIVE_D_HEAD_H',
        script_sha256=sha(__file__),observer_sha256=sha(original),mapper=sys.argv[1],
        retained_failed_G_preparer_sha256=sha(D/'prepare-native-e.py'),
        binding_sha256=sha(D/f'native-head-e-{sys.argv[1]}.json'),
        changed_settings=['D output/build directory only; original observer uses complete fixed input so its empty control function is ignored.']),indent=2)+'\n')


if __name__=='__main__':main()
