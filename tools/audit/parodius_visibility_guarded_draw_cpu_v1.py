"""Paired complete DrawAll CPU components, never native/controller evidence."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_roll_renderer import Memory
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def execute(b,rec,profile,mode,facing,actor,actor_frame):
    l=lambda n:address(b,n)
    mem=bytearray(65536)
    for seg in b['segs'].values():
        if seg.get('name')=='"SMCCODE"':
            st,sz,off=[int(seg[k],0)for k in ['start','size','ooffs']];mem[st:st+sz]=b['raw'][off:off+sz]
    ref=rec['refs'][0];x,y,prior,flip=profile
    vals=dict(SelectedCharacter=18,VvVariant=ref['variant'],PnPool=ref['pool'],PnFrame=ref['frame'],GameEngineSubroutine=8,OperMode=1,CrossoverBehaviorVersion=mode,ObjectMetasprite=l('METASPRITE_SAMUS_BODY'),Player_X_Position=x&255,Player_PageLoc=(x>>8)&255,Player_Y_Position=y&255,Player_Y_HighPos=(1+(y>>8))&255,CurrentBank=132,CurrentBankC=rec['bank']|128,RgOamUsed=40,RgOamFirst=prior,InvHudActive=0,PlayerFacingDir=facing,ObjectVerticalFlip=flip)
    poollo=location(b,'PnPoolBodyLo')+ref['pool'];vals['SmChrBank']=b['raw'][poollo]
    for n,v in vals.items():mem[l(n)]=v
    ptr=rec['pointer'];mem[l('SmPosePtr')]=ptr&255;mem[l('SmPosePtr')+1]=ptr>>8
    if actor:
        mem[l('PnFrame')+1]=actor_frame;mem[l('PnX')+1]=(x+32)&255;mem[l('PnY')+1]=(y-24)&255
    stop=0x5b00;sp=217;mem[0x101+sp]=(stop-1)&255;mem[0x102+sp]=(stop-1)>>8
    bus=Memory(b['raw'],mem,{0x8000:126,0xa000:4,0xc000:rec['bank'],0xe000:127})
    c=NesMPU(memory=bus);c.pc=l('DrawAllMetasprites');c.sp=sp;c.a=173;c.x=73;c.y=19;c.p=0x6d
    for steps in range(50000):
        if c.pc==stop:break
        c.step()
    else:raise AssertionError(('DrawAll unbounded',c.pc,bus.banks,ref,profile))
    assert c.sp==sp+2 and bus.banks[0xa000]==4 and bus.banks[0xc000]==rec['bank']
    begin=l('Sprite_Y_Position');oam=bytes(bus.data[begin:begin+256]);start=(bus.data[l('RgOamPlayerStart')]+bus.data[l('RgOamRotation')])&255
    size=len(rec['parts'])*4;indices=[((start+i)&255)//4 for i in range(0,size,4)]
    pointer=bus.data[l('SmPosePtr')]+256*bus.data[l('SmPosePtr')+1]
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,ram=bus.data,oam=oam,indices=indices,physical_start=start,pointer=pointer,banks=bus.banks,begin=begin)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['baseline','candidate','body-config','aliases','output']:ap.add_argument('--'+n,type=Path,required=True)
    ap.add_argument('--quick',action='store_true')
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    bundles=[scoped_load(a.baseline),scoped_load(a.candidate)];cfg=json.loads(a.body_config.read_text());records=list(cfg['body_sources'].values())
    aliases=json.loads(a.aliases.read_text())['all_records'];actors={}
    for refs in aliases.values():
        for r in refs:
            if not r['body']:actors.setdefault(r['pool'],r['frame'])
    # Rebind literal original record bytes, not the sorted input config bytes.
    for r in records:
        at=16+r['bank']*8192+r['pointer']%8192;r['parts']=[list(bundles[0]['raw'][i:i+4])for i in range(at+1,at+1+bundles[0]['raw'][at],4)]
    if a.quick:records=records[:1]
    profiles=[(96,120,12,0),(96,120,20,0),(4,120,12,0),(96,24,12,0),(96,120,12,1),(96,64,12,32)]
    rows=[];scratch=Counter();cost=Counter();case=None
    allowed={address(bundles[0],n)for n in ['PnDrawFrame','VvTemp','VvTemp2']}
    allowed.update([address(bundles[0],'SmPosePtr'),address(bundles[0],'SmPosePtr')+1])
    apps=list(range(0x100))+list(range(0x300,0x800))+list(range(0x5c00,0x8000))
    try:
        for rec,profile,mode,facing,actor in itertools.product(records,profiles,[0,1],[1,2],[0,1]):
            ref=rec['refs'][0];case=dict(record=rec['label'],ref=ref,profile=profile,mode=mode,facing=facing,staged_source_actor=actor)
            x,y=[execute(b,rec,profile,mode,facing,actor,actors[ref['pool']])for b in bundles]
            assert x['regs']==y['regs'],('Public DrawAll AXYP/SP changed',case,x['regs'],y['regs'])
            assert x['banks']==y['banks'] and x['indices']==y['indices']
            assert Counter(x['oam'][i*4:i*4+4]for i in x['indices'])==Counter(y['oam'][i*4:i*4+4]for i in y['indices']),('Complete body multiset',case)
            for i in range(64):
                if i not in x['indices'] and (x['oam'][i*4]<239 or y['oam'][i*4]<239):assert x['oam'][i*4:i*4+4]==y['oam'][i*4:i*4+4],('Active other actor',case,i)
            for scanline in range(32,240):
                sets=[]
                for z in [x,y]:
                    eligible=[i for i in range(64)if z['oam'][i*4]+1<=scanline<=z['oam'][i*4]+16]
                    sets.append([i for i in eligible[:8]if i not in z['indices']])
                assert sets[0]==sets[1],('Other actor8sprite admission changed',case,scanline,sets)
            diffs=[i for i in apps if x['ram'][i]!=y['ram'][i]]
            assert set(diffs)<=allowed,('Nonstack application RAM changed',case,[(hex(i),x['ram'][i],y['ram'][i])for i in diffs if i not in allowed])
            scratch.update(diffs)
            selected=y['pointer']!=rec['pointer'];wrap=y['physical_start']+len(rec['parts'])*4>256
            if selected:
                assert not wrap and profile[3]==0 and 32<=profile[0]<224 and 64<=profile[1]<176
                assert y['pointer']==address(bundles[1],'PnGuardAlt_'+rec['label'])
            elif wrap or profile[3] or not(32<=profile[0]<224 and 64<=profile[1]<176):assert x['oam']==y['oam'],('Original fallback must emit exact wholeOAM',case)
            path='sorted'if selected else'original-wrap'if wrap else'original-offset'if profile[3]else'original-clip'if not(32<=profile[0]<224 and 64<=profile[1]<176)else'original-unsupported'
            delta=y['cycles']-x['cycles'];rows.append(dict(case,path=path,physical_start=y['physical_start'],delta=delta,baseline_cycles=x['cycles'],candidate_cycles=y['cycles']))
    except Exception as ex:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,case=case,error=repr(ex),completed_cases=len(rows)),indent=2)+'\n');raise
    (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    paths={p:dict(cases=sum(r['path']==p for r in rows),min_delta=min(r['delta']for r in rows if r['path']==p),max_delta=max(r['delta']for r in rows if r['path']==p))for p in set(r['path']for r in rows)}
    q=dict(passed=True,native_run=False,component_only=True,quick=a.quick,body_records=len(records),complete_DrawAll_cases=len(rows),public_AXYP_SP_exact=True,banks_exact=True,active_other_OAM_exact=True,all_scanline_other8sprite_admission_exact=True,body_parts_multiset_exact=True,only_intended_pointer_and_named_scratch_RAM_differences=True,scratch_difference_addresses={hex(k):v for k,v in scratch.items()},scratch_liveness_still_requires_source_review=True,paths=paths,baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),limits='Synthetic complete CPU DrawAll controls with source-valid body/pool and0or1 explicitly staged native nonbody record; no native lifecycle/gameplay reachability claim. All scratch differences are named/disclosed, not a literal wholeRAM equality assertion. Row pixel/core dominance, interrupts, native cadence, IRQ/PPU visibility and flagoff builds remain separate requirements.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
