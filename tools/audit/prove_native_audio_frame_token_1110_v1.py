"""Prove current ground music data fit and source-owned decoder funding."""

from collections import Counter
from itertools import product
import json
from pathlib import Path

from audit_mini_audio_mask_feasibility_1108_v3 import project_stream,stream
from build_playlist_audio import lz
import measure_mini_audio_1108_v1 as M

R,N = M.ROOT,M.N
BASE = R/'build/mini-lane-audio-native-1110/candidate.nes'
PIN = 'a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746'
OUT = R/'build/native-audio-frame-token-1110'
PREFIXES = ('XgArea','XgLoop','XgEvent','XgEventLoop')
LEFT,RIGHT = (0,2,3),(4,6,7)
BOUND = 63


def offset(bank,pc):
    return 16+8192*bank+(pc&8191)


def matrices(b):
    raw = b['raw']
    tables,readers,foreign = [],{},[]
    for prefix in PREFIXES:
        names = [prefix+s for s in ('Banks','Lo','Hi')]
        starts = [M.location(b,n) for n in names]
        assert starts[1]-starts[0]==starts[2]-starts[1]==BOUND
        addresses = [M.address(b,n) for n in names]
        old = bytes((0xbd,addresses[0]&255,addresses[0]>>8,0x8d,0x39,0x6f,
                     0xbd,addresses[1]&255,addresses[1]>>8,0x85,0xde,
                     0xbd,addresses[2]&255,addresses[2]>>8,0x85,0xdf))
        assert raw.count(old)==1
        where = raw.index(old)
        assert (where-16)//8192==38
        readers[prefix] = 0xc000+((where-16)&8191)
        for a in addresses:
            key = bytes((0xbd,a&255,a>>8))
            if a != 0xc000:
                assert raw[16:1048592].count(key)==1, (prefix,hex(a))
                continue
            # Three ordinary art readers use the same CPU address after a
            # physically different C-window bank has been selected.
            for pose,art,rel in (('KbSetPose','KbArtStart',0x9df),
                                 ('TnSetPose','TnArtStart',0xcf3),
                                 ('JnSetPose','JnArtStart',0x295)):
                entry = M.location(b,pose)
                prg = (entry-16)//8192
                tag = (M.location(b,art)-16)//8192|128
                match = 16+8192*prg+rel
                packet = bytes((0xa9,tag,0x8d,0xa1,0x7d,0xa9,tag,0x8d,0x16,0x51))
                assert raw[entry:entry+len(packet)]==packet and raw[match:match+3]==key
                assert tag!=166 and b'\x8d\x16\x51' not in raw[entry+len(packet):match]
                foreign.append(dict(pose=pose,physical_PRG=prg,physical_C_bank=tag&127))
            assert raw[16:1048592].count(key)==1+len(foreign)
        tables.append(tuple(zip(*(raw[at:at+BOUND] for at in starts),strict=True)))
    assert M.location(b,'XgMacroLo')-M.location(b,'XgAreaBanks')==BOUND*3*4
    return tables,readers,foreign


def table_compression(tables):
    distinct = list(dict.fromkeys(record for group in tables for record in group))
    assert len(distinct)==66
    to_index = {record:i for i,record in enumerate(distinct)}
    row_indices = [bytes(to_index[record] for record in group) for group in tables]
    row_data = [bytes(values) for values in zip(*distinct,strict=True)]
    packed = b''.join(row_indices+row_data)
    assert len(packed)==450
    for group,index in zip(tables,row_indices,strict=True):
        assert group==tuple(tuple(values[i] for values in row_data) for i in index)
    return packed,dict(original_bytes=756,compact_bytes=450,unique_records=len(distinct),
                       exact_recovered_CPU_half_open=[0xc1c2,0xc2f4],available_code_bytes=306)


