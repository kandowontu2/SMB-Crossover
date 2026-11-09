"""Build and test the private Prince pipe-landing projection in memory."""

import argparse
import hashlib
import json
from pathlib import Path
import re

import check_prince_climb_funded_irq_1109_v2 as Async
import measure_prince_climb_descent_1110 as M


P, R, N, I, E = M.P, M.R, M.N, M.I, M.E
SOURCE = R/'tools/reference/prince_climb_descent_1110_v1.s'
TRACE = R/'build/prince-climb-exit-trace-1109/capture/prince-diagnostic.json'
FUNDED_ROOT = M.FUNDED.parent
DRAW = 0xd7b3
WORKER = DRAW+178
VERTICAL = 0xbd42


def replace(blob, base, pc, old, new):
    at = pc-base
    assert len(old) == len(new) and blob[at:at+len(old)] == old,(hex(pc),old.hex())
    blob[at:at+len(new)] = new


def layout(out,base,seed):
    old_receipt = json.loads(M.FUNDED.read_text())
    assert old_receipt['layout']['compact_half_open'][1] == DRAW
    assert old_receipt['layout']['worker_half_open'] == [P.WORKER,P.WORKER+178]
    recipe = json.loads(P.OLD.read_text())
    carriers = sorted((row for row in recipe['patches'] if 'physical_CHR' in row),
                      key=lambda row:row['source_offset'])
    assert len(carriers) == 44 and all(not 962 <= row['physical_CHR'] <= 968 for row in carriers)
    raw = base['raw']
    backing = b''.join(raw[r['file_offset']:r['file_offset']+1024] for r in carriers)
    first,staged = P.Q.source_images()[0],P.Q.source_images()[2]
    live = bytearray(seed.ram[3][:len(first)])
    assert live[0x1fa3:0x1fd8] == (P.V.O/'native-live-v149.bin').read_bytes()
    live[0x1fa3:0x1fd8] = first[0x1fa3:0x1fd8]
    meta = bytearray(seed.ram[2][0x800:0x1fcc])
    before = (bytes(live),bytes(meta),staged)
    encode = P.Q.M.CODEC.encode
    packed = [encode(data) for data in before]
    decoder_end = 31072+len((P.V.O/'cold-decoder-v25.bin').read_bytes())
    current_loader = (FUNDED_ROOT/'cold-loader.bin').read_bytes()
    prefix_end = decoder_end+len(current_loader)
    assert backing[decoder_end:prefix_end] == current_loader
    assert [len(b) for b in packed] == old_receipt['layout']['new_packed_bytes']
    assert backing[prefix_end:prefix_end+sum(map(len,packed))] == b''.join(packed)

    config = (f'MEMORY{{M:start=${DRAW:04x},size=${P.GRID_END-DRAW:04x},file=%O;}}'
              'SEGMENTS{CLIMB_EDGE:load=M,type=ro;CLIMB_DESCENT:load=M,type=ro;}')
    workers,lab = P.assemble(out,'climb-descent',E.WORKER.read_text()+SOURCE.read_text(),config)
    assert lab['PpClimbEdgeAlign'] == DRAW and lab['PpClimbDescentExport'] == WORKER
    assert 178 < len(workers) <= P.GRID_END-DRAW
    old_worker = (FUNDED_ROOT/'climb.bin').read_bytes()
    assert len(old_worker) == 178 and meta[P.WORKER-0xc800:P.WORKER-0xc800+178] == old_worker
    assert workers[:155]+workers[158:178] == old_worker[:155]+old_worker[158:]
    assert int.from_bytes(workers[156:158],'little') == DRAW+172
    assert all(v == 0 for v in meta[DRAW-0xc800:P.WORKER-0xc800])
    assert all(v == 0 for v in meta[P.WORKER-0xc800+178:P.GRID_END-0xc800])
    meta[DRAW-0xc800:P.GRID_END-0xc800] = workers.ljust(P.GRID_END-DRAW,b'\0')
    P.call(live,0xa000,E.PC,P.WORKER,DRAW)
    assert live.count(bytes.fromhex('384c42bd')) == 0  # This caller lives in RAM2.
    assert seed.ram[2].count(bytes.fromhex('384c42bd')) == 1
    assert live[VERTICAL-0xa000:VERTICAL-0xa000+9] == bytes.fromhex('ad84c0ed86c0858e60')
    replace(live,0xa000,VERTICAL,bytes.fromhex('ad84c0'),bytes([0x4c])+WORKER.to_bytes(2,'little'))
    after = (bytes(live),bytes(meta),staged)
    streams = [encode(data) for data in after]
    boot = (FUNDED_ROOT/'cold-loader.s').read_text()
    for name,data in zip(('Runtime','Metadata','State'),streams,strict=True):
        src = 0xc500 if name == 'Runtime' else 0xc300 if name == 'State' else 0xe100-len(data)
        for suffix,value in [('Input',src),('Packed',len(data))]:
            boot,count = re.subn(rf'(?m)^{name}{suffix}=\$[0-9a-f]+$',f'{name}{suffix}=${value:04x}',boot)
            assert count == 1
    loader,_ = P.assemble(out,'descent-loader',boot,(P.O/'pose-worker.cfg').read_text())
    assert len(loader) == len(current_loader)
    assert 0xe100-len(streams[1]) >= 0xc300
    payload = backing[:decoder_end]+loader+b''.join(streams)
    assert len(payload) <= 44*1024
    cookie = bytes([0xa7,38,2])+hashlib.sha256(b''.join(after)+payload).digest()[:13]

    original = M.BASE.read_bytes()
    candidate = bytearray(base['raw'])
    ranges = []
    for i,row in enumerate(carriers):
        at = row['file_offset']
        data = payload[i*1024:(i+1)*1024]
        if data:
            candidate[at:at+1024] = data+original[at+len(data):at+1024]
            ranges.append((at,len(data),f'Prince physical CHR {row["physical_CHR"]}'))
    candidate[P.COOKIE:P.COOKIE+16] = cookie
    ranges.append((P.COOKIE,16,'Prince owner cookie'))
    for row in old_receipt['patches']:
        if 'frontend' in row['role']:
            at = row['offset']
            ranges.append((at,len(bytes.fromhex(row['preimage'])),row['role']))
    copy = bytearray(original)
    patches = []
    for at,n,role in ranges:
        before,after_bytes = original[at:at+n],candidate[at:at+n]
        if before == after_bytes:
            continue
        assert copy[at:at+n] == before
        copy[at:at+n] = after_bytes
        patches.append(dict(offset=at,preimage=before.hex(),replacement=after_bytes.hex(),role=role))
    assert copy == candidate
    return bytes(candidate),patches,after,cookie,dict(pool_bytes=len(payload),
        pool_spare=44*1024-len(payload),worker_half_open=[DRAW,WORKER],
        descent_half_open=[WORKER,DRAW+len(workers)],packed_bytes=list(map(len,streams)))


