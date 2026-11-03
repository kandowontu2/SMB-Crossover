"""Actual current32slot menu CPU differentials for the source-only Jr plan."""
from pathlib import Path
import collections,itertools,json,sys
import measure_dkjr_current_menu_1103_v2 as B
import prepare_prince_frontend_proposal_1102_v109 as P
V,N,F,O,R=B.V,B.N,B.F,B.O,B.R
address,location,off,sha=B.address,B.location,B.off,B.sha


def load():
    old,_,_=V.current();q=json.loads((O/'current-menu-v2.json').read_text());assert sha(old['raw'])==q['current_input_SHA256'];post=bytearray(old['raw'])
    for row in q['patches']:
        at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert post[at:at+len(before)]==before;post[at:at+len(after)]=after
    assert sha(post)==q['expected_memory_only_SHA256'];return old,dict(old,raw=bytes(post)),q


def main():
    negative=O/'current-menu-v3-negative.json';keep=O/'current-menu-v2-unmerged-queue-negative.json'
    if negative.exists() and not keep.exists():keep.write_bytes(negative.read_bytes())
    old,new,proposal=load();counts=collections.Counter();rows=[];points=collections.Counter();fields=sorted(n for n,s in old['syms'].items()if 'Variant'in n and '::'not in n and 0<=int(s['val'],0)<0x8000 and not n.startswith('.'))
    def watch(c):
        if c.pc>=0x8000:
            tag=c.memory.rawtags[(c.pc-0x8000)//8192]
            for name in ['FmDrawPreviewSelected','DkPortrait','DkSetPose','MenuPreviewBudget','NrMenuCharacter','FmStartRetireFlags']:
                if name in old['syms'] and c.pc==address(old,name)and tag==((location(old,name)-16)//8192)|128:points[name]+=1
    for slot in range(32):
        pair=[V.seed(b,slot)for b in [old,new]];seen=set()
        for cycle in range(32):
            a,b=pair;name,cells=V.menu_name(a);sig=(name,N.get(a,'SelectedCharacter'),a[0x5fe5],a[0x5fe8],a[0x5ffe],tuple(N.get(a,n)for n in fields))
            if sig in seen:break
            seen.add(sig);assert P.view(a)==P.view(b),(slot,cycle,name,'initial')
            ra=F.invoke(a,'FmPending');rb=F.invoke(b,'FmPending');assert ra==rb and P.view(a)==P.view(b)
            rows.append(dict(slot=slot,cycle=cycle,name=name,raw=N.get(a,'SelectedCharacter'),pending_index=ra['A'],pending_C=bool(ra['P']&1)))
            counts['current_machine_states']+=1
            for key in [16,128,48,160,176]:
                tries=[]
                for initial in pair:
                    m=N.fork(initial);N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0);z=F.invoke(m,'CrossoverMenuInput',watch=watch);tries.append((m,z))
                x,zx=tries[0];y,zy=tries[1]
                if slot==27 and key&32:
                    assert N.get(y,'SelectedCharacter')==40 and N.get(y,'CrossoverMenuState')==0 and V.menu_name(y)[0]=='DONKEY KONG JR';counts['DK_Select_confirm']+=1
                else:
                    assert zx==zy and P.view(x)==P.view(y),(slot,cycle,name,key,'foreign confirm')
                    counts['foreign_confirm_exact']+=1
            # The old single DK profile does not cycle; its proposed second
            # profile is verified separately through actual public inputs.
            if slot==27:break
            for m in pair:
                N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput',watch=watch)
        else:raise AssertionError(('finite family cycle',slot))
    assert len(rows)==94 and len({(r['slot'],r['name'])for r in rows})==93,(len(rows),rows)
    # All native navigation/cursor paths are exercised, including flag and
    # nonzero command-buffer positions; no table arithmetic Python substitute.
    seeds=[N.fresh(b)for b in [old,new]]
    for slot,p,mask in itertools.product(range(32),[0x30,0x31,0x70,0xf1],[0,1,2,4,8,15]):
        out=[]
        for initial in seeds:
            m=N.fork(initial);N.put(m,CrossoverMenuIndex=slot,CrossoverMenuPressed=mask,VRAM_Buffer1_Offset=0);z=F.invoke(m,'NrMenuNavigate',p=p);out.append((m,z))
        assert out[0][1]==out[1][1]and P.view(out[0][0])==P.view(out[1][0]);counts['navigation_AXYP_state_exact']+=1
    for slot,p,offset in itertools.product(range(32),[0x30,0x31,0x70,0xf1],[0,32,76]):
        out=[]
        for initial in seeds:
            m=N.fork(initial);N.put(m,CrossoverMenuIndex=slot,VRAM_Buffer1_Offset=offset);z=F.invoke(m,'QueueCursor',p=p);out.append((m,z))
        assert out[0][1]==out[1][1]and P.view(out[0][0])==P.view(out[1][0]);counts['cursor_AXYP_state_exact']+=1
    own=[];pose=proposal['source_portrait']['native_8x16_OAM'];sp=address(new,'Sprite_Data');vp=address(new,'VRAM_Buffer1')
    for p,offset,pad,groups in itertools.product([0x30,0x31,0x70,0xf1],[0,8,32],[1,2],[0,0x7f,0x80,255]):
        m=V.seed(new,27);N.put(m,FmGroups=groups,VRAM_Buffer1_Offset=offset,CrossoverMenuButtons=0,SavedJoypad1Bits=32 if pad==1 else 0,SavedJoypad2Bits=32 if pad==2 else 0)
        # A legal prefix of complete single-byte commands fills the selected
        # nonzero offset; arbitrary bytes would invalidate the parser fixture.
        prefix=[]
        while len(prefix)<offset:prefix += [0x20,0x00,1,0x24]
        assert len(prefix)==offset
        m[vp:vp+offset]=prefix;F.invoke(m,'CrossoverMenuInput',p=p,watch=watch)
        assert N.get(m,'SelectedCharacter')==40 and V.menu_name(m)[0]=='DONKEY KONG JR',(p,offset,pad,groups,N.get(m,'SelectedCharacter'),V.menu_name(m))
        assert list(m[sp:sp+16])==pose and m[sp+16]==m[sp+20]==248 and N.get(m,'CurrentOAMOffset')==16
        assert N.get(m,'CurrentCHRBank',1)==192 and N.get(m,'X5ChrMode',1)==131 and N.get(m,'ReloadCHRBank')==1
        end=N.get(m,'VRAM_Buffer1_Offset')
        assert m[vp:vp+offset]==prefix
        commands=F.commands(m);assert sum(c['address']==0x2328 and c['length']==16 for c in commands)==1
        assert m[vp+end-3:vp+end]==[48,6,54] and m[vp+end]==0
        assert N.get(m,'ObjectMetasprite')==0 and m[address(new,'SmPosePtr')]+256*m[address(new,'SmPosePtr')+1]==address(new,'ObjectMetasprite')
        F.invoke(m,'MenuResolveCharacter',p=p);assert N.get(m,'SelectedCharacter')==40
        held=N.fork(m);N.put(held,VRAM_Buffer1_Offset=0);F.invoke(held,'CrossoverMenuInput',p=p);assert N.get(held,'SelectedCharacter')==40
        for key in [16,128]:
            t=N.fork(m);N.put(t,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0);F.invoke(t,'CrossoverMenuInput',p=p)
            assert N.get(t,'CrossoverMenuState')==0 and N.get(t,'SelectedCharacter')==40;counts['Jr_Start_A']+=1
        N.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);F.invoke(m,'CrossoverMenuInput',p=p)
        assert N.get(m,'SelectedCharacter')==28 and V.menu_name(m)[0]=='DONKEY KONG'
        N.put(m,CrossoverMenuIndex=27,SelectedCharacter=40);F.invoke(m,'MenuResolveCharacter');assert N.get(m,'SelectedCharacter')==40
        N.put(m,CrossoverMenuIndex=26);F.invoke(m,'MenuResolveCharacter');assert N.get(m,'SelectedCharacter')!=40
        N.put(m,CrossoverMenuIndex=27);F.invoke(m,'MenuResolveCharacter');assert N.get(m,'SelectedCharacter')==28
        counts['Jr_focus_both_Select_P1_P2_buffer_palette_cases']+=1
    for slot in range(32):
        pair=[N.fork(m)for m in seeds]
        for m in pair:N.put(m,CrossoverMenuState=1,CrossoverMenuIndex=slot,Mirror_PPUMASK=0,DisableScreenFlag=1,VRAM_Buffer1_Offset=0)
        z=[F.invoke(m,'CrossoverMenuInput',watch=watch)for m in pair]
        assert z[0]==z[1]and P.view(pair[0])==P.view(pair[1])and pair[0].vram==pair[1].vram
        counts['actual_32slot_constructor_NT_and_state_exact']+=1
    out=dict(passed=True,CPU_only=True,ROM_written=False,shared_approval=False,native_qualified=False,current_input_SHA256=sha(old['raw']),expected_memory_only_SHA256=sha(new['raw']),checks=dict(counts),current_unique_profiles=93,current_machine_states=94,proposed_unique_profiles=94,proposed_machine_states=95,selectable_count_status='Future94 is a source/CPU proposal, not native admission or delivered playable count.',actual_native_calls=dict(points),rows=rows,focused_policy='Select28<->40 at originalDK slot27; repeated resolve/heldSelect retains highlighted identity; leaving focus may resetDK. Start/A launches40. No new selector RAM. Life/respawn/stage/game-select need separate actual owner/public ingress qualification.',remaining=['Full source/compiled direct/indexed/indirect entry and read closure for reused padding and public3B QueueSelection hook.','Actual NMI/IRQ/cold clear/current scene/Main/Fresh/retire classifiers, including B013 CMP3 currently rejecting40, require exact source-bound successor and root grants.','No menu/native/ROM/nightly permission implied. No helpers placed; traversal remains untested.'],bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(B.__file__),O/'current-menu-v2.json',O/'current-menu-v2.s',O/'current-menu-v2.bin',O/'current-menu-code-v2.bin',O/'current-menu-data-v2.bin']})
    (O/'current-menu-v3-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['bindings','rows']}))


if __name__=='__main__':
    try:main()
    except Exception as e:
        (O/'current-menu-v3-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
