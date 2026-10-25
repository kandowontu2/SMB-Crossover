"""Linked injury-end differential; only Proto's premature CHR writes differ."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, Memory, address, location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU


def run(bundle, entry, character, variant, state, low, reload, flags, registers,mode=None):
    m = Memory(bundle); m.page(1, 10)
    seed = dict(CurrentBank=138, SelectedCharacter=character, ProtoVariant=variant,
                Player_State=state, PlayerChrBank=low, ReloadCHRBank=reload,
                X5ChrMode=0x81 if character == 1 and variant else 0,RlVariant=variant,
                GuestHurtTicks=0,ObjectOffset=5, MmVX=0xab, Player_X_Speed=0xfe, MmLastXSpeed=0xfb)
    if mode is not None:seed['X5ChrMode']=mode
    for name, value in seed.items(): m[address(bundle, name)] = value
    m[address(bundle, 'MmVX')+1] = 0xcd; m[address(bundle, 'MmVX')+2] = 0xff
    m[0x1fe] = 255; m[0x1ff] = 0x7e; m.writes = []
    c = NesMPU(memory=m, pc=address(bundle, entry)); c.sp=0xfd
    c.a,c.x,c.y=registers;c.p=flags
    minimum_sp=c.sp
    for _ in range(5000):
        if c.pc == 0x7f00: break
        c.step();minimum_sp=min(minimum_sp,c.sp)
    else: raise AssertionError(('timeout', entry, character, variant))
    assert minimum_sp>=0xc0,'Reserved stack-page application bytes remain live'
    ram=bytearray(m[:0x8000]);ram[0x1c0:0x200]=bytes(64);ram[0x5114:0x5118]=bytes(4)
    for segment in bundle['segs'].values():
        if segment.get('name')=='"SMCCODE"':
            start=int(segment['start'],0);size=int(segment['size'],0);ram[start:start+size]=bytes(size)
    for name in ['safecall_a','SafecallA']:
        if name in bundle['syms']:ram[address(bundle,name)]=0
    hardware=[q for q in m.writes if (0x2000<=q[0]<0x4018 or 0x5000<=q[0]<0x5207)and not 0x5114<=q[0]<0x5118]
    return (c.a,c.x,c.y,c.p&0xcf,c.sp),ram,hardware,m.banks,c.processorCycles,m.writes


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    old,new=load(a.baseline),load(a.rom)
    before,after=qualified(a.baseline),qualified(a.rom)
    assert all(after.get(n)==v for n,v in before.items()if n!=('_FARCALL_COUNT',)),'An old linked address changed'
    assert after[('_FARCALL_COUNT',)]==before[('_FARCALL_COUNT',)]+2
    raw0,raw1=old['raw'],new['raw']
    assert raw0[16+1048576:]==raw1[16+1048576:]
    call=location(new,'MegaManHurtEnd');gate=location(new,'ProtoHurtEndCore')
    seg=next(s for s in new['segs'].values()if s['name']=='"PROTO_HURT_END"');end=int(seg['ooffs'],0)+int(seg['size'],0)
    draw=location(new,'MmRecoveryDrawBranch')
    assert all(raw0[i]==raw1[i]or call<=i<call+52 or draw<=i<draw+5 for i in range(16+10*8192,16+11*8192))
    assert all(raw0[i]==raw1[i]or gate<=i<end for i in range(16+66*8192,16+67*8192))
    cases=[];intentional=0
    for args in itertools.product(range(20),[0,1],[0,1],[0,11,64,129,255],[0,255],[0x30,0x71],[(0x56,3,7),(0xa9,0xfe,0x81)]):
        x=run(old,'MegaManHurtEnd',*args);y=run(new,'MegaManHurtEnd',*args)
        char,var,state,low,reload,flags,regs=args
        if char in [1,9]:
            # Independent contract: preserve the last committed body page and
            # reload marker; run the original velocity/stack cleanup unchanged.
            x[1][address(old,'PlayerChrBank')]=low
            x[1][address(old,'ReloadCHRBank')]=reload
            assert not any(at in [address(new,'PlayerChrBank'),address(new,'ReloadCHRBank')] for at,v in y[5])
            intentional+=1
        assert x[:4]==y[:4],(args,x[0],y[0],[(hex(i),x[1][i],y[1][i])for i in range(0x8000)if x[1][i]!=y[1][i]][:12])
        cases.append(dict(character=char,variant=var,state=state,low=low,reload=reload,flags=flags,registers=regs,old_cycles=x[4],new_cycles=y[4]))
    end_cases=len(cases);draw_cases=0
    for char,var,low,reload,flags,regs,mode in itertools.product(range(20),[0,1],[11,64,129,130,224],[0,255],[0x30,0x71],[(0x56,3,7),(0xa9,0xfe,0x81)],[0,0x81]):
        args=(char,var,0,low,reload,flags,regs)
        x=run(old,'MegaManHurtDraw',*args,mode=mode);y=run(new,'MegaManHurtDraw',*args,mode=mode)
        if mode==0 and var==0 and((char==1 and low==129)or(char==9 and low==130)):
            x[1][address(old,'PlayerChrBank')]=64 if char==1 else 224
            x[1][address(old,'ReloadCHRBank')]=(reload+1)&255
        assert x[:4]==y[:4],('draw',args,mode,x[0],y[0],[(hex(i),x[1][i],y[1][i])for i in range(0x8000)if x[1][i]!=y[1][i]][:12])
        cases.append(dict(phase='zero-timer-draw',character=char,variant=var,low=low,reload=reload,flags=flags,registers=regs,mode=mode,old_cycles=x[4],new_cycles=y[4]));draw_cases+=1
    q=dict(passed=True,ROM_sha256=hashlib.sha256(raw1).hexdigest(),baseline_ROM_sha256=hashlib.sha256(raw0).hexdigest(),
           cases=len(cases),injury_end_cases=end_cases,zero_timer_draw_cases=draw_cases,intentional_MM_Proto_Bass_cases=intentional,all_preexisting_addresses_unchanged=True,
           changed_PRG_banks=[10,66],CHR_unchanged=True,
           scope='Real linked old injury end vs new gate across20IDs, both variants, ground/air, five page bytes, wrapping reload markers, flags and registers. Exact A/X/Y/meaningfulP/SP, application RAM except discarded stack/SMC/safecall bookkeeping, non-banking hardware stores and final mappings. MM/Proto/Bass intentionally retain incoming PlayerChrBank/ReloadCHRBank until drawing; original motion/stack cleanup semantics are copied. Native PPU/NMI/replay evidence remains separate.')
    (a.output/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
