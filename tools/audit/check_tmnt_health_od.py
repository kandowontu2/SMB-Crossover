"""Execute real health draw routines for valid and rejected cache/ring states."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU


def run(b,pc,record,offset,rotation,flags):
    m=Memory(b);bank=(location(b,'TnDraw')-16)//8192;art=(location(b,'TnArtStart')-16)//8192
    m.page(1,bank);m.page(2,art)
    for i in range(256):m[0x200+i]=(i*73+29)&255
    for i,v in enumerate(record):m[0x5ca0+i]=v
    for n,v in {'R0':0xa0,'R1':0x5c,'R2':0x96,'R3':0x83,'R4':80,'R5':0,'R6':7,'R7':0x84,
                'CurrentBank':bank|128,'CurrentBankC':art|128,'CurrentOAMOffset':offset,
                'GuestOamRotationActive':rotation[0],'RgOamRotation':rotation[1]}.items():m[address(b,n)]=v
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=pc);c.a=0x55;c.x=3;c.y=7;c.p=flags;c.sp=0xfd;fallback=0
    for _ in range(20000):
        if c.pc==0x7f00:break
        if c.pc==address(b,'MetaspriteRenderLoop'):fallback+=1
        c.step()
    else:raise AssertionError(('Health CPU timeout',hex(c.pc),record[0],offset,rotation))
    excluded=set(range(0x100,0x200))|set(range(0x5114,0x5118))
    for s in b['segs'].values():
        if s.get('name')=='"SMCCODE"':excluded.update(range(int(s['start'],0),int(s['start'],0)+int(s['size'],0)))
    for name in ['safecall_a','SafecallA']:
        if name in b['syms']:excluded.add(address(b,name))
    ram=bytes(0 if i in excluded else m[i]for i in range(0x8000))
    oam=[(at,v)for at,v in m.writes if 0x200<=at<=0x302]
    return(c.a,c.x,c.y,c.p&0xcf,c.sp),ram,oam,list(m.banks),c.processorCycles,fallback


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom)
    before,after=qualified(a.baseline),qualified(a.rom)
    # TnResidentEnd is used only by .res to keep the fixed return at EB3A.
    # It is a linker padding boundary, never a callable/runtime label.
    moved={str(n):[v,after.get(n)]for n,v in before.items()if after.get(n)!=v and n not in
           [('_FARCALL_COUNT',),('SamusAudioUpdate','TnResidentEnd')]}
    assert not moved,moved
    raw0,raw1=old['raw'],new['raw'];call=location(new,'TnHealthDrawCall');start=location(new,'TnHealthRender')
    assert raw1[call]==0x20 and int.from_bytes(raw1[call+1:call+3],'little')==address(new,'TnHealthRender')
    changed=[b for b in range(128)if raw0[16+b*8192:16+(b+1)*8192]!=raw1[16+b*8192:16+(b+1)*8192]]
    assert changed in [[89],[59,89],[59,86,89],[59,86,89,123],[4,59,86,88,89,123,127]]and raw0[16+1048576:]==raw1[16+1048576:]
    counter_delta=(2 if 86 in changed else 1)+int('TnPrimaryRender'in new['syms'])+int('X5OwnMovement'in new['syms'])
    assert after[('_FARCALL_COUNT',)]==before[('_FARCALL_COUNT',)]+counter_delta
    if 59 in changed:
        inv=location(old,'InventorySupported')
        assert all(raw0[pos]==raw1[pos]or inv<=pos<inv+46 for pos in range(16+59*8192,16+60*8192))
    if 86 in changed:
        ui=location(new,'X5OwnUiCall');extra=location(new,'X5OwnInventoryUi')
        assert raw1[ui]==0x4c and raw1[ui+3:ui+18]==bytes([0xea])*15
        move=location(new,'X5OwnMovementCall')if'X5OwnMovementCall'in new['syms']else -20
        if move>=0:
            assert raw1[move]==0x20 and int.from_bytes(raw1[move+1:move+3],'little')==address(new,'X5OwnMovement')
            assert raw1[move+3:move+18]==bytes([0xea])*15
        assert all(raw0[pos]==raw1[pos]or ui<=pos<ui+18 or move<=pos<move+18 or pos>=extra for pos in range(16+86*8192,16+87*8192))
    if 123 in changed:
        extra=location(new,'TnNativeDuration');end=location(new,'TnSevenProduct')+256
        patch=16+123*8192+0xc75
        assert raw1[patch]==0x20 and int.from_bytes(raw1[patch+1:patch+3],'little')==address(new,'TnNativeDuration')
        assert raw1[patch+3:patch+6]==bytes([0x4c,0x89,0xac]) and raw1[patch+6:patch+20]==bytes([0xea])*14
        assert end<=16+123*8192+0x612
        assert all(raw0[pos]==raw1[pos]or patch<=pos<patch+20 or extra<=pos<end
                   for pos in range(16+123*8192,16+124*8192))
    if 88 in changed:
        extra=location(new,'TnBodyRender');g=next(q for q in new['segs'].values()if q['name']=='"TMNT_GFX"')
        end=int(g['ooffs'],0)+int(g['size'],0)
        assert all(raw0[pos]==raw1[pos]or extra<=pos<end for pos in range(16+88*8192,16+89*8192))
        gate=location(new,'TnBodyGate');end=location(new,'TnBodyLegacy')+5
        assert end<=16+127*8192+0xb3a
        assert all(raw0[pos]==raw1[pos]or gate<=pos<end for pos in range(16+127*8192,16+128*8192))
        tail=location(new,'TnBodyFallbackCall')
        assert raw1[tail]==0x4c and int.from_bytes(raw1[tail+1:tail+3],'little')==address(new,'TnBodyGate')
        assert all(raw0[pos]==raw1[pos]or tail+1<=pos<tail+3 for pos in range(16+4*8192,16+5*8192))
    for i in range(8192):
        pos=16+89*8192+i
        primary=location(new,'TnPrimaryDrawCall')if'TnPrimaryDrawCall'in new['syms']else -10
        if raw0[pos]!=raw1[pos]:assert call+1<=pos<call+3 or primary+1<=pos<primary+3 or pos>=start,pos
    oldpc=before[('TnDraw','Draw')];newpc=address(new,'TnHealthRender');rows=[];fast=slow=0
    def check(record,offset,rotation,flags,tag):
        nonlocal fast,slow
        x=run(old,oldpc,record,offset,rotation,flags);y=run(new,newpc,record,offset,rotation,flags)
        assert x[:4]==y[:4],(tag,record,offset,rotation,hex(flags),x[0],y[0],
            [(hex(i),x[1][i],y[1][i])for i in range(0x8000)if x[1][i]!=y[1][i]][:12],x[3],y[3])
        fast+=y[5]==0;slow+=y[5]>0
        rows.append(dict(tag=tag,header=record[0],offset=offset,rotation=rotation,flags=flags,old_cycles=x[4],new_cycles=y[4],fallback=bool(y[5])))
    offsets=[0,1,8,112,124,128,232,236,239,240,244,248,252,255]
    rotations=[(0,0),(1,0),(1,4),(1,128),(1,252),(1,255)]
    flags=[0x30,0x71,0x39,0xee]
    for tile,off,rot,flag in itertools.product([0,1,15,16,31,32,63,64,96,127,128,255],offsets,rotations,flags):
        record=[16]
        for i in range(4):record.extend([(tile+17*i)&255,0,0,i*8])
        check(record,off,rot,flag,'valid-cache')
    base=[16,10,0,0,0,20,0,0,8,30,0,0,16,40,0,0,24]
    for header,off,rot,flag in itertools.product([0,1,3,4,8,12,20,124,128,252,255],[0,112,239,240,255],rotations,[0x30,0xee]):
        q=base.copy();q[0]=header;check(q,off,rot,flag,'unsupported-header')
    for cell,value,off,rot,flag in itertools.product([2,3,4,6,7,8,10,11,12,14,15,16],[1,8,16,24,255],[0,112,239,240],rotations,[0x30,0xee]):
        if base[cell]==value:continue
        q=base.copy();q[cell]=value;check(q,off,rot,flag,'changed-coordinate-or-attribute')
    savings=[q['old_cycles']-q['new_cycles']for q in rows if not q['fallback']]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(raw1).hexdigest(),baseline_ROM_sha256=hashlib.sha256(raw0).hexdigest(),
           cases=len(rows),fast_cases=fast,fallback_cases=slow,native_valid_cycles_saved=[min(savings),max(savings)],
           all_preexisting_runtime_labels_preserved=True,build_only_farcall_counter_delta=counter_delta,changed_PRG_banks=changed,CHR_unchanged=True,
           scope='Actual linked private health-call ABI with its fixed caller position/pointer. Valid dynamic tiles, every cached coordinate/attribute changed independently, unsupported headers, capacity rejection, unaligned and rotated OAM including page overflow. Exact A/X/Y/meaningfulP/SP, all RAM outside discarded stack/SMC/safecall scratch/mapper latches, ordered OAM including overflow bytes and final banks. No native IRQ, timing or campaign claim.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
