"""Execute the relocated TMNT engine against every recorded original NSF call."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
from py65.devices.mpu6502 import MPU

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')


class Bus(list):
    def __init__(self,raw):
        super().__init__([0]*65536);self[0xa000:0xe000]=raw;self.events=[];self.writes=set()
    def __setitem__(self,at,v):
        if isinstance(at,int):
            assert at<0x8000,('Unexpected relocated ROM write',hex(at),v)
            self.writes.add(at)
            if 0x4000<=at<=0x4017:self.events.append((at,v))
        super().__setitem__(at,v)


def main():
    p=argparse.ArgumentParser();p.add_argument('--driver',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    coverage=OUT/'probe-v2/coverage.json';source=json.loads(coverage.read_text())
    prepared=json.loads((a.driver/'preparation.json').read_text());binary=(a.driver/'raw-test.bin').read_bytes()
    assert hashlib.sha256(binary).hexdigest()==prepared['raw_binary_sha256']
    assert prepared['coverage_sha256']==hashlib.sha256(coverage.read_bytes()).hexdigest()
    songs={};calls=events=0;peak=0
    for song,record in source['songs'].items():
        file=coverage.parent/f'song-{int(song):02d}.json.gz'
        assert hashlib.sha256(file.read_bytes()).hexdigest()==record['capture_sha256']
        expected=json.loads(gzip.decompress(file.read_bytes()));m=Bus(binary);c=MPU(memory=m)
        for q in expected:
            c.sp=0xfd;m[0x1fe]=0xff;m[0x1ff]=0x01;m.events=[];m.writes=set()
            if q['call']==-1:c.a=int(song)-1;c.x=c.y=0;c.pc=0xa000
            else:c.pc=0xa644
            start=c.processorCycles
            for _ in range(50000):
                if c.pc==0x0200:break
                c.step()
            else:raise AssertionError(('Relocated NSF timeout',song,q['call'],hex(c.pc)))
            assert m.events==list(map(tuple,q['writes'])),(song,q['call'],m.events,q['writes'])
            assert c.processorCycles-start==q['cycles'],(song,q['call'],c.processorCycles-start,q['cycles'])
            allowed=lambda at:(0xe0<=at<=0xed or 0x1f0<=at<=0x1ff or 0x4000<=at<=0x4017 or 0x7000<=at<=0x70ad)
            assert all(allowed(at)for at in m.writes),(song,q['call'],[hex(at)for at in m.writes if not allowed(at)])
            calls+=1;events+=len(m.events);peak=max(peak,c.processorCycles-start)
        songs[song]=dict(calls=len(expected),ordered_APU_writes_exact=True,cycles_exact=True,state_writes_owned=True)
        print('song',song,'matched',len(expected),'calls',flush=True)
    q=dict(passed=True,native_songs=len(songs),calls=calls,ordered_APU_events=events,maximum_call_cycles=peak,songs=songs,
           original_NSF_sha256=source['source_sha256'],coverage_sha256=hashlib.sha256(coverage.read_bytes()).hexdigest(),
           preparation_sha256=hashlib.sha256((a.driver/'preparation.json').read_bytes()).hexdigest(),
           binary_sha256=hashlib.sha256(binary).hexdigest(),checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           scope='Standalone original/relocated CPU execution, all16songs and12000playcalls/song plusinit. Ordered APU requests and emulated CPU cycles exact. Source state is relocated to owned RAM and14 borrowed ZP bytes. No PPU, interrupts, waveform, DMC hardware or game integration claim.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','native_songs','calls','ordered_APU_events','maximum_call_cycles']}))


if __name__=='__main__':main()
