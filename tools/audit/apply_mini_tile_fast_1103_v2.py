"""Pinned, composable Mini query transformation and exact data companion.

Does not own or alter the caller's source file. Root/fire integration supplies
its current source plus ORIGINAL256 native attribute bytes.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import optimize_mini_tile_1103_v1 as V
digest=lambda data:hashlib.sha256(data).hexdigest()
TILE_PIN='6d9dc58c2ee06244d61bff3540bf8bbaf8e0322dda8111ffa4f393f28649e888'
FILTER_PIN='34f78cf384fa84f524437c145f8eab4b30121b17f1c48515f1d61c6d63c352af'
ATTR_PIN='02ca3678ee8114a3eb336262b9472ee9929237a31f39d5b6886886dc252b8470'
ENCODED_PIN='aec04d8e6465b5ba04b09af9c49beb7b49e9471f84127e6845de15f0c331f73a'


def transform(source,original_attributes):
    """Return successor full source, replacement D300..D400 immutable bytes."""
    a=source.index('MiniNativeTile:\n');z=source.index('MiniNativeTileEnd:\n',a)+len('MiniNativeTileEnd:\n')
    assert digest(source[a:z].encode())==TILE_PIN,'Unqualified query source'
    a=source.index('MiniHostFilterSolid:');z=source.index('MiniHostPickup:',a)
    assert digest(source[a:z].encode())==FILTER_PIN,'Unqualified second attribute consumer'
    assert digest(original_attributes)==ATTR_PIN,'Supply original, not already-encoded attributes'
    table=V.encoded_attributes(original_attributes);assert digest(table)==ENCODED_PIN
    return V.successor(source,encoded=True),table


def main():
    V.G.preflight(private_root=V.O,reserved_bytes=18000,reserved_files=1,fresh=True)
    assert not (V.O/'source-stage.json').exists()
    original=R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin'
    source,table=transform(V.BASE.read_text(),original.read_bytes())
    assert source==(V.O/'tile-encoded.s').read_text()
    assert table==(V.O/'encoded-attributes.bin').read_bytes()
    proof=json.loads((V.O/'tile-proof.json').read_text());encoded=proof['results'][1]
    assert encoded['passed'] and encoded['cases']==221952 and encoded['kernel_bytes']==5111
    assert digest((V.O/'tile-encoded.bin').read_bytes())==encoded['kernel_SHA256']
    # Original metatile authority is present literally in the immutable Mini
    # page967, D300 quarter, of this retained source parent.
    parent=R/'build/mini-zero-visible-direct/mini-empty-draw.nes';raw=parent.read_bytes()
    assert digest(raw)=='a09a538e550b912e0d4e131c4328902e26aaa94844448c6eedf4a5dd1be317ad'
    at=16+128*8192+967*1024+768;assert raw[at:at+256]==original.read_bytes()
    files=[Path(__file__),Path(V.__file__),V.BASE,V.BIN,V.LABELS,original,parent,
        V.O/'tile-proof.json',V.O/'tile-encoded.s',V.O/'tile-encoded.bin',V.O/'tile-encoded.lbl',V.O/'encoded-attributes.bin']
    q=dict(status='SOURCE_CPU_QUALIFIED_READY_FOR_ROOT_COMPOSITION',ROM_written=False,Mesen_run=False,
        safe_without_new_mutable_instruction_operands=True,source_kernel_bytes=[5119,5111],recovered_code_bytes=8,
        original_query_source_SHA256=TILE_PIN,unchanged_filter_source_SHA256=FILTER_PIN,
        original_attributes_SHA256=ATTR_PIN,encoded_attributes_SHA256=ENCODED_PIN,
        metadata_write_only_half_open=[0xd300,0xd400],new_RAM_bytes=0,new_carriers=0,
        proof_cases=221952,solid_cycles_saved=28,ordinary_empty_cycles_saved=23,out_of_range_cycles_saved=27,
        function='apply_mini_tile_fast_1103_v2.transform(current_source, original_attributes256)',
        source_ownership='Only query block changes; all fire/CHR/selector/publicvector source outside it stays caller-owned and exact.',
        remaining='Root/fire relink combined kernel, update metadata quarter/cookie and actual current native/interrupt qualification. No native performance/frame-budget claim.',
        bindings={p.relative_to(R).as_posix():digest(p.read_bytes()) for p in files})
    (V.O/'source-stage.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))


if __name__=='__main__':main()