def ground_loop(b,tables):
    raw = b['raw']
    bank,lo,hi = tables[1][7]
    start = offset(bank,lo|hi<<8)
    assert (bank,lo|hi<<8,start)==(57,0xb74c,0x7375c)
    pointers = [(kind,i) for kind,group in zip(PREFIXES,tables,strict=True)
                for i,(bno,l,h) in enumerate(group) if offset(bno,l|h<<8)==start]
    assert pointers==[('XgLoop',7)]
    ml,mh = [M.location(b,'XgMacro'+s) for s in ('Lo','Hi')]
    macros = [offset((ml-16)//8192,raw[ml+i]|raw[mh+i]<<8) for i in range(mh-ml)]
    frames,old_bytes,macro_bytes,macro_calls,terminal = project_stream(raw,start,macros)
    assert (len(frames),old_bytes,terminal)==(3264,1132,255)
    overlap = [(kind,i) for kind,group in zip(PREFIXES,tables,strict=True)
               for i,(bno,l,h) in enumerate(group) if start<offset(bno,l|h<<8)<start+old_bytes]
    assert not overlap
    assert all(f[-1]==(21,15) and tuple(k for k,v in f)==tuple(sorted({k for k,v in f}))
               for f in frames)

    def tri(f, regs):
        out = dict(f)
        assert all(v!=255 for k,v in f if k in regs)
        return bytes(out.get(k,255) for k in regs)

    for f in frames:
        assert all(k in (*LEFT,*RIGHT,21) for k,v in f),f
    a,b = ([tri(f,regs) for f in frames] for regs in (LEFT,RIGHT))
    p1 = [key for key,count in Counter(a).most_common()]
    p2 = list(dict.fromkeys(b))
    assert (len(p1),len(p2))==(22,44)
    pairing = Counter(zip(a,b,strict=True))
    ids,ends,second = {},[],[]
    for left in p1:
        for right in p2:
            if (left,right) not in pairing:
                continue
            ids[left,right] = len(second)
            second.append(p2.index(right))
        ends.append(len(second))
    assert len(second)==149
    tokens = bytes(ids[t] for t in zip(a,b,strict=True))+b'\xff'
    packed = lz(tokens)
    assert len(packed)==735
    sequence = stream(packed,0)
    for i in range(len(frames)+1):
        tok,read = next(sequence)
        if i==len(frames):
            assert tok==255 and read==len(packed)
            break
        first = next(j for j,end in enumerate(ends) if tok<end)
        out = [(reg,val) for regs,values in ((LEFT,p1[first]),(RIGHT,p2[second[tok]]))
               for reg,val in zip(regs,values,strict=True) if val!=255]
        assert tuple(out)+((21,15),)==frames[i],i
    # Maps to the original LZ bytes, and to exact per-frame original ordered
    # register image updates. No raw byte or timing quantization changes.
    data = packed + bytes(second) + bytes(ends) + b''.join(p1) + b''.join(p2)
    assert len(data)==1104 and len(data)<=old_bytes
    return data,dict(original_frames=len(frames),old_bytes=old_bytes,new_bytes=len(data),
                     spare_bytes=old_bytes-len(data),physical_PRG=bank,file_offset=start,
                     CPU_half_open=[0xb74c,0xbbb8],stored_AudioBank=57,logical_owners=[7],
                     sole_track_table_reader=pointers,frame_token_count=len(second),
                     packed_token_bytes=len(packed),last_pointer_CPU=0xb74c+len(packed),
                     voice_packet_counts=[len(p1),len(p2)],left_registers=list(LEFT),
                     right_registers=list(RIGHT),constant_ordered_status=[21,15],
                     original_macro_calls=macro_calls,original_macro_reads=macro_bytes)


def prove_actual_readers(b,readers):
    seen = Counter()
    max_x = Counter()
    cpu = N.NesMPU
    points = {pc:name for name,pc in readers.items()}

    class Trace(cpu):
        def step(self):
            name = points.get(self.pc)
            if name and self.memory.rawtags[2]==166:
                assert self.x<BOUND,(name,self.x,N.get(self.memory,'SelectedCharacter'))
                seen[name,self.x] += 1
                max_x[name] = max(max_x[name],self.x)
            return cpu.step(self)

    seeds = [M.seed(b,who) for who in range(42)]
    for who,s in enumerate(seeds):
        for kind,choice,alt in product(('AreaMusicQueue','EventMusicQueue'),(1,2,4,8,16,32,64),(0,1)):
            m = N.fork(s)
            N.put(m,KbVariant=alt)
            N.put(m,**{kind:choice})
            N.NesMPU = Trace
            try:
                M.direct(m,'AudioUpdate',Trace)
            finally:
                N.NesMPU = cpu
    assert all(any(k==name for k,_ in seen) for name in ('XgArea','XgEvent'))
    return dict(staged_public_AudioUpdate_calls=42*2*7*2,
                reader_visits={name:sum(v for (k,x),v in seen.items() if k==name) for name in readers},
                actual_indices={name:sorted(x for (k,x),v in seen.items() if k==name) for name in readers},
                actual_reader_CPU=readers,actual_max_index=dict(max_x),
                notes='Loop selectors reread the respective saved area or event index. Cold first-frame fixtures need not naturally reach the original long loop.')


def main():
    raw = BASE.read_bytes()
    assert M.sha(raw)==PIN
    b = M.bundle(raw)
    rows,readers,foreign = matrices(b)
    table,funding = table_compression(rows)
    data,codec = ground_loop(b,rows)
    print('Music data fit',codec,'funded code',funding,flush=True)
    reachable = prove_actual_readers(b,readers)
    OUT.mkdir(exist_ok=True)
    (OUT/'ground-loop.bin').write_bytes(data)
    (OUT/'song-pointer-table.bin').write_bytes(table)
    paths = (Path(__file__),R/'src/expanded_audio.s',R/'src/expanded_music.inc',
             R/'src/full_roster_music.inc',OUT/'ground-loop.bin',OUT/'song-pointer-table.bin')
    q = dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
             scope='Source-owned data/code funding, exact old and proposed music-frame register lists. No runtime code, patched ROM or native timing claim yet.',
             funding=funding,codec=codec,reader_closure=reachable,foreign_C000_art_aliases=foreign,
             bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes()) for p in paths})
    (OUT/'format-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(reachable,flush=True)


if __name__=='__main__':
    main()