def exercise(reference,successor):
    rows = []
    for case in ('actual','mirrored','no_crossing','shaft_only','ceiling','plain_terrain','next_row','rising','foreign_action'):
        x,foot,old,facing = (465,193,175,0) if case=='mirrored' else (446,193,175,255)
        if case == 'no_crossing':
            foot = 176
        elif case == 'next_row':
            old = 159
        elif case == 'rising':
            foot,old = 170,190
        pair = [N.fork(m) for m in (reference,successor)]
        results = []
        for m in pair:
            M.geometry(m,x=x,foot=foot,old=old,facing=facing)
            if case == 'shaft_only':
                m[E.block(x+8,176)] = 0x14
            elif case == 'ceiling':
                m[E.block(x+8,160)] = 0x54
            elif case == 'plain_terrain':
                m[E.block(x+8,176)] = 0x54
            elif case == 'foreign_action':
                m[0xc616] = 4
            I.invoke(m,3,0xc383,(0,0,0,0x21))
            result = I.invoke(m,3,VERTICAL,(83,71,109,0x61))
            results.append(result['regs'])
        assert results[0] == results[1],(case,results)
        before,after = [N.get(m,'Player_Y_Position') for m in pair]
        intended = case in ('actual','mirrored','next_row')
        assert after == (144 if intended else before),(case,before,after)
        assert bytes(pair[0].ram[2][:0x800]) == bytes(pair[1].ram[2][:0x800])
        assert all(N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc') == x for m in pair)
        assert all(N.get(m,'Player_Y_Speed') == (foot-old)&255 for m in pair)
        rows.append(dict(case=case,native_y=[before,after],vertical_abi_exact=True))
        if case in ('actual','mirrored'):
            views = [N.fork(m) for m in pair]
            for m in views:
                N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=0)
                m[0x200:0x300] = bytes([0xf8])*256
            draw = [I.invoke(m,3,0xbbc1,(83,71,109,0x61))['regs'] for m in views]
            a,b = views
            assert draw[0] == draw[1] and bytes(a[0x200:0x300]) == bytes(b[0x200:0x300])
            assert a.chr_latches == b.chr_latches and N.get(a,'SmPose') == N.get(b,'SmPose') > 0
            rows[-1]['exact_source_oam_and_chr_at_projected_top'] = True
            baseline,new = [M.observe(m,lambda m=m:N.invoke(m,'PlayerBGCollision',a=0,x=0,y=0,p=0x21))
                            for m in pair]
            assert baseline['after']['x'] != x and new['after']['x'] == x,(case,baseline,new)
            assert new['after']['y'] == 144 and new['after']['native_state'] == 0
            # The next real donor terrain consumer resolves the same surface
            # and action itself. Re-import each actual native X as Main does.
            native = []
            for m in pair:
                I.invoke(m,3,0xb3d1,(0,0,0,0x21))
                native.append(M.observe(m,lambda m=m:I.invoke(m,3,0xa5d9,(0,0,0,0x21))))
            assert native[1]['after']['action'] == 17 and native[1]['after']['surface'] == 176
            rows[-1].update(native_before=baseline['after'],native_after=new['after'],
                            actual_source_continuation=native[1]['after'])
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    evidence = json.loads(TRACE.read_text())
    assert evidence['ROM_sha256'] == '652fd04e2f48bb673c4966a16874c861df1b56973ea9fff700f6ab4ab65d7797'
    trace = evidence['first_pipe_route']['exit_trace']
    bad, = [q for q in trace if q['Main']==405 and q['event']=='generic native right clamp']
    assert (bad['world_x'],bad['native_y'],bad['oldFoot'],bad['physical_foot']) == (446,160,175,193)
    base = M.image()
    assert I.address(base,'Player_Y_Position') == 0xbd
    reference,_ = P.Q.C.C.cold(base,38)
    raw,patches,chunks,cookie,fit = layout(args.output,base,reference)
    current = dict(base,raw=raw)
    successor,cold = P.Q.C.C.cold(current,38)
    runtime,meta,_ = chunks
    assert bytes(successor.ram[3][:len(runtime)]) == P.live(runtime)
    assert bytes(successor.ram[2][0x800:0x800+len(meta)]) == meta
    assert all(bytes(successor.ram[k][0x1fe0:0x1ff0]) == cookie for k in (2,3))
    for row in (15,36):
        warm = N.fork(successor)
        assert I.invoke(warm,193,0xb08c+3*row)['regs'][3]&1
        assert bytes(warm.ram[2][WORKER-0xc000:fit['descent_half_open'][1]-0xc000]) == meta[WORKER-0xc800:fit['descent_half_open'][1]-0xc800]
    _,reference,_ = P.Q.loaded(base,reference)
    _,successor,_ = P.Q.loaded(current,successor)
    N.put(successor,NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,GameEngineSubroutine=8,OperMode=1)
    rows = exercise(reference,successor)
    print(json.dumps(dict(geometry=rows,fit=fit)),flush=True)
    geometry = N.fork(successor)
    M.geometry(geometry,x=446,foot=193,old=175,facing=255)
    def export_regs(m):
        regs = I.invoke(m,3,VERTICAL,(83,71,109,0x61))['regs']
        return (*regs[:3],regs[3]&0xef,regs[4])
    irq = Async.stress('cold-backed Prince pipe-top projection',geometry,
        export_regs,
        [(2,*fit['descent_half_open']),(3,0xb310,0xb369)])
    refs = [Path(__file__),Path(M.__file__),SOURCE,TRACE,M.BASE,M.FUNDED,
            FUNDED_ROOT/'climb.bin',FUNDED_ROOT/'cold-loader.bin',FUNDED_ROOT/'cold-loader.s',
            args.output/'climb-descent.s',args.output/'climb-descent.bin',
            args.output/'descent-loader.s',args.output/'descent-loader.bin']
    report = dict(passed=True,parent_SHA256=M.BASE_PIN,expected_memory_only_SHA256=P.sha(raw),
        Prince_cookie=cookie.hex(),patches=patches,layout=fit,cold_CPU=cold['CPU'],
        both_complete_headers=True,warm_rows=[15,36],observed_main405=bad,
        qualified_cases=rows,interrupt=irq,ROM_written=False,Mesen_run=False,
        bindings={str(f.resolve()):P.sha(f.read_bytes()) for f in refs})
    (args.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,image_SHA256=report['expected_memory_only_SHA256'],interrupt=irq)))


if __name__ == '__main__':
    main()
