"""Extend the exact existing32B source-owned cycle capsule to valid variant8."""
import json
from pathlib import Path
import check_mini_mario_menu_1103_v15 as C
B,O,R=C.B,C.O,C.R


def main():
    old,new,q=C.load();raw=bytearray(new['raw']);at=B.location(old,'KmNextVariant')
    before=bytes(raw[at:at+32]);assert before[:7]==bytes.fromhex('ae0a73e0089002')
    assert before[16:24]==bytes([1,5,3,4,7,6,2,0])and before[24:]==bytes([234])*8
    source=R/'tools/audit/prepare_mario_tank_candidate_1101_v5.py'
    assert 'new[24:]=bytes([0xea])*8'in source.read_text()
    for relative,value,role in[(4,9,'KmNextVariant valid domain8→9; oldinvalid≥9 fallback4 unchanged'),(24,0,'Cycle[8]=0 in source-declared8B pad; old8entries untouched')]:
        pos=at+relative;q['patches'].append(dict(physical_PRG=(pos-16)//8192,CPU_half_open=[0xa000+(pos-16)%8192,0xa001+(pos-16)%8192],file_offset=pos,old_hex=bytes([raw[pos]]).hex(),new_hex=bytes([value]).hex(),role=role));raw[pos]=value
    for value in range(256):
        original=before[16+(value if value<8 else 4)]
        after=raw[at+16+(value if value<9 else 4)]
        assert after==(0 if value==8 else original)
    q.update(expected_memory_only_SHA256=B.V.sha(raw),cycle_256_domains_exact_except_new8=True,
        source_owned_cycle_capsule=dict(CPU=B.address(old,'KmNextVariant'),bytes=32,old_hex=before.hex(),new_hex=bytes(raw[at:at+32]).hex(),source=source.relative_to(R).as_posix()),
        bindings={p.relative_to(R).as_posix():B.sha(p)for p in[Path(__file__),Path(B.__file__),O/'proposal.json',source]})
    (O/'proposal-v16.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_written=False,expected_memory_only_SHA256=q['expected_memory_only_SHA256'],new_cycle8=0)))


if __name__=='__main__':main()
