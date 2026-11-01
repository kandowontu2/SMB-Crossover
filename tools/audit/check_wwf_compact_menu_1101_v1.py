"""All90 current menu identities; only six WWF drawing outputs may differ."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
O=R/'build/menu-wwf-compact-1101-v1';J=R/'build/doki-current-component-1101-v1'
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def queue(m):
    p=address(m.bundle,'VRAM_Buffer1');n=C.get(m,'VRAM_Buffer1_Offset');return bytes(m[p:p+n+1])

def draw(m):
    p=address(m.bundle,'CurrentCHRBank');mode=address(m.bundle,'X5ChrMode')
    n=C.get(m,'CurrentOAMOffset')
    return bytes(m[0x200:0x200+n]),bytes(m[i]for i in range(0x200+n,0x300,4)),n,bytes(m[p:p+12]),bytes(m[mode:mode+12]),queue(m)

def application(m):return bytes(m[:0x100])+bytes(m[0x200:0x8000])

def persistent(m):
    names=['SelectedCharacter','CrossoverMenuIndex','CrossoverMenuState','MarioVariant','FmAlts','FmGroups','PlayerStatus','PlayerSize','CurrentPlayer','NumberofLives','NumberOfPlayers','WorldNumber','LevelNumber','AreaAddrsLOffset','PlayerOutlinesOff','CrossoverBehaviorVersion']
    names+=[n for n in m.bundle['syms']if(n.startswith('Cheat')or n.startswith('Cheats'))and int(m.bundle['syms'][n]['val'],0)<0x8000 and '::'not in n]
    names+=[n for n in ['S2Variant','Cv3Variant','TnVariant','BillVariant','WfCharacter','WfPower','WfHealth']if n in m.bundle['syms']]
    return {n:C.get(m,n)for n in set(names)if n in m.bundle['syms']}

def main():
    report=dict(passed=False,source_CPU=True,native=False,installed=False)
    try:
        stage=json.loads((O/'assembly-stage.json').read_text());assert stage['passed']
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        old,new=[C.scoped_load(p/'candidate.nes')for p in [J,O]]
        # Pure actual machine-code funding proof: every legal index and all256P.
        memories=[];pcs=[];ends=[]
        at=location(old,'DrawSelectionPreview');hi=location(old,'QueueVariantHint');table=address(old,'DrawSelectionPreview::PreviewX')
        pattern=bytes([0xbd,table&255,table>>8]);offset=old['raw'].index(pattern,at,hi)
        for b,pc,end in [(old,address(old,'DrawSelectionPreview')+offset-at,address(old,'DrawSelectionPreview')+offset-at+3),(new,address(new,'DrawSelectionPreview::WfCompactX'),address(new,'DrawSelectionPreview::WfCompactHaveX'))]:
            m=bytearray(65536);bank=(location(b,'DrawSelectionPreview')-16)//8192;m[0xa000:0xc000]=b['raw'][16+bank*8192:16+(bank+1)*8192];memories.append(m);pcs.append(pc);ends.append(end)
        cpus=[NesMPU(memory=m)for m in memories];funding=0
        for index,flags in itertools.product(range(32),range(256)):
            out=[]
            for c,pc,end in zip(cpus,pcs,ends):
                c.a,c.x,c.y,c.p,c.sp,c.pc=85,index,91,flags,224,pc
                for _ in range(10):
                    if c.pc==end:break
                    c.step()
                else:raise AssertionError(('X funding loop',index,flags,hex(c.pc)))
                out.append((c.a,c.x,c.y,c.p,c.sp))
            assert out[0]==out[1],('Exact X funding ABI',index,flags,out);funding+=1
        identities=ready=starts=unchanged=0;variants=[];draw_delta_addresses=set();wwf=[];world_windows=0
        for slot,total in enumerate(COUNTS):
            pair=[C.fresh(b)for b in [old,new]]
            for m in pair:C.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
            for variant in range(total):
                if variant:
                    for m in pair:
                        C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);C.invoke(m,'CrossoverMenuInput')
                pending=[bool(C.invoke(m,'FmPending')['P']&1)for m in pair]
                actual=[C.get(m,'MarioVariant')if slot==0 else variant for m in pair]
                assert pending[0]==pending[1]and actual[0]==actual[1]and persistent(pair[0])==persistent(pair[1]),('Identity/persistent data',slot,variant,pending,actual)
                assert C.get(pair[0],'SelectedCharacter')==C.get(pair[1],'SelectedCharacter')
                if slot!=28:
                    aa,bb=map(application,pair)
                    assert aa==bb,('Non-WWF whole application changed',slot,variant,[(hex(i if i<256 else i+256),a,b)for i,(a,b)in enumerate(zip(aa,bb))if a!=b][:16])
                    assert draw(pair[0])==draw(pair[1]),('Non-WWF drawing',slot,variant)
                    assert [bytes(z)for z in pair[0].ram]==[bytes(z)for z in pair[1].ram],('Non-WWF conditional caches',slot,variant)
                    unchanged+=1
                else:
                    aa,bb=map(application,pair)
                    draw_delta_addresses|={i if i<256 else i+256 for i,(a,b)in enumerate(zip(aa,bb))if a!=b}
                    expected=C.fork(pair[0]);candidate=C.fork(pair[1])
                    for m in [expected,candidate]:C.put(m,VRAM_Buffer1_Offset=0)
                    C.invoke(expected,'FmDrawPreview');result=C.invoke(candidate,'DrawSelectionPreview')
                    assert draw(expected)==draw(candidate),('Existing compact pipeline',variant,[(i,a,b)for i,(a,b)in enumerate(zip(draw(expected),draw(candidate)))if a!=b])
                    assert persistent(expected)==persistent(candidate),('Compact draw modified persistent data',variant)
                    assert C.get(candidate,'CurrentOAMOffset')==16
                    preview=18+variant;p=location(old,'FmPreviewTiles')+4*preview;tiles=old['raw'][p:p+4]
                    wanted=bytes(sum(([159+(i//2)*16,t,0,120+(i%2)*8]for i,t in enumerate(tiles)),[]))
                    assert bytes(candidate[0x200:0x210])==wanted,('Exact packed WWF OAM',variant)
                    colors=old['raw'][location(old,'FmPreviewColors')+3*preview:location(old,'FmPreviewColors')+3*preview+3]
                    assert queue(candidate)==bytes([63,17,3,*colors,0])
                    ch=address(old,'CurrentCHRBank');mode=address(old,'X5ChrMode')
                    assert bytes(candidate[ch+4:ch+12])==bytes(expected[ch+4:ch+12])and bytes(candidate[mode+4:mode+12])==bytes(expected[mode+4:mode+12]);world_windows+=1
                    wwf.append(dict(variant=variant,preview_index=preview,tiles=list(tiles),palette=list(colors),OAM=list(wanted),minimum_SP=result['minimum_SP']))
                for key,flags in itertools.product([16,128],[0x30,0x31,0x71,0xf1]):
                    outcomes=[]
                    for m in pair:
                        z=C.fork(m);C.put(z,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
                        result=C.invoke(z,'CrossoverMenuInput',p=flags);outcomes.append((persistent(z),tuple(result[k]for k in ['A','X','Y','P'])))
                        assert(C.get(z,'CrossoverMenuState')==0)!=pending[0],('Start admission',slot,variant,key,flags)
                    assert outcomes[0]==outcomes[1],('Start/scene identity changed',slot,variant,key,flags)
                    starts+=1
                variants.append(dict(slot=slot,variant=actual[0],raw=C.get(pair[1],'SelectedCharacter'),pending=pending[1]));identities+=1;ready+=not pending[1]
        assert(identities,ready,unchanged,starts)==(90,85,84,720)
        # Name each changed WWF byte/array; persistent data was separately exact.
        named=[]
        for a in sorted(draw_delta_addresses):
            names=[n for n,s in old['syms'].items()if '::'not in n and int(s['val'],0)==a]
            named.append(dict(address=hex(a),symbols=names[:12]))
        report.update(passed=True,ROM_sha256=stage['ROM_sha256'],parent_ROM=stage['parent_ROM'],menu_identities=identities,playable=ready,non_WWF_whole_application_contexts_exact=unchanged,Start_A_cases=starts,X_funding_all_indices_all_status_flags=funding,original_compact_WWF_profiles=wwf,world_window_cases=world_windows,WWF_draw_local_difference_addresses=named,rows=variants,scope='Actual assembled90-identity resolution/Select/queue/preview and720 Start/A comparisons. All84 non-WWF application/caches/drawing outputs exact. Six WWF previews match the unchanged original packed16x32 pipeline/OAM/palette and retain persistent/identity/Start state.8192 actual instruction fallback ABI comparisons. No emulator/raster/lives/gameplay or nightly qualification.')
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
    report['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(C.__file__),O/'assembly-stage.json',O/'candidate.nes',O/'candidate.dbg',J/'candidate.nes',J/'candidate.dbg']}
    (O/'menu-CPU-controls.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report.get(k)for k in ['passed','ROM_sha256','menu_identities','playable','non_WWF_whole_application_contexts_exact','Start_A_cases','X_funding_all_indices_all_status_flags','error']}));assert report['passed'],report.get('traceback')

if __name__=='__main__':main()
