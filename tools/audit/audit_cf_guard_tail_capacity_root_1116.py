"""Source-declared PRG69 tail inspection; no allocation, image or CPU mount."""
from hashlib import sha256
import json
from pathlib import Path
import re

import compose_battletoads_mature8_1116 as BT

H=lambda value:sha256(value).hexdigest()
CFG=BT.R/'build/contra-force-world-roles-1031-v2/joint/candidate.cfg'
CFG_SHA='06b92a8954d94957aa80bc830a2bfac5b84e1a25b642ce9958010f1df966888c'


def inspect(actual):
    assert H(actual)==BT.CANDIDATE
    reference=BT.inverse(actual)
    assert H(reference)==BT.PIN
    assert H(CFG.read_bytes())==CFG_SHA
    text=CFG.read_text();before,segments=text.split('SEGMENTS',1)
    names=['X5_NEW_45','CF_GUARD_MEM','CF_RETIRE_MEM','CF_SCENE_RETIRE_MEM','CF_GUARD_POST']
    intervals=[]
    for name in names:
        line=next(s.strip()for s in before.splitlines()if s.strip().startswith(name+':'))
        fields=dict(re.findall(r'(start|size|bank)=\$([0-9a-fA-F]+)',line))
        lo,size,bank=(int(fields[k],16)for k in('start','size','bank'))
        assert bank==69
        intervals.append(dict(name=name,CPU_half_open=[lo,lo+size],bytes=size,declaration=line))
    assert [q['CPU_half_open']for q in intervals]==[[0xa000,0xbf47],[0xbf47,0xbfbd],
        [0xbfbd,0xbfe1],[0xbfe1,0xbff2],[0xbff2,0xc000]]
    assert text.count('CF_GUARD_POST')==1 and 'load=CF_GUARD_POST'not in segments
    at=16+69*8192;bank=actual[at:at+8192];prg=actual[16:1048592]
    assert bank==reference[at:at+8192]
    assert H(bank[0x1f47:])=='cd0041177c211e64f57a1669930108020c5f7b8759905087934f2c9858d82475'
    assert bank[0x1ff2:]==bytes([255])*14
    same=[];tuples=[];setup=[]
    for target in range(0xbff2,0xc000):
        word=target.to_bytes(2,'little')
        for op in(0x20,0x4c,0x6c):
            pos=0
            while(pos:=bank.find(bytes([op])+word,pos))>=0:
                same.append(dict(target=target,file=at+pos,opcode=op));pos+=1
        pos=0;pattern=word+bytes([0xc5])
        while(pos:=prg.find(pattern,pos))>=0:
            tuples.append(dict(target=target,file=16+pos,physical_PRG=pos//8192));pos+=1
        pattern=bytes([0xa9,word[0],0x8d,0x6c,1,0xa9,word[1],0x8d,0x6d,1,0xa9,0xc5])
        if pattern in prg:setup.append(dict(target=target,file=16+prg.index(pattern)))
    return dict(actual_input_SHA256=H(actual),reference_SHA256=H(reference),source_cfg_SHA256=CFG_SHA,
        complete_PRG69_unchanged_by_BT=True,PRG69_SHA256=H(bank),source_memory_intervals=intervals,
        tail_source_memory_is_unloaded=True,tail_file_half_open=[at+0x1ff2,at+8192],tail_bytes=14,
        same_bank_literal_transfers=same,global_standard_bank_tuples=tuples,global_standard_far_setups=setup,
        scope='Exact linker MEMORY fill interval with no assigned load segment, unchanged current guard185 preimage and conservative ingress census. Nonliteral consumers still require source/producer closure before any game lease.',
        no_allocation_granted=True,no_game_bytes_changed=True,CPU_executed=False,ROM_composed=False,outputs=0)


if __name__=='__main__':
    q=inspect(BT.ROM.read_bytes());encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('CF_TAIL_SOURCE '+encoded,flush=True)
    print('CF_TAIL_SOURCE_SHA256 '+H(encoded.encode()),flush=True)
