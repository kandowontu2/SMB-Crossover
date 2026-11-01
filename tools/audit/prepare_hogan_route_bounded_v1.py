"""Prepare the longer route without changing the qualified frontend observer."""
from pathlib import Path
import hashlib
import json
import sys

import prepare_hogan_native_bounded_v1 as frontend


def main():
    assert '--frontend-only' not in sys.argv
    frontend.main()
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    controller = output / 'controller.lua'
    original = controller.read_text(encoding='utf-8')
    text = original
    for old, new in [('updates>=500', 'updates>=700'),
                     ('500 Main route bound:', '700 Main route bound:'),
                     ('frame>=1800', 'frame>=2400'),
                     ('1800 physical frame bound', '2400 physical frame bound')]:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    controller.write_text(text, encoding='utf-8', newline='\n')
    ready_path = output / 'ready.json'
    ready = json.loads(ready_path.read_text())
    ready['route_bounds'] = dict(Main=700, physical_frames=2400, wall_seconds=90)
    ready['observer_transform'] = dict(
        before_sha256=hashlib.sha256(original.encode()).hexdigest(),
        purpose='Allow the607Main source-tested route within a finite native bound.')
    ready['bindings'][str(controller)] = frontend.sha(controller)
    ready['bindings'][str(Path(__file__).resolve())] = frontend.sha(__file__)
    ready_path.write_text(json.dumps(ready, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
