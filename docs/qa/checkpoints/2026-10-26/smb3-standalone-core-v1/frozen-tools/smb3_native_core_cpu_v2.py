"""Standalone actual assembled SMB3 core vs frozen12-role original calls.

Logical source stores and physical sample translations are separate oracles.
No host AudioUpdate, native timing or universal71-song reachability claim.
"""
from pathlib import Path
from collections import Counter
import argparse,gzip,hashlib,json,math,traceback
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
TRACE=D/'smb3-original-music-closure-v3'
NSF=R/'reference/new-roster-audio/mario3/crossover-named.nsf'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Bus(Memory):
    def __init__(self,b,image):
        self.armed=False;super().__init__(b);self.image=image;self.logical=[];self.physical=[];self.sourcewrites=[];self.virtualwrites=[]
        self.pc=0;self.source12=address(b,'B3Source4012');self.maps=address(b,'B3VirtualMaps');self.sourceapu=[0]*24;self.hw=[0]*24
        self.dmc_configs=set();self.samplebytes=set();self.samples=Counter();self.samplechecks=0
        self.mapperPCs={address(b,'B3Source9004'),address(b,'B3Source900A')}
        closure=json.loads((TRACE/'dynamic-closure.json').read_text());self.source_write_cells={i for lo,hi in closure['RAM_writes']for i in range(lo,hi+1)}
        self.work=range(address(b,'B3VirtualMaps'),address(b,'B3WorkEnd'))
        self.allowed=set(self.work)|self.source_write_cells|{3,4,address(b,'CurrentBank')}|set(range(0x100,0x200))|{0x5115,0x5117}|set(range(0x4000,0x4018))
        self.armed=True
    def __setitem__(self,at,value):
        if isinstance(at,int)and self.armed:
            assert at in self.allowed,('First unowned write',hex(self.pc),hex(at),value)
            if at in self.source_write_cells:self.sourcewrites.append((at,value))
            if at==self.source12 and self.pc!=0:
                # Only the genuine writer store publishes a source request;
                # standalone metadata reset is not an original APU event.
                if self.writer_start<=self.pc<self.writer_end:
                    self.logical.append((0x4012,value));self.sourceapu[18]=value
            if self.maps<=at<self.maps+8 and self.pc in self.mapperPCs:self.virtualwrites.append((0x5ff8+at-self.maps,value))
            if 0x4000<=at<=0x4017:
                self.physical.append((at,value));self.hw[at-0x4000]=value
                if at!=0x4012:self.logical.append((at,value));self.sourceapu[at-0x4000]=value
                if at==0x4015 and value&16:
                    logical=self.sourceapu[18];length=self.hw[19]*16+1
                    start=0xc000+logical*64;physical_start=0xc000+self.hw[18]*64
                    maps=tuple(list.__getitem__(self,slice(self.maps,self.maps+8)))
                    offsets=[maps[((start+i)&65535)-0x8000>>12]*4096+((start+i)&4095)for i in range(length)]
                    wanted=bytes(self.image[i]for i in offsets)
                    actual=bytes(list.__getitem__(self,(physical_start+i)&65535)for i in range(length))
                    assert actual==wanted,('Wrong physical DMC sample',hex(self.pc),logical,self.hw[18],length,self.banks[3],maps)
                    key=(self.sourceapu[16],self.sourceapu[17],logical,self.sourceapu[19],maps)
                    self.dmc_configs.add(key);self.samplebytes.update(offsets);self.samplechecks+=1
                    self.samples[(offsets[0],length,hashlib.sha256(actual).hexdigest())]+=1
        super().__setitem__(at,value)

