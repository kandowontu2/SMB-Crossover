"""Compare the linked buffered music port with the original hardware writes."""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import port_wwf_audio_private_bounded_v2 as V
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
J=R/'build/wwf-roster-native-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();o=a.output;o.mkdir(exist_ok=True)
    b=scoped_load(J/'candidate.nes');image=(J/'stream.chr').read_bytes()[8192:16384];scratch=address(b,'WfAudioScratch');apu=address(b,'GuestNativeApu')
    class BufferedBus(V.HostBus):
        def __setitem__(self,at,value):
            super().__setitem__(at,value)
            if apu<=at<apu+16:self.apu.append((0x4000+at-apu,value))
    raw=V.V.V.raw();bank=raw[65536:98304];rows=[]
    for char in V.V.V.tables(raw):
        src=V.V.V.Bus(bank);host=BufferedBus(image,scratch);writes=0;digest=hashlib.sha256();periods=set()
        for entry in [0xe22e,0xe249]:
            if entry==0xe249:src.m[1]=host.m[scratch+1]=char['theme']
            src.apu=[];host.apu=[];V.V.invoke(src,entry,original=True);V.V.invoke(host,address(b,'WfAudio_%04X'%entry));assert src.apu==host.apu
        for tick in range(600):
            src.apu=[];host.apu=[];old,_=V.V.invoke(src,0xe4de,original=True);new,_=V.V.invoke(host,address(b,'WfAudio_E4DE'))
            assert src.apu==host.apu,('Buffered ordered APU',char['name'],tick,src.apu,host.apu)
            assert src.m[0x500:0x5c0]==host.m[0xc500:0xc5c0]
            assert (old.a,old.x,old.y,old.p)==(new.a,new.x,new.y,new.p)
            assert host.m[3:5]==[165,90]
            periods.add(tuple(host.m[apu+i]for i in [2,3,6,7,10,11]));writes+=len(host.apu)
            digest.update(bytes(v for p,v in host.apu))
        assert len(periods)>10,('Theme did not progress',char['name'],len(periods))
        rows.append(dict(name=char['name'],theme=char['theme'],ticks=600,ordered_APU_writes=writes,distinct_period_packets=len(periods),trace=digest.hexdigest()))
    report=dict(passed=True,source_CPU=True,native=False,candidate=sha(J/'candidate.nes'),rows=rows,scope='Linked A1 code including buffered writes/dirty flags, original ordered APU events, channel state, AXYP, restored native pointers. No acoustic recording.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'stream.chr',Path(V.__file__),Path(V.V.__file__)]})
    (o/'controls.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='bindings'}))


if __name__=='__main__':main()
