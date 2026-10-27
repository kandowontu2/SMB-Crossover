"""Strict postpack recipe: authentic missile pairs into reserved mouse-page gaps.

No atlas regeneration, recoloring, existing pair movement, or source-file writes.
Call plan() and explicitly save its two returned private asset overlays.
"""
from pathlib import Path
import hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda b:hashlib.sha256(b).hexdigest()

def plan(root,rom,overrides=None):
    root=Path(root);b=scoped_load(Path(rom));raw=b['raw'];base=16+128*8192
    art=address(b,'AV_ART_SAMUSSHOT7');assert art==44
    family=raw[location(b,'AvArtFamilies')+art]
    page=raw[location(b,'AvPhysicalBanks')+family]|1
    assert (family,page)==(6,215)
    ptr=raw[location(b,'AvArtRightLo')+art]+256*raw[location(b,'AvArtRightHi')+art]
    bank=raw[location(b,'AvArtBanks')+art];at=16+bank*8192+ptr%8192
    assert raw[at:at+9]==bytes([8,59,194,252,251,61,194,252,3])
    pairs=[raw[base+page*1024+(tile&62)*16:base+page*1024+(tile&62)*16+32]for tile in (59,61)]
    assert all(len(p)==32 and any(p)for p in pairs)
    names=['chr/mmc5/sprites_enemies.chr','chr/characters/packed-mmc5-expanded.chr']
    assets={n:(overrides or {}).get(n,(root/n).read_bytes())for n in names}
    enemies,packed=(assets[n]for n in names);misc=enemies[3072:4096]
    assert len(enemies)==4096 and len(packed)==247*1024
    assert packed[20*1024:21*1024]==misc
    assert raw[base+20*1024:base+21*1024]==misc
    assert misc[8*32:]==bytes(1024-8*32),'Only pairs6/7 may become nonzero'
    old=misc[6*32:8*32];wanted=b''.join(pairs)
    assert old in (bytes(64),wanted),'Reserved pairs already owned by different art'
    modified=bytearray(misc);modified[6*32:8*32]=wanted
    replacement=bytearray(packed);replacement[20*1024:21*1024]=modified
    out={names[0]:enemies[:3072]+bytes(modified),names[1]:bytes(replacement)}
    proof=dict(source_art=art,source_family=family,source_page=page,
      source_tiles=[59,61],destination_page=20,destination_pairs=[6,7],
      destination_tiles=[77,79],pair_sha256=[sha(p)for p in pairs],
      only_two_authenticated_pairs=True,mouse_pairs_0_to_5_exact=misc[:192]==modified[:192],
      changed_asset_bytes=sum(x!=y for x,y in zip(misc,modified)),
      idempotent=old==wanted,input_assets={n:sha(v)for n,v in assets.items()})
    return out,proof
