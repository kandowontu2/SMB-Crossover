"""Actual linked TMNT source requests, writer ABI and private memory ownership."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
from check_tmnt_render_oa import load,Memory,address
from verify_native_relocation import NesMPU

OB=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    b=load(a.rom);prepared=json.loads((OB/'driver-v3/preparation.json').read_text())
    source=json.loads((OB/'probe-v2/coverage.json').read_text());helpers={};sites={}
    move=lambda pc:pc+0x2000 if pc<0xc000 else pc-0x2000
    for q in prepared['APU_stores']:
        pc=address(b,q['helper']);helpers[pc]=q['helper'];sites[move(q['pc'])]=q
    raw=b['raw'];fixed=16+127*8192+0x08c0
    drum=(OB/'space-v3/source/audio/tmnt/native-drum.dmc').read_bytes()
    assert raw[fixed:fixed+129]==drum and address(b,'TnMusicDpcm')==0xe8c0
    zp=address(b,'TnAudioZp');assert zp==address(b,'XgAudioPtr')and address(b,'XgAudioZeroPageEnd')-zp==14
    allowed=set(range(zp,zp+14))|set(range(0x1c0,0x200))|set(range(0x4000,0x4018))
    for n,size in [('TnAudioRam',0xd8),('GuestNativeApu',16),('GuestNativeDirty',16),('GuestNativeEnable',1),('GuestCombinedEnable',1),('BassDmcActive',1)]:
        allowed.update(range(address(b,n),address(b,n)+size))
    calls=events=writer_returns=0;songs={};peak=0
    for song,info in source['songs'].items():
        expected=json.loads(gzip.decompress((OB/f'probe-v2/song-{int(song):02d}.json.gz').read_bytes()))
        m=Memory(b);m.page(1,123);m.page(2,124);m[address(b,'CurrentBankC')]=0xfc
        c=NesMPU(memory=m);image=[0]*16;dmc=[0]*4;status=0;count=0
        for q in expected:
            c.sp=0xfd;m[0x1fe]=0xff;m[0x1ff]=1;m.writes=[]
            for i in range(16):m[address(b,'GuestNativeDirty')+i]=0
            if q['call']==-1:c.a=int(song)-1;c.x=c.y=0;c.pc=address(b,'TnNativeInit')
            else:c.pc=address(b,'TnNativePlay')
            start=c.processorCycles;actual=[];pending=None
            for _ in range(50000):
                if c.pc==0x0200:break
                if pending is not None and c.pc==pending['pc']and c.sp==pending['sp']:
                    assert(c.a,c.x,c.y,c.p&0xcf)==pending['registers'],(song,q['call'],pending,c.a,c.x,c.y,c.p)
                    pending=None;writer_returns+=1
                if c.pc in helpers:
                    ret=(m[0x100+(c.sp+1)%256]+256*m[0x100+(c.sp+2)%256]+1)&65535
                    site=sites.get(ret-3)
                    if site is not None:
                        assert pending is None and site['helper']==helpers[c.pc]
                        index=c.x if site['mode']=='abx'else c.y if site['mode']=='aby'else 0
                        actual.append((site['address']+index,c.a))
                        pending=dict(pc=ret,sp=(c.sp+2)%256,registers=(c.a,c.x,c.y,c.p&0xcf))
                c.step()
            else:raise AssertionError(('Linked native timeout',song,q['call'],hex(c.pc),m.banks))
            assert pending is None
            assert actual==list(map(tuple,q['writes'])),(song,q['call'],actual,q['writes'])
            for at,value in actual:
                reg=at-0x4000
                if reg<16:image[reg]=value
                elif reg<20:dmc[reg-16]=value
                elif reg==21:status=value
            assert list(m[address(b,'GuestNativeApu'):address(b,'GuestNativeApu')+16])==image,(song,q['call'],'image')
            assert list(m[address(b,'TnAudioDmcRegs'):address(b,'TnAudioDmcRegs')+4])==dmc,(song,q['call'],'DMC image')
            assert m[address(b,'TnAudioVirtualEnable')]==status
            assert m[address(b,'GuestNativeEnable')]==status&15
            assert m[0x4015]==status and m[0x4010]==dmc[0]and m[0x4011]==dmc[1]and m[0x4013]==dmc[3]
            assert m[0x4012]==(dmc[2]+0xa2)&255
            assert all(at in allowed for at,value in m.writes),(song,q['call'],[(hex(at),v)for at,v in m.writes if at not in allowed][:12])
            assert m.banks==[126,123,124,127]
            calls+=1;count+=1;events+=len(actual);peak=max(peak,c.processorCycles-start)
        songs[song]=dict(calls=count,source_requests_exact=True,images_exact=True,writer_registers_and_flags_preserved=True,state_writes_owned=True)
        print('song',song,'linked calls',count,flush=True)
    proof=dict(passed=True,ROM_sha256=hashlib.sha256(raw).hexdigest(),native_songs=16,calls=calls,source_APU_requests=events,
               writer_ABI_returns=writer_returns,maximum_linked_call_cycles=peak,songs=songs,fixed_drum_bytes_exact=True,
               scope='Actual linked source engine and actual buffering/DMC writers. All original song requests, native register images, virtual DMC parameters, writer A/X/Y/meaningfulP, allowed writes and physical banking checked. No hardware sample clock, shared-mixer, interrupt or gameplay claim.',
               checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:proof[k]for k in ['passed','ROM_sha256','calls','source_APU_requests','writer_ABI_returns','maximum_linked_call_cycles']}))


if __name__=='__main__':main()
