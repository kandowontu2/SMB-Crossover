"""Explicit parity domain and the native/source four-state induction."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

import compose_dkjr_platform_footer_current_1116 as C
import check_dkjr_carry_camera_route_1116 as R
import dkjr_footer_source_input_1116 as Input

N=R.N
H=lambda value:sha256(value).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--public',type=Path,required=True)
    ap.add_argument('--input-kind',required=True,choices=('exact-6a3','bt91dc-reference-only'))
    args=ap.parse_args();public,binding=Input.normalize(args.public.read_bytes(),kind=args.input_kind)
    parent,_=C.Camera.proposal(public);raw,composition=C.proposal(parent)
    _,m=R.cold(raw)
    assert N.get(m,'Player_State')==0
    whole,labels=C.Camera.Plan.source_inputs()
    first=whole.index(' lda $c06b\n cmp #1\n beq DkMainGround',whole.index('DkNativeMain:'))
    end=whole.index('DkMainNo:',first)
    fragment=whole[first:end]
    assert fragment.count(' sta Player_State')==1
    actual=bytes(m.ram[2][0x165e:0x16a7])
    pattern=bytes.fromhex('ad6bc0c901')
    assert actual.count(pattern)==1
    pc=0xd65e+actual.index(pattern)
    assembled=C.Plan.Funding.H.T.assemble(C.Camera.Plan.numeric(whole)+'.segment "STATE"\n'+fragment,dict(STATE=(pc,64)))
    code=assembled['images']['STATE']
    assert actual[pc-0xd65e:pc-0xd65e+len(code)]==code
    values=set()
    for phase in range(256):
        q=R.Cold.H.L.clone(m);q.ram[2][0x6b]=phase
        # Declared straight-line post-phase suffix fixture. No Main, scene or
        # ordinary-gameplay state is seeded by this check.
        R.Cold.H.call(q,pc)
        expected=0 if phase==1 else 3 if phase==2 else 2
        assert N.get(q,'Player_State')==expected
        values.add(expected)
    paths=('player.s','collision.s','cheats_four.s','expanded.s','roster.s',
        'guest_injury.s','roster_weapons.s','ryu_platform.s')
    inventory=[]
    for name in paths:
        path=C.R/'src'/name;data=path.read_bytes();lines=data.decode().splitlines()
        for index,line in enumerate(lines):
            code_line=line.split(';',1)[0]
            match=re.search(r'\b(sta|stx|sty|inc|dec|asl|lsr|rol|ror)\s+Player_State\b',code_line,re.I)
            if not match:continue
            op=match[1].lower();assert op in('sta','sty','stx'),(name,index+1,line)
            reg={'sta':'lda','stx':'ldx','sty':'ldy'}[op]
            context='\n'.join(s.split(';',1)[0]for s in lines[max(0,index-8):index])
            loads=re.findall(r'\b'+reg+r'\s+#(?:\$([0-9a-fA-F]+)|([0-9]+))\b',context)
            assert loads,(name,index+1,'No bounded native state source')
            value=int(loads[-1][0],16)if loads[-1][0]else int(loads[-1][1])
            assert 0<=value<=3,(name,index+1,value)
            inventory.append(dict(file='src/'+name,line=index+1,opcode=op,
                nearest_constant=value,source_SHA256=H(data)))
    player=(C.R/'src/player.s').read_text()
    assert '.word OnGroundStateSub\n.word JumpSwimSub\n.word FallingSub\n.word ClimbingSub' in player
    collision=(C.R/'src/collision.s').read_text()
    bg=collision[collision.index('PlayerBGCollision:'):collision.index('ChkOnScr:',collision.index('PlayerBGCollision:'))]
    assert re.search(r'lda #\$01.*?ldy SwimmingFlag.*?bne SetPSte',bg,re.S)
    assert re.search(r'SetFallS:.*?lda #\$02.*?SetPSte:.*?sta Player_State',bg,re.S)
    assert 'jmp DkNativeMain' in whole[whole.index('DkServices:'):whole.index('.export DkjrInitialize')]
    assert not re.search(r'\b(?:inc|dec|stx|sty) Player_State\b',whole)
    assert whole.count(' sta Player_State\n')==1
    report=dict(passed=True,composition=composition,input_binding=binding,
        actual_cold_native_state=0,actual_compiled_projection=dict(PC=pc,bytes=len(code),SHA256=H(code),
            all256_source_values_checked=True,outputs=sorted(values)),
        selected40_service0_is_normalized_D65E_Main=True,
        native_state_contract=[0,1,2,3],native_core_direct_writer_source_inventory=inventory,
        native_BG_variable_A_preserves_input_domain_or_uses1_or2=True,
        invalid_manual_bytes=dict(even4_through254='admitted when all other footer predicates hold',
            odd5_through255='rejected by parity',all_invalid_rejection_claim=False),
        induction='Native player initialization writes0. Selected40 movement service0 projects every returned source phase into0/2/3. Native movement/action dispatch has four entries; core collision/entry/death/vine and shared jump/cheat writes preserve0..3. Other character workers require their typed owner and are not valid Selected40 ingress. This is the engine caller contract, not byte-hardening of manually poisoned state.',
        scope='Actual current compiled DK projection and cold, plus retained native-core/shared source writer census. No claim of exhaustive arbitrary foreign kernel/raw-address poisoning rejection.',
        output_files=0,native_claim=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_STATE_DOMAIN '+encoded,flush=True);print('DKJR_FOOTER_STATE_DOMAIN_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
