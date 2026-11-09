"""Check the compact enemy offset and raw horizontal far-edge tail."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_post_scroll_offscreen_1110 as Post
from check_mini_funded_actor_1108_v3 import install, registers, run


P,N,R = Post.P,Post.N,Post.R
BASE = R/'build/mini-step-scroll-weapon-native-1110/candidate.nes'
PIN = '991b4cd1033890aaa7dc0fa773dc167496fd0937bc449c8a3a209709f2a6c318'
SOURCE = R/'tools/reference/native_raw_offscreen_tail_1110_v1.s'
PROFILE = R/'build/mini-player-cost-profile-1110/capture/instruction-sample.json'
SPANS = (('ENEMY',0x8ae9,0x8af0,'a901a0014cf48a'),
         ('NEG_BRANCH',0x8b2b,0x8b2d,'3029'),
         ('FAR_TAIL',0x8b4f,0x8b63,'c001900c8810c8c001b005a900388860a9ff3860'))
ENEMY,RAW = 0x8ae9,0x8b1a


def offset(pc):
    return Post.offset(126,pc)


def census(raw):
    common = (R/'src/common.s').read_text()
    assert common.count('SetOffscrBitsOffset')==2
    assert '  jmp SetOffscrBitsOffset' in common and '  adc R0' in common
    code = raw[16:1048592]
    found = {}
    for i in range(len(code)-2):
        if code[i] not in (0x20,0x4c,0x6c):
            continue
        to = int.from_bytes(code[i+1:i+3],'little')
        if to in (ENEMY,RAW,0x8af4) or 0x8b4f<=to<0x8b63:
            found.setdefault(to,[]).append((i//8192,i&8191))
    assert found[0x8af4]==[(126,0xaed)]
    assert found[RAW]==[(1,0xa41),(26,0x104c),(126,0xafc),(126,0x1f26)]
    assert set(found)=={ENEMY,RAW,0x8af4,0x8b55}
    assert found[0x8b55]==[(40,0x1957),(41,0x121a)]
    for bank,index,at in ((40,'01',0x1957),(41,'02',0x121a)):
        blob = (R/f'audio/expanded/playlist-{index}.bin').read_bytes()
        start = Post.offset(bank,0xa000)
        assert raw[start:start+len(blob)]==blob and blob[at:at+3]==b'\x20\x55\x8b'
    for addr in (0x8af4,*range(0x8b4f,0x8b63)):
        assert code.count(bytes((0xa9,addr&255,0x8d,0x6c,1,0xa9,addr>>8,0x8d,0x6d,1)))==0
    assert len(found[ENEMY])==15
    return found


def compose(raw,output):
    assert P.sha(raw)==PIN
    calls = census(raw)
    # The combined vertical contract and actual first-player reuse stay fixed.
    Post.read(raw,1,0xa13c,'2065ed20c78b208c8a')
    Post.read(raw,126,0x8bc7,'ad0260c912f008a503d004484c058b4cce8a')
    with tempfile.TemporaryDirectory(prefix='link-',dir=output) as temp:
        work = Path(temp)
        cfg,obj,binpath = (work/f'offscreen.{ext}' for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY {\n'+''.join(f'{s}:start=${lo:04x},size={hi-lo},file=%O;\n'
            for s,lo,hi,_ in SPANS)+'}\nSEGMENTS {\n'+''.join(f'{s}:load={s},type=ro;\n'
            for s,*_ in SPANS)+'}\n',encoding='utf-8')
        cc = R/'tools/Windows/cc65/bin'
        subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
        subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binpath],check=True)
        data = binpath.read_bytes()
    patches = []
    for name,lo,hi,old in SPANS:
        Post.read(raw,126,lo,old)
        assert len(bytes.fromhex(old))==hi-lo
        patches.append(dict(role=name,physical_PRG=126,CPU_half_open=[lo,hi],file_offset=offset(lo),
                            old_hex=old,new_hex=data[:hi-lo].hex()))
        data = data[hi-lo:]
    assert not data
    return install(raw,patches),patches,calls


def leaves(before,after):
    cpus = []
    for raw in (before,after):
        mem = bytearray(65536)
        mem[0x8000:0xa000] = raw[offset(0x8000):offset(0x8000)+8192]
        cpus.append(N.NesMPU(memory=mem))
    counts = Counter()

    def check(pc,edge,pos,slot,p):
        a = []
        lpage,rpage,lx,rx = edge
        page,x = pos
        object_slot = (slot+int(pc==ENEMY))&255
        initial = bytes((29*i+17*slot+page+p)&255 for i in range(256))
        for c in cpus:
            m = c.memory
            m[:256] = initial
            m[0x71d:0x721] = bytes((lpage,rpage,lx,rx))
            m[(0x75+object_slot)&255],m[(0x5c+object_slot)&255] = x,page
            m[0x5a1] = 0xf9
            c.pc,c.a,c.x,c.y,c.p,c.sp = pc,0xd4,slot,0x49,p,242
            c.processorCycles = 0
            c.stPushWord(0x5aff)
            run(c,lambda z:(z.pc,z.sp)==(0x5b00,242))
            a.append((registers(c),bytes(m[:256]),m[0x5a1],c.processorCycles))
        assert a[0][:-1]==a[1][:-1],(hex(pc),edge,pos,slot,p,a)
        counts[hex(pc),a[0][-1]-a[1][-1]] += 1

    edges = ((0,0,0,255),(0,1,43,42),(255,0,233,232),(127,128,113,112),
             (128,127,18,200),(1,15,8,33),(0,128,228,19),(3,0,45,231))
    for edge,delta,x,slot in product(edges,(-129,-128,-1,0,1,127,128),range(256),(0,1,5,17)):
        check(RAW,edge,((edge[0]+delta)&255,x),slot,(0x20,0x25,0x63,0xe9)[x&3])
    for edge,slot,x in product(edges,range(256),(0,7,23,24,55,56,121,176,231,255)):
        check(ENEMY,edge,((edge[0]+(x&1))&255,x),slot,(0x20,0x25,0x63,0xe9)[slot&3])
    # A left far pass always follows a right far pass, so the extra INY
    # only reduces an existing saving. No public raw path takes longer.
    assert {delta for (name,delta) in counts if name==hex(RAW)}=={0,3,4}
    assert {delta for (name,delta) in counts if name==hex(ENEMY)}=={7,10,11}
    return dict(cases=sum(counts.values()),savings_histogram=[[*key,v] for key,v in sorted(counts.items())])


def profile_scope():
    q = json.loads(PROFILE.read_text())
    assert json.loads(PROFILE.with_name('binding.json').read_text())['ROM_sha256']==Post.Relative.PIN
    fg = q['foreground_opcodes']
    assert q['scene']['frame']==1452 and q['scene']['x']==694
    enemy = fg['126:8ae9']//2
    raw = fg['126:8b1a']//3
    edges = fg['126:8b1e']//4
    assert (enemy,raw,edges)==(4,10,17)
    # Every second edge proves an initial right-far branch. The trace does
    # not distinguish how many left passes also used Far. One known first
    # player pass is removed in the current post-scroll predecessor.
    right_far = edges-raw-1
    return dict(sample_ROM_SHA256=Post.Relative.PIN,frame=1452,enemy_calls=enemy,
                earlier_raw_calls=raw,earlier_edge_iterations=edges,
                current_path_projection=[enemy*7+right_far*3,enemy*7+right_far*4])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    final,patches,calls = compose(raw,out)
    leaf = leaves(raw,final)
    print(f"Raw and enemy public leaves passed {leaf['cases']} cases.",flush=True)
    core = Post.check_full_cpu(raw,final,{})
    loop = Post.PlatformBox.whole(raw,final)
    refs = (Path(__file__),SOURCE,BASE,PROFILE,PROFILE.with_name('binding.json'),
            R/'src/common.s',R/'src/player.s',R/'src/object.s',R/'src/enemy_offscreen_fast.s',
            R/'audio/expanded/playlist-01.bin',R/'audio/expanded/playlist-02.bin')
    q = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(final),
             patches=patches,absolute_caller_sites=calls,leaf=leaf,whole_GameCore=core,
             whole_GameLoop=loop,profile_projection=profile_scope(),
             bindings={p.resolve().relative_to(R).as_posix():P.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('expected_memory_only_SHA256','leaf','whole_GameCore',
                                      'whole_GameLoop','profile_projection')}),flush=True)


if __name__=='__main__':
    main()
