"""Retain two superseded lossless captures while making room for new-roster QA."""
from pathlib import Path

base = Path(__file__).with_name('archive_capture_headroom_ms.py').read_text()
old = "('root-rygar-palette-av-fy-7-v0-mmc3','root-rygar-current-fl-av-fq-7-v0-mmc3')"
new = "('root-bass-av-im-9-v0-mmc3','root-mario-av-if-0-v0-mmc3')"
assert base.count(old) == 1
base = base.replace(old, new).replace('workspace-headroom-ms', 'workspace-headroom-nd')
exec(compile(base, __file__, 'exec'))
