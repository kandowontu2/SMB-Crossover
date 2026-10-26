"""Check real Chip adapter tracks, borrowed pointers, pause, and foreign callers."""
from pathlib import Path
import argparse
import gzip
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, address, location
from check_tmnt_audio_fallback_oc import qualified, execute, result
from mike_native_music_cpu import MusicMemory
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
TRACKS = {2:(1,0),4:(2,0),5:(4,0),8:(8,0),12:(16,0),13:(32,0),14:(64,0),
          15:(0,1),16:(0,2),11:(0,4),10:(0,64)}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Run:
    def __init__(self,b):
        self.b=b; self.m=MusicMemory(b); self.c=NesMPU(memory=self.m)
        self.m[:256]=[(71+19*i)&255 for i in range(256)]
        self.foreground=bytes(self.m[:256])
        for n,v in dict(SelectedCharacter=14,OperMode=1,XgAudioCharacter=255,
                        CurrentBank=215,CurrentBankC=166).items():
            self.set(n,v)

    def set(self,n,v):
        self.m[address(self.b,n)]=v

    def get(self,n):
        return self.m[address(self.b,n)]

    def call(self,area=0,event=0,pause=0):
        self.set('AreaMusicQueue',area);self.set('EventMusicQueue',event)
        self.set('GamePauseStatus',pause)
        self.m.page(1,78);self.set('CurrentBank',215)
        c=self.c;m=self.m;c.pc=address(self.b,'ChNativeAudioUpdate')
        c.a,c.x,c.y,c.p,c.sp=85,3,7,0x24,253
        m[510],m[511]=255,126
        m.events=[];m.lowwrites=[];m.writes=[]
        start=c.processorCycles;source_start=None;source_end=None
        bridge_return=address(self.b,'ChNativeBridgeReturn')
        for _ in range(200000):
            if c.pc==0x7f00:
                break
            if c.pc in [address(self.b,'ChNativeSourceInit'),address(self.b,'ChNativeSourcePlay')]:
                assert source_start is None
                source_start=len(m.events)
            if source_start is not None and c.pc==bridge_return:
                assert source_end is None
                source_end=len(m.events)
            assert m[c.pc] != 0,('Unexpected BRK',hex(c.pc),m.banks)
            m.pc=c.pc;c.step()
        else:
            raise AssertionError(('Adapter timeout',hex(c.pc),m.banks))
        m.pc=None
        assert c.sp==255 and m.banks[1:3]==[78,94]
        assert bytes(m[:256])==self.foreground,'Borrowed foreground pointers not restored'
        assert self.get('CurrentBank')==215 and self.get('CurrentBankC')==222
        return c.processorCycles-start, m.events[source_start:source_end] if source_start is not None else []


