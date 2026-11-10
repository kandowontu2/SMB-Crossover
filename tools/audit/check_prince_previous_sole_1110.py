"""Qualify Prince's previous-Main sole export in memory; never write a ROM.

Two compact receipts are the only permitted output. The natural Mesen failure
is the oracle; explicit CPU scenes and real vector interruptions are separate.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct
import re

import check_prince_camera_easy_contact_1110 as Failure
import check_prince_camera_framing_1110 as Camera
import compose_remaining_roster_starts_1110 as Start
from py65.assembler import Assembler

R, N, I, P = Camera.R, Camera.N, Camera.I, Camera.P
Route, Seam, Recovery = Failure.Route, Failure.Seam, Failure.Roof.Recovery
OUT = R / 'build/prince-previous-sole-1110'
SOURCE = R / 'tools/reference/prince_previous_sole_1110.s'
ROM = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
COOKIE = 535469
HOOK, EXPORT = 0xd9db, 0xbd45
CAPTURE, CONTACT, OPERAND = 0, 0, 0


def digest(data):
    return sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def assembly(base, origin):
    """Assemble actual source instructions directly in memory, with no files."""
    assembler = Assembler(N.NesMPU(memory=[0] * 65536))
    labels={name:I.address(base,name) for name in
            ('CrossoverBehaviorVersion','AreaType','FrameCounter','Enemy_ID','Enemy_Y_HighPos','EnemyStomped')}
    lines=[line.split(';',1)[0].strip() for line in SOURCE.read_text().splitlines()]
    def number(text):
        if text.startswith('<'):return number(text[1:])&255
        if text.startswith('>'):return number(text[1:])>>8
        if text.startswith('$'):return int(text[1:],16)
        return int(text) if text.isdigit() else labels.get(text,origin)
    result=None
    for iteration in range(2):
        pc=origin;data=bytearray()
        for text in lines:
            if not text or text.startswith(('.setcpu','.segment')):continue
            if text.endswith(':'):
                labels[text[:-1]]=pc;continue
            if text.startswith('.byte '):
                encoded=bytes(number(v) for v in text[6:].split(','))
            else:
                expanded=re.sub(r'([A-Za-z_][A-Za-z_0-9]*)(\+1)?',
                    lambda m:f'${labels.get(m[1],origin)+(1 if m[2] else 0):04x}'
                    if m[1] in labels or m[2] else m[0],text)
                for name in ('PreviousSole','PreviousHigh','Original'):
                    expanded=expanded.replace(name,f'${labels.get(name,pc):04x}')
                encoded=assembler.assemble(expanded,pc=pc)
            data.extend(encoded);pc+=len(encoded)
        result=bytes(data)
    return result,labels


def fund_grid(meta):
    grid=meta[:0xd622-0xc800]
    tags=[int.from_bytes(grid[i:i+2],'little') for i in range(0,478,2)]
    order=sorted(set(tags)-{65535},key=lambda t:t&0x3fff)
    packets={tag:grid[tag&0x3fff:end] for tag,end in zip(order,[t&0x3fff for t in order[1:]]+[len(grid)])}
    canonical={};drop={};reclaimed=0
    for tag in order:
        geometry=Camera.Funded.Pack.geometry(grid,tags.index(tag))
        if geometry in canonical:
            drop[tag]=canonical[geometry];reclaimed+=len(packets[tag])
        else:canonical.setdefault(geometry,tag)
    packed=bytearray(bytes([255])*478);offsets={}
    for tag in order:
        if tag not in drop:
            offsets[tag]=(tag&0xc000)|len(packed);packed.extend(packets[tag])
    for i,tag in enumerate(tags):
        if tag!=65535:packed[2*i:2*i+2]=offsets[drop.get(tag,tag)].to_bytes(2,'little')
    assert len(grid)-len(packed)==reclaimed>=160
    assert all(Camera.Funded.Pack.geometry(grid,f)==Camera.Funded.Pack.geometry(packed,f) for f in range(239))
    return bytes(packed),dict(geometry_cases=239,reclaimed=reclaimed,removed_packets=drop)


def compose(base, seed):
    global CAPTURE,CONTACT,OPERAND
    original, _, state = P.Q.source_images()
    runtime = bytearray(seed.ram[3][:len(original)])
    runtime[0x1fa3:0x1fd8] = original[0x1fa3:0x1fd8]
    assert P.live(runtime) == bytes(seed.ram[3][:len(runtime)])
    meta = bytes(seed.ram[2][0x800:0x1fcc])
    assert runtime[EXPORT-0xa000:EXPORT-0xa000+6] == bytes.fromhex('ed86c0858e60')
    assert runtime[EXPORT-0xa000-3:EXPORT-0xa000] == bytes.fromhex('4c7dd8')
    assert meta[HOOK-0xc800:HOOK-0xc800+3] == bytes.fromhex('206eb3')
    packed,funding=fund_grid(meta)
    code,entries=assembly(base,0xc800+len(packed))
    assert len(code)<=funding['reclaimed'],(len(code),funding)
    CAPTURE,CONTACT,OPERAND=(entries[n] for n in ('PpCapturePreviousSole','PpLandingContact','PreviousSole'))
    OPERAND+=1
    changed_meta, changed_rt = bytearray(meta), bytearray(runtime)
    for data,name in ((bytes(seed.ram[2][0x7f3:0x7f7]),'LandingLo'),
                      (bytes(seed.ram[2][0x7f7:0x7fb]),'LandingHi'),
                      (meta[0x12c2:0x12c6],'LandingBank')):
        at=entries[name]-(0xc800+len(packed))
        assert code[at:at+4]==data,(name,code[at:at+4].hex(),data.hex())
    changed_meta[:0xd622-0xc800]=packed+code+bytes([255])*(funding['reclaimed']-len(code))
    changed_meta[HOOK-0xc800:HOOK-0xc800+3] = bytes([0x20])+CAPTURE.to_bytes(2, 'little')
    assert runtime[0x1d2f:0x1d32]==bytes.fromhex('20ddda')
    changed_rt[0x1d30:0x1d32]=CONTACT.to_bytes(2,'little')
    for old,name in ((0xc7f3,'LandingLo'),(0xc7f7,'LandingHi'),(0xdac2,'LandingBank')):
        pattern=bytes([0xb9])+old.to_bytes(2,'little')
        hits=[i for i in range(0x121b,0x1269) if meta[i:i+3]==pattern]
        assert len(hits)==1,(name,hits)
        at=hits[0];changed_meta[at+1:at+3]=entries[name].to_bytes(2,'little')
    old_chunks = (bytes(runtime), meta, state)
    new_chunks = (bytes(changed_rt), bytes(changed_meta), state)
    encode = P.Q.M.CODEC.encode
    old, new = [[encode(data) for data in chunks] for chunks in (old_chunks, new_chunks)]
    previous = read(R/'build/prince-camera-framing-1110/proof.json')
    assert list(map(len, old)) == previous['layout']['packed_bytes'] == [6386, 5621, 1232]
    pages = sorted((row for row in read(P.OLD)['patches'] if 'physical_CHR' in row),
                   key=lambda row: row['source_offset'])
    assert len(pages) == len({row['file_offset'] for row in pages}) == 44
    raw = base['raw']
    payload = b''.join(raw[row['file_offset']:row['file_offset']+1024] for row in pages)
    decoder_end = 31072 + len((P.V.O/'cold-decoder-v25.bin').read_bytes())
    loader_end = decoder_end + 444
    assert payload[loader_end:loader_end+sum(map(len, old))] == b''.join(old)
    old_extent = previous['layout']['payload_bytes']
    old_cookie = bytes([167, 38, 2]) + sha256(b''.join(old_chunks)+payload[:old_extent]).digest()[:13]
    assert raw[COOKIE:COOKIE+16] == old_cookie
    # Source loader Config is exactly its final 24-byte word table before
    # 28 fixed physical-page bytes. No loader instruction or atlas changes.
    loader = bytearray(payload[decoder_end:loader_end])
    at = 444 - 52
    config = lambda sizes: struct.pack('<12H', 0xc500, 0xa000, sizes[0], len(runtime),
        0xe100-sizes[1], 0xc800, sizes[1], len(meta), 0xc300, 0xc100, sizes[2], len(state))
    assert loader[at:at+24] == config(list(map(len, old)))
    loader[at:at+24] = config(list(map(len, new)))
    updated = payload[:decoder_end] + bytes(loader) + b''.join(new)
    assert len(updated) <= len(payload), (len(updated), len(payload))
    cookie = bytes([167, 38, 2]) + sha256(b''.join(new_chunks)+updated).digest()[:13]
    image, patches = bytearray(raw), []
    def add(offset, data, role):
        before = raw[offset:offset+len(data)]
        if before != data:
            image[offset:offset+len(data)] = data
            patches.append(dict(file_offset=offset, old_hex=before.hex(), new_hex=data.hex(), role=role))
    add(COOKIE, cookie, 'Authentic Prince typed cookie, current relocated descriptor')
    for index, row in enumerate(pages):
        data = updated[index*1024:(index+1)*1024]
        if data:
            add(row['file_offset'], data, 'Existing Prince authenticated carrier')
    assert image[:1048592] == raw[:COOKIE] + cookie + raw[COOKIE+16:1048592]
    return dict(base, raw=bytes(image)), new_chunks, cookie, patches, dict(
        capture=[CAPTURE,CAPTURE+15], contact=[CONTACT,entries['LandingLo']],
        allocation=[CAPTURE,0xd622], funding=funding, entries=entries,
        vertical_export_unchanged=True, hook=[HOOK,HOOK+3],
        previous_sole_operand=OPERAND, packed_bytes=list(map(len, new)),
        payload_bytes=len(updated), spare=len(payload)-len(updated),
        no_new_RAM=True, original_terrain_oldfoot_unchanged=True)


def fixture(base):
    env, model, labels, _ = Failure.Roof.Climb.Earned.fixture(base)
    Seam.terrain(model, Failure.Roof.terrain)
    Seam.layout(model, 811-255, 678, scroll=0)
    Route.install_group(model)
    pad = 0
    for tick in range(172):
        pad = {0:1, 8:0, 51:8, 106:9, 112:8}.get(tick, pad)
        Route.controls(env, model, labels, pad)
    row = Recovery.sample(model, 172)
    assert (row['x'], row['y'], row['foot'], row['hp'], row['lives']) == (723, 112, 145, 5, 2)
    Failure.shift_goombas(model, 30)
    return env, model, labels


def inspect_funding(seed):
    grid=bytes(seed.ram[2][0x800:0xd622-0xc000])
    assert len(grid)==0xd622-0xc800
    tags=[int.from_bytes(grid[i:i+2],'little') for i in range(0,478,2)]
    order=sorted(set(tags)-{65535},key=lambda t:t&0x3fff)
    packets={tag:grid[tag&0x3fff:end] for tag,end in zip(order,[t&0x3fff for t in order[1:]]+[len(grid)])}
    groups={}
    for tag,packet in packets.items():
        geometry=Camera.Funded.Pack.geometry(grid,tags.index(tag))
        groups.setdefault(geometry,[]).append(tag)
    print('Geometry duplicate groups',[(g,[len(packets[t]) for t in g]) for g in groups.values() if len(g)>1],flush=True)
    overlaps=[]
    for left,a in packets.items():
        for right,b in packets.items():
            if left==right:continue
            overlap=max((k for k in range(1,min(len(a),len(b))) if a[-k:]==b[:k]),default=0)
            if overlap:overlaps.append((overlap,left,right))
    print('Top suffix overlaps',sorted(overlaps,reverse=True)[:30],flush=True)


def replay(base, behavior=0, bound=145):
    env, model, labels = fixture(base)
    N.put(model, CrossoverBehaviorVersion=behavior)
    stage, events, contacts, transitions, speed_writes = 'run', {}, [], [], []
    holders = {}; contact_seeds=[]; frame_seed=None
    native, tick = N.NesMPU, 0
    class Trace(native):
        def step(self):
            prior_speed = N.get(model,'Player_Y_Speed') if tick==90 else None
            writer_pc=self.pc
            writer_bank=model.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else None
            if self.memory is model and self.pc >= 0x8000:
                bank = model.rawtags[(self.pc-0x8000)//8192]
                if bank == 2 and self.pc == CAPTURE:
                    holders[tick] = frame_seed
                if bank == 3 and self.pc in (0xbd22, EXPORT):
                    row = Recovery.sample(model, tick)
                    row.update(point='injury' if self.pc == 0xbd22 else 'export',
                               prior_sole=model.ram[2][OPERAND-0xc000],
                               terrain_oldfoot=int.from_bytes(model.ram[2][0x86:0x88], 'little'))
                    (contacts if self.pc == 0xbd22 else transitions).append(row)
                    if self.pc==0xbd22:contact_seeds.append(N.fork(model))
            value=super().step()
            if tick==90 and prior_speed != N.get(model,'Player_Y_Speed'):
                speed_writes.append(dict(pc=writer_pc,bank=writer_bank,before=prior_speed,after=N.get(model,'Player_Y_Speed')))
            return value
    N.NesMPU = Trace
    try:
        for tick in range(bound):
            row = Recovery.sample(model, tick)
            x,y = row['x'],row['y']
            if row['hp'] == 0 or row['engine'] != 8 or row['lives'] != 2:
                stage='death';break
            if tick==91 and row['hp']==5 and N.get(model,'Enemy_State',1)==4:
                stage='landing-repaired';break
            if stage == 'run' and 745 <= x <= 752 and abs(y-112) <= 2 and Recovery.running(model,row):
                events['request']=row;stage='takeoff'
            if stage == 'takeoff' and row['action'] == 4:
                events['admission']=row;stage='flight'
            if stage == 'flight' and x >= 784 and y == 176 and Recovery.grounded(model,row):
                events.setdefault('land',row)
            if stage == 'flight' and x >= 902 and 'land' in events:
                stage='clear';break
            frame_seed=N.fork(model)
            Route.controls(env,model,labels,{'run':1,'takeoff':129,'flight':1}[stage])
    finally:
        N.NesMPU=native
    return dict(behavior=behavior,result=stage,terminal=row,events=events,
                injuries=contacts,exports=transitions,speed_writes=speed_writes,actors=Route.actors(model)), holders, (env,labels,contact_seeds)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--vectors', action='store_true')
    cli.add_argument('--inspect-funding', action='store_true')
    args=cli.parse_args();out=args.output.resolve()
    assert out == OUT
    out.mkdir(exist_ok=True)
    base=Start.W.bundle(ROM.read_bytes());assert digest(base['raw']) == PIN
    Failure.evidence()
    before,cold=P.Q.C.C.cold(base,38)
    if args.inspect_funding:
        inspect_funding(before);return
    updated,chunks,cookie,patches,layout=compose(base,before)
    after,loaded=P.Q.C.C.cold(updated,38)
    assert bytes(after.ram[3][:len(chunks[0])]) == P.live(chunks[0])
    assert bytes(after.ram[2][0x800:0x800+len(chunks[1])]) == chunks[1]
    assert all(bytes(after.ram[k][0x1fe0:0x1ff0]) == cookie for k in (2,3))
    print('Authenticated current cold; source-owned allocation',layout,flush=True)
    results=[];seed=None;operation=None
    for label,bundle,behavior in (('old-easy',base,0),('new-easy',updated,0),('new-hard',updated,1)):
        result,held,(env,labels,contact_seeds)=replay(bundle,behavior)
        print(label,result['result'],result['terminal'],flush=True)
        print('Landing transport', result['exports'][-1:], 'contact', result['injuries'][-1:],flush=True)
        print('DY writes',result['speed_writes'],flush=True)
        results.append(dict(label=label,**result))
        if label == 'old-easy':
            assert result['result']=='death' and result['terminal']['x']==891
        elif label == 'new-easy':
            assert result['result']=='landing-repaired' and result['terminal']['hp']==5
            landing=[q for q in result['exports'] if q['x']==891 and q['foot']==210]
            assert landing and landing[0]['prior_sole']==196 and landing[0]['terrain_oldfoot']==210
            assert len(result['injuries'])==1
            seed=held[90]
            operation=lambda m:Route.controls(env,m,labels,1)['regs']
        else:
            assert result['result']=='death' and result['terminal']['x']==891
    vectors=None
    if args.vectors:
        N.put(seed,NmiDisable=255)
        vectors=Camera.Funded.Life.stress('Prince actual captured landing update',seed,operation,
                    [(2,CAPTURE,CAPTURE+9),(2,HOOK,HOOK+3),(3,EXPORT,EXPORT+6)])
        print('Real interrupted landing',vectors,flush=True)
    report=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=digest(updated['raw']),
        ROM_written=False,Mesen_run=False,native_pending=True,Prince_cookie=cookie.hex(),
        layout=layout,patches=patches,cold_CPU=loaded['CPU'],cases=results,real_vectors=vectors,
        scope='Natural native X891 failure retained; exact current ROM CPU terrain/controller reproduction. '
              'Only native transport sole history changes. Actual current-hash Mesen route remains pending.',
        bindings={p.relative_to(R).as_posix():digest(p.read_bytes()) for p in
            (Path(__file__),SOURCE,ROM,Failure.CAPTURE/'full11.json',Failure.CAPTURE/'prince-diagnostic.json')})
    (out/('proof-vectors.json' if args.vectors else 'proof.json')).write_text(json.dumps(report,separators=(',',':'))+'\n')


if __name__=='__main__':
    main()
