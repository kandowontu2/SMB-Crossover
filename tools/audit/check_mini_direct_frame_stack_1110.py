"""Qualify the smaller Mini direct service frame over the exact 76bd image."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import check_mini_after_bg_1110 as Q
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_lift_admission_async_1108_v1 import tags


A,L,M,N,R = Q.A,Q.L,Q.M,Q.N,Q.R
BASE = R/'build/mini-lift-afterbg-audio-bounds-native-1110/candidate.nes'
PIN = '76bd6772112ec63d086865210f4e20f62f59156d182136f23bd627db0df3d811'
SOURCE = R/'tools/reference/mini_direct_frame_stack_1110.s'
ORIGINAL = R/'tools/reference/mini_mario_direct_native_1103.s'
ENTRY,END = 0xb44d,0xb4cd
OLD = bytes.fromhex('088a489848ada17d48ad6c0138e9208d6c01a9a08d6d01a50fc908d029'
                    'a90220c280ad00c3c902d01da203ade0dfc9a7d014ade1dfc929d00d8a20c280'
                    'cae001d0e9a903d010ad6c0118698c8d6c01a9b08d6d01a9c18d6201babd0401'
                    '48bc0201bd0301aa28205d0108488a489848babd05018da17d8d1651a0044cf0b5eaea')
STUBS = bytes.fromhex('4c4db44c4db44c4db44c4db44c4db44c4db44c4db44c4db44c4db44ce4b3'
                      '4c4db44c4db44ce6b34c54a74c4db4')
PUBLIC = ('NrMovement','NrGraphics','NrDraw','NrPortrait','NrWeapons','NrInjury',
          'NrLegacyInjuryStatus','NrDeathStart','NrDeath','NrVisible','NrHead','NrBody',
          'NrAdder','NrBox','NrSide')


def build(out):
    raw = BASE.read_bytes()
    assert M.sha(raw)==PIN
    at = lambda bank,pc,n:raw[Q.offset(bank,pc):Q.offset(bank,pc)+n]
    assert at(84,0xb420,45)==STUBS and at(84,ENTRY,128)==OLD
    assert at(84,0xb3dd,15)==bytes.fromhex('68a868aa6828603860a0023860eaea')
    assert at(84,0xb5f0,16)==bytes.fromhex('bd01019d0501e888d0f69a4cddb3ffff')
    assert at(126,0x80c2,7)==bytes.fromhex('8da17d8d165160')
    assert at(1,0xa000,33)==bytes.fromhex(
        '8d6201ad450148a9428d45018d1551a94220defa8d7901688d45018d1551a94260')
    original = ORIGINAL.read_text()
    assert '.segment "DIRECT_BODY"' in original and '.repeat 15, I' in original
    assert 'jmp MiniDirectResult' in original and 'jmp MiniDirectFinish' in original
    bank = at(84,0xa000,8192)
    for target in range(ENTRY+1,END):
        assert all(bytes((op,target&255,target>>8)) not in bank for op in (0x20,0x4c)),hex(target)
    code_range = at(84,ENTRY,128)
    assert code_range.count(bytes.fromhex('4cf0b5'))==1
    assert bank.count(bytes.fromhex('4cf0b5'))==1 and bank.count(bytes.fromhex('4cddb3'))==1
    cfg,obj,binary,lbl = (out/f'direct.{ext}' for ext in ('cfg','o','bin','lbl'))
    cfg.write_text('MEMORY { A:start=$B44D,size=$80,file=%O; } SEGMENTS { DIRECT:load=A,type=ro; }\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
    obj.unlink()
    code = binary.read_bytes()
    labels = {line.split()[2][1:]:int(line.split()[1],16) for line in lbl.read_text().splitlines()}
    live_end = labels['MiniDirectWorkerEnd']
    assert labels['MiniDirectWorker']==ENTRY and len(code)==128
    assert ENTRY<live_end<END and code[live_end-ENTRY:]==b'\xea'*(END-live_end)
    rows = [dict(file_offset=Q.offset(84,ENTRY),physical_PRG=84,CPU_half_open=[ENTRY,END],
                 old_hex=OLD.hex(),new_hex=code.hex(),role='same complete authenticated worker span')]
    return raw,install(raw,rows),rows,labels


def qualify(before,after):
    images = L.bundles(before,after)
    seeds = [L.fixture(b,0,False,False) for b in images]
    counts = Counter()
    modes = ('warm','engine4','engine7','death','ready0','ready1','bank2marker','bank2owner',
             'bank3marker','bank3owner','bank2digest','bank3digest')

    def start(seed,pc,flags,mode,old_c,epoch):
        m = slim_fork(seed)
        N.put(m,SelectedCharacter=41,FrameCounter=epoch,
              GameEngineSubroutine={'engine4':4,'engine7':7,'death':11}.get(mode,8),
              Player_State=2,Player_Y_Speed=4,Player_Rel_XPos=72,Player_Rel_YPos=176,
              SavedJoypadBits=0,SavedJoypad1Bits=0)
        if mode in ('ready0','ready1'):
            m.ram[2][0x300] = int(mode=='ready1')
        if mode.startswith('bank'):
            at = {'marker':0,'owner':1,'digest':15}[mode[5:]]
            m.ram[int(mode[4])][0x1fe0+at] ^= 1
        m[0x5115],m[0x5116] = 129,old_c
        N.put(m,CurrentBank=129,CurrentBankC=old_c)
        m[0x16a],m[0x16c],m[0x16d] = 0x91,pc&255,pc>>8
        m.writes.clear()
        m.ram_writes.clear()
        c = N.NesMPU(memory=m,pc=0x15a)
        c.a,c.x,c.y,c.p,c.sp = 212,0,14,flags,234
        c.stPushWord(0x5aff)
        return c

    for row,mode,flags,old_c,epoch in product((0,1,2,4,5,6,7,8,10,11,14),modes,
                                             (0x21,0x65),(0x82,2),(0,7)):
        pc = 0xb420+3*row
        a,b = [start(seed,pc,flags,mode,old_c,epoch) for seed in seeds]
        visits = []
        for c in (a,b):
            hit = Counter()
            def watch(z):
                if tags(z) in (3,193,212,213):
                    hit[tags(z),z.pc] += 1
            run(c,lambda z:(z.pc,z.sp)==(0x5b00,234),watch)
            visits.append(hit)
        case = row,mode,flags,old_c,epoch
        assert registers(a,0xef)==registers(b,0xef) and live_stack(a)==live_stack(b),case
        A.P.compare_memory(a.memory,b.memory)
        assert Q.memory(a.memory)==Q.memory(b.memory) and a.memory.ram_writes==b.memory.ram_writes,case
        writes = lambda c:[(k,v) for k,v in c.memory.writes if not 0x17b<=k<=0x100+c.sp]
        assert writes(a)==writes(b),case
        target = 0xa000+3*row if mode in ('warm','bank2digest','bank3digest') else 0xb08c+3*row
        tag = 3 if target<0xb000 else 193
        assert all(visit[tag,target] for visit in visits),(case,visits)
        assert all(visit[212,ENTRY]==1 for visit in visits),case
        assert visits[0][212,0xb5f0]==4 and visits[1][212,0xb5f0]==0,case
        counts[mode,a.processorCycles-b.processorCycles] += 1
    return [[key[0],key[1],count] for key,count in sorted(counts.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    before,after,rows,labels = build(out)
    print('Linked direct frame',M.sha(after),labels,flush=True)
    direct = qualify(before,after)
    print('Exact direct services',direct,flush=True)
    core = A.P.check_full_cpu(before,after,{})
    loop = Q.Lift.Edges.Composed.whole_loop(before,after,{})
    refs = (Path(__file__),SOURCE,ORIGINAL,BASE,out/'direct.bin',out/'direct.lbl',
            R/'tools/audit/prepare_mini_direct_native_1103.py',R/'src/mmc5.s')
    proof = dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),ROM_written=False,
                 patches=rows,labels=labels,direct=direct,whole_GameCore=core,whole_GameLoop=loop,
                 available_inside_worker=[labels['MiniDirectWorkerEnd'],END],
                 now_unreached_return_sites=[[0xb3dd,0xb3e4],[0xb5f0,0xb5fe]],
                 bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(core),flush=True)


if __name__=='__main__':
    main()
