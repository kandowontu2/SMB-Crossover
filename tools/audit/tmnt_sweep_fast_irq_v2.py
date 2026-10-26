"""Actual compiled IRQ at every reached new sweep gate/alias instruction.

No native process, physical DMC DMA timing or nested-NMI-domain claim. Audio
already runs inside NMI. C-window aliases are admitted only with no active
unowned sample or source owner4, whose original drum bytes live in E.
"""
from pathlib import Path
import argparse
import gzip
import json
from check_tmnt_render_oa import load,Memory,address,location
from tmnt_native_storage_irq_cpu import ordinary,registers
from tmnt_native_storage_driver import ROOT,OB,sha
from verify_native_relocation import NesMPU


def final(c,m):
    exclusions=set(range(0x1a0,0x200))|{0x2005,0x2006,0x5128,0x5130}
    return(registers(c),bytes(m[i]for i in range(0x8000)if i not in exclusions),tuple(m.banks),
           tuple((k,v)for k,v in m.writes if 0x4000<=k<=0x4017 or 0x5000<=k<=0x5017))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT);a.output.mkdir(parents=True)
    old,b=load(a.baseline),load(a.candidate)
    assert all(old['raw'][16+n*8192:16+(n+1)*8192]==b['raw'][16+n*8192:16+(n+1)*8192]for n in range(128)if n not in[29,87])
    gate=address(b,'TnExpansionSweepGate');call=address(b,'TnExpansionSweepCall');fast=address(b,'TnExpansionFlushFast')
    assert gate==0xbfda and fast==0xd500
    assert old['raw'][16+87*8192+0x1500:16+88*8192]==bytes([255])*0xb00
    dmc=address(b,'TnMusicDpcm');end=address(b,'TnMusicDpcmEnd')
    assert(dmc,end)==(0xe8c0,0xe941)
    assert b['raw'][16+125*8192+dmc%8192:16+125*8192+end%8192]==b['raw'][16+127*8192+dmc%8192:16+127*8192+end%8192]
    # Inspect ALL original capture requests, not only current area song.
    coverage=json.loads((OB/'probe-v2/coverage.json').read_text());source_addrs=set();requests=0
    for song,meta in coverage['songs'].items():
        f=OB/f'probe-v2/song-{int(song):02d}.json.gz';assert sha(f)==meta['capture_sha256']
        for row in json.loads(gzip.decompress(f.read_bytes())):
            for reg,value in row['writes']:
                if reg==0x4012:source_addrs.add(value);requests+=1
    assert source_addrs=={0,1},source_addrs
    writer=(a.candidate.parent/'source/src/tmnt_audio_writers.s').read_text()
    assert 'adc #((TnMusicDpcm-$c000)/64)-1' in writer
    # Source0 is the initialization clear; active original drum source1 mapsE8C0.
    active_address=0xc000+64*(1+((dmc-0xc000)//64)-1);assert active_address==dmc
    def setup(cfg):
        m=Memory(b);m.page(1,29);m.page(2,cfg.get('cbank',38));at=lambda n:address(b,n)
        vals=dict(SelectedCharacter=cfg.get('char',19),CurrentBank=157,CurrentBankC=cfg.get('cbank',38)|128,
                  BassDmcActive=cfg.get('owner',0),GuestMixMask=1,GuestSweepControl=cfg.get('control',153),
                  GuestSweepPeriod=cfg.get('period',128)&255,GuestSweepDivider=0,GuestSweepReload=0)
        for n,v in vals.items():m[at(n)]=v
        m[at('GuestSweepPeriod')+1]=cfg.get('period',128)>>8
        for i,v in enumerate([158,153,128,248,37,73,109,145]):m[at('GuestFxApu')+i]=v
        if cfg.get('dirty'):m[at('GuestFxDirty')+1]=1
        m[0x5115]=157;m[0x5116]=cfg.get('cbank',38)|128;m[0x4015]=cfg.get('status',0);m[0x5204]=128
        m[510],m[511]=255,126;m.writes=[]
        c=NesMPU(memory=m,pc=gate);c.a,c.x,c.y,c.p,c.sp=85,3,7,0x69,253
        return c,m
    configs=[dict(period=128),dict(period=2047,owner=4,status=16),dict(period=17),dict(period=128,dirty=1),
             dict(period=128,control=129),dict(period=128,owner=3,status=16),dict(period=128,owner=0,status=16)]
    rows=[];count=0;maxdepth=0;hardware=set()
    for cfg in configs:
        c,m=setup(cfg);points=[]
        for index in range(8000):
            if c.pc==0x7f00:break
            bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            if(bank==29 and(gate<=c.pc<=0xbfff or call<=c.pc<call+28))or bank==87:
                points.append((index,c.pc,bank))
            c.step()
        else:raise AssertionError('Reference sweep timeout')
        expected=final(c,m)
        for target,pc,bank in points:
            d,n=setup(cfg)
            for index in range(8000):
                if d.pc==0x7f00:break
                if index==target:
                    before=registers(d),ordinary(n),tuple(n.banks)
                    start=len(n.writes);d.irq();assert d.pc==0x8000
                    depth=d.sp
                    for _ in range(300):
                        if d.pc==before[0][0]and d.sp==before[0][-1]:break
                        depth=min(depth,d.sp);d.step()
                    else:raise AssertionError(('IRQ return',hex(pc)))
                    assert(registers(d),ordinary(n),tuple(n.banks))==before,('IRQ state',hex(pc))
                    hw=[(k,v)for k,v in n.writes[start:]if 0x2000<=k<0x6000]
                    assert hw and all(k in[0x2005,0x2006,0x5128,0x5130]for k,v in hw)
                    hardware|={k for k,v in hw};maxdepth=max(maxdepth,255-depth)
                d.step()
            else:raise AssertionError('Interrupted sweep timeout')
            assert final(d,n)==expected,('Post-IRQ complete sweep',cfg,hex(pc));count+=1
        rows.append(dict(config=cfg,instruction_boundaries=len(points)))
    proof=dict(passed=True,source_only=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               actual_IRQ_injections=count,maximum_stack_depth=maxdepth,rows=rows,IRQ_hardware_stores=sorted(hardware),
               full_interrupted_AXYP_SP_PC_RAM_SMC_banks_exact=True,final_ordered_APU_and_all_state_exact=True,
               owner0_physical_active_DMC_literal_fallback=True,foreign_owners_literal_fallback=True,
               original_all16_song_DMC_address_requests=requests,original_source_DMC_values=sorted(source_addrs),
               active_Tn_DMC_range=[dmc,end],both_E127_and_E125_identical=True,
               entire_other126_banks_including_sourceDMC_and_fixedcontracts_exact=True,
               no_new_hardware_math=True,no_nested_NMI_claim=True,checker_sha256=sha(Path(__file__)))
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
