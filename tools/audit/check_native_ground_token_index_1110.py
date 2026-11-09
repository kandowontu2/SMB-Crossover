"""Qualify a source-funded index for the exact packed ground-theme decoder."""

import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_audio_frame_token_1110_v1 as Token
import check_native_raw_offscreen_tail_1110 as Current
from check_mini_funded_actor_1108_v3 import install


F,M,N,R = Token.F,Token.M,Token.N,Token.R
BASE,PIN = Current.BASE,Current.PIN
SOURCE = R/'tools/reference/native_ground_token_index_1110_v1.s'
SPANS = (('DECODER',38,0xc217,0xc2f4),('TIMED_OFFSETS',57,0xbb9c,0xbbb8))
DECODE = 0xc228


def records(raw):
    format_proof = json.loads(Token.FORMAT.read_text())
    runtime = json.loads((Token.OUT/'runtime-proof.json').read_text())
    assert format_proof['passed'] and runtime['passed']
    assert format_proof['codec']['CPU_half_open']==[0xb74c,0xbbb8]
    assert format_proof['codec']['spare_bytes']==28
    for row in runtime['patches']:
        if row['physical_PRG'] in (38,57):
            start = row['file_offset']
            data = bytes.fromhex(row['new_hex'])
            assert raw[start:start+len(data)]==data,row['role']
    code_end = runtime['labels']['EndCode']
    assert code_end==0xc2a4 and runtime['labels']['GroundLoopFrame']==0xc217
    at = lambda p:F.offset(57,p)
    raw_tokens = raw[at(0xb74c):at(0xba2b)]
    tokens = []
    for token,used in F.stream(raw_tokens,0):
        if token==255:
            break
        tokens.append(token)
    assert (len(tokens),used)==(3264,735) and set(tokens)==set(range(149))
    left = [raw[at(0xbac0)+4*i:at(0xbac0)+4*i+4] for i in range(22)]
    right = [raw[at(0xbb18)+3*i:at(0xbb18)+3*i+3] for i in range(44)]
    assert sorted({row[0] for row in left})==[row[0] for row in left] and left[-1][0]==149
    assert left[0]==b'\x08\xff\xff\xff' and left[6][0]==53
    assert all(row[1]!=255 and row[2:]==b'\xff\xff' for row in left[1:7])
    assert all(255 not in row[2:] for row in left[7:])
    assert all(row[2]!=255 or row[1]==255 for row in right)
    assert [i for i,row in enumerate(right) if row[1]==255 and row[2]!=255]==[29,41]
    offsets = raw[at(0xba2b):at(0xbac0)]
    assert set(offsets)=={3*i for i in range(44)}
    group = [next(i for i,row in enumerate(left) if token<row[0]) for token in range(149)]
    volume = bytes(left[group[token]][1] for token in range(8,53))
    bucket = bytes(4*group[lower] for lower in range(52,149,4))
    assert len(volume)==45 and len(bucket)==25
    for token in range(53,149):
        row = bucket[(token>>2)-13]//4
        assert row<=group[token] and group[token]-row<=2
        assert next(i for i in range(row,22) if token<left[i][0])==group[token]
    return tokens,volume,bucket


def compose(raw,output):
    assert M.sha(raw)==PIN
    tokens,volume,bucket = records(raw)
    with tempfile.TemporaryDirectory(prefix='link-',dir=output) as temp:
        work = Path(temp)
        cfg,obj,data,lbl = (work/f'ground.{ext}' for ext in ('cfg','o','bin','lbl'))
        cfg.write_text('MEMORY {\n'+''.join(f'{name}:start=${lo:04x},size={hi-lo},file=%O;\n'
            for name,_,lo,hi in SPANS)+'}\nSEGMENTS {\n'+''.join(f'{name}:load={name},type=ro;\n'
            for name,*_ in SPANS)+'}\n',encoding='utf-8')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',data,'-Ln',lbl],check=True)
        labels = {line.split()[2][1:]:int(line.split()[1],16) for line in lbl.read_text().splitlines()}
        linked = data.read_bytes()
    assert labels['GroundLoopFrame']==0xc217 and labels['DecodeToken']==DECODE
    assert labels['TimedBucket']==0xbb9c and labels['EndDecoder']<=0xc2f4
    lo = labels['VolumeForToken']-0xc217
    assert linked[lo:lo+45]==volume and linked[-28:]==bucket+b'\xff'*3
    rows = []
    for role,bank,lo,hi in SPANS:
        at,n = F.offset(bank,lo),hi-lo
        old,new = raw[at:at+n],linked[:n]
        linked = linked[n:]
        assert len(old)==len(new)==n
        if bank==38:
            assert old[:DECODE-lo]==new[:DECODE-lo]  # Same loop/corrupt dispatch.
        else:
            assert old==b'\xff'*28
        rows.append(dict(role=role,physical_PRG=bank,CPU_half_open=[lo,hi],file_offset=at,
                         old_hex=old.hex(),new_hex=new.hex()))
    assert not linked
    return install(raw,rows),rows,labels,tokens