def source_state(m,b):
    data=bytearray(list.__getitem__(m,slice(0,256))+list.__getitem__(m,slice(0x200,0x800))+list.__getitem__(m,slice(0x6000,0x8000)))
    # Extra adapter metadata is not original source state. Original dynamic
    # closure proves no source read/write to any of these cells in12 contracts.
    for at in list(m.work)+[address(b,'CurrentBank'),address(b,'CurrentBankC')]:
        index=at if at<256 else at-256 if at<0x800 else at-0x5900
        assert at>=0x6000
        data[index]=0
    return bytes(data)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['rom','output']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--calls',type=int,default=18000);p.add_argument('--role');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    b=scoped_load(a.rom);image=NSF.read_bytes()[128:];proof=json.loads((TRACE/'proof.json').read_text());rows=[]
    try:
        for role,wantrole in proof['roles'].items():
            if a.role and a.role!=role:continue
            m=Bus(b,image);m.armed=False;m.page(1,86);m.page(2,38)
            m[address(b,'CurrentBank')]=86|128;m[address(b,'CurrentBankC')]=38|128
            m.writer_start=address(b,'B3Write4012');m.writer_end=address(b,'B3Write4015');m.armed=True
            c=NesMPU(memory=m);costs=[];stores=0;rawstores=0;digest=hashlib.sha256();minsp=255
            with gzip.open(TRACE/f'{role}-{wantrole["one_based_track"]:02d}/calls.jsonl.gz','rt')as f:
                for line in f:
                    want=json.loads(line);tick=want['tick']
                    if tick>a.calls:break
                    m.armed=False;m[510],m[511]=255,126;m.armed=True
                    c.pc=address(b,'B3StandaloneCold'if tick==0 else'B3SourceA000');c.a=wantrole['one_based_track']-1 if tick==0 else 0;c.x=c.y=0;c.p=0x24;c.sp=253
                    m.logical=[];m.physical=[];m.sourcewrites=[];m.virtualwrites=[];m.writes=[];initial=c.processorCycles
                    for _ in range(200000):
                        if c.pc==0x7f00:break
                        assert c.pc>=0x8000,('Bad source PC',role,tick,hex(c.pc))
                        assert m[c.pc]!=0,('Unexpected BRK/domain exit',role,tick,hex(c.pc),c.a,c.x,c.y)
                        m.pc=c.pc;minsp=min(minsp,c.sp);c.step()
                    else:raise AssertionError(('Core timeout',role,tick,hex(c.pc),m.banks))
                    got=[c.a,c.x,c.y,c.p&207,c.sp]
                    expected_regs=want['post_AXY_P_SP'][:];expected_regs[3]&=207
                    assert got==expected_regs,('Source ABI divergence',role,tick,got,want['post_AXY_P_SP'])
                    assert list(map(list,m.logical))==want['APU'],('Ordered original APU divergence',role,tick,m.logical,want['APU'])
                    assert list(map(list,m.sourcewrites))==want['ordered_nonstack_RAM_writes'],('Ordered source RAM divergence',role,tick,m.sourcewrites,want['ordered_nonstack_RAM_writes'])
                    assert list(map(list,m.virtualwrites))==want['mapper'],('Original mapper divergence',role,tick,m.virtualwrites,want['mapper'])
                    maps=list.__getitem__(m,slice(m.maps,m.maps+8));assert maps==want['banks'],('Logical page mapping divergence',role,tick,maps,want['banks'])
                    state=source_state(m,b);h=hashlib.sha256(state).hexdigest()
                    assert h==want['full_nonstack_source_RAM_sha256'],('Complete canonical source state divergence',role,tick,h,want['full_nonstack_source_RAM_sha256'])
                    assert m.banks[1]==86 and m.banks[2]==38 and m[address(b,'CurrentBank')]==214,('Failed reader bank restoration',role,tick,m.banks)
                    costs.append(c.processorCycles-initial);stores+=len(m.logical);rawstores+=len(m.physical);digest.update(state)
            row=dict(role=role,song=wantrole['one_based_track'],calls=len(costs),ordered_original_APU_stores=stores,physical_APU_stores=rawstores,init_cycles=costs[0],mean_play_cycles=sum(costs[1:])/max(1,len(costs)-1),p95=sorted(costs[1:])[math.ceil(.95*(len(costs)-1))-1]if len(costs)>1 else None,peak_play_cycles=max(costs[1:],default=0),original_mean=wantrole['mean_play_cycles'],original_peak=wantrole['peak']['cycles'],minimum_SP=minsp,source_state_digest=digest.hexdigest(),physical_DMC_sample_checks=m.samplechecks,distinct_DMC_configs=len(m.dmc_configs),DMC_payload_union_bytes=len(m.samplebytes),samples=[dict(source_first=k[0],bytes=k[1],sha256=k[2],requests=v)for k,v in sorted(m.samples.items())])
            rows.append(row);(a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
        result=dict(passed=True,source_only=True,native_run=False,host_integration=False,ROM_sha256=sha(a.rom),source_NSF_sha256=sha(NSF),original_trace_proof_sha256=sha(TRACE/'proof.json'),calls=sum(q['calls']for q in rows),ordered_original_APU_stores=sum(q['ordered_original_APU_stores']for q in rows),roles=rows,all_original_source_RAM_writes_state_AXYP_SP_maps_ordered_APU_exact=True,full_original_payload_preserved=True,physical_sample_bytes_match_original_virtual_payload=True,checker_sha256=sha(__file__),limits='Standalone fixed12 cold init/play contract only. Original numeric RAM remains live in isolated fixture; helper metadata7B00..7B14 and host bank shadows are explicitly canonicalized. No host borrow/ownership/lifecycle, native scheduling/DMC DMA/PPU, all71 songs or universal/static reachability claim.')
        (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    except Exception as e:
        result=dict(passed=False,ROM_sha256=sha(a.rom),checker_sha256=sha(__file__),completed_roles=rows,error=str(e),traceback=traceback.format_exc())
        (a.output/'failure.json').write_text(json.dumps(result,indent=2)+'\n');raise

if __name__=='__main__':main()
