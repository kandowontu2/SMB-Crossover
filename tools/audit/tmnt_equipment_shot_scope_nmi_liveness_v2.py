"""Actual lag-NMI CPU body at fused-scratch boundaries; no hardware clock claim."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import qualified
from tmnt_equipment_empty_scans_cpu_v1 import setup
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_irq_cpu import registers
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['candidate','literal-reference','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    b=load(a.candidate);q=qualified(a.candidate);literal=load(a.literal_reference)
    hook=q['TnDrawEquipment','ShotPointer'];base=16+87*8192+hook-0xa000
    original=literal['raw'][base:base+3];assert original==bytes([0xbc,address(b,'TnShotFace')&255,address(b,'TnShotFace')>>8])
    begin=address(b,'TnShotOwnerScope');end=begin+int(b['syms']['TnShotOwnerScope']['size'],0)
    def make(cfg,old=False):
        c,raw=setup(b,cfg);m=MathMemory(b)
        for bank,page in enumerate(raw.banks):m.page(bank,page)
        # Clone RAM bytes without replaying synthetic writes to $5114..$5117.
        # Actual mapper windows were copied from raw.banks immediately above.
        list.__setitem__(m,slice(0,0x8000),list(raw[:0x8000]))
        m[address(b,'NmiDisable')]=255;m[address(b,'DisableScreenFlag')]=0
        m[address(b,'GuestAudioCharacter')]=19;m[address(b,'XgAudioCharacter')]=255
        m[address(b,'AreaMusicQueue')]=1
        if old:
            for i,v in enumerate(original):list.__setitem__(m,hook+i,v)
        cpu=NesMPU(memory=m);cpu.pc,cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=c.pc,c.a,c.x,c.y,c.p,c.sp
        m.writes=[];m.math_events=[];return cpu,m
    def nmi(c,m):
        before=registers(c);banks=list(m.banks);scratch=[m[address(b,'R'+str(i))]for i in range(8)]
        first=len(m.writes);c.nmi();assert c.pc==address(b,'NonMaskableInterrupt');minimum=c.sp
        for _ in range(50000):
            if c.pc==before[0]and c.sp==before[-1]:break
            minimum=min(minimum,c.sp);m.executing_PC=c.pc;c.step()
        else:raise AssertionError('Actual lag NMI return timeout')
        assert registers(c)==before and m.banks==banks
        assert [m[address(b,'R'+str(i))]for i in range(8)]==scratch,('NMI consumed foreground scratch',hex(c.pc))
        writes=[(at,v)for at,v in m.writes[first:]if not 0x100<=at<0x200]
        assert not any(0x200<=at<0x300 or at==0x4014 for at,v in writes),'Lag NMI cannot publish unfinished OAM'
        return writes,255-minimum
    cases=[];depth=0
    for pose,face,edge in itertools.product([60,73,74,75],[1,2],[0,1]):
        cfg=dict(shots=[(1,pose,2)],face=face,flags=0x20 if edge==0 else 0xe9,
                 x=128 if edge==0 else 7,scroll=0 if edge==0 else 8,
                 page=0,camera_page=0 if edge==0 else 255,y=176 if edge==0 else 23,offset=48 if edge==0 else 252)
        c,m=make(cfg,True)
        for _ in range(30000):
            if c.pc==address(b,'TnWorldDraw')and m.banks[1]==87:break
            c.step()
        else:raise AssertionError('Literal original caller did not reach world draw')
        expected,_=nmi(c,m)
        c,m=make(cfg);points=[]
        for index in range(30000):
            if c.pc==0x7f00:break
            if m.banks[1]==87 and begin<=c.pc<end:points.append((index,c.pc))
            c.step()
        for at,pc in points:
            c,m=make(cfg)
            for _ in range(at):c.step()
            assert c.pc==pc
            stores,used=nmi(c,m);depth=max(depth,used)
            assert stores==expected,('NMI outputs depended on omitted input copy/intermediate Y',cfg,hex(pc))
            cases.append(dict(cfg=cfg,PC=pc,nonstack_NMI_stores=len(stores)))
    (a.output/'cases.json').write_text(json.dumps(cases,separators=(',',':'))+'\n')
    proof=dict(passed=True,source_only=True,native_run=False,accepted=False,candidate_ROM_sha256=sha(a.candidate),
               literal_original_setup_reference_ROM_sha256=sha(a.literal_reference),literal_hook_bytes=original.hex(),
               actual_compiled_lag_NMI_injections=len(cases),maximum_total_stack_depth=depth,
               CPU_AXYP_PC_SP_banks_and_all_foreground_R0_toR7_preserved=True,
               every_ordered_nonstack_NMI_store_equals_literal_original_setup=True,
               unfinished_OAM_never_published=True,case_file_sha256=sha(a.output/'cases.json'),checker_sha256=sha(Path(__file__)),
               limits='CPU executes real vector/NMI/RTI on explicitly arranged cold guest19 lag path, including real source music. Literal setup is the verified old3-byte LDY hook in memory only. No physical PPU/DMC DMA/IRQ scheduling, whole foreground RAM snapshot, natural acquisition or recovered draw claim.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
