"""Preserve superseded route-search/capture evidence for five-agent QA space."""
from pathlib import Path
base=Path(__file__).with_name('archive_capture_headroom_ms.py').read_text()
old="('root-rygar-palette-av-fy-7-v0-mmc3','root-rygar-current-fl-av-fq-7-v0-mmc3')"
new="('root-bass-broad-ke-9-v0-mmc3','root-v34-mario-capture-a-0-v0-mmc3','root-bass-retime-gr-9-v0-mmc3','root-bass-bowser-he-9-v0-mmc3','root-bass-pipe-gz-9-v0-mmc3','root-bass-castle-hb-9-v0-mmc3','root-rygar-enemy-proof-dn-7-v0-mmc3','root-bass-pipe-gy-9-v0-mmc3')"
assert base.count(old)==1
base=base.replace(old,new).replace('workspace-headroom-ms','workspace-headroom-ne2')
exec(compile(base,__file__,'exec'))
