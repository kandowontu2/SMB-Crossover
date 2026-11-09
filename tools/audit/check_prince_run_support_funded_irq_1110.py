"""Qualify the cold-linked Prince support and pose decoder in the current image."""

import argparse
import json
from pathlib import Path

import check_prince_run_support_funding_1110 as F
from check_prince_player_pipeline_1102_v67 import terrain


Current,P,Support,R,N,I = F.Current,F.P,F.Support,F.R,F.N,F.I
FUNDED = R/'build/prince-run-support-funded-1110/proof.json'
FUNDED_PIN = 'f90f0b44f60edb8ef76e0f42535a3fad11ce420be378f7f8c5a38465d1d1284d'
Async = Support.V3.V.Async


def linked_route(seed,base,expected):
    e,m,labels = P.Q.first8(base,seed)
    left,right,top = Current.LEFT,Current.RIGHT,Current.TOP

    def pipe(x,y):
        if y>=208:
            return 0x54
        if not left<=x<right or y<top:
            return 0
        return (0x12 if y<top+16 else 0x14)+int(x>=left+16)

    terrain(m,pipe)
    checkpoints = expected['checkpoints']
    by_epoch = {row['epoch']:(name,row) for name,row in checkpoints.items()}
    observed = {}
    pad = 1
    for epoch in range(checkpoints['far_ground']['epoch']+1):
        now = Current.row(m,epoch)
        assert now['engine']==8 and now['lives']==2 and now['hp']==5
        if epoch in by_epoch:
            name,row = by_epoch[epoch]
            assert now==row,(name,now,row)
            observed[name] = now
            pad = {'release':0,'stand':8,'climb':1}.get(name,pad)
        if 'far_ground' in observed:
            break
        m.controller_pad = pad
        N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        e['run'](m,'GameLoop',labels)
    assert observed==checkpoints
    return dict(actual_linked_cold=True,emulated_state_writes_after_explicit_terrain_fixture=False,
                checkpoints=observed,auth_epoch='Original current GameLoop and native collision')


def vectors(seed,prior,layout):
    support_start,support_end = layout['support_half_open']
    checks = []
    for covered in (False,True):
        m = Support.fixture(seed,mode=1,frame=1,covered=covered)
        N.put(m,NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30)
        baseline = Support.result(Support.fixture(prior,mode=1,frame=1,covered=covered),Support.TERRAIN)

        def call(q):
            out = Support.result(q,Support.TERRAIN)
            assert out['X']==(baseline['X'] if covered else 731)
            assert out['action']==(baseline['action'] if covered else 1)
            return out['ret']

        checks.append(Async.stress('actual D297 exposed cap' if not covered else 'actual D297 covered cap',m,call,
                                   [(2,support_start,support_end),(3,0xb310,0xb369)]))

    art = Current.read(P.V.O/'source-art.json')['poses']
    for compact in (False,True):
        def is_compact(frame):
            i = 0x800+2*frame
            start = int.from_bytes(seed.ram[2][i:i+2],'little')&0x3fff
            header = seed.ram[2][0x800+start]
            return bool(seed.ram[2][0x800+start+2+((header>>4)&3)]&0x80)

        candidates = (p for p in art if p['source_frame'] in layout['hybrid_frames']
                      and is_compact(p['source_frame'])==compact)
        pose = max(candidates,key=lambda p:len(p['parts_8x16']))
        m = N.fork(seed)
        m.raw_page(2,2)
        N.put(m,CurrentBankC=2,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=0,
              NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,GameEngineSubroutine=8,OperMode=1)
        m.ram[2][0x617],m.ram[2][0x615] = pose['source_frame'],pose['source_facing']
        I.invoke(m,3,0xbd06,(83,71,109,0x61))
        I.invoke(m,3,0xc383,(83,71,109,0x61))
        check = Async.stress('mixed compact draw' if compact else 'mixed wide draw',m,
                             lambda q:I.invoke(q,3,0xbbc1,(83,71,109,0x61))['regs'],
                             [(2,*layout['decoder_half_open'])])
        checks.append(dict(check,source_frame=pose['source_frame']))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    path = out/'irq-linked.json'
    assert not path.exists() and P.sha(FUNDED.read_bytes())==FUNDED_PIN
    proof,prototype = Current.read(FUNDED),Current.read(F.POSITIVE)
    assert proof['passed'] and prototype['passed'] and proof['parent_SHA256']==Current.BASE_PIN
    base,_,_ = Current.current()
    parent = Current.BASE.read_bytes()
    assert P.sha(parent)==Current.BASE_PIN
    raw = Current.apply(parent,proof['patches'])
    assert P.sha(raw)==proof['expected_memory_only_SHA256']
    candidate = dict(base,raw=raw)
    seed,cold = P.Q.C.C.cold(candidate,38)
    cookie = bytes.fromhex(proof['Prince_cookie'])
    assert all(bytes(seed.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    route = linked_route(seed,candidate,prototype['replay'])
    print('Exact cold-linked GameLoop route reached the far ground.',flush=True)

    failures = 0
    for bank in (2,3):
        for byte in range(16):
            m = N.fork(seed)
            m.ram[bank][0x1fe0+byte] ^= 1
            previous = tuple(map(bytes,m.ram))
            call = I.invoke(m,193,0xb08c,(83,71,109,0x21))
            assert not call['regs'][3]&1 and tuple(map(bytes,m.ram))==previous
            failures += 1
    foreign = []
    for owner in (37,39,41):
        a,b = [P.Q.C.C.cold(image,owner) for image in (base,candidate)]
        assert a[1]['regs']==b[1]['regs'] and tuple(map(bytes,a[0].ram))==tuple(map(bytes,b[0].ram)),owner
        foreign.append(owner)
    prior,_ = P.Q.C.C.cold(base,38)
    irqs = vectors(seed,prior,proof['layout'])
    refs = (Path(__file__),FUNDED,F.POSITIVE,Path(Async.__file__),Current.BASE,Current.SHAFT)
    receipt = dict(passed=True,ROM_written=False,Mesen_run=False,expected_memory_only_SHA256=P.sha(raw),
                   parent_SHA256=Current.BASE_PIN,live_CPU=cold['CPU'],cold_linked_route=route,
                   bad_header_bytes_rejected=failures,foreign_cold_parity=foreign,interrupts=irqs,
                   bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(irqs),flush=True)


if __name__=='__main__':
    main()