def exact_state(a,b):
    M.compare_state(a,b)
    # Audio queue variables occupy the bottom of the stack page. Return
    # address bytes above the fixture's live SP can differ as code moves.
    assert list.__getitem__(a,slice(0x100,0x17b))==list.__getitem__(b,slice(0x100,0x17b))


def whole_audio(before,after,tokens):
    images = [M.bundle(im) for im in (before,after)]
    rows = {}
    expected = Counter(tokens)
    for owner in (7,41):
        pair = [M.seed(b,owner) for b in images]
        stats = defaultdict(list)
        decoded = [[],[]]

        def trace(index):
            class Trace(N.NesMPU):
                def step(self):
                    if self.pc==DECODE and self.memory.rawtags[2]==166:
                        assert self.memory.rawtags[1]==185
                        decoded[index].append(self.a)
                    return super().step()
            return Trace

        classes = [trace(i) for i in range(2)]

        def frame(fields,phase):
            start = [len(a) for a in decoded]
            result = []
            for m,cls in zip(pair,classes,strict=True):
                m.writes.clear()
                N.put(m,**fields)
                result.append(M.direct(m,'AudioUpdate',cls))
            a,b = result
            assert a[1]==b[1],(owner,phase,fields,a,b)
            assert decoded[0][start[0]:]==decoded[1][start[1]:]
            exact_state(*pair)
            kind = 'token' if len(decoded[0])!=start[0] else 'untouched'
            stats[phase,kind].append(a[0]-b[0])

        for tick in range(129+3264+4):
            frame(dict(AreaMusicQueue=int(tick==0),FrameCounter=tick&255,
                       Square1SoundQueue=32 if tick in (180,409,1260) else 0,
                       Square2SoundQueue=1 if tick in (250,653) else 0,NoiseSoundQueue=0),'ground')
        assert Counter(decoded[0][:3264])==expected and decoded[0][:3264]==tokens
        assert len(decoded[0])==3268 and not any(stats['ground','untouched'])
        assert min(stats['ground','token'])>0
        events = {0:dict(GamePauseStatus=1),12:dict(GamePauseStatus=0),26:dict(EventMusicQueue=64),
                  206:dict(AreaMusicQueue=4),249:dict(AreaMusicQueue=1)}
        for tick in range(430):
            frame(dict(FrameCounter=tick&255)|events.get(tick,{}),'transitions')
        assert stats['transitions','token'] and stats['transitions','untouched']
        rows[str(owner)] = {f'{phase}_{kind}':dict(frames=len(times),savings=[min(times),max(times)],
                       average_saved=sum(times)/len(times)) for (phase,kind),times in stats.items()}
        print(f'Owner {owner} exact ordered hardware and complete decoder state passed.',flush=True)

    # Cover other owners too. A native hurry event can share the same
    # linked ground-loop decoder even when its actor is not Rygar or Mini.
    other = Counter()

    class OtherTrace(N.NesMPU):
        def step(self):
            if self.pc==DECODE and self.memory.rawtags[2]==166:
                self.memory.actual_ground_decodes += 1
            return super().step()

    for owner,area,event in product((0,15,36,39),(1,4),(0,4,64)):
        pair = [M.seed(b,owner) for b in images]
        for tick in range(16):
            outcomes = []
            for m in pair:
                N.put(m,FrameCounter=tick,AreaMusicQueue=area if tick==0 else 0,
                      EventMusicQueue=event if tick==2 else 0)
                m.writes.clear()
                m.actual_ground_decodes = 0
                outcomes.append(M.direct(m,'AudioUpdate',OtherTrace))
            a,b = outcomes
            assert a[1]==b[1] and pair[0].actual_ground_decodes==pair[1].actual_ground_decodes
            exact_state(*pair)
            used = bool(pair[0].actual_ground_decodes)
            assert (a[0]>b[0] if used else a[0]==b[0]),(owner,area,event,tick,outcomes,used)
            other['shared_ground' if used else 'unchanged'] += 1
    return rows,dict(other)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    before = BASE.read_bytes()
    after,patches,labels,tokens = compose(before,out)
    counts,other = whole_audio(before,after,tokens)
    refs = (Path(__file__),SOURCE,BASE,Token.SOURCE,Token.FORMAT,Token.OUT/'runtime-proof.json',
            Token.OUT/'vectors.json',Token.OUT/'lifecycle.json',R/'src/expanded_audio.s')
    q = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
             patches=patches,labels=labels,actual_unique_tokens=len(set(tokens)),
             actual_full_loop_frames=len(tokens),AudioUpdate=counts,other_owner_ticks=other,
             exact_decoder_state_no_exclusions=True,
             bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items() if k not in ('patches','bindings')}),flush=True)


if __name__=='__main__':
    main()
