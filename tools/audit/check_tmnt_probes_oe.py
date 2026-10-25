"""Differential complete public source probe calls, including non-turtle gates."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load,Memory,address,location
from check_tmnt_audio_fallback_oc import qualified
from verify_native_relocation import NesMPU


def run(b,entry,char,variant,scenario,y,flags,visibility_model=False,overrides=None,physical=1):
    m=Memory(b);m.page(1,physical);m.page(2,88)
    seed={'CurrentBank':physical|128,'CurrentBankC':216,'SelectedCharacter':char,'TnVariant':variant,
          'RlVariant':variant,'Cv3Variant':variant,'Z2Variant':variant,'KbVariant':variant,'VvVariant':variant,
          'Player_X_Position':[128,15,250,0,128,128][scenario],'Player_PageLoc':1,
          'Player_Y_Position':[176,32,24,15,176,176][scenario],'Player_Y_HighPos':1,
          'Player_Y_Speed':0xfc if scenario in [2,4]else 0,'GameEngineSubroutine':8 if scenario!=5 else 5,
          'TnSeq':0x87 if variant==2 else 0x80,'RgCrouch':variant&1,'Local_eb':y,'R0':2,'R1':0x17,
          'R2':0x91,'R3':0x83,'R4':0x55,'R5':0x7c,'R6':0x11,'R7':0x22,
          'PlayerSize':0,'CrossoverBehaviorVersion':scenario&1}
    if overrides:seed.update(overrides)
    for n,v in seed.items():m[address(b,n)]=v
    for n in ['Block_Buffer_1','Block_Buffer_2']:
        for i in range(208):m[address(b,n)+i]=0 if scenario in [0,2,3,5]else[0x61,0x10,0xc1,0,0x24][i%5]
    # Independent empty-result model has only LDA0/STA R3/RTS. Seed the same
    # unused test RAM on both machines so it cannot mask application writes.
    m[0x7e00:0x7e05]=[0xa9,0,0x85,address(b,'R3'),0x60]
    m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[]
    c=NesMPU(memory=m,pc=entry if isinstance(entry,int)else address(b,entry));c.a=0x56;c.x=0;c.y=y;c.p=flags;c.sp=0xfd
    suppressed=0
    for _ in range(100000):
        if c.pc==0x7f00:break
        if char==15 and c.pc==address(b,'BlockBufferColli_Side'):
            sample=(m[address(b,'Player_Y_Position')]+m[address(b,'BlockBuffer_Y_Adder')+c.y])&255
            ret=m[0x100+(c.sp+1)%256]|m[0x100+(c.sp+2)%256]<<8
            private=ret+1 in b.get('mac_reference_returns',set())
            if visibility_model and private and not 32<=sample<240:
                c.a=0;c.p=(c.p&~0x82)|2;m[address(b,'R3')]=0;c.pc=(ret+1)&65535;c.sp=(c.sp+2)&255
                c.processorCycles+=6;suppressed+=1;continue
            if 'TnMacVisibleSideProbe'in b['syms']:
                assert 32<=sample<240,('new Mac query escaped terrain domain',entry,scenario,c.y,sample)
        c.step()
    else:raise AssertionError(('timeout',entry,char,variant,scenario,y,flags,hex(c.pc),m.banks))
    ram=bytearray(m[:0x8000]);ram[0x100:0x200]=bytes(256);ram[0x5114:0x5118]=bytes(4)
    for s in b['segs'].values():
        if s.get('name')=='"SMCCODE"':
            at=int(s['start'],0);n=int(s['size'],0);ram[at:at+n]=bytes(n)
    for n in ['safecall_a','SafecallA']:
        if n in b['syms']:ram[address(b,n)]=0
    hardware=[(at,v)for at,v in m.writes if 0x2000<=at<0x4018 or 0x5000<=at<0x5114 or 0x5118<=at<0x5207]
    return((c.a,c.x,c.y,c.p&0xcf,c.sp),bytes(ram),hardware,m.banks,c.processorCycles,suppressed)


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mac-visibility-model',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=load(a.baseline),load(a.rom);rows=[]
    if a.mac_visibility_model:
        assert'TnMacVisibleSideProbe'in new['syms']
        q=qualified(a.baseline);lo=q[('LmSideGate',)];hi=q[('LmSideGate','Offsets')]
        base=location(old,'LmSideGate')-address(old,'LmSideGate');target=address(old,'BlockBufferColli_Side')
        sites=[pc for pc in range(lo,hi)if old['raw'][base+pc:base+pc+3]==bytes([0x20,target&255,target>>8])]
        assert len(sites)==2;old['mac_reference_returns']={pc+3 for pc in sites}
    for entry,ys in [('CrossoverSourceSideProbe',[3,4,6,7]),('KbNativeHeadBridge',[0,7,14,30])]:
        for char,variant,scenario,y,flags in itertools.product(range(20),range(4),range(6),ys,[0x30,0x71]):
            x=run(old,entry,char,variant,scenario,y,flags,visibility_model=a.mac_visibility_model)
            z=run(new,entry,char,variant,scenario,y,flags)
            assert x[:4]==z[:4],(entry,char,variant,scenario,y,flags,x[0],z[0],
                [(hex(i),x[1][i],z[1][i])for i in range(0x8000)if x[1][i]!=z[1][i]][:16])
            rows.append(dict(entry=entry,character=char,variant=variant,scenario=scenario,y=y,flags=flags,
                             old_cycles=x[4],new_cycles=z[4],modeled_unmapped_queries=x[5]))
    stats={}
    for e in ['CrossoverSourceSideProbe','KbNativeHeadBridge']:
        stats[e]={}
        for category,chars in [('turtle',[19]),('Mac',[15]),('other',[c for c in range(20)if c not in [15,19]])]:
            s=[r['old_cycles']-r['new_cycles']for r in rows if r['entry']==e and r['character']in chars]
            stats[e][category+'_cycles_saved']=[min(s),max(s)]
    q=dict(passed=True,ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
           cases=len(rows),stats=stats,modeled_unmapped_queries=sum(r['modeled_unmapped_queries']for r in rows),
           scope='Complete public head/side calls, all20 internal IDs/four variants, empty/mixed terrain, cell/page/status edges, upward/ground and non-gameplay inputs. Only the two original Mac private side-getter sites are modeled as an empty result outside terrain32..239 when requested; every other call executes the unmodified baseline. Exact A/X/Y/meaningfulP/SP, application RAM except discarded stack/SMC/safecall bookkeeping/mapper latches, non-banking hardware writes and final physical banks. Seeded CPU components; native routes/items/timing remain separate.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