def tracks(b,calls,out):
    rows=[]
    for song,(area,event) in TRACKS.items():
        r=Run(b);zp=address(b,'ChNativeZp');ram=address(b,'ChNativeRam')
        costs=[];stores=0
        with gzip.open(D/f'root-chip-native-music-source-v1/song-{song:02d}.jsonl.gz','rt') as f:
            for tick,line in enumerate(f):
                if tick>calls:
                    break
                want=json.loads(line)
                cost,events=r.call(area if tick==0 else 0,event if tick==0 else 0)
                actual=[[at,r.m[zp+at-0xc0] if at<256 else r.m[ram+at-0x700]] for at,_ in want['RAM']]
                assert actual==want['RAM'],('Original state divergence',song,tick,[(x,y)for x,y in zip(actual,want['RAM'])if x!=y][:8])
                assert list(map(list,events))==want['writes'],('Original source stores differ',song,tick,events,want['writes'])
                assert r.get('RgAudioSong')==song
                for name in ['AreaMusicQueue','EventMusicQueue','Square1SoundQueue','Square2SoundQueue','NoiseSoundQueue']:
                    assert r.get(name)==0
                costs.append(cost);stores+=len(events)
        row=dict(song=song,calls=len(costs),ordered_source_stores=stores,init_cycles=costs[0],
                 peak_play_cycles=max(costs[1:]),mean_play_cycles=sum(costs[1:])/len(costs[1:]))
        rows.append(row);print(json.dumps(row),flush=True)
        (out/'track-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
    return rows


def pause(b):
    r=Run(b);r.call(1)
    for _ in range(9):r.call()
    ram=address(b,'ChNativeRam');before=bytes(r.m[ram:ram+0xa4])
    for _ in range(4):
        _,events=r.call(pause=1)
        assert not events and bytes(r.m[ram:ram+0xa4])==before
        assert r.get('GuestNativeEnable')==0
    r.call();assert r.get('GuestNativeEnable')==15
    dirty=address(b,'GuestNativeDirty');assert all(r.m[dirty+i] for i in range(16))
    # A new request while muted stays pending until the real resume update.
    r.call(2,pause=1);assert r.get('ChNativePending')==4
    r.call();assert r.get('RgAudioSong')==4 and r.get('ChNativePending')==0
    # Silence does not advance source, and a later real area request resumes it.
    before=bytes(r.m[ram:ram+0xa4]);r.call(128)
    assert bytes(r.m[ram:ram+0xa4])==before and r.get('GuestNativeEnable')==0
    r.call(4);assert r.get('RgAudioSong')==5 and r.get('GuestNativeEnable')==15
    return dict(paused_source_updates=4,held_request=True,resume_dirty_image=True,silence_resume=True)


def foreign(old,new,quick):
    rows=[]
    for name in ['ExpandedAudioUpdate','AudioUpdate']:
        count=0;deltas=set()
        chars=[x for x in range(20) if x!=14 and (name=='AudioUpdate' or x>=6)]
        for char,var,flags,phase in itertools.product(chars,[0,1],[0x20,0x21,0x60,0xe1],range(2 if quick else 6)):
            areas=[1,0,4,128,0,64];events=[0,4,0,0,64,8]
            seed=dict(SelectedCharacter=char,OperMode=1,AreaMusicQueue=areas[phase],EventMusicQueue=events[phase],
                      GamePauseStatus=int(phase==4),VvVariant=var,KbVariant=var,RlVariant=var,CurrentBank=215,CurrentBankC=166)
            c,m=execute(old,name,seed,flags=flags);d,n=execute(new,name,seed,flags=flags)
            assert result(c,m)==result(d,n),('Foreign outer divergence',name,char,var,flags,phase,
                   [(i,m[i],n[i])for i in range(0x8000)if m[i]!=n[i]and not 0x100<=i<0x200][:12],m.banks,n.banks)
            deltas.add(d.processorCycles-c.processorCycles);count+=1
        rows.append(dict(entry=name,cases=count,cycle_deltas=sorted(deltas)))
        print(json.dumps(rows[-1]),flush=True)
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--calls',type=int,default=512);p.add_argument('--quick',action='store_true')
    a=p.parse_args();assert not a.output.exists();a.output.mkdir(parents=True)
    base=ROOT/'build/smb-crossover-mmc5-expanded.nes';old,new=load(base),load(a.rom)
    assert sha(base)=='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    qb,qn=qualified(base),qualified(a.rom)
    changed={str(k):[v,qn.get(k)]for k,v in qb.items()if qn.get(k)!=v};assert not changed,changed
    parent=load(D/'root-chip-native-relocation-v5/candidate.nes')
    for name,size in [('ChNativeStart',address(parent,'ChNativeEnd')-address(parent,'ChNativeStart')),
                      ('ChNativeTargetLo',43),('ChNativeTargetHi',43),('ChNativeHighMap',48)]:
        assert old is not None
        x,y=location(parent,name),location(new,name)
        assert parent['raw'][x:x+size]==new['raw'][y:y+size],name
    driver=tracks(new,a.calls,a.output)
    paused=pause(new)
    others=foreign(old,new,a.quick)
    report=dict(passed=True,accepted=False,native_run=False,candidate_ROM_sha256=sha(a.rom),
                old_scoped_symbols_retained=len(qb),qualified_driver_code_exact=True,
                tracks=driver,pause=paused,foreign_callers=others,checker_sha256=sha(__file__),
                limits='Real assembled CPU adapter and whole callers only; no actual PPU/DMC/IRQ/native-cadence or complete roster verdict.')
    (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,calls=sum(x['calls'] for x in driver))))


if __name__=='__main__':
    main()
