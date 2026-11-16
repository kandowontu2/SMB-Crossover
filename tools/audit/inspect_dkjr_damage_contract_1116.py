"""Read-only actuala3fb injury versus original landing/off-bottom writers."""
from hashlib import sha256
import json
import re

import compose_dkjr_footer_bt91dc_current_1116 as C
import check_dkjr_stair_query_contract_1116 as Query

H=lambda value:sha256(value).hexdigest()


def contract(raw):
    assert H(raw)==C.CANDIDATE
    whole,_=C.Camera.Plan.source_inputs();_,labels=Query.Source.closure(raw)
    body=C.Camera.payload(raw);rows=[]
    for begin,end in(('DkNativeInjuryStatus','DkNativeDeath'),('D_d405','D_d412'),
        ('D_d631','D_d650'),('D_d60d','D_d612'),('D_da22','D_da48')):
        fragment=whole[whole.index(begin+':'):whole.index(end+':')]
        defined=set(re.findall(r'^(\w+):',fragment,re.M))
        prefix=C.Camera.Plan.numeric(whole)+''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
        lo,hi=labels[begin],labels[end]
        linked=C.Footer.Plan.Funding.H.T.assemble(prefix+'.segment "CHECK"\n'+C.Camera.Plan.Source.expand_branches(fragment),dict(CHECK=(lo,hi-lo)))
        data=linked['images']['CHECK'];at=Query.Source.H.T.offset(lo)
        assert body[at:at+len(data)]==data
        rows.append(dict(first=begin,end_exclusive=end,PC=lo,bytes=len(data),SHA256=H(data),hex=data.hex()))
    services={}
    for index,name in((5,'DkNativeInjury'),(6,'DkNativeInjuryStatus'),(7,'DkNativeDeathStart')):
        code=bytes((0x4c,labels[name]&255,labels[name]>>8));at=index*3
        assert body[at:at+3]==code
        services[index]=dict(name=name,service_PC=0xa000+at,target_PC=labels[name],preimage=code.hex())
    writers={}
    for name,meaning in(('D_d407','Explicit original Damage entered by admitted native injury/deathstart'),
        ('D_da31','Original landing decision: phase1 if safe, phase5 if sourceY-origin>=limit'),
        ('D_d64d','Original fall with no support: sourceY>=216, independent of fall limit'),
        ('D_d60f','Original jump off-bottom: sourceY>=216')):
        pc=labels[name];at=Query.Source.H.T.offset(pc);assert body[at:at+3]==bytes.fromhex('8d6bc0')
        writers[name]=dict(PC=pc,WRAM_bank=3,preimage8=body[at:at+8].hex(),meaning=meaning)
    return dict(passed=True,actual_image_SHA256=H(raw),CPU_executed=False,services=services,
        byte_exact_source_fragments=rows,phase_writers=writers,
        injury_contract='BD93 is service5. Source hit-active C068!=0 or phase5 absorbs the call. Otherwise BD9F checks ready C8FE==2, unwinds native pause, then enters original Damage; handled return Cset prevents native shrink/recoil/death replacement.',
        original_landing_contract='DA34 returns unsafe only if sourceY>=origin and unsigned sourceY-origin>=C07B. DA22 calls it before original DAA5 landing snap. Unsafe writes5; safe snaps contacted top-17 and writes1.',
        off_bottom_contract='Fall support is queried first. If absent, sourceY>=D8(216) sets5 directly. C07B is not the cause of that off-bottom branch.',
        classification_limit='BD93 admission plus actual first A2DA writer supports an external native injury path; an A8DD or A406 writer without that admission instead identifies original landing damage or off-bottom fall. Entry alone does not identify enemy versus hazardous terrain or explain prior support loss.',
        observed_pipe5_failure_not_yet_classified=True,new_game_code_bytes=0,outputs=0)


if __name__=='__main__':
    raw,_=C.proposal(C.BT.ROM.read_bytes());q=contract(raw)
    encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('DKJR_DAMAGE_CONTRACT '+encoded,flush=True);print('DKJR_DAMAGE_CONTRACT_SHA256 '+H(encoded.encode()),flush=True)
