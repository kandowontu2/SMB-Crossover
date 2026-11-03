"""Complete actual legacy menu differentials and Mini P1/P2/confirm queue cases."""
import collections,itertools,json
from pathlib import Path
import measure_mini_mario_menu_1103_v14 as B
import prepare_prince_frontend_proposal_1102_v109 as P
N,F,V,R,O,address=B.N,B.F,B.V,B.R,B.O,B.address


def load():
    base,_,_=V.current();old=dict(base,raw=B.ROM.read_bytes());q=json.loads((O/'proposal.json').read_text())
    raw=bytearray(old['raw']);assert V.sha(raw)==q['current_input_SHA256']
    for row in q['patches']:
        at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
    assert V.sha(raw)==q['expected_memory_only_SHA256']
    return old,dict(old,raw=bytes(raw)),q


def key(m,value,p=0x30,pad=1):
    N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=value if pad==1 else 0,SavedJoypad2Bits=value if pad==2 else 0)
    return F.invoke(m,'CrossoverMenuInput',p=p)


def main():
    old,new,q=load();counts=collections.Counter();rows=[]
    fields=sorted(n for n,s in old['syms'].items()if'Variant'in n and'::'not in n and 0<=int(s['val'],0)<0x8000 and not n.startswith('.'))
    for slot in range(32):
        pair=[V.seed(b,slot)for b in[old,new]];seen=set()
        for cycle in range(32):
            a,b=pair;name,_=V.menu_name(a);mv=N.get(a,'MarioVariant')
            sig=(name,N.get(a,'SelectedCharacter'),a[0x5fe5],a[0x5fe8],a[0x5ffe],tuple(N.get(a,n)for n in fields))
            if sig in seen:break
            seen.add(sig);assert P.view(a)==P.view(b),(slot,cycle,name,'initial')
            assert F.invoke(a,'FmPending')==F.invoke(b,'FmPending')and P.view(a)==P.view(b)
            rows.append(dict(slot=slot,cycle=cycle,name=name,raw=N.get(a,'SelectedCharacter'),MarioVariant=mv));counts['legacy_states_exact']+=1
            for value in[16,128,48,160,176]:
                tests=[]
                for initial in pair:
                    m=N.fork(initial);z=key(m,value);tests.append((m,z))
                x,zx=tests[0];y,zy=tests[1]
                if slot==0 and mv==7 and value&32:
                    assert N.get(y,'SelectedCharacter')==41 and N.get(y,'MarioVariant')==8 and N.get(y,'CrossoverMenuState')==0 and V.menu_name(y)[0]=='MINI MARIO'
                    counts['Mini_simultaneous_Select_confirm']+=1
                else:assert zx==zy and P.view(x)==P.view(y),(slot,cycle,name,value,'foreignconfirm');counts['legacy_confirm_exact']+=1
            for m in pair:key(m,32)
            if slot==0 and N.get(pair[1],'MarioVariant')==8:
                assert N.get(pair[1],'SelectedCharacter')==41 and V.menu_name(pair[1])[0]=='MINI MARIO'
                key(pair[1],32) # New ninth profile wraps to genuine oldMario0.
                assert N.get(pair[1],'MarioVariant')==0 and N.get(pair[1],'SelectedCharacter')==0,('Miniwrap',N.get(pair[1],'MarioVariant'),N.get(pair[1],'SelectedCharacter'),V.menu_name(pair[1]))
        else:raise AssertionError(('finite familycycle',slot))
    assert len(rows)==94 and len({(r['slot'],r['name'])for r in rows})==93
    seeds=[N.fresh(b)for b in[old,new]]
    for slot,p,mask in itertools.product(range(32),[0x30,0x31,0x70,0xf1],[0,1,2,4,8,15]):
        results=[]
        for initial in seeds:
            m=N.fork(initial);N.put(m,CrossoverMenuIndex=slot,CrossoverMenuPressed=mask,VRAM_Buffer1_Offset=0)
            results.append((m,F.invoke(m,'NrMenuNavigate',p=p)))
        assert results[0][1]==results[1][1]and P.view(results[0][0])==P.view(results[1][0]);counts['legacy_navigation_AXYP_state_exact']+=1
    for slot,p,offset in itertools.product(range(32),[0x30,0x31,0x70,0xf1],[0,32,76]):
        results=[]
        for initial in seeds:
            m=N.fork(initial);N.put(m,CrossoverMenuIndex=slot,VRAM_Buffer1_Offset=offset)
            results.append((m,F.invoke(m,'QueueCursor',p=p)))
        assert results[0][1]==results[1][1]and P.view(results[0][0])==P.view(results[1][0]);counts['legacy_cursor_AXYP_state_exact']+=1
    own=[];vp=address(new,'VRAM_Buffer1');sp=address(new,'Sprite_Data')
    for p,offset,pad,groups in itertools.product([0x30,0x31,0x70,0xf1],[0,8,32],[1,2],[0,0x7f,0x80,255]):
        m=V.seed(new,0);N.put(m,MarioVariant=7);F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
        prefix=[0x20,0,1,36]*(offset//4);m[vp:vp+offset]=prefix
        N.put(m,FmGroups=groups,VRAM_Buffer1_Offset=offset,CrossoverMenuButtons=0,SavedJoypad1Bits=32 if pad==1 else 0,SavedJoypad2Bits=32 if pad==2 else 0)
        F.invoke(m,'CrossoverMenuInput',p=p)
        assert N.get(m,'SelectedCharacter')==41 and N.get(m,'MarioVariant')==8 and V.menu_name(m)[0]=='MINI MARIO'
        assert m[vp:vp+offset]==prefix and list(m[sp:sp+4])==[176,64,0,124]
        assert all(m[sp+i]==248 for i in[4,8,12,16,20])and N.get(m,'CurrentOAMOffset')==8
        end=N.get(m,'VRAM_Buffer1_Offset');assert m[vp+end-3:vp+end]==[39,22,24]and m[vp+end]==0
        assert sum(c['address']==0x2328 and c['length']==16 for c in F.commands(m))==1
        assert N.get(m,'ObjectMetasprite')==0 and m[address(new,'SmPosePtr')]+256*m[address(new,'SmPosePtr')+1]==address(new,'ObjectMetasprite')
        # Mapper argument0 is deliberately unallocated placeholder. Assert
        # the exact typed publisher contract, not authenticity of page0 art.
        assert N.get(m,'CurrentCHRBank',1)==0 and N.get(m,'X5ChrMode',1)==128 and N.get(m,'ReloadCHRBank')==1
        F.invoke(m,'MenuResolveCharacter',p=p);assert N.get(m,'SelectedCharacter')==41
        for value in[16,128]:
            t=N.fork(m);key(t,value,p);assert N.get(t,'CrossoverMenuState')==0 and N.get(t,'MarioVariant')==8 and N.get(t,'SelectedCharacter')==41
            counts['Mini_Start_A']+=1
        key(m,32,p);assert N.get(m,'MarioVariant')==0 and N.get(m,'SelectedCharacter')==0 and V.menu_name(m)[0]=='MARIO'
        counts['Mini_P1_P2_flags_queue_groups']+=1
    for slot in range(32):
        pair=[N.fork(m)for m in seeds]
        for m in pair:N.put(m,CrossoverMenuState=1,CrossoverMenuIndex=slot,Mirror_PPUMASK=0,DisableScreenFlag=1,VRAM_Buffer1_Offset=0)
        z=[F.invoke(m,'CrossoverMenuInput')for m in pair]
        assert z[0]==z[1]and P.view(pair[0])==P.view(pair[1])and pair[0].vram==pair[1].vram
        counts['legacy_32constructors_NT_exact']+=1
    out=dict(passed=True,CPU_only=True,ROM_written=False,native_qualified=False,art_allocation=False,current_input_SHA256=B.PIN,
        expected_memory_only_SHA256=q['expected_memory_only_SHA256'],checks=dict(counts),legacy_unique_profiles=93,legacy_machine_states=94,
        Mini_variant=8,Mini_raw=41,actual_legacy_rows=rows,source_pose='Natural originalsmallidle pair0; NES one8x16sprite/rightfacing; originalMario firstY176 retained, Xcenter124, fiveoldparts hidden.',
        ABI='All legacy whole public MenuInput/Navigation/Cursor AXYP/application/SMC/maps/PPUlog exact. Mini only owns newSelect from7 and queue after raw41. TemporaryMarioVariant0/Selected0 prevents old8entry indexing. Carry from successfulCMP7 survivesINC/LDA/STA and supplies consumedSEC result.',
        pending=['Bind a formally allocated original-art physical page instead of placeholder0.','Final currentbackend/scene/Fresh/body lifecycle integration and actual native Mini UI/launch/traversal remain root-owned.','Exact compiled source-reader/IRQ closure for newly reclaimed menu spans remains before any native admission.'],
        bindings={p.relative_to(R).as_posix():B.sha(p)for p in[Path(__file__),Path(B.__file__),O/'proposal.json',O/'menu.s',O/'menu.bin',O/'code.bin',O/'data.bin',O/'nav.s',O/'nav.bin']})
    (O/'menu-CPU-v15.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in['bindings','actual_legacy_rows']}))


if __name__=='__main__':
    try:main()
    except Exception as e:
        (O/'menu-CPU-v15-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
