"""Trace true731 NMI arrivals at the genuine Mega/Proto-only audio core."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import traceback

from current3cee_postdma_mask_cpu_v4 import Bus, seed
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    rows=[]
    try:
        assert sha(BASE/'candidate.nes')=='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
        b=scoped_load(BASE/'candidate.nes');l=lambda n:address(b,n)
        off=location(b,'NonMaskableInterrupt');start=l('NonMaskableInterrupt');size=int(b['syms']['NonMaskableInterrupt']['size'],0)
        body=b['raw'][off:off+size]
        target=bytes([0x20,l('AudioUpdate')&255,l('AudioUpdate')>>8])
        calls=[start+i for i in range(len(body)-2) if body[i:i+3]==target]
        assert len(calls)==2
        source=(BASE/'source/src/reset.s').read_text()
        assert source.count('jsr AudioUpdate')==2
        regular_return,lag_return=calls[1]+2,calls[0]+2
        flags=[0x20|sum((n>>i&1)*v for i,v in enumerate([1,2,4,8,64,128])) for n in range(64)]
        for variant,lag,sp,p in itertools.product([0,1],[0,1],[0xfd,0xc0],flags):
            q=seed(b,1,1,lag,0,0,0);q.put(ProtoVariant=variant)
            m=Bus(b,bytes(q.m[:0x8000]),(0,0));m[l('CurrentBank')]=215;m[l('CurrentBankC')]=141
            c=NesMPU(memory=m,pc=0x5b00);c.a,c.x,c.y,c.p,c.sp=0xa7,73,19,p,sp;m.cpu=c
            c.nmi();m.writes=[];trace=[]
            for steps in range(30000):
                if c.pc==l('ProtoNmiAudioCore') and m.banks[1]==(location(b,'ProtoNmiAudioCore')-16)//8192:
                    break
                trace.append(c.pc);c.step()
            else:raise AssertionError(('No actual core arrival',variant,lag,sp,p,hex(c.pc)))
            def word(delta):return m[0x100+((c.sp+delta)&255)]+256*m[0x100+((c.sp+delta+1)&255)]
            stack_return=word(5)
            assert stack_return==(lag_return if lag else regular_return)
            assert sum(at==0x4014 for at,v in m.writes)==(0 if lag else 1)
            assert m.serial==([0,0] if lag else [8,8])
            assert c.sp==(sp-13)&255
            rows.append(dict(variant=variant,lag=lag,input_SP=sp,input_P=p,core_SP=c.sp,
                             real_outer_audio_return=stack_return,ordinary_return=regular_return,
                             lag_return=lag_return,DMA_stores_before_core=0 if lag else 1,
                             actual_controller_reads=list(m.serial),cycles_to_core=c.processorCycles,
                             source_core_entry=c.pc,physical_bank=m.banks[1],
                             stack_top_return=word(1),audio_branch_return=word(3)))
        (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
        deps=[Path(__file__),BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'source/src/reset.s',BASE/'source/src/music_drivers/audio.s',BASE/'source/src/megaman_audio.s',BASE/'source/src/protoman_cold.s',Path(__file__).parent/'current3cee_postdma_mask_cpu_v4.py',Path(__file__).parent/'check_tmnt_render_oa.py',Path(__file__).parent/'verify_native_relocation.py',Path(__file__).parent/'link_pit_rygar_sophia_audit_cpu.py']
        proof=dict(passed=True,source_only=True,native_run=False,implementation=False,ROM_sha256=sha(BASE/'candidate.nes'),
                   actual_partial_NMI_paths=len(rows),variants=2,incoming_physical_flag_contexts=64,incoming_SP=[253,192],
                   genuine_AudioUpdate_calls=calls,regular_stack_return=regular_return,lag_stack_return=lag_return,
                   Proto_core_original_stack_offset=5,after_proposed_PHP_PHX_stack_offset=7,
                   regular_path_already_completed_DMA_and_input=True,lag_path_no_DMA_or_input=True,
                   no_foreign_branch_added=True,actual_driver_or_state_mutation=False,
                   possible_design='A savedP/X stack selector in the existing genuine Mega/Proto-only NMI core can distinguish the outer regular return before acknowledging the new pending byte. It must preserve all original source state/AXYP/stack and no-current-song dependence; no implementation exists here.',
                   limits='Finite actual compiled NMI arrival/stack/IO trace only. No new ack instructions, full-core or full-NMI differential/native timing proof. Physical DMA is not modeled by these CPU traces; actual original STA4014 and controller ordering is observed.',
                   cases_sha256=sha(a.output/'cases.json'),bindings={str(p.resolve()):sha(p) for p in deps})
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
        print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),**proof),indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(e),traceback=traceback.format_exc(),completed_cases=len(rows)),indent=2)+'\n')
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':main()
