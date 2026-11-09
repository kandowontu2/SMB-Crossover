"""Qualify saved native primary alignment with the original donor on both sides."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile

import check_prince_post_pit_original_align_1110 as D
from check_prince_player_pipeline_1102_v67 import terrain


W, R, Route, Original = D.Writer,D.R,D.Route,D.Original
Pair, N, I = W.Pair,W.N,W.Pair.I
P = Pair.Second.First.Pit.P
V8 = D.ROOT/'retreat/native/capture'
WRITER = D.ROOT/'writer.json'
DONOR = D.ROOT/'donor/donor-align.json'
ASM = R/'tools/reference/prince_d6c0_primary_align_1110.s'
TEST_ADDRESS = 0xc491
ENTRY = 0xa5d9
FIRST, SECOND = 0xa9b3,0xaa43
ORIGIN = 1280


def donor(snapshot, local_x, face, alternate, primary, back, filled):
    c = Original.machine()
    m = c.memory
    m.switch(5)
    state = bytearray.fromhex(snapshot['ram'])
    state[0x60f:0x611] = local_x.to_bytes(2,'little')
    state[0x615],state[0x4fe] = face,alternate
    state[0x6cd:0x6cf] = (0x300).to_bytes(2,'little')
    state[0x300:0x31e] = bytes(30)
    state[0x300+primary],state[0x300+back] = 20,filled
    list.__setitem__(m,slice(0,2048),state)
    c.a,c.x,c.y,c.p = snapshot['registers'][:4]
    c.pc,c.sp = 0xd17a,0xfd
    c.stPushWord(0x5aff)
    aligns,queries,writes = [],[],[]

    def actor():
        return [m[0x60f]+256*m[0x610],m[0x611],m[0x616],m[0x617],m[0x618]]

    for _ in range(12000):
        if c.pc==0x5b00:
            break
        pc,before = c.pc,actor()
        if pc==0xc8d4:
            aligns.append([m[0x4b1],c.y,before[0],m[0x101+c.sp]+256*m[0x102+c.sp]+1])
        if pc==0xce68:
            queries.append([c.y,c.a&31,m[0x101+c.sp]+256*m[0x102+c.sp]+1])
        assert m[pc]!=0,(hex(pc),before)
        c.step()
        after = actor()
        if before[0]!=after[0] and pc in (0xae88,0xae90,0xaeac):
            writes.append([pc,before[0],after[0]])
    else:
        raise AssertionError('Original D17A did not return')
    assert c.sp==0xfd
    return dict(aligns=aligns,queries=queries,writes=writes,actor=actor(),return_regs=[c.a,c.x,c.y,c.p,c.sp])


def host(seed, snapshot, local_x, face, alternate, origin, walls, back_floor, code=None, entries=None):
    m = N.fork(seed)
    src = m.ram[2]
    src[:0x800] = bytes.fromhex(snapshot['ram'])
    x = origin+local_x
    src[0x60f:0x611] = x.to_bytes(2,'little')
    src[0x615],src[0x4fe] = face,alternate
    N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=38,GameEngineSubroutine=8,OperMode=1,
          Player_State=2,Player_Y_HighPos=1,Player_Y_Position=145,Player_X_Position=(x-8)&255,
          Player_PageLoc=(x-8)>>8,NmiDisable=255)
    m.raw_page(1,3)
    m.raw_page(2,2)
    wall_tiles = {v%512 for v in walls}
    floor_tiles = {v%512 for v in back_floor}
    terrain(m,lambda u,y:0x58 if y==144 and u in wall_tiles else 0x54 if y>=208 or y==176 and u in floor_tiles else 0)
    assert bytes(m[FIRST:FIRST+3])==bytes(m[SECOND:SECOND+3])==b'\x20\x0b\xc4'
    if code is not None:
        at = TEST_ADDRESS-0xc000
        assert src[at:at+len(code)]==bytes(len(code))
        src[at:at+len(code)] = code
        for pc,name in ((FIRST,'PpSavePrimaryAlign'),(SECOND,'PpRestorePrimaryAlign')):
            m.ram[3][pc-0xa000+1:pc-0xa000+3] = entries[name].to_bytes(2,'little')
    aligns,queries,contexts = [],[],[]
    original = N.NesMPU

    def actor():
        return [int.from_bytes(src[0x60f:0x611],'little'),src[0x611],src[0x616],src[0x617],src[0x618]]

    class Trace(original):
        def step(self):
            pc = self.pc
            if self.memory is m:
                if pc==0xc420 and m.rawtags[2]==2:
                    aligns.append(dict(context=list(src[0x78:0x7b]),cell=int.from_bytes(src[0x7d:0x7f],'little'),
                                       index=src[0x4b1],offset=src[0xa1],actor=actor(),SP=self.sp))
                if pc in (0xa875,0xa9ea,0xa9fa) and m.rawtags[1]==3:
                    queries.append([pc,self.a,list(src[0x78:0x7b])])
                if pc in (FIRST,SECOND) and m.rawtags[1]==3:
                    contexts.append([pc,actor(),list(src[0x78:0x7b]),list(src[0xa1:0xa4])])
            return super().step()

    N.NesMPU = Trace
    try:
        res = I.invoke(m,3,ENTRY,tuple(snapshot['registers'][:4]))
    finally:
        N.NesMPU = original
    return dict(actor=actor(),aligns=aligns,queries=queries,contexts=contexts,return_regs=res['regs'],CPU=res['CPU']),m


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out==R/'build/prince-d6c0-align-1110' and not (out/'proof.json').exists()
    assert sha256(WRITER.read_bytes()).hexdigest()==D.WRITER_SHA
    assert sha256(DONOR.read_bytes()).hexdigest()=='d420b2982893a122c75d562526ff6a27e3bff20c7d4e6708ff652de5dc8ade23'
    read = Pair.Second.First.Pit.Current.read
    positive,negative = (read(V8/name) for name in ('post-pit-goombas.json','full11.json'))
    assert positive['passed'] and not negative['passed'] and positive['ROM_sha256']==negative['ROM_sha256']==Route.PIN
    assert (positive['frame'],positive['state']['world_x'],positive['state']['HP'],negative['frames'],negative['state']['world_x'])==(
        7506,1456,4,7763,1678)
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    seed,_ = P.Q.C.C.cold(base,38)
    snap = read(WRITER)['retained_D17A_inputs']['190']
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out) as temp:
        code,entries = P.assemble(Path(temp),'primary',ASM.read_text(),P.one_segment(TEST_ADDRESS,32))
    assert len(code)==29 and entries['PpSavePrimaryAlign']==TEST_ADDRESS
    cases = (
        ('right authentic coordinates',299,255,0,19,18,ORIGIN,(1600,),(),0),
        ('left standard',260,0,0,16,17,0,(208,),(),0),
        ('left alternate',190,0,1,15,16,0,(176,),(),0),
        ('left alternate low-byte wrap',244,0,1,17,19,0,(240,),(),0),
        ('right original solid-back control',299,255,0,19,18,ORIGIN,(1600,),(1552,),1),
    )
    rows = []
    for name,x,face,alt,primary,back,origin,wall,floor,filled in cases:
        d = donor(snap,x,face,alt,primary,back,filled)
        old,_ = host(seed,snap,x,face,alt,origin,wall,floor)
        new,_ = host(seed,snap,x,face,alt,origin,wall,floor,code,entries)
        row = dict(name=name,local_x=x,origin=origin,facing=face,alternate=alt,wall=wall,back_floor=floor,
                   donor=d,before=old,after=new)
        rows.append(row)
        print(name,'original',d['actor'],'native old',old['actor'],'native repaired',new['actor'],
              'donor align',d['aligns'],'host cells',[x['cell'] for x in new['aligns']],flush=True)
    assert all(r['after']['actor'][0]==r['donor']['actor'][0]+r['origin'] and
               r['after']['actor'][2:]==r['donor']['actor'][2:] for r in rows),[(r['name'],r['before']['actor'],r['after']['actor']) for r in rows]
    refs = (Path(__file__),ASM,WRITER,DONOR,Route.ROM,V8/'post-pit-goombas.json',V8/'full11.json',Path(D.__file__))
    proof = dict(passed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,donor_SHA256=Original.SHA,
                 native_V8=dict(crossing=positive['state'],new_obstruction=negative['state']),cases=rows,
                 proposed_CPU_call_sites=[FIRST,SECOND],prototype_test_address=TEST_ADDRESS,worker=code.hex(),
                 worker_bytes=len(code),execution_funding_granted=False,
                 scope='Memory-only typed worker comparison with genuine original donor D17A and native terrain. '
                       'C491 is a prototype placement only, outside the current exact runtime execution grant. '
                       'This receipt does not admit a new executable span or compose a cold backing image.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
