"""Bind moved helper callers and compare the real scene loader's public state."""
import copy
import json
import re
import propose_wwf_generic_helper_1102_v1 as P
import check_hogan_current_bounded_v1 as M

O = P.R / 'build/wwf-helper-stable-1102-v2'

def main():
    q = json.loads((O/'proposal.json').read_text())
    b = P.scoped_load(P.BASE)
    assert P.sha(P.BASE) == q['base_ROM_SHA256']
    z = copy.deepcopy(b); raw = bytearray(b['raw'])
    begin = 16+26*8192+0x800
    old = (O/'original.bin').read_bytes(); new = (O/'proposed.bin').read_bytes()
    assert raw[begin:begin+len(old)] == old
    raw[begin:begin+len(new)] = new
    routes = []
    pattern = re.compile(b'\xa9(.)\x8d\x6c\x01\xa9(.)\x8d\x6d\x01\xa9\x9a',re.S)
    moved = {v['old']:(n,v['new']) for n,v in q['relocations'].items()}
    for match in pattern.finditer(b['raw']):
        target = match[1][0]+256*match[2][0]
        if target not in moved: continue
        at = match.start(); name, replacement = moved[target]
        assert name == 'HpLoadArea' and at == 1034317
        assert b['raw'][at+12:at+15] == bytes.fromhex('205a01')
        raw[at+1] = replacement & 255; raw[at+6] = replacement >> 8
        routes.append(dict(name=name,offset=at,old=target,new=replacement,type='farcall26'))
    assert len(routes) == 1
    positions = [213027,213064,213142,213225,213313,213395,213543]
    target = q['original_labels']['HpCurrentArea']
    found = [at for at in range(16+26*8192,16+27*8192-2)
        if not begin <= at < begin+len(old) and b['raw'][at:at+3] == bytes([32,target&255,target>>8])]
    assert [at+1 for at in found] == positions
    for at in found:
        replacement = q['labels']['HpCurrentArea']
        raw[at+1:at+3] = replacement.to_bytes(2,'little')
        routes.append(dict(name='HpCurrentArea',offset=at,old=target,new=replacement,type='bank26-near-JSR'))
    # The previously missed Rogue Dawn pause tail must stay byte-identical.
    assert raw[521244:521259] == b['raw'][521244:521259]
    assert q['labels']['HpPauseCold'] == q['original_labels']['HpPauseCold']
    z['raw'] = bytes(raw)
    for name,pc in q['labels'].items():
        if name in z['syms']: z['syms'][name]['val'] = hex(pc)
    seed = M.fresh(b); count = 0
    for flags in range(256):
        for owner in [0,29,34]:
            rows = []
            for bundle in [b,z]:
                m = M.fork(seed); m.bundle = bundle
                M.put(m,SelectedCharacter=owner,WorldNumber=0,LevelNumber=0,AreaPointer=37,
                    AreaType=1,AreaAddrsLOffset=5,FamilyMainCommit=1,NmiDisable=1,
                    GamePauseStatus=0,TimerControl=1,VRAM_Buffer1_Offset=0)
                for i in range(8): m[3+i]=(flags*13+i*37+17)&255
                result=M.invoke(m,'HpLoadArea',a=(flags*17+85)&255,x=flags^177,y=flags^66,p=flags)
                rows.append((tuple(result[k] for k in ['A','X','Y','P','minimum_SP']),bytes(m[3:11]),tuple(m.rawtags)))
            assert rows[0] == rows[1], (flags,owner)
            count += 1
    receipt=dict(passed=True,ROM_written=False,native=False,installed=False,base_ROM_SHA256=P.PIN,
        actual_HpLoadArea_AXYP_stack_scratch_maps_cases=count,canonical_and_same_bank_routes=routes,
        late_entries_and_Rogue_pause_tail_preserved=True,
        remaining='Complete split-pointer/source caller census, ISR cuts and actual assisted crossing before ROM admission.')
    (O/'caller-load-CPU.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__ == '__main__':
    main()
