"""Preserve four older Rygar packets using the existing bounded archive process."""
from pathlib import Path
base=Path(__file__).with_name('archive_capture_headroom_ms.py').read_text()
old="('root-rygar-palette-av-fy-7-v0-mmc3','root-rygar-current-fl-av-fq-7-v0-mmc3')"
new="('root-rygar-current-ht-7-v0-mmc3','root-rygar-weapon-gm-7-v0-mmc3','root-rygar-full-visible-fr-7-v0-mmc3','root-rygar-current-fl-proof-fp-7-v0-mmc3')"
assert base.count(old)==1
base=base.replace(old,new).replace('workspace-headroom-ms','workspace-headroom-na')
exec(compile(base,__file__,'exec'))
