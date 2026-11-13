"""Read-only Prince original reach/host geometry audit; writes no outputs."""

from hashlib import sha256
import contextlib
import io
import inspect
import re
import json
from pathlib import Path
import sys
from unittest.mock import patch

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/reference'))
import prince_original_cpu_1101_v1 as P
import check_prince_brick_support_1111 as B
import prince_cold_packet_1111 as Packet

PIN = 'cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7'
O = R / 'build/prince-actor-1101-v1'


def animation(action):
    c = P.machine()
    c.memory.switch(5)
    list.__setitem__(c.memory, slice(0, 2048), (O/'state-899.bin').read_bytes())
    for at, value in ((0x69,0),(0x615,0),(0x616,0),(0x611,128)):
        c.memory[at] = value
    P.call(c, 0x8730, a=action, x=31, y=0, p=0x21)
    points, seen = [], set()
    for _ in range(512):
        pointer = c.memory[0x613] | c.memory[0x614] << 8
        if pointer in seen:
            break
        seen.add(pointer)
        c.memory[0x69] = c.memory[0x2c] = 0
        c.a, c.x, c.y, c.p = 85, 0, 0, 0x20
        c.sp = 0xfd
        c.stPushWord(0x5ffe)
        c.pc = 0xf158
        P.until(c, 0xf1a2, limit=6000)
        points.append(dict(pose=c.memory[0x617], y=c.memory[0x611], action=c.memory[0x616]))
    else:
        raise AssertionError(('Unbounded original animation',action))
    return points


