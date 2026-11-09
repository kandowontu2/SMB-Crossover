"""Qualify a source-reproduced, same-span MMC5 native audio flush."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import re
import tempfile

import check_native_ground_token_index_1110 as Token
from check_mini_funded_actor_1108_v3 import install, registers


M,N,R = Token.M,Token.N,Token.R
BASE = R/'build/mini-edges-draw-offscreen-native-1110/candidate.nes'
PIN = '90a8ac32d51acd29965a45aa5fd512b0b2d77d1c01b03982b62e6d9bed1d1d82'
SOURCE = R/'src/guest_audio.s'
PROPOSAL = R/'tools/reference/native_audio_dirty_clear_1110_v1.s'
ENTRY,END = 0xa92d,0xaab5
ADDRS = dict(GuestNativeApu=0x7282,GuestApuLast=0x72ca,GuestNativeDirty=0x72aa,
             GuestFxDirty=0x72ba,GuestMixOwner=0x72e4,GuestMixValue=0x72e3,
             GuestMixRegister=0x72e2,GuestMixChannel=0x72e1)
ACTIVE = tuple(i for i in range(16) if i not in (9,13))
CALLS = {(29,0xa58b):'native_mix',(62,0xbf9a):'rogue_pause',(82,0xbe6b):'smb2_pause'}


def position(bank,pc):
    return 16+bank*8192+(pc&8191)


def code(raw,bank,pc,size):
    off = position(bank,pc)
    return raw[off:off+size]


def compose(raw,out):
    b = M.bundle(raw)
    assert M.address(b,'GuestAudioNativeFlush')==ENTRY
    assert M.address(b,'GuestExpansionFlush')==END
    assert {n:M.address(b,n) for n in ADDRS}==ADDRS
    body = SOURCE.read_text().split('.proc GuestAudioNativeFlush\n',1)[1].split('.endproc',1)[0]
    prefix = 'MAPPER_MMC5=1\n'+''.join(f'{n}=${v:04x}\n' for n,v in ADDRS.items())
    source = '.segment "CODE"\n'+body
    with tempfile.TemporaryDirectory(prefix='link-',dir=out) as tmp:
        old,_ = M.assemble(Path(tmp)/'native-old',prefix+source,ENTRY,END-ENTRY)
        new,lbl = M.assemble(Path(tmp)/'native-new',prefix+PROPOSAL.read_text(),ENTRY,END-ENTRY)
    assert len(old)==len(new)==END-ENTRY and old==code(raw,29,ENTRY,END-ENTRY)
    assert lbl==dict(NativeFlush=ENTRY,NativeFlushEnd=END)
    row = dict(role='Native APU dirty clear after corresponding ordered hardware write',physical_PRG=29,
               CPU_half_open=[ENTRY,END],file_offset=position(29,ENTRY),old_hex=old.hex(),new_hex=new.hex())
    return install(raw,[row]),row


def census(raw):
    prg = raw[16:16+128*8192]
    assert code(raw,29,0xa58b,3)==b'\x4c\x2d\xa9'
    jsr = bytes.fromhex('202da9')
    assert [i for i in range(len(prg)-2) if prg.startswith(jsr,i)]==[25*8192+0x44]
    # False JSR at the start of Zelda's songDescriptor29/34: command byte
    # $20, the resolved pointer $A92D, and the three voice deltas.
    zelda = (R/'src/audio/roster/zelda.inc').read_text()
    assert re.search(r'songDescriptor29:\nsongDescriptor34:\n\.byte \$20\n\.addr song29voiceA',zelda)
    assert code(raw,25,0xa044,8)==bytes.fromhex('202da93e25218080')
    assert code(raw,25,0xa000+29,1)==code(raw,25,0xa000+34,1)==b'\x44'
    assert prg.count(bytes.fromhex('4c2da9'))==1
    same_bank = code(raw,29,0xa000,8192)
    absolute = [(0xa000+i,same_bank[i]) for i in range(8190)
                if same_bank[i] in (0x20,0x4c,0x6c) and
                ENTRY<=int.from_bytes(same_bank[i+1:i+3],'little')<END]
    assert absolute==[(0xa58b,0x4c)]
    far = []
    for i in range(len(prg)-16):
        q = prg[i:i+16]
        if (q[0]==q[5]==q[10]==0xa9 and q[2:5]==b'\x8d\x6c\x01' and
            q[7:10]==b'\x8d\x6d\x01' and q[11]==157 and
            q[12] in (0x20,0x4c) and q[13:15]==b'\x5a\x01'):
            dst = q[1]|q[6]<<8
            if ENTRY<=dst<END:
                bank,rel = divmod(i,8192)
                far.append((bank,0xa000+rel,dst))
    assert far==[(62,0xbf9a,ENTRY),(82,0xbe6b,ENTRY)]
    assert not any(bytes.fromhex(f'a9{hi:02x}8d6d01a9{lo:02x}8d6c01a99d') in prg
                   for pc in range(ENTRY,END) for lo,hi in [(pc&255,pc>>8)])
    return dict(bank29_absolute_calls=absolute,bank25_data_alias=[0xa044,0xa04c],farcall_packets=far,
                linked_ingresses=[[bank,pc,role] for (bank,pc),role in CALLS.items()],
                scope='Native-only body has no subcalls, bank maps, or branches into another code extent. Its one same-bank tail and two existing far call packets retain the original public entry. The older SMB2 source pause body is not used as the linked preimage.')


class DirectBus(bytearray):
    def __setitem__(self,at,v):
        if isinstance(at,int) and 0x4000<=at<=0x4017:
            self.hardware.append((at,v))
        super().__setitem__(at,v)


def direct_cases(before,after):
    costs = Counter()
    # Independently combine equal/change masks and each ordinary/high dirty
    # class across every hardware row, including two nonexistent registers.
    masks = (0,0xffff,0xaaaa,0x5555,*(1<<i for i in range(16)))
    for changed,dirty,mark,carry in product(masks,masks,(1,255),(0,1)):
        outcomes = []
        for raw in (before,after):
            mem = DirectBus(65536)
            mem.hardware = []
            mem[ENTRY:END] = code(raw,29,ENTRY,END-ENTRY)
            current = bytes((i*29+changed+dirty)&255 for i in range(16))
            mem[0x7282:0x7292] = current
            mem[0x72ca:0x72da] = bytes(v^0xff if changed>>i&1 else v for i,v in enumerate(current))
            mem[0x72aa:0x72ba] = bytes(mark if dirty>>i&1 else 0 for i in range(16))
            mem[0x72ba:0x72ca] = bytes(range(201,217))
            mem[0x72e1:0x72e5] = b'\xcc\xbb\xaa\x99'
            c = N.NesMPU(memory=mem,pc=ENTRY)
            c.a,c.x,c.y,c.p,c.sp = 173,23,61,0xe4|carry,224
            c.stPushWord(0x5aff)
            for _ in range(180):
                if c.pc==0x5b00:
                    break
                c.step()
            assert c.pc==0x5b00 and c.sp==224
            expected = [(0x4000+i,current[i]) for i in ACTIVE if (dirty|changed)>>i&1]
            assert mem.hardware==expected and mem[0x72aa:0x72ca]==bytes(32)
            outcomes.append((registers(c),bytes(mem[:0x8000]),mem.hardware,c.processorCycles))
        old,new = outcomes
        assert old[:-1]==new[:-1]
        delta = old[-1]-new[-1]
        # Relocating the unrolled branches can change the old page-crossing
        # penalty by one cycle in either direction.
        conditional_writes = len(expected)-int(any(at==0x4008 for at,_ in expected))
        assert 0<=delta<=52 and abs(delta-(52-4*conditional_writes))<=1,(changed,dirty,delta)
        costs[len(expected),delta] += 1
    return dict(cases=sum(costs.values()),ordered_write_count_and_savings=[[*k,v] for k,v in sorted(costs.items())])


def trace_kind(pc,m):
    if pc>=0x8000:
        tag = m.rawtags[(pc-0x8000)//8192]
        return CALLS.get((tag&127,pc)) if tag&128 else None
    return None


def seed(b,owner):
    m = M.seed(b,owner)
    if owner==2:
        # Rogue Dawn uses the existing Samus family alternate selector.
        N.put(m,RdVariant=1)
        # Main owns context commitment. The audio fixture starts at a
        # published stable context with no in-flight Main.
        m[0x5fb6] = 0
    if owner==25:
        N.invoke(m,'S2ColdInit')
        assert N.get(m,'S2Ready')==0xb2
    return m


def fields(t):
    return dict(AreaMusicQueue=1 if t==0 else 4 if t==17 else 0,
                EventMusicQueue=4 if t==22 else 0,Square1SoundQueue=32 if t in (3,12) else 0,
                Square2SoundQueue=1 if t in (5,13) else 0,NoiseSoundQueue=1 if t in (8,20) else 0,
                GamePauseStatus=int(t in (10,11,12,13)),FrameCounter=t)


def whole_audio(before,after):
    images = [M.bundle(raw) for raw in (before,after)]
    owner_hits = Counter()
    costs = Counter()
    for owner in range(42):
        pair = [seed(b,owner) for b in images]
        for tick in range(26):
            results = []
            for m in pair:
                sites = Counter()

                class Trace(N.NesMPU):
                    def step(self):
                        site = trace_kind(self.pc,self.memory)
                        if site:
                            sites[site] += 1
                        return super().step()

                N.put(m,**fields(tick))
                m.writes.clear()
                results.append((*M.direct(m,'AudioUpdate',Trace),sites))
            old,new = results
            assert old[1:]==new[1:],(owner,tick,old,new)
            Token.exact_state(*pair)
            delta = old[0]-new[0]
            assert -2<=delta<=58 and (new[2] or delta==0),(owner,tick,delta,new[2])
            for kind,hits in new[2].items():
                owner_hits[owner,kind] += hits
            costs[delta] += 1
    assert any(role=='native_mix' for _,role in owner_hits)
    return dict(complete_updates=sum(costs.values()),cycles_saved_histogram=costs,
                actual_ingress_counts_by_owner=[[*k,v] for k,v in sorted(owner_hits.items())])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    assert not (out/'proof.json').exists()
    before = BASE.read_bytes()
    assert M.sha(before)==PIN
    after,row = compose(before,out)
    refs = (Path(__file__),SOURCE,PROPOSAL,Path(Token.__file__),R/'src/reset.s',R/'src/music_drivers/audio.s',
            R/'src/sound_test.s',R/'src/audio/roster/zelda.inc',R/'src/rogue_dawn_audio_scheduler_hooks_v5.s',
            R/'src/smb2_roster_common_audio_v9.s')
    closures = census(before)
    direct = direct_cases(before,after)
    print('direct',json.dumps(direct),flush=True)
    whole = whole_audio(before,after)
    result = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                  patches=[row],ingress=closures,direct_flush=direct,whole_audio=whole,
                  bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['expected_memory_only_SHA256'],json.dumps(whole),flush=True)


if __name__=='__main__':
    main()
