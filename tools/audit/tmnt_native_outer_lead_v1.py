"""Profile a disclosed empty-owner full AudioUpdate with native source states.

The retained native snapshot covers original driver RAM, not mixer state.
This profile never labels its arranged empty mixer as a literal native snapshot.
"""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import json
from py65.disassembler import Disassembler
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['storage','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();d,out=a.storage,a.output
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    out.mkdir(parents=True)
    rom=d/'parser-ready-v1/candidate.nes';digest=sha(rom)
    assert digest=='9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
    native=d/'parser-native-pilot-v1/candidate-easy/source-state.csv'
    states={int(r['sourceTick']):bytes.fromhex(r['ZP14_RAM174_hex']) for r in csv.DictReader(native.open())}
    b=load(rom);q=qualified(rom);m=MathMemory(b);m.page(2,38)
    for name,value in dict(SelectedCharacter=19,TnVariant=0,OperMode=1,CrossoverBehaviorVersion=0,AreaMusicQueue=1,
                           CurrentBank=215,CurrentBankC=166,XgAudioCharacter=255).items():m[address(b,name)]=value
    c=NesMPU(memory=m)
    names=['AudioUpdate','ExpandedAudioUpdate','TnAudioUpdate','TnMusicInitCall','TnMusicPlayCall',
           'RemainingAudioBegin','RemainingAudioSupported','GuestAudioBegin','BassAudioBegin','SophiaLandAudioTick',
           'RemainingAudioTick','GuestAudioFinish','GuestDmcStatus','GuestExpansionFlush','GuestAudioNativeFlush',
           'X5NativeNoiseMask','Cv3DmcEndedGate','TnAudioGlobalGate','TnAudioDispatch']
    hooks={}
    for name in names:
        hooks[(location(b,name)-16)//8192,address(b,name)]=name
    hooks[29,q['GuestSharedSfx','SFXSoundEngine']]='GuestSharedSfx::SFXSoundEngine'
    for name in ['TnNativeInit','TnNativePlay']:hooks[63,address(b,name)]=name
    def bank(pc):return m.banks[(pc-0x8000)//8192] if pc>=0x8000 else -1
    profiles=[]
    for tick in range(506):
        c.pc,c.a,c.x,c.y,c.p,c.sp=address(b,'AudioUpdate'),85,3,7,0x20,253
        m[510],m[511]=255,126;m.writes=[];m.math_events=[]
        frames=[];spans=[];own=Counter();instructions=Counter();trace=[];start=c.processorCycles
        dis=Disassembler(c)
        for index in range(50000):
            if tick in [407,505]:
                while frames and (c.pc,c.sp,bank(c.pc))==(frames[-1]['return'],frames[-1]['sp'],frames[-1]['return_bank']):
                    row=frames.pop();row['cycles']=c.processorCycles-row['start'];spans.append(row)
            if c.pc==0x7f00:break
            if tick in [407,505]:
                name=hooks.get((bank(c.pc),c.pc))
                if name:
                    ret=(m[0x100+(c.sp+1)%256]+256*m[0x100+(c.sp+2)%256]+1)&65535
                    frames.append(dict(name=name,return_=ret,return_bank=bank(ret),sp=(c.sp+2)&255,start=c.processorCycles))
                    frames[-1]['return']=frames[-1].pop('return_')
                assert frames,('Unowned full-outer cycle',hex(c.pc))
                owner=frames[-1]['name'];pc=c.pc;before=c.processorCycles;instruction=dis.instruction_at(pc)[1]
                before_state=[c.a,c.x,c.y,c.p&207,c.sp]
            m.executing_PC=c.pc;c.step()
            if tick in [407,505]:
                elapsed=c.processorCycles-before;own[owner]+=elapsed;instructions[owner,pc,instruction]+=elapsed
                trace.append(dict(owner=owner,PC=pc,instruction=instruction,cycles=elapsed,registers=before_state))
        else:raise AssertionError(('Full outer timeout',tick,hex(c.pc)))
        zp,ram=address(b,'TnAudioZp'),address(b,'TnAudioRam')
        state=bytes(m[zp:zp+14]+m[ram:ram+174])
        assert state==states[tick],('Full outer original188byte state differs from retained native',tick)
        if tick in [407,505]:
            assert not frames and sum(own.values())==c.processorCycles-start
            saved={n:m[address(b,n)] for n in ['BassDmcActive','GuestMixMask','GuestMixPreviousMask','GuestWorldQueues',
                   'Square1SoundBuffer','Square2SoundBuffer','NoiseSoundBuffer','PauseModeFlag','PauseSoundQueue',
                   'AvAudioChar','AvAudioId','AvAudioRequest','AvAudioOldMask','GuestAudioCharacter']}
            profiles.append(dict(tick=tick,CPUcycles=c.processorCycles-start,exclusive=dict(own),spans=spans,
                top_instructions=[dict(owner=k[0],PC=k[1],instruction=k[2],cycles=v) for k,v in instructions.most_common(35)],
                arranged_final_mixer=saved,full188byte_original_native_state_exact=True))
            (out/f'empty-owner-{tick}.json.gz').write_bytes(gzip.compress(json.dumps(trace).encode()))
    proof=dict(valid_source_profile=True,source_only=True,native_run=False,ROM_sha256=digest,
        exact_original188byte_native_states_all506calls=True,arranged_empty_owner_states=True,literal_full_native_mixer_snapshot=False,
        retained_native_source_states_sha256=sha(native),profiles=profiles,checker_sha256=sha(Path(__file__)),
        limits='The complete original driver RAM is bound to actual native states. Mixer queues/buffers/physical DMC reads are explicitly arranged CPU state; this is not literal outer2056 reconstruction or a native timing/recovery proof. No implementation changes.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__=='__main__':main()
