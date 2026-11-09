"""Assemble and compare the funded frame-token player without writing a ROM."""

from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import prove_native_audio_frame_token_1110_v1 as F
from check_mini_funded_actor_1108_v3 import install

M,N,R,OUT = F.M,F.N,F.R,F.OUT
SOURCE = R/'tools/reference/native_audio_frame_token_1110_v1.s'
FORMAT = OUT/'format-proof.json'
NEW_CODE, LIMIT = 0xc1c2,0xc2f4


def source_patch(raw, *, assemble=True):
    q = json.loads(FORMAT.read_text())
    assert q['passed'] and q['parent_SHA256']==M.sha(raw)==F.PIN
    for file,digest in q['bindings'].items():
        assert M.sha((R/file).read_bytes())==digest,file
    b = M.bundle(raw)
    tables,readers,_ = F.matrices(b)
    prefix = b'\x4c'
    cfg,obj,binary,labels_file = (OUT/f'player.{ext}' for ext in ('cfg','o','bin','lbl'))
    if assemble:
        cfg.write_text('MEMORY{C:start=$C1C2,size=$0132,file=%O;}SEGMENTS{CODE:load=C,type=ro;}\n')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',labels_file],check=True)
        obj.unlink()
    labels = {line.split()[2][1:]:int(line.split()[1],16) for line in labels_file.read_text().splitlines()}
    code = binary.read_bytes()
    assert labels['ReadSongPointer']==NEW_CODE and labels['EndCode']==NEW_CODE+len(code)<=LIMIT
    patches = []

    def row(bank,pc,new,role):
        at = F.offset(bank,pc)
        patches.append(dict(file_offset=at,physical_PRG=bank,CPU_half_open=[pc,pc+len(new)],
            old_hex=raw[at:at+len(new)].hex(),new_hex=new.hex(),role=role))

    ptr = (OUT/'song-pointer-table.bin').read_bytes()
    assert len(ptr)==450 and len(ptr)+len(code)<=756
    row(38,0xc000,(ptr+code).ljust(756,b'\xea'),'existing song pointer table and funded player')
    for i,name in enumerate(F.PREFIXES):
        pc = readers[name]
        record = 0xc000+i*63
        continuation = pc+16
        emitted = b'\xbd'+record.to_bytes(2,'little')+b'\x20'+NEW_CODE.to_bytes(2,'little')
        emitted += prefix+continuation.to_bytes(2,'little')
        row(38,pc,emitted.ljust(16,b'\xea'),'exact song pointer load '+name)
    pc = M.address(b,'CodecCommands')
    assert pc==0xc94c and raw[F.offset(38,pc):F.offset(38,pc)+10]==bytes.fromhex('ad376fc90d90034cf6c9')
    row(38,pc,(prefix+labels['GroundCodecDispatch'].to_bytes(2,'little')).ljust(10,b'\xea'),
        'one admission per decoded music frame')

    old = (OUT/'ground-loop.bin').read_bytes()
    tokens,offsets,ends,lvoices,rvoices = old[:735],old[735:884],old[884:906],old[906:972],old[972:]
    # Identical records as the proven data. Co-locate a voice group's upper
    # bound with its three values and store right-record byte offsets directly.
    left = b''.join(bytes([end])+lvoices[3*i:3*i+3] for i,end in enumerate(ends))
    reorganized = tokens + bytes(i*3 for i in offsets) + left + rvoices
    assert len(reorganized)==len(old)==1104
    row(57,0xb74c,reorganized.ljust(1132,b'\xff'),'same ground loop, exact ordered frame tokens')
    return install(raw,patches),patches,labels,len(code)


def external_state(a,b,packed=False):
    address = lambda n:M.address(a.bundle,n)
    intervals = [(address('XgAudioPtr'),address('XgLzSavedY')+1),
                 (address('XgAudioBank'),address('XgAudioBank')+1),
                 (address('XgAudioDepth'),address('XgAudioStackBank')+32),
                 (address('XgLzHistory'),address('XgLzHistory')+2048)]
    # Compare all normal mutable RAM, excluding only proven decoder-private
    # history/cursors. Original macro frames may suspend a recursion between
    # ticks. New packed frames do not create a live macro stack.
    regions = [(0,0x100),(0x15a,0x17b),(0x200,0x8000)]
    excluded = set(i for lo,hi in intervals for i in range(lo,hi))
    flat = lambda m,lo,hi:list.__getitem__(m,slice(lo,hi))
    for lo,hi in regions:
        aa,bb = flat(a,lo,hi),flat(b,lo,hi)
        assert all(at in excluded for at,(x,y) in enumerate(zip(aa,bb),lo) if x!=y),(
            'external RAM',[(hex(at),x,y) for at,(x,y) in enumerate(zip(aa,bb),lo)
                            if x!=y and at not in excluded][:8])
    def hardware(m):
        # The original can suspend in a C38 macro between video ticks and
        # select A38 as its old resume mapping. Packed data selects A57.
        # Exclude only those writes at two bound physical decoder sites.
        ignored = set(m.packed_map_sites) if packed else set()
        return [(at,v) for i,(at,v) in enumerate(m.writes) if i not in ignored and (
            0x4000<=at<=0x4017 or 0x5000<=at<=0x5015 or 0x5114<=at<=0x5130
            or at in (0x2000,0x2001,0x2005,0x2006,0x2007))]
    aa,bb = [hardware(m) for m in (a,b)]
    assert aa==bb,('ordered APU/PPU and external mapper writes',packed,aa,bb)
    assert a.rawtags==b.rawtags and a.ram==b.ram and a.chr_latches==b.chr_latches
    return intervals


