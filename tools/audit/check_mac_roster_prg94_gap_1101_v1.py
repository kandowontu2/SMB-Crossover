"""Bound all compiled Mac roster descriptors below the proposed PRG94 gap."""
from pathlib import Path
import hashlib,json,sys,re
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
O=R/'build/mac-roster-prg94-gap-1101-v1'
def main():
    rom=R/'build/kirby-approach-owner-1101-v3/candidate.nes'
    b=scoped_load(rom);raw=b['raw'];base=16+94*8192;records=[]
    for prefix,count,bottom,top in [('MacRoster',51,0xc2c0,0xcd98),('LmPose',10,0xc000,0xc2b9),('Sunny',35,0xce00,0xdfff)]:
      for face in ['R','L']:
        lo=location(b,prefix+face+'Lo');hi=location(b,prefix+face+'Hi')
        for i in range(count):
            ptr=raw[lo+i]+256*raw[hi+i];offset=base+ptr-0xc000
            n=raw[offset];assert n%4==0 and 0<n<=252
            end=ptr+1+n
            assert bottom<=ptr<end<=top,(prefix,face,i,ptr,end)
            records.append(dict(owner=prefix,face=face,index=i,start=ptr,end=end))
    star=location(b,'LmStar');n=raw[star]
    assert n%4==0 and 0<n<=252 and base<=star<star+1+n<=base+0x2b9
    assert set(raw[base+0xd98:base+0xe00])=={255}
    prior=(R/'build/kirby-owner-main-1101-v2/candidate.nes').read_bytes()
    assert raw[base:base+8192]==prior[base:base+8192]
    sources=[R/'src'/n for n in ['mac_roster.s','mac_roster_data.inc','sunny.s','sunny_art.inc','sunny_state.inc','little_mac_render.s']]
    mac=sources[0].read_text();sunny=sources[2].read_text()
    assert 'cmp #MAC_ROSTER_VARIANTS\n bcc Done\n lda #MAC_ROSTER_MAC' in mac
    selector=mac.split('.proc MacRosterSelectFrame',1)[1].split('.endproc',1)[0]
    tables=sorted(set(re.findall(r'lda (MacRoster\w+),y',selector)))
    assert tables
    for name in tables:
        at=location(b,name);assert max(raw[at:at+3])<51,name
    assert 'cmp #120\n bcc Ready\n lda #0\n sta SunnyClock' in sunny
    assert 'cpx #SUNNY_POSE_COUNT\n bcc Valid\n ldx #SUNNY_POSE_IDLE' in sunny
    animation_cases=0
    for name in ['SunnySemanticSmall','SunnySemanticBig']:
        at=location(b,name)
        for pose,value in enumerate(raw[at:at+17]):
            for clock in range(120):
                frame=value
                if pose==0:frame+=[0,0,1,2,2,1][clock//20]
                elif pose==7:frame+=(clock//(15 if value<33 else 30))&1
                assert 0<=frame<35,(name,pose,clock,frame)
                animation_cases+=1
    O.mkdir(exist_ok=True)
    result=dict(passed=True,grant=False,ROM_sha256=hashlib.sha256(raw).hexdigest(),
        bank_sha256=hashlib.sha256(raw[base:base+8192]).hexdigest(),
        proposed_half_open=[0xd98,0xe00],descriptors=records,
        maximum_descriptor_end=max(r['end'] for r in records),
        Mac_selector_tables=tables,Sunny_animation_cases=animation_cases,
        source_bindings={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        remaining=['Owning linker must shrink Mac art capacity toCD98 before reserving gap.'],
        scope='All192 compiled roster/nativeMac/Sunny sprite records and Mac star stay within their owners, outside the proposed interval. Partial owner proof; FF bytes alone are not an allocation.')
    (O/'mac-records.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='descriptors'}))
if __name__=='__main__':main()
