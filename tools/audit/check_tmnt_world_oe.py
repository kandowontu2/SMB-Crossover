"""Actual linked private world renderers: state, ordered stores and fallback ABI."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU


def run(b,pc,record,state,offset,rotation,flags,attr,header=None,shadow=216,physical=88):
    m=Memory(b);m.page(1,87);m.page(2,physical)
    for i in range(259):m[0x200+i]=(i*73+29)&255
    x,y,xp,yp=state
    values={'R0':record&255,'R1':record>>8,'R3':attr,'R4':x,'R5':xp,'R6':y,'R7':yp,
            'CurrentOAMOffset':offset,'GuestOamRotationActive':rotation[0],'RgOamRotation':rotation[1],
            'CurrentBank':215,'CurrentBankC':shadow}
    if header is not None:
        values.update(R0=0xa0,R1=0x5c);m[0x5ca0]=header
        for i in range(1,257):m[0x5ca0+i]=[1,0xa2,0xf8,0xfc][(i-1)%4]
    for n,v in values.items():m[address(b,n)]=v
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=pc);c.sp=0xfd;c.a=0x55;c.x=3;c.y=7;c.p=flags
    for _ in range(20000):
        if c.pc==0x7f00:break
        c.step()
    else:raise AssertionError(('timeout',hex(record),state,offset,rotation,flags,header,hex(c.pc)))
    ram=bytearray(m[:0x8000]);ram[0x100:0x200]=bytes(256);ram[0x5114:0x5118]=bytes(4)
    for s in b['segs'].values():
        if s.get('name')=='"SMCCODE"':
            at=int(s['start'],0);n=int(s['size'],0);ram[at:at+n]=bytes(n)
    for n in ['safecall_a','SafecallA']:
        if n in b['syms']:ram[address(b,n)]=0
    return((c.a,c.x,c.y,c.p&0xcf,c.sp),bytes(ram),
           [(at,v)for at,v in m.writes if 0x200<=at<=0x302],m.banks,c.processorCycles)


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--hud',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    before,after=qualified(a.baseline),qualified(a.rom)
    has_probes='TnFastSideGate'in new['syms']
    has_mac_visibility='LmVisibleSideProbe'in new['syms']
    assert all(after.get(n)==v for n,v in before.items()if n!=('_FARCALL_COUNT',)),'A preexisting label moved'
    assert after[('_FARCALL_COUNT',)]==before[('_FARCALL_COUNT',)]+((2 if'TnMacSideProbe'in new['syms']else 4)if has_probes else 0)
    raw0,raw1=old['raw'],new['raw']
    call=location(new,'TnHudWorldBranch'if a.hud else'TnWorldBakedCall')
    extra=location(new,'TnHudWorldRender'if a.hud else'TnWorldBakedRender')
    if a.hud:
        assert raw1[call]==0x90 and address(new,'TnHudWorldRender')==(address(new,'TnHudWorldBranch')+2+(raw1[call+1]-256 if raw1[call+1]&128 else raw1[call+1]))&65535
    else:assert raw1[call]==0x20 and int.from_bytes(raw1[call+1:call+3],'little')==address(new,'TnWorldBakedRender')
    banks=[i for i in range(128)if raw0[16+i*8192:16+(i+1)*8192]!=raw1[16+i*8192:16+(i+1)*8192]]
    expected_banks=[87,89,93,127]if has_mac_visibility else([87,89,127]if has_probes else[87])
    assert banks==expected_banks and raw0[16+1048576:]==raw1[16+1048576:]
    g=next(s for s in new['segs'].values()if s['name']=='"TMNT_CORE"');end=int(g['ooffs'],0)+int(g['size'],0)
    assert all(raw0[i]==raw1[i]or call+1<=i<call+(2 if a.hud else 3) or extra<=i<end for i in range(16+87*8192,16+88*8192))
    if has_probes:
        extra89=location(new,'TnFastSideGate');g89=next(s for s in new['segs'].values()if s['name']=='"TMNT_COMBAT"')
        end89=int(g89['ooffs'],0)+int(g89['size'],0)
        assert all(raw0[i]==raw1[i]or extra89<=i<end89 for i in range(16+89*8192,16+90*8192))
        spans=[location(new,n)for n in ['CrossoverSourceSideProbe','KbNativeHeadBridge']]
        assert all(raw0[i]==raw1[i]or any(at<=i<at+18 for at in spans)for i in range(16+127*8192,16+128*8192))
    if has_mac_visibility:
        helper=location(new,'LmVisibleSideProbe');g93=next(s for s in new['segs'].values()if s['name']=='"LM_CORE"')
        end93=int(g93['ooffs'],0)+int(g93['size'],0);spans=[location(new,n)for n in ['LmVisibleSideCall','LmVisibleLowerCall']]
        for at in spans:assert raw1[at]==0x20 and int.from_bytes(raw1[at+1:at+3],'little')==address(new,'LmVisibleSideProbe')
        assert all(raw0[i]==raw1[i]or helper<=i<end93 or any(at+1<=i<at+3 for at in spans)
                   for i in range(16+93*8192,16+94*8192))
    records={};bounds=[]
    for face in ['R','L']:
        lo,hi=location(old,'TnWorld'+face+'Lo'),location(old,'TnWorld'+face+'Hi')
        for pose in range(84):
            ptr=raw0[lo+pose]|raw0[hi+pose]<<8;at=16+88*8192+ptr-0xc000;n=raw0[at]
            assert n%4==0 and n<128;records[ptr]=n
            for j in range(1,n+1,4):
                tile,attr,y,x=raw0[at+j:at+j+4];dx=x-256 if x&128 else x;dy=y-256 if y&128 else y
                assert -8<=dx<=0 and -24<=dy<=0;bounds.append((dx,dy))
    rows=[];oldpc=address(old,'TnFastWorldRender');newpc=address(new,'TnFastWorldRender'if a.hud else'TnWorldBakedRender')
    def check(ptr,state,offset,rotation,flags,attr,header=None,tag='source',**kw):
        x=run(old,oldpc,ptr,state,offset,rotation,flags,attr,header,**kw)
        y=run(new,newpc,ptr,state,offset,rotation,flags,attr,header,**kw)
        assert x[:4]==y[:4],(tag,hex(ptr),state,offset,rotation,flags,attr,header,kw,x[0],y[0],
            [(hex(i),x[1][i],y[1][i])for i in range(0x8000)if x[1][i]!=y[1][i]][:12])
        rows.append(dict(tag=tag,pointer=ptr,header=records.get(ptr,header),state=state,offset=offset,
                         rotation=rotation,flags=flags,attribute=attr,old_cycles=x[4],new_cycles=y[4],**kw))
    states=[(8,24,0,1),(128,128,0,1),(255,255,0,1),(0,24,0,1),(7,24,0,1),(8,23,0,1),
            (8,0,0,1),(128,23,0,1),(255,24,255,1),(0,24,1,1),(128,255,0,0),(128,0,0,2)]
    if a.hud:states += [(8,y,0,1)for y in range(15,25)]+[(255,23,0,1)]
    offsets=[0,16,128,232,240,248,252];rotations=[(0,0),(1,4),(1,128),(1,252)]
    for i,(ptr,state,off,rot,flags)in enumerate(itertools.product(records,states,offsets,rotations,[0x30,0x71])):
        check(ptr,state,off,rot,flags,[0,0x20,3,0xff][i%4])
    for header,off,rot,flags in itertools.product([0,1,3,4,8,16,124,128,252,255],offsets,rotations,[0x30,0x71]):
        check(0x5ca0,(128,128,0,1),off,rot,flags,0,header,tag='RAM-header')
    for ptr,flags in itertools.product(range(0xd100,0xd400),[0x30,0x71]):
        check(ptr,(128,128,0,1),0,(1,128),flags,0,tag='every-hash-input')
    for ptr,off,flags in itertools.product(records,[0,255],[0x30,0x71]):
        check(ptr,(128,128,0,1),off,(1,252),flags,0,tag='other-bank',shadow=224,physical=96)
    interior=[r['old_cycles']-r['new_cycles']for r in rows if r['tag']=='source'and r['header']in [8,16]
              and r['state']in states[:3]and r['attribute']&3==0 and r['header']+r['offset']<=255]
    hud_savings=[r['old_cycles']-r['new_cycles']for r in rows if r['tag']=='source'and r['header']==16
                 and r['state'][2:]==(0,1)and 16<=r['state'][1]<24 and r['state'][0]>=8
                 and r['attribute']&3==0 and r['offset']+16<=255
                 and r['pointer']in [0xd18a,0xd19b,0xd1ac,0xd1bd,0xd2ef,0xd300,0xd311,0xd322]]if a.hud else[]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(raw1).hexdigest(),baseline_ROM_sha256=hashlib.sha256(raw0).hexdigest(),
           cases=len(rows),source_table_entries=168,unique_source_records=len(records),changed_PRG_banks=banks,CHR_unchanged=True,
           all_preexisting_runtime_labels_unchanged=True,build_only_farcall_counter_delta=after[('_FARCALL_COUNT',)]-before[('_FARCALL_COUNT',)],
           interior_cycles_saved=[min(interior),max(interior)],
           HUD_cycles_saved=[min(hud_savings),max(hud_savings)]if hud_savings else None,
           scope='Actual old/new private helper, all168 world table entries collapsed by identical pointer, signed page/edge states, palettes, capacity and rotated OAM, RAM header mutations, every D1..D3 hash input and other-bank fallback. Exact A/X/Y/meaningfulP/SP, application RAM except discarded stack/SMC/safecall bookkeeping/mapper latches, ordered OAM including overflow and final banks. Native timing/IRQ/routes remain separate.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
