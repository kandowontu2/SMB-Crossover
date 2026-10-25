"""Compare both possible DPCM status outcomes through actual Kirby source code."""
from pathlib import Path
import argparse
import hashlib
import json
import probe_kirby_audio_on as source


class BusyMemory(source.Memory):
    def __getitem__(self,at):
        value=super().__getitem__(at)
        return 16 if at==0x4015 else value


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--calls',type=int,default=15000);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    path=next((source.ROOT/'reference/new-roster-audio/kirby').glob('*.nsf'));raw=path.read_bytes()
    digest=hashlib.sha256(raw).hexdigest();assert digest=='eecc93d7b56379d399896c3608ef83a304a0cc54bef4f715fac585054c8eda17'
    rows={}
    for track in [2,13]:
        normal,busy=source.Memory(raw),BusyMemory(raw)
        left,right=source.NesMPU(memory=normal),source.NesMPU(memory=busy)
        source.invoke(left,0xffef,track-1);source.invoke(right,0xffef,track-1)
        assert normal.writes==busy.writes and normal.ram==busy.ram
        differences=set();stores=0
        for call in range(a.calls):
            normal.writes=[];busy.writes=[]
            c0,c1=source.invoke(left,0xff28),source.invoke(right,0xff28)
            assert normal.writes==busy.writes,(track,call,'Ordered APU mismatch')
            assert normal.ram[:0x100]==busy.ram[:0x100]and normal.ram[0x200:]==busy.ram[0x200:],(track,call,'Application state mismatch')
            assert normal.banks==busy.banks
            differences.add(c0-c1);stores+=len(normal.writes)
        assert differences=={9}
        rows[str(track)]=dict(play_calls=a.calls,APU_stores_exact=stores,application_RAM_exact=True,bank_mappings_exact=True,
            DPCM_idle_extra_CPU_cycles=9,scope='The actual source read at823C masks4015with10 and skips fiveNOPs when busy. The returned A/P may differ; the fixed NSF play-call wrapper reinitializes input registers. Source APU stores and application RAM remain exact for every tested call. This does not model sample playback or establish hardware timing.')
        print('PASS source track',track,'both DPCM status paths',flush=True)
    q=dict(passed=True,accepted=False,game_changes=False,source_sha256=digest,tracks=rows,
        source_probe_sha256=hashlib.sha256(Path(source.__file__).read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Instruction-level source status-path differential only. No DPCM sample rendering, native Mesen source-call comparison, installed encoder or new game soundtrack is certified.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
