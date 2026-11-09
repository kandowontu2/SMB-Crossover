"""Fit a single additional exposed-pipe-top sample in the funded ledge code."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

import qualify_prince_climb_descent_1110 as V


M,P,R,N,I,E = V.M,V.P,V.R,V.N,V.I,V.E
PARENT = R/'build/prince-descent-native-1110/prince-private.nes'
PARENT_SHA = '37d3146b2441142c50a3b44b74af074c01192d61a567212ebf70c5ea1142b2d7'
OLD = R/'build/prince-climb-descent-1110/proof.json'
FAIL = R/'build/prince-full11-native-1110-v2/capture/full11.json'


def once(source,before,after):
    assert source.count(before) == 1,before
    return source.replace(before,after)


def source():
    edge = E.WORKER.read_text()
    edge = once(edge,''' inx
 beq Fallback                  ; Reject wrapped 16-bit right edge.
 bne Boundary
Left:''',''' inx
 bne Boundary
Fallback:                      ; Reject wrapped 16-bit right edge.
 jmp Align
Left:''')
    edge = once(edge,''' jsr ReadPoint                  ; Reject a wall with no exposed top here.
 bcc Accepted
Fallback:
 jmp Align

Accepted:''',''' jsr ReadPoint
 bcc Accepted
 ; A native pipe cap can be one row above the first solid hand cell.
 ; Extend only across that typed cap and require actual air above it.
 and #$fc
 cmp #$10
 bne Fallback
 lda QueryY
 sbc #16                        ; Equal CMP above already set carry.
 sta QueryY
 jsr ReadPoint
 bcs Fallback

Accepted:''')
    desc = V.SOURCE.read_text()
    desc = once(desc,''' ora OldFoot+1
 bne Original
 lda Foot''',''' ora OldFoot+1
 bne Original
 sta QueryY+1
 lda Foot''')
    desc = once(desc,''' cmp Foot
 bcs Original
 adc #15
 and #$f0
 sta QueryY
 cmp Foot
 bcs Original
 lda #0
 sta QueryY+1''',''' cmp #240
 bcs Original
 adc #15
 and #$f0
 cmp Foot
 bcs Original
 sta QueryY''')
    desc = once(desc,''' cmp #$10
 bcc Original
 cmp #$14
 bcs Original''',''' and #$fc
 cmp #$10
 bne Original''')
    desc = once(desc,''' lda QueryY
 sec
 sbc #32
 sta NativeY''',''' lda QueryY
 sbc #31                         ; Empty point left carry clear.
 sta NativeY''')
    return edge+desc


def compose(out,base,seed,prior):
    decoder_end = 31072+len((P.V.O/'cold-decoder-v25.bin').read_bytes())
    recipe = json.loads(P.OLD.read_text())
    pages = sorted((q for q in recipe['patches'] if 'physical_CHR' in q),
                   key=lambda q:q['source_offset'])
    assert len(pages)==44 and all(not 962<=q['physical_CHR']<=968 for q in pages)
    old = base['raw']
    prior_payload = b''.join(old[q['file_offset']:q['file_offset']+1024] for q in pages)
    original_runtime,_,state = P.Q.source_images()
    runtime = bytearray(seed.ram[3][:len(original_runtime)])
    assert runtime[0x1fa3:0x1fd8] == (P.V.O/'native-live-v149.bin').read_bytes()
    runtime[0x1fa3:0x1fd8] = original_runtime[0x1fa3:0x1fd8]
    meta = bytearray(seed.ram[2][0x800:0x1fcc])
    encode = P.Q.M.CODEC.encode
    before = [encode(v) for v in (bytes(runtime),bytes(meta),state)]
    old_loader = (OLD.with_name('descent-loader.bin')).read_bytes()
    assert [len(v) for v in before] == prior['layout']['packed_bytes']
    known = old_loader+b''.join(before)
    assert prior_payload[decoder_end:decoder_end+len(known)] == known

    start,end = V.DRAW,P.GRID_END
    config = (f'MEMORY{{M:start=${start:04x},size=${end-start:04x},file=%O;}}'
              'SEGMENTS{CLIMB_EDGE:load=M,type=ro;CLIMB_DESCENT:load=M,type=ro;}')
    with tempfile.TemporaryDirectory(dir=out) as directory:
        tmp = Path(directory)
        workers,labels = P.assemble(tmp,'workers',source(),config)
        assert len(workers)<=end-start and labels['PpClimbEdgeAlign']==start
        entry = labels['PpClimbDescentExport']
        old_entry = prior['layout']['descent_half_open'][0]
        V.replace(runtime,0xa000,V.VERTICAL,bytes([0x4c])+old_entry.to_bytes(2,'little'),
                  bytes([0x4c])+entry.to_bytes(2,'little'))
        meta[start-0xc800:end-0xc800] = workers.ljust(end-start,b'\0')
        chunks = bytes(runtime),bytes(meta),state
        packed = [encode(data) for data in chunks]
        boot = OLD.with_name('descent-loader.s').read_text()
        for name,data in zip(('Runtime','Metadata','State'),packed,strict=True):
            src = 0xc500 if name=='Runtime' else 0xc300 if name=='State' else 0xe100-len(data)
            for suffix,value in [('Input',src),('Packed',len(data))]:
                boot,count = re.subn(rf'(?m)^{name}{suffix}=\$[0-9a-f]+$',f'{name}{suffix}=${value:04x}',boot)
                assert count==1
        loader,_ = P.assemble(tmp,'loader',boot,(P.O/'pose-worker.cfg').read_text())
        assert len(loader)==len(old_loader) and 0xe100-len(packed[1])>=0xc300
    payload = prior_payload[:decoder_end]+loader+b''.join(packed)
    assert len(payload)<=44*1024
    cookie = bytes([0xa7,38,2])+hashlib.sha256(b''.join(chunks)+payload).digest()[:13]
    installed = M.BASE.read_bytes()
    candidate = bytearray(old)
    spans = []
    for i,row in enumerate(pages):
        at = row['file_offset']
        data = payload[i*1024:(i+1)*1024]
        if data:
            candidate[at:at+1024] = data+installed[at+len(data):at+1024]
            spans.append((at,len(data),f'Prince physical CHR {row["physical_CHR"]}'))
    candidate[P.COOKIE:P.COOKIE+16] = cookie
    spans.append((P.COOKIE,16,'Prince owner cookie'))
    for q in prior['patches']:
        if 'frontend' in q['role']:
            spans.append((q['offset'],len(bytes.fromhex(q['preimage'])),q['role']))
    patches = []
    reconstructed = bytearray(installed)
    for at,length,role in spans:
        a,b = installed[at:at+length],candidate[at:at+length]
        if a!=b:
            assert reconstructed[at:at+length] == a
            reconstructed[at:at+length] = b
            patches.append(dict(offset=at,preimage=a.hex(),replacement=b.hex(),role=role))
    assert reconstructed==candidate
    info = dict(edge_half_open=[start,entry],descent_half_open=[entry,start+len(workers)],
                pool_bytes=len(payload),pool_spare=44*1024-len(payload),
                packed_bytes=list(map(len,packed)))
    return bytes(candidate),patches,chunks,cookie,info,workers


def prepare(seed,edge,top,foot,facing,roof):
    m = N.fork(seed)
    m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=38,GameEngineSubroutine=8,
          NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode=1)
    actor = edge+(-15 if facing else 15)
    E.put(m,0xc60f,actor)
    m[0xc615]=facing;m[0xc616]=24;m[0xc618]=2;m[0xc617]=91;m[0xc611]=128
    E.put(m,0xc084,foot);E.put(m,0xc078,actor-(20 if facing else 31))
    m[0xc07a]=9;m[0xc4b1]=19;E.put(m,0xc07f,208);m[0xc081]=1
    E.put(m,0xc089,77);m[0xc6d1]=5
    m[0x300:0x4a0]=bytes(416)
    inside = edge if facing else edge-1
    m[E.block(inside,top)] = 0x12 if facing else 0x13
    for y in range(top+16,208,16):
        m[E.block(inside,y)] = 0x14 if facing else 0x15
    if roof:
        m[E.block(inside,top-1)] = 0x54
    return m


def align(m):
    c = N.NesMPU(memory=m,pc=E.PC)
    c.a,c.x,c.y,c.p,c.sp = 43,19,24 if m[0xc615] else 58,0x61,186
    for _ in range(2400):
        if c.pc==E.PC+3:
            return c.a,c.x,c.y,c.p,c.sp
        assert m[c.pc]!=0,hex(c.pc)
        c.step()
    raise AssertionError('Original F801 continuation bound')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    prior = json.loads(OLD.read_text())
    evidence = json.loads(FAIL.read_text())
    assert evidence['ROM_sha256']==prior['expected_memory_only_SHA256']==PARENT_SHA
    assert not evidence['passed'] and evidence['route']['index']==1 and evidence['HP']==5
    hang = evidence['route']['hang']
    assert (hang['world_x'],hang['physical_foot'],hang['source_mode'])==(585,203,2)
    cross, = [e for e in evidence['route']['events'] if e['tag']=='pipe-cross']
    assert cross['physical_foot']==157 and cross['world_x']==560 and cross['source_action']==10
    parent = PARENT.read_bytes();assert P.sha(parent)==PARENT_SHA
    template = M.image()
    base = dict(template,raw=parent)
    ref,_ = P.Q.C.C.cold(base,38)
    raw,patches,chunks,cookie,layout,workers = compose(args.output,base,ref,prior)
    new,cold = P.Q.C.C.cold(dict(base,raw=raw),38)
    assert bytes(new.ram[3][:len(chunks[0])])==P.live(chunks[0])
    assert bytes(new.ram[2][0x800:0x800+len(chunks[1])])==chunks[1]
    assert all(bytes(new.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    for row in (15,36):
        warm=N.fork(new)
        assert I.invoke(warm,193,0xb08c+3*row)['regs'][3]&1
        assert bytes(warm.ram[2][V.DRAW-0xc000:V.DRAW-0xc000+len(workers)])==workers
    outcomes = []
    for edge,top,foot,face,roof,wanted in (
        (448,176,203,255,False,440),(480,176,203,0,False,488),
        (608,160,203,255,False,600),(640,160,203,0,False,648),
        (608,160,203,255,True,None),(640,160,203,0,True,None),
        (736,144,203,255,False,None),(768,144,203,0,False,None),
        (736,144,193,255,False,728),(768,144,193,0,False,776)):
        a,b = [prepare(m,edge,top,foot,face,roof) for m in (ref,new)]
        assert align(a)==align(b),(edge,top,face,roof)
        xa,xb = E.word(a,0xc60f),E.word(b,0xc60f)
        assert xb==(wanted if wanted is not None else xa),(edge,foot,face,xa,xb,wanted)
        assert bytes(a.ram[2][:0x60f])==bytes(b.ram[2][:0x60f])
        assert bytes(a.ram[2][0x611:0x800])==bytes(b.ram[2][0x611:0x800])
        outcomes.append(dict(edge=edge,top=top,foot=foot,facing=face,roof=roof,old_x=xa,new_x=xb))
    assert next(q for q in outcomes if q['edge']==608 and not q['roof'])['old_x']==568
    original,_ = P.Q.C.C.cold(template,38)
    V.exercise(original,new)  # Prove the compact descent has the same nine outcomes.
    irq = V.Async.stress('cold-backed one-row typed pipe cap',
        prepare(new,608,160,203,255,False),align,
        [(2,*layout['edge_half_open']),(3,0xb310,0xb369)])
    packed_path = args.output/'tall-workers.bin'
    packed_path.write_bytes(workers)
    refs = [Path(__file__),V.SOURCE,E.WORKER,OLD,FAIL,M.BASE,PARENT,packed_path,
            OLD.with_name('descent-loader.bin'),OLD.with_name('descent-loader.s')]
    q = dict(passed=True,parent_SHA256=M.BASE_PIN,previous_private_SHA256=PARENT_SHA,
        expected_memory_only_SHA256=P.sha(raw),Prince_cookie=cookie.hex(),patches=patches,
        layout=layout,actual_second_pipe=hang,outcomes=outcomes,cold_CPU=cold['CPU'],
        warm_rows=[15,36],descent_cases_reverified=9,interrupt=irq,
        ROM_written=False,Mesen_run=False,bindings={str(f.resolve()):P.sha(f.read_bytes()) for f in refs})
    (args.output/'two-row-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','layout','outcomes','interrupt')}))


if __name__=='__main__':
    main()
