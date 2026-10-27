"""Expanded-only fixed HUD assets. Ordinary enemies/packed assets never change."""
from pathlib import Path
import hashlib,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
VARIANT='samus-fixed-hud-enemies-mmc5-expanded.chr'
PAIR_HASHES=['f732c0bb57ee9a1ad5a2dbc05b58857197d2f33edd0726e42f450db4781a5ac0','48a3176832ae6de66ed04c848dcf28c62aa113d045b4478e819db9d7246a9171']
sha=lambda b:hashlib.sha256(b).hexdigest()

def source_pairs(root):
    """Authenticate the actual art44 record and its source family6 page bytes."""
    root=Path(root);inc=(root/'src/remaining_art.inc').read_text()
    record=inc[inc.index('AvArt44Right:'):inc.index('AvArt44Left:')]
    assert record.splitlines()==['AvArt44Right:',' .byte 8',' .byte MetaspriteVramOffset{$3a}, {SPRITE_BANK_4}, $c2, -4, -5',' .byte MetaspriteVramOffset{$3c}, {SPRITE_BANK_4}, $c2, -4, 3']
    ids=(root/'src/remaining_art_ids.inc').read_text();assert re.search(r'^AV_ART_SAMUSSHOT7=44$',ids,re.M)
    families=inc[inc.index('AvArtFamilies:'):].splitlines()[1]
    assert int(families.split('.byte',1)[1].split(',')[44])==6
    art=(root/'chr/characters/remaining-weapons-mmc5.chr').read_bytes()
    # Remaining families0/1 alias Samus/special; family6 is source block4,
    # upper1KB. Its two unflipped32B source pairs are58/60.
    offset=(6-2)*2048+1024+58*16;pairs=art[offset:offset+64]
    assert len(pairs)==64 and[sha(pairs[:32]),sha(pairs[32:])]==PAIR_HASHES
    return pairs

def make_variant(ordinary,pairs):
    assert len(ordinary)==4096 and len(pairs)==64
    assert ordinary[3072+192:]==bytes(4096-3072-192),'Ordinary gap must remain originalzero'
    variant=bytearray(ordinary);variant[3072+192:3072+256]=pairs
    return bytes(variant)

def expanded_only(packed,ordinary,variant,pairs):
    """Pure conditional postpack: one expanded page; never dedup/rewrite ordinary."""
    assert len(packed)==247*1024
    assert variant==make_variant(ordinary,pairs),'Variant must be exact authenticated64B overlay'
    page=packed[20*1024:21*1024];original=ordinary[3072:4096]
    assert page in (original,variant[3072:4096]),'Expanded page is unexpectedly owned'
    assert page[:192]==original[:192]and page[256:]==bytes(768)
    result=bytearray(packed);result[20*1024:21*1024]=variant[3072:4096]
    return bytes(result)

def apply_expanded_assets(folder):
    """Narrow optional pack_chr hook, after its two ordinary outputs finish."""
    folder=Path(folder);variant=folder/VARIANT
    if not variant.exists():return False
    root=folder.parents[1];pairs=source_pairs(root)
    ordinary=(root/'chr/mmc5/sprites_enemies.chr').read_bytes()
    target=folder/'packed-mmc5-expanded.chr'
    target.write_bytes(expanded_only(target.read_bytes(),ordinary,variant.read_bytes(),pairs))
    return True

def plan(root,rom):
    root=Path(root);b=scoped_load(Path(rom));raw=b['raw'];base=16+128*8192;pairs=source_pairs(root)
    assert address(b,'AV_ART_SAMUSSHOT7')==44
    family=raw[location(b,'AvArtFamilies')+44];page=raw[location(b,'AvPhysicalBanks')+family]|1
    assert(family,page)==(6,215)
    assert raw[location(b,'AvArt44Right'):location(b,'AvArt44Right')+9]==bytes([8,59,194,252,251,61,194,252,3])
    assert raw[base+215*1024+928:base+215*1024+992]==pairs
    ordinary=(root/'chr/mmc5/sprites_enemies.chr').read_bytes();variant=make_variant(ordinary,pairs)
    packed=(root/'chr/characters/packed-mmc5-expanded.chr').read_bytes()
    assert raw[base:base+len(packed)]==packed
    changed=expanded_only(packed,ordinary,variant,pairs)
    assert expanded_only(changed,ordinary,variant,pairs)==changed
    return {'chr/characters/'+VARIANT:variant,'chr/characters/packed-mmc5-expanded.chr':changed},dict(source_art44=True,source_family=6,source_page=215,source_pair_sha256=PAIR_HASHES,destination_page=20,destination_pairs=[6,7],mouse_pairs0_to5_exact=True,original_ordinary_gap_zero=True,ordinary_asset_sha256=sha(ordinary),ordinary_asset_unchanged=True,expanded_changed_bytes=sum(x!=y for x,y in zip(packed,changed)),idempotent=True)