def frame_pair(pair,fields,trace=None):
    for m in pair:
        m.writes.clear()
        m.packed_map_sites = []
        N.put(m,**fields)
    old = M.direct(pair[0],'AudioUpdate',trace)
    new = M.direct(pair[1],'AudioUpdate',trace)
    assert old[1]==new[1],('outer AXYP/SP',fields,old,new)
    return old[0]-new[0]


def whole_ground(images,labels):
    out = {}
    cpu = N.NesMPU
    notes = []
    for who in (7,41):
        pair = [M.seed(b,who) for b in images]
        stats = Counter()
        saves = []
        intro = []

        class Trace(cpu):
            def step(self):
                m = self.memory
                if m.rawtags[2]==166:
                    if self.pc==labels['GroundLoopFrame'] and m.bundle is pair[1].bundle:
                        stats['packed_entry'] += 1
                    if self.pc in (0xc949,0xcaea) and self.a in (0xa6,0xb9):
                        assert bytes(m[self.pc:self.pc+3])==b'\x8d\x15\x51'
                        m.packed_map_sites.append(len(m.writes))
                return cpu.step(self)

        # Includes initial 129 ticks, a complete 3264-tick loop and its real
        # natural next-loop branch. No source clock or sound outcome seeded.
        for t in range(129+3264+4):
            fields = dict(AreaMusicQueue=int(t==0),FrameCounter=t&255,
                          Square1SoundQueue=32 if t in (180,409,1260) else 0,
                          Square2SoundQueue=1 if t in (250,653) else 0,NoiseSoundQueue=0)
            before = stats['packed_entry']
            delta = frame_pair(pair,fields,Trace)
            notes = external_state(*pair,packed=stats['packed_entry']>before)
            if stats['packed_entry']==before:
                intro.append(delta)
            else:
                saves.append(delta)
        assert len(saves)==3268 and len(intro)==129,(who,len(saves),len(intro))
        assert stats['packed_entry']==len(saves)+1,'Both packed loop terminator and first new frame'
        out[who] = dict(ordered_output_frames=len(saves),source_intro_frames=len(intro),
                        packed_min=min(saves),packed_max=max(saves),packed_mean=sum(saves)/len(saves),
                        intro_min=min(intro),intro_max=max(intro),packed_entries=stats['packed_entry'])

        # Hurry's original track takes its first tick from its own intro,
        # then $1C enters the same ground loop with AudioEvent still set.
        # For Mini also continue through a natural FF/LoopEvent round-trip.
        cave = 27+3264+22 if who==41 else 206
        restart = cave+43
        timeline = {0:dict(GamePauseStatus=1),12:dict(GamePauseStatus=0),26:dict(EventMusicQueue=64),
                    cave:dict(AreaMusicQueue=4),restart:dict(AreaMusicQueue=1)}
        transitions = []
        for t in range(restart+181):
            n = stats['packed_entry']
            fields = {'FrameCounter':t&255}|timeline.get(t,{})
            frame_pair(pair,fields,Trace)
            try:
                external_state(*pair,packed=stats['packed_entry']>n)
            except AssertionError as cause:
                names = ('XgAudioCharacter','XgAudioStatus','XgAudioBank','XgAudioPtr',
                         'XgAudioEvent','XgAudioDepth','XgAudioSelection','XgAudioEventSelection')
                raise AssertionError(('ground transition',who,t,fields,
                    [{name:N.get(m,name) for name in names}|{'pointer_high':N.get(m,'XgAudioPtr',1)}
                     for m in pair],cause.args)) from cause
            transitions.append(stats['packed_entry']>n)
        assert not any(transitions[:12]) and any(transitions[12:26])
        assert not transitions[26] and all(transitions[27:27+min(3264,cave-27)])
        assert not any(transitions[cave:restart+129]) and all(transitions[restart+129:])
        out[who]['transition_ticks'] = len(transitions)
        out[who]['hurry_packed_ticks'] = sum(transitions[27:cave])
    return out,notes


def foreign(images):
    rows = {}
    for who in range(42):
        pair = [M.seed(b,who) for b in images]
        for t in range(28):
            frame_pair(pair,dict(FrameCounter=t,AreaMusicQueue=4 if t in (0,7) else 0,
                           EventMusicQueue=64 if t==10 else 0,Square1SoundQueue=32 if t==2 else 0))
            M.compare_state(*pair)
        rows[who] = 28
    return rows


def main():
    raw = F.BASE.read_bytes()
    after,patches,labels,size = source_patch(raw)
    images = [M.bundle(b) for b in (raw,after)]
    records,excluded = whole_ground(images,labels)
    print('Actual ground music',records,flush=True)
    others = foreign(images)
    q = dict(passed=True,parent_SHA256=F.PIN,expected_memory_only_SHA256=M.sha(after),
        source_CPU_only=True,ROM_written=False,patches=patches,code_bytes=size,labels=labels,
        actual_ground_loop=records,untouched_mode_exact_audio_updates=sum(others.values()),
        private_decoder_state_differences_half_open=excluded,
        scope='Actual linked whole AudioUpdate intro, full loop, next-loop, pause, hurry and area restart. Ordered APU/MMC5/PPU writes and external RAM/AXYP/map parity. Private compressed state differs during the ground loop.',
        bindings={f.relative_to(R).as_posix():M.sha(f.read_bytes())
                  for f in (Path(__file__),SOURCE,FORMAT,OUT/'player.bin',OUT/'player.lbl')})
    (OUT/'runtime-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(q['expected_memory_only_SHA256'],size,q['untouched_mode_exact_audio_updates'],flush=True)


if __name__=='__main__':
    main()
