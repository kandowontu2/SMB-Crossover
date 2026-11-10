"""Preserve the frozen v1 source while rebinding prototype menu-state bits.

CrossoverContinue bits5/6 are the two new declared profile bits; bit7 remains
continue, bit0 remains the deferred edge, and low campaign bits are untouched.
The rejected ExRAM FmGroups bit6 is a live palette-dirty flag.
"""
from pathlib import Path
import json
import build_mike_alternate_prototypes_1110 as B


def main():
    old=B.read(B.OUT/'linked.json')
    assert old['expected_memory_only_SHA256']=='8cd8afc1e6dca21b34e2213b41e518a2ad3b8ee5b885198a99b784d2f3f94770'
    parent=B.source_bundle()['raw']
    new=json.loads(json.dumps(old))
    changed=[]
    for row in new['patches']:
        blob=bytearray.fromhex(row['new_hex'])
        for i in range(len(blob)-2):
            if blob[i] in (0xad,0x8d) and blob[i+1:i+3]==bytes.fromhex('e85f'):
                at=row['file_offset']+i
                assert ((at-16)//8192,0xa000+(at-16)%8192) in {
                    (96,0xa1cf),(76,0xbf65),(76,0xbf04),
                    (97,0xa307),(97,0xa38c),(97,0xa3be)},(at,hex(0xa000+(at-16)%8192))
                blob[i+1:i+3]=bytes.fromhex('0b73')
                changed.append(at)
        row['new_hex']=blob.hex()
    assert len(changed)==6,changed
    pose=next(row for row in new['patches'] if row['file_offset']==B.off(96,0xa276))
    blob=bytes.fromhex(pose['new_hex'])
    needle=bytes.fromhex('c902d0058a186907aa')
    assert blob.count(needle)==1 and blob[-1]==0xea
    # The original left-facing CMP leaves carry1. The compact14-entry table
    # needs an index addition, whose carry must be restored before the native
    # physical-CHR tail. Consume one of the explicitly funded eleven NOPs.
    blob=blob.replace(needle,bytes.fromhex('c902d0068a186907aa38'))[:-1]
    assert len(blob)==85
    pose['new_hex']=blob.hex()
    raw=bytearray(parent)
    for row in new['patches']:
        at=row['file_offset'];before,after=(bytes.fromhex(row[k])for k in ('old_hex','new_hex'))
        assert raw[at:at+len(before)]==before
        raw[at:at+len(after)]=after
    new.update(expected_memory_only_SHA256=B.digest(raw),selector=dict(address=0x730b,mask=0x60,
        values={'Mike':0,'Jay':0x20,'Steve':0x40},existing_bits_preserved='bit7 continue; bit0 deferred Select; campaign low bits'),
        version=2,previous_private_SHA256=old['expected_memory_only_SHA256'],
        source_transform='Six typed prototype LDA/STA operands5FE8→730B, plus explicit left-facing carry restoration in the original85-byte set-pose envelope. No original global-state reader is modified.',
        rebound_instruction_offsets=changed)
    new['source_bindings'][Path(__file__).relative_to(B.R).as_posix()]=B.digest(Path(__file__).read_bytes())
    (B.OUT/'linked-v2.json').write_text(json.dumps(new,indent=2)+'\n')
    print('Rebound prototype selector',new['expected_memory_only_SHA256'],changed,flush=True)


if __name__=='__main__':main()