def raster(pose, atlas):
    pixels = {}
    for part in reversed(pose['parts_8x16']):
        pair = atlas[32*part['pattern_pair']:32*(part['pattern_pair']+1)]
        attr = part['attribute']
        for y in range(16):
            sy = 15-y if attr & 128 else y
            base = (sy//8)*16
            for x in range(8):
                bit = x if attr & 64 else 7-x
                value = ((pair[base+sy%8] >> bit)&1) | (((pair[base+8+sy%8] >> bit)&1)<<1)
                if value:
                    pixels[part['x']+x,part['y']+y] = value
    return pixels


def head_worker(bundle):
    from check_prince_wall_sweep_1110_v6 import assemble
    symbols = {n:B.N.address(bundle,n) for n in ('Player_Y_Position','R3','BlockBufferColli_Head')}
    text = '''ReachHead:
 lda $c617
 cmp #78
 bne OriginalHead
 lda Player_Y_Position
 cmp #48
 bcc OriginalHead
 pha
 sec
 sbc #16
 sta Player_Y_Position
 jsr BlockBufferColli_Head
 pla
 sta Player_Y_Position
 lda R3
 rts
OriginalHead:
 jmp BlockBufferColli_Head
'''
    return assemble(text,0xb0fe,symbols)[0]


def head_vector(metadata):
    hits = [i for i in range(len(metadata)-2) if metadata[i:i+3] == bytes.fromhex('4c8795')]
    assert len(hits) == 1, hits
    return 0xc800+hits[0]


def current_episode(seed, art, atlas, row=False, facing=255, proposal=False, capture=None):
    model = B.Q.Sonic.slim_fork(seed)
    if proposal:
        worker = head_worker(model.bundle)
        assert len(worker) <= 33
        assert bytes(model.ram[3][0x10fe:0x111f]) == bytes(33)
        vector = head_vector(bytes(model.ram[2][0x800:0x1fe0]))-0xc000
        model.ram[3][0x10fe:0x10fe+len(worker)] = worker
        model.ram[2][vector:vector+3] = bytes.fromhex('4cfeb0')
    B.N.put(model, SelectedCharacter=38,OperMode=1,OperMode_Task=3,
            GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,
            Player_X_Position=77,Player_PageLoc=1,Player_Y_Position=176,
            Player_Y_HighPos=1,PlayerSize=1,PlayerStatus=0,NmiDisable=255,
            DisableScreenFlag=0,Mirror_PPUMASK=30,Mirror_PPUCTRL=160,
            FamilyMainCommit=1,ReloadCHRBank=0,NumberofLives=2,
            TimerControl=0,AreaType=1,Player_Rel_XPos=77,Player_Rel_YPos=176,
            ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=1,
            ScreenRight_X_Pos=255,ScreenRight_PageLoc=1)
    B.terrain(model,lambda x,y:0xc1 if x==336 and y==144 else
              0x51 if row and 320<=x<400 and y==144 else 0x54 if y>=208 else 0)
    poses = {(p['source_frame'],p['source_facing']):raster(p,atlas) for p in art['poses']}
    rows, previous = [], None
    original = B.N.NesMPU
    hits = []
    effects = []
    return_points = set()
    pending = []
    class Trace(original):
        def step(self):
            if self.pc == B.N.address(model.bundle,'PlayerHeadCollision'):
                effects.append(dict(epoch=epoch,tile=self.a,x=B.N.get(model,'Player_X_Position')|
                                    B.N.get(model,'Player_PageLoc')<<8,
                                    y=B.N.get(model,'Player_Y_Position'),scratch=list(model[3:11])))
            if self.pc == 0xf113:
                ret = (self.memory[0x100+((self.sp+1)&255)]|
                       self.memory[0x100+((self.sp+2)&255)]<<8)+1
                pending.append(ret)
                return_points.add(ret)
            elif self.pc in return_points and pending and self.pc == pending[-1]:
                pending.pop()
                hits.append(dict(tile=self.a,epoch=epoch,x=B.N.get(model,'Player_X_Position')|
                                 B.N.get(model,'Player_PageLoc')<<8,
                                 native_y=B.N.get(model,'Player_Y_Position')))
            return super().step()
    B.N.NesMPU = Trace
    try:
        for epoch in range(180):
            pad = 8 if 16 <= epoch < 100 else 0
            B.N.put(model,FrameCounter=epoch&255,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
            if capture is not None and epoch == 60:
                capture.append(B.Q.Sonic.slim_fork(model))
            B.N.invoke(model,'PlayerCtrlRoutine',a=83,x=0,y=0,p=0x21)
            if epoch == 8:
                model.ram[2][0x615] = facing
            ram = model.ram[2]
            x = B.N.get(model,'Player_X_Position') | B.N.get(model,'Player_PageLoc')<<8
            source_x = int.from_bytes(ram[0x60f:0x611],'little')
            anchor_y = ram[0x611]+int.from_bytes(ram[0x89:0x8b],'little',signed=True)
            key = (x,ram[0x611],ram[0x616],ram[0x617],ram[0x618])
            if key != previous:
                pix = poses.get((ram[0x617],ram[0x615]),{})
                top = min((anchor_y+y for px,y in pix),default=None)
                opaque_block = [(source_x+px,anchor_y+py) for px,py in pix
                                if 336<=source_x+px<352 and 144<=anchor_y+py<160]
                rows.append(dict(epoch=epoch,x=x,native_y=B.N.get(model,'Player_Y_Position'),
                                 source_y=ram[0x611],anchor_y=anchor_y,action=ram[0x616],
                                 pose=ram[0x617],mode=ram[0x618],opaque_top=top,
                                 opaque_in_block=len(opaque_block),
                                 dy=B.N.get(model,'Player_Y_Speed')))
                previous = key
    finally:
        B.N.NesMPU = original
    assert not pending
    return dict(scope='Staged native terrain and initial position; original live controller/physics',
                row=row,facing=facing,rows=rows,head_returns=len(hits),
                nonempty_heads=[v for v in hits if v['tile']],native_effects=effects,
                proposal=proposal,worker_bytes=len(worker) if proposal else 0)


def funding(metadata):
    from check_prince_native_foot_motion_1110 import overlap_funding
    from check_prince_run_support_funding_1110 import geometry
    with contextlib.redirect_stdout(io.StringIO()):
        changed, result = overlap_funding(metadata)
    assert len(changed) == len(metadata)
    assert all(geometry(metadata,f) == geometry(changed,f) for f in range(239))
    used = result['best']['used']
    end = 0xd46e-0xc800
    assert changed[used:end] == bytes([255])*(end-used)
    assert changed[end:] == metadata[end:]
    return dict(exact_239_decoded_pose_records=True,
                proposed_reclaimed_half_open=[0xc800+used,0xd46e],
                reclaimed_bytes=end-used,
                old_metadata_packed_bytes=len(Packet.encode(metadata)),
                proposed_metadata_packed_bytes=len(Packet.encode(changed)),
                strategy=result['best'],
                scope='In-memory exact packet byte sharing only; not a ROM or ISR qualification')


def code_funding(chunks,bundle):
    runtime,metadata,state = chunks
    worker = head_worker(bundle)
    assert runtime[0x10fe:0x111f] == bytes(33)
    vector = head_vector(metadata)-0xc800
    rt = runtime[:0x10fe]+worker+runtime[0x10fe+len(worker):]
    md = metadata[:vector]+bytes.fromhex('4cfeb0')+metadata[vector+3:]
    namespace = dict(Packet.encode.__globals__)
    source = inspect.getsource(Packet.encode).replace('range(3):','range(20):').replace('iteration<2:','iteration<19:')
    exec(source,namespace)
    return dict(worker_bytes=len(worker),worker_hex=worker.hex(),
                code_half_open=[0xb0fe,0xb0fe+len(worker)],declared_slot=[0xb0fe,0xb11f],
                native_head_vector=[vector+0xc800,vector+0xc803],
                proposed_packed_bytes=[len(Packet.encode(rt)),len(Packet.encode(md)),len(Packet.encode(state))],
                extended_dictionary_iterations_runtime=len(namespace['encode'](rt)),
                runtime_staging_limit=6400,
                scope='Source-buffer/RAM-only proposed worker; no rebuilt ROM')


def decoder_funding(head,runtime,bundle):
    from py65.devices.mpu6502 import MPU
    worker = head_worker(bundle)
    data = runtime[:0x10fe]+worker+runtime[0x10fe+len(worker):]
    packed = Packet.encode(data)
    decoder = bytearray(head[31072:Packet.LOADER])
    assert len(decoder) == 254
    wrap, = [i for i in range(len(decoder)-14) if decoder[i:i+2] == bytes.fromhex('c9dc')]
    assert decoder[wrap+4:wrap+7] == bytes.fromhex('a9008d')
    assert decoder[wrap+9:wrap+12] == bytes.fromhex('a9c38d')
    decoder[wrap+5],decoder[wrap+10] = 0x80,0xc2
    load = int.from_bytes(decoder[wrap+7:wrap+9],'little')-1
    remaining, = [int.from_bytes(decoder[i+1:i+3],'little') for i in range(len(decoder)-6)
                  if decoder[i] == 0xad and decoder[i+3] == 0x0d and decoder[i+6] == 0xf0
                  and int.from_bytes(decoder[i+4:i+6],'little') == int.from_bytes(decoder[i+1:i+3],'little')+1]
    labels = dict(PpLdLoad=load,PpLdRemain=remaining,PpLdDecode=0xc000)
    assert decoder[labels['PpLdLoad']-0xc000] == 0xad
    assert decoder.count(bytes.fromhex('9103d103')) == 1
    addresses = list(range(0xc500,0xdc00))+list(range(0xc280,0xc500))
    assert len(addresses) == 6528 and len(packed) <= len(addresses)
    addresses = addresses[:len(packed)]
    class Memory(list):
        watch = False
        cursor = 0
        def __getitem__(self,address):
            if (isinstance(address,int) and self.watch and self.cursor<len(addresses)
                    and address == addresses[self.cursor]):
                self.cursor += 1
            return super().__getitem__(address)
        def __setitem__(self,address,value):
            if isinstance(address,int) and self.watch:
                assert address not in addresses[self.cursor:],('Unread source overwrite',hex(address))
            return super().__setitem__(address,value)
    memory = Memory([0]*65536)
    memory[0xc000:0xc000+len(decoder)] = decoder
    for address,value in zip(addresses,packed,strict=True):
        memory[address] = value
    for address,value in ((labels['PpLdLoad']+1,0xc500),
                          (3,0xa000),(labels['PpLdRemain'],len(data))):
        memory[address:address+2] = value.to_bytes(2,'little')
    memory.watch = True
    cpu = MPU(memory=memory,pc=labels['PpLdDecode'])
    cpu.sp = 224
    cpu.stPushWord(0x5ffe)
    for count in range(1000000):
        if cpu.pc == 0x5fff:
            break
        assert memory[cpu.pc] != 0,hex(cpu.pc)
        cpu.step()
    else:
        raise AssertionError(('Decoder instruction bound',hex(cpu.pc)))
    assert cpu.sp == 224
    assert memory.cursor == len(packed)
    assert bytes(memory[0xa000:0xa000+len(data)]) == data
    return dict(actual_6502_decoder=True,decoded_bytes=len(data),packed_bytes=len(packed),
                proposed_staging_capacity=6528,spare_bytes=6528-len(packed),
                proposed_wrap=0xc280,current_wrap=0xc300,
                decoder_wrap_immediate_addresses=[0xc000+wrap+5,0xc000+wrap+10],
                decoder_bytes_unchanged=254,unread_source_preserved=True,
                instructions=count,source_bytes_consumed=memory.cursor,
                scope='Actual revised decoder only; Stage insertion, loader offsets and complete cold admission remain unqualified')


def full_cold(raw,interrupts=False):
    import prince_pickup_reach_1112 as Source
    from prepare_prince_climb_funded_1109_v1 import live
    changed,chunks,layout = Source.transform(raw)
    new_head,extracted,packed_lengths = Packet.extract(changed)
    assert extracted == chunks and len(new_head) == Source.STREAMS
    assert tuple(packed_lengths) == tuple(layout['packed_bytes'])
    assert Source.reverse(changed) == raw
    format_roundtrips = []
    for image in (raw,changed):
        old_header,old_chunks,_ = Packet.extract(image)
        def one_byte(runtime,metadata,state):
            state[-1] ^= 1
            return runtime,metadata,state
        rebuilt,_ = Packet.rebuild(image,one_byte)
        header,parts,_ = Packet.extract(rebuilt)
        assert len(header) == len(old_header)
        assert parts[:2] == old_chunks[:2]
        assert parts[2][:-1] == old_chunks[2][:-1] and parts[2][-1] == old_chunks[2][-1]^1
        format_roundtrips.append(len(header)-Packet.LOADER)
    model = B.Q.Sonic.O.blank(B.C.Start.W.bundle(changed))
    bus = type(model)
    read,write,native = bus.__getitem__,bus.__setitem__,B.N.NesMPU
    active,stages = None,[]
    cuts,depth = set(),224
    if interrupts:
        import check_sonic_seventh_cold_vectors_1110 as ColdISR
        watch = {pc+4 if pc>=layout['insert_PC'] else pc for pc,_,_ in layout['relocations']}
        watch.update((layout['insert_PC'],layout['insert_PC']+2,
                      layout['insert_PC']+4,layout['insert_PC']+6,0xc0bc,0xc0c1))
        loader_head = b''.join(changed[Packet.CHR+p*1024:Packet.CHR+(p+1)*1024] for p in Packet.PAGES)
        loader = loader_head[Packet.LOADER:Source.STREAMS]
        data_op, = [i+0xc100-97 for i in range(97,396) if loader[i:i+5] == bytes.fromhex('9103d103d0')]
    configs = ((0xc500,0xa000,len(chunks[0]),layout['packed_bytes'][0]),
               (layout['metadata_input'],0xc800,len(chunks[1]),layout['packed_bytes'][1]),
               (0xc300,0xc100,len(chunks[2]),layout['packed_bytes'][2]))
    class Trace(native):
        def step(self):
            nonlocal active,depth
            if self.memory is model and self.pc == 0xc000 and model.rawtags[2] == 2:
                if active is not None:
                    assert active['cursor'] == len(active['addresses'])
                    stages.append(dict(stage=len(stages),consumed=active['cursor'],
                                       minimum_unread_margin=active['margin']))
                start,dest,size,count = configs[len(stages)]
                stop = min(start+count,0xdc00)
                addresses = list(range(start,stop))+list(range(Source.WRAP,Source.WRAP+count-(stop-start)))
                assert len(addresses) == len(set(addresses)) == count
                active = dict(dest=dest,size=size,addresses=addresses,
                              indices={address:i for i,address in enumerate(addresses)},
                              cursor=0,margin=65536)
            if interrupts and self.memory is model and self.pc in watch and model.rawtags[2] == 2:
                key = (self.pc,self.sp,self.p&4,len(stages),model[data_op])
                if key not in cuts:
                    cuts.add(key)
                    B.Q.Sonic.O.clear_logs(model)
                    depth = min(depth,ColdISR.V.interrupt(ColdISR.clone(self),'FF'))
            return super().step()
    def reader(self,key):
        if self is model and active is not None and isinstance(key,int):
            index = active['cursor']
            if index<len(active['addresses']) and key == active['addresses'][index]:
                active['cursor'] += 1
        return read(self,key)
    def writer(self,key,value):
        if self is model and active is not None and isinstance(key,int):
            if active['dest']<=key<active['dest']+active['size']:
                index = active['indices'].get(key)
                if index is not None:
                    assert index < active['cursor'],('Unread source overwritten',len(stages),hex(key),index,active['cursor'])
                    active['margin'] = min(active['margin'],active['cursor']-index)
        return write(self,key,value)
    with patch.object(bus,'__getitem__',reader),patch.object(bus,'__setitem__',writer),\
         patch.object(B.N,'NesMPU',Trace),patch.object(B.Q.Sonic.O,'NesMPU',Trace):
        result = B.Q.Sonic.C.cold(model,38,None)
    assert active['cursor'] == len(active['addresses'])
    stages.append(dict(stage=len(stages),consumed=active['cursor'],minimum_unread_margin=active['margin']))
    assert len(stages) == 3
    assert bytes(model.ram[3][:len(chunks[0])]) == live(chunks[0])
    assert bytes(model.ram[2][0x800:0x800+len(chunks[1])]) == chunks[1]
    assert B.Q.Sonic.O.headers(model) == (bytes.fromhex(layout['cookie']),)*2
    assert B.Q.Sonic.C.invoke(model,B.Q.Sonic.O.AUTH)['P']&1
    assert raw[:Packet.COOKIE]+raw[Packet.COOKIE+16:Packet.CHR] == \
           changed[:Packet.COOKIE]+changed[Packet.COOKIE+16:Packet.CHR]
    assert all(raw[Packet.CHR+page*1024:Packet.CHR+(page+1)*1024] ==
               changed[Packet.CHR+page*1024:Packet.CHR+(page+1)*1024]
               for page in range(1024) if page not in Packet.PAGES)
    return dict(layout=layout,actual_cold=result,three_staged_inputs=stages,
                exact_live_runtime=True,exact_metadata=True,both_headers=True,
                native_authentication=True,ROM_written=False,
                exact_parent_reverse_SHA256=sha256(Source.reverse(changed)).hexdigest(),
                extract_rebuild_loader_formats=format_roundtrips,
                changed_cold_FFNMI_cuts=len(cuts),cold_ISR_minimum_SP=depth if cuts else None,
                scope='Complete actual current resident/PPU/copy/reread/decode/finalize/constructor; no emulator or delivery')


def slot_closure(chunks,seed):
    from py65.devices.mpu6502 import MPU
    from py65.disassembler import Disassembler
    from check_prince_exposed_brick_idle_1111 import material_domain
    runtime,metadata,state = chunks
    assert runtime[0x10ef:0x10fe] == bytes.fromhex('ad69b3291fc91fd0034c17a94c0bc4')
    assert runtime[0x10fe:0x111f] == bytes(33)
    absolute = [(origin+i,int.from_bytes(chunk[i+1:i+3],'little'))
                for origin,chunk in ((0xa000,runtime),(0xc800,metadata),(0xc0b0,state))
                for i in range(len(chunk)-2) if chunk[i] in (0x20,0x4c)
                and 0xb0fe<=int.from_bytes(chunk[i+1:i+3],'little')<0xb11f]
    assert not absolute,absolute
    memory = [0]*65536
    memory[0xa000:0xa000+len(runtime)] = runtime
    decoder = Disassembler(MPU(memory=memory))
    branches = []
    pc = 0xb06c
    while pc < 0xb1a2:
        size,operation = decoder.instruction_at(pc)
        assert operation != '???',hex(pc)
        if memory[pc]&0x1f == 0x10:
            target = int(operation.rsplit('$',1)[1],16)
            if 0xb0fe<=target<0xb11f:
                branches.append((pc,target))
        pc += size
    assert not branches,branches
    vector_words = [int.from_bytes(runtime[i:i+2],'little') for i in range(0x1ba1,0x1bc1,2)]
    assert all(not 0xb0fe<=target<0xb11f for target in vector_words)
    assert runtime[0x10eb:0x10ef] == bytes.fromhex('c904d030')
    return dict(slot=[0xb0fe,0xb11f],current_coordinate_wrapper_ends_at=0xb0fe,
                current_wrapper_paths='JMP A917 or JMP C40B; neither falls through',
                absolute_entries=absolute,relative_entries=branches,
                original_animation_vector_entries=len(vector_words),
                exact_material_provider_returns=material_domain(seed))


def main():
    raw = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    assert sha256(raw).hexdigest() == PIN
    head, chunks, packed = Packet.extract(raw)
    art = json.loads((O/'source-art.json').read_text())
    atlas = (O/'prince-body-8x16.chr').read_bytes()
    assert sha256(atlas).hexdigest() == '477c6856e7d349aab73aedef65cc69b233714e1809e1fdbf2322f9977a223a8b'
    reach = []
    for pose in art['poses']:
        if pose['source_frame'] not in (15,77,78,79,80):
            continue
        pix = raster(pose,atlas)
        top = min(y for x,y in pix)
        reach.append(dict(pose=pose['source_frame'],facing=pose['source_facing'],
                          top=top,upper_rows=[dict(y=y,x=sorted(x for x,py in pix if py==y))
                          for y in range(top,min(top+5,0))],
                          geometry=pose['source_projection_geometry']))
    seed, cold = B.cold(raw)
    original_slot_closure = slot_closure(chunks,seed)
    names = ('HuHead','HuFullBox','PlayerHeadCollision','PlayerBGCollision','PlayerCtrlRoutine',
             'BillBGHeadConsumer','BlockBufferColli_Head','HuMain','Player_Y_Position')
    symbols = {}
    for name in names:
        try:
            symbols[name] = B.N.address(seed.bundle,name)
        except (KeyError,AssertionError,ValueError):
            pass
    captures = []
    episodes = [current_episode(seed,art,atlas,row,facing)
                for row,facing in ((False,255),(True,255),(True,0))]
    episodes.append(current_episode(seed,art,atlas,True,255,True,captures))
    assert not episodes[1]['native_effects'] and not episodes[2]['native_effects']
    assert episodes[1]['head_returns'] == episodes[2]['head_returns'] == 180
    assert len(episodes[3]['native_effects']) == 1
    assert episodes[3]['native_effects'][0]['tile'] == 0xc1
    assert episodes[3]['native_effects'][0]['y'] == 173
    assert [{k:v for k,v in row.items() if k!='dy'} for row in episodes[1]['rows']] == \
           [{k:v for k,v in row.items() if k!='dy'} for row in episodes[3]['rows']]
    head_interrupts = None
    if '--interrupts' in sys.argv:
        def head_call(model):
            result = B.N.invoke(model,'PlayerCtrlRoutine',a=83,x=0,y=0,p=0x21)
            return result['A'],result['X'],result['Y'],result['P']&0xef
        head_interrupts = B.Async.stress('real pose78 PlayerCtrlRoutine head projection',captures[0],
            head_call,
            [(3,0xb0fe,0xb11d)])
    report = dict(rom_SHA256=PIN,donor_SHA256=P.SHA,
                         original_slot_closure=original_slot_closure,
                         animations={action:animation(action) for action in (3,4,14)},
                         opaque_reach=reach,actual_current_symbols=symbols,
                         decoded_bytes=list(map(len,chunks)),packed_bytes=packed,
                         carrier_spare=len(Packet.PAGES)*1024-len(head)-sum(packed),
                         export_code=bytes(seed.ram[2][0x383:0x409]).hex(),
                         proposed_funding=funding(chunks[1]),
                         proposed_code_funding=code_funding(chunks,seed.bundle),
                         proposed_decoder_funding=decoder_funding(head,chunks[0],seed.bundle),
                         full_cold=full_cold(raw,'--interrupts' in sys.argv),head_interrupts=head_interrupts,
                         current_episodes=episodes,output_files=0)
    report['receipt_SHA256'] = sha256(json.dumps(report,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if '--summary' in sys.argv:
        print(json.dumps({k:report[k] for k in ('rom_SHA256','proposed_code_funding',
                         'proposed_decoder_funding','full_cold','head_interrupts','receipt_SHA256','output_files')}))
    else:
        print(json.dumps(report))


if __name__ == '__main__':
    main()
