"""Retain seven historical Rygar proof packets outside the bounded workspace."""
from pathlib import Path

base = Path(__file__).with_name('archive_capture_headroom_ms.py').read_text()
old = "('root-rygar-palette-av-fy-7-v0-mmc3','root-rygar-current-fl-av-fq-7-v0-mmc3')"
new = "('root-rygar-current-scene-df-7-v0-mmc3','root-rygar-prefix-proof-dk-7-v0-mmc3','root-rygar-finish-fo-7-v0-mmc3','root-rygar-water-eq-7-v0-mmc3','root-rygar-water-tail-fk-7-v0-mmc3','root-rygar-world2-ef-7-v0-mmc3','root-rygar-castle-tail-dv-7-v0-mmc3')"
assert base.count(old) == 1
base = base.replace(old, new).replace('workspace-headroom-ms', 'workspace-headroom-nb')
exec(compile(base, __file__, 'exec'))
