"""Same targeted four FF cold/lives and128-totalMain checks on combinedcart."""
from pathlib import Path
p=Path(__file__).with_name('ff_coherent62_cold_controls_v1.py');s=p.read_text()
s=s.replace('build/ff-coherent62-cold-controls-v1','build/ff-remap-palette-combined-controls-v1')
s=s.replace('build/functional-roster-coherent62-v4/joint','build/arthur-goku-smb2-palette-v1/joint')
s=s.replace('408acae2712c1d9bbbe34233f8261fcf27723907d37acf020e3f5314be3b8604','37210891ffbf79373bf3390d16ead891b0e8f43408603a07273f12297a36121a')
exec(compile(s,__file__,'exec'),globals())
