"""Bind Jay's hot transport to source-funded PRG94 and the current Mike tail."""
from pathlib import Path
import json

import check_jay_silius_stream_carrier_1110 as S

C,H,W,N = S.C,S.H,S.W,S.N
HOT_SOURCE=H.ROOT/'tools/reference/jay_silius_bank94_hot_1110.s'


def proposal(raw,donor):
    base,trial,program,linked,runtime,stage,cookie,decoder,extra,sizes=S.proposal(raw,donor)
    gate=H.assemble('PrivateUpdate=$a785\n'+HOT_SOURCE.read_text().replace('CookieBytes',','.join(map(str,cookie))),
                    {'HOT94':(0xb25f,161)})
    assert gate['used']['HOT94']==124
    route=(S.Funding.SOURCE.read_text().split('JayMovementRoute:',1)[0]+'''JayMovementRoute:
 lda #$5f
 sta $016c
 lda #$b2
 sta $016d
 lda #$de
 jmp $015a
''')
    pose=H.assemble(route,{'MIKE_POSE':(0xa276,85)})
    assert pose['used']['MIKE_POSE']==85 and pose['symbols']['JayMovementRoute']==0xa2bc
    raw_next=bytearray(trial['raw'])
    start=C.offset(94,0xb25f)
    assert raw[start:start+161]==bytes([255])*161
    raw_next[start:start+161]=gate['images']['HOT94'].ljust(161,b'\xea')
    start=C.offset(96,0xa276)
    raw_next[start:start+85]=pose['images']['MIKE_POSE']
    raw_next[C.offset(96,0xa53d):C.offset(96,0xa540)]=bytes.fromhex('4cbca2')
    # The two proposed storage pages are the only CHR delta. Sonic333 and
    # every DK page keep their current source preimages.
    changed={i for i,(a,b) in enumerate(zip(raw,raw_next)) if a!=b and i>=C.CHR}
    allowed={i for page in C.PAGES for i in range(C.CHR+1024*page,C.CHR+1024*(page+1))}
    assert changed <= allowed
    return base,dict(base,raw=bytes(raw_next)),program,linked,runtime,cookie,gate,extra,sizes


def opening(trial,program,linked,runtime,cookie,gate,extra,donor):
    m=C.menu(trial,1,program)
    pads=[0]*8+[1]*28+[128]*14+[0]*36
    reports=[]
    snapshots=[]
    seen=set()
    cuts={'NMI':0,'IRQ':0,'mapper_split':0}
    imports=0
    private_calls=0
    last_live=None
    for epoch in range(700):
        active=tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)
        if active and len(reports)==len(pads):
            break
        m.controller_pad=pads[len(reports)] if active else 0

        def observe(memory,cpu):
            nonlocal imports,private_calls,last_live
            assert cpu.pc!=program['symbols']['JayHot'], 'Synthetic hot dispatch remains reachable'
            if cpu.pc==0xb000 and memory.rawtags[1]==3:
                C.bridge(memory,cpu,donor,linked)
                imports+=1
            if cpu.pc==extra['symbols']['PrivateUpdate'] and memory.rawtags[1]==3:
                private_calls+=1
            if cpu.pc==extra['symbols']['PublishPosition'] and memory.rawtags[1]==3:
                snapshots.append((memory[linked['ram'][0x10]]*256+memory[linked['ram'][0x11]],
                                  memory[linked['ram'][0x12]]*256+memory[linked['ram'][0x13]]))
                if len(reports)==len(pads)-1:
                    last_live=C.Vector.clone(memory)
            used=memory.rawtags[1]==222 and any(i['pc']==cpu.pc for i in gate['instructions'])
            used|=memory.rawtags[1]==3 and 0xa785<=cpu.pc<0xa8c0
            key=cpu.pc,tuple(memory.rawtags),cpu.p&4
            if active and used and key not in seen:
                seen.add(key)
                for kind in('NMI','IRQ'):
                    q,d=C.Vector.clone(memory,cpu)
                    maps=tuple(q.rawtags)
                    before=tuple(map(bytes,q.ram)),bytes(q[3:11]),bytes(q[0x15a:0x17b]),bytes(q[0x101+cpu.sp:0x200])
                    C.Vector.isr(q,d,kind)
                    assert before==(tuple(map(bytes,q.ram)),bytes(q[3:11]),bytes(q[0x15a:0x17b]),bytes(q[0x101+cpu.sp:0x200]))
                    if maps!=tuple(q.rawtags):
                        ins=bytes(q[cpu.pc:cpu.pc+3])
                        assert ins in(bytes.fromhex('8d1651'),bytes.fromhex('8e1651'))
                        assert q.rawtags[2]==q[0x7da1] and all(maps[i]==q.rawtags[i]for i in(0,1,3))
                        cuts['mapper_split']+=1
                    cuts[kind]+=1

        C.Game.frame(m,observe)
        if active:
            reports.append(tuple(N.get(m,n)for n in('Player_X_Position','Player_Y_Position','NumberofLives')))
    assert len(reports)==86 and private_calls==imports==86
    assert reports[-1]==(78,176,2) and snapshots[-1]==(1252,3072)
    assert min(y for _,y in snapshots)==2232
    assert bytes(m.ram[3][:len(runtime)])==runtime and C.Common.headers(m)==(cookie,)*2
    assert last_live is not None
    for bank in (2,3):
        for index in range(16):
            q=C.Vector.clone(last_live)
            q.ram[bank][0x1fe0+index]^=1
            prior=tuple(map(bytes,q.ram))
            legacy=[]

            def reject(memory,cpu):
                assert not(memory.rawtags[1]==3 and 0xa000<=cpu.pc<0xc000)
                if cpu.pc==0xa2cb and memory.rawtags[1]==224:
                    legacy.append(1)

            C.Vector.call(q,'JnMovementDispatch',observe=reject)
            assert legacy==[1] and tuple(map(bytes,q.ram))==prior
    return dict(updates=86,private_calls=private_calls,actual_weapon_imports=imports,
                terminal_native=reports[-1],terminal_donor_16ths=snapshots[-1],held_apex_16ths=840,
                genuine_hot_vectors=cuts,all32_real_gate_header_rejections=True)


def main():
    donor=C.actual_donor()
    raw=H.ROM.read_bytes()
    base,trial,program,linked,runtime,cookie,gate,extra,sizes=proposal(raw,donor)
    families=C.family_parity(base,trial,program,linked,donor)
    actual=opening(trial,program,linked,runtime,cookie,gate,extra,donor)
    print(json.dumps(dict(passed=True,ROM_SHA256=S.PIN,ROM_written=False,Mesen=False,build_files=0,
        stream=sizes,real_PRG_hot_bytes=124,source_funded_pose_route_bytes=15,
        image_SHA256=C.digest(trial['raw']),gate_source_SHA256=C.digest(HOT_SOURCE.read_bytes()),
        exact_Mike_Steve=families,native_Main=actual,unfunded_cold_and_descriptor_bytes=161,
        no_allocation_or_native_delivery_granted=True),sort_keys=True),flush=True)


if __name__=='__main__':
    main()
