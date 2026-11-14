"""Legal current769 platform-query lifecycle; source/controller proof only."""
from collections import Counter
from hashlib import sha256
import json
import re

import replay_dkjr_final_handoff_1114 as F

G,T=F.Gate,F.T
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def closure(raw):
    source,*_=H.T.old_source();labels=P.frozen_labels();body=T.P.T.payload(raw)
    # ca65's retained public map omits some unexported original labels.
    # Recover them by assembling the complete retained source in memory,
    # anchoring every published label and reverse-resolving public aliases.
    aliases=re.findall(r'^(\w+)\s*=\s*(\w+)\s*$',source,re.M)
    known=dict(labels)
    for name in set(re.findall(r'\bDData_c[0-9a-f]{3}\b',source)):
        known[name]=labels['DkjrSourceData']+int(name[6:],16)-0xc2cd
    for _ in range(len(aliases)):
        for alias,target in aliases:
            if alias in known and target not in known:known[target]=known[alias]
    pre=''.join(f'{n}=${v:x}\n'for n,v in known.items())
    complete=H.T.assemble(pre+P.expand_branches(source),dict(DKJR=(0xa000,8160),
        DK_MAIN=(0xd65e,73),DK_PAUSE=(0xd540,286),DK_PORTS=(0xd6a7,345)))
    assert all(complete['symbols'][n]==v for n,v in labels.items())
    labels=complete['symbols']
    constants=''.join(f'{n}={v}\n'for n,v in re.findall(r'^(\w+)\s*=\s*(\$[0-9a-fA-F]+|[0-9]+)\s*$',source,re.M))
    # Current signed-terrain repack predates769. Rebuild its small retained
    # reference in memory; do not mistake the older frozen World text for it.
    ref_path=P.B.R/'tools/reference/dkjr_scroll_publish_1110_v1.s'
    ref=ref_path.read_text();active=True;current=[];conditions=0
    for line in ref.splitlines():
        if line.strip()=='.ifdef ORIGINAL':active=False;conditions+=1
        elif line.strip()=='.else':active=True
        elif line.strip()=='.endif':active=True
        elif active and not line.strip().startswith('.assert '):current.append(line)
    assert conditions==3
    repack=H.T.assemble('\n'.join(current),dict(CAMERA=(0xd240,30),WORLD=(0xb345,0x72)))
    assert repack['symbols']['DkWorldRow']==0xb39d and repack['used']['WORLD']==0x72
    checks=[]
    for begin,end in(('D_ce6c','D_cea2'),('D_cf37','D_d1ae'),('D_d251','D_d2bd'),('D_d412','D_d56e'),
                      ('D_d56e','D_d5d7'),('D_d5d7','D_d600'),('D_d631','D_d650'),
                      ('D_d913','D_d955'),('D_e9ae','D_e9ee'),
                      ('D_e893','D_e8a7'),('DkjrNativeTerrainHook','DkjrNativeWorldBuild'),
                      ('DkjrNativeWorldBuild','NativeObjects'),('NativeObjects','Platforms'),
                      ('DkjrNativePhase','DkjrNativeSourcePhase'),('DkjrNativeSourcePhase','DkjrNativePhaseEnd'),
                      ('DkNativeBounce','DkBounceNo'),('DkNativeDeathStart','DkNativeReset')):
        fragment=source[source.index(begin+':'):source.index(end+':')]
        defined=set(re.findall(r'^(\w+):',fragment,re.M))
        defs=constants+''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
        lo,hi=labels[begin],labels[end]
        code=H.T.assemble(defs+'.segment "CHECK"\n'+P.expand_branches(fragment),dict(CHECK=(lo,hi-lo)))
        image=code['images']['CHECK'];at=H.T.offset(lo)
        if begin=='DkjrNativeWorldBuild':
            image=bytearray(image)
            image[0xb345-lo:0xb3b7-lo]=repack['images']['WORLD']
            assert image[0xb49a-lo:0xb49c-lo]==bytes.fromhex('a3b3')
            image[0xb49a-lo:0xb49c-lo]=bytes.fromhex('9db3')
            image=bytes(image)
        assert code['used']['CHECK']==hi-lo and body[at:at+len(image)]==image,(begin,end,hex(lo),len(image),[(hex(lo+i),image[i],body[at+i])for i in range(len(image))if image[i]!=body[at+i]][:32])
        checks.append(dict(first=begin,end_exclusive=end,PC=lo,bytes=len(image),SHA256=sha256(image).hexdigest()))
    query=source[source.index('D_e893:'):source.index('D_e8a7:')]
    for name,kind in(('D_e893',0),('D_e897',1),('D_e89b',2),('D_e89f',3),('D_e8a3',4)):
        assert re.search(r'^'+name+r':[^\n]*\n lda #\$0'+str(kind)+r'\b',query,re.M)
    jump=source[source.index('D_d5d7:'):source.index('D_d600:')]
    assert jump.index('jsr D_e893')<jump.index('lda $c07e')<jump.index('cmp #$03')<jump.index('bcc D_d5ee')<jump.index('jsr D_e89f')
    assert jump.index('jsr D_e89f')<jump.index('D_d5ee:')<jump.index('jsr D_e89b')<jump.index('jsr D_d913')
    objects=source[source.index('NativeObjects:'):source.index('GrowingVine:')]
    assert 'cmp #3' in objects and re.search(r'jcs Platforms\n rts',objects)
    motion=source[source.index('D_d913:'):source.index('D_d955:')]
    assert motion.index('jsr D_e9ae')<motion.index('lda $c054')<motion.index('cmp #$03')
    gravity=source[source.index('D_e9ae:'):source.index('D_e9ee:')]
    assert gravity.index('lda $c07e,x')<gravity.index('bne D_e9c3')<gravity.index('sta $c083,x')<gravity.index('lda #$08')<gravity.index('sta $c082,x')<gravity.index('inc $c07e,x')
    transition=source[source.index('D_d291:'):source.index('D_d2a4:')]
    assert 'lda #$00' in transition and 'sta $c07e' in transition
    assert not re.search(r'\$c08[2367]',transition)
    phase=source[source.index('DkjrNativeSourcePhase:'):source.index('DkjrNativePhaseEnd:')]
    assert phase.index('cmp #3')<phase.index('beq SourcePhaseMove',phase.index('cmp #3'))<phase.index('jsr DkjrInput')<phase.index('jsr DkjrTransition')<phase.index('jsr DkjrMove')
    bounce=source[source.index('DkNativeBounce:'):source.index('DkBounceNo:')]
    assert bounce.index('lda #3')<bounce.index('sta $c06b')<bounce.index('jsr DkjrJumpRestart')
    # Complete local literal ingress census across both actual code carriers.
    # A conservative byte census includes data; it must equal known callers.
    def callers(target):
        out=[]
        for lo,data in((0xa000,body[:0x1fe0]),(0xd000,body[9*1024:])):
            for i in range(len(data)-2):
                if data[i]in(0x20,0x4c)and int.from_bytes(data[i+1:i+3],'little')==target:
                    out.append((lo+i,data[i]))
        return out
    support=callers(labels['D_e89f'])
    expected=[(labels[n],0x20)for n in('D_cf49','D_d575','D_d593','D_d5e7','D_d631')]
    assert sorted(support)==sorted(expected),(support,expected)
    assert callers(labels['D_e8a3'])==[]
    assert callers(labels['DkjrNativeWorldBuild'])==[(labels['DkjrNativeTerrainHook']+18,0x20)]
    assert callers(labels['Platforms'])==[(labels['NativeObjects']+11,0x4c)]
    services=source[source.index('DkServices:'):source.index('D_ca82:')]
    assert not re.search(r'\b(?:D_e8a3|D_e89f|DkjrSupportProbe|DkjrPlatformProbe|DkjrNativeWorldBuild)\b',
        '\n'.join(line.split(';')[0]for line in services.splitlines()if line.strip().startswith('jmp ')))
    outside=[]
    for path in sorted((P.B.R/'src').glob('*.s')):
        for number,line in enumerate(path.read_text().splitlines(),1):
            code=line.split(';',1)[0]
            if re.search(r'\b(?:D_e8a3|D_e89f|DkjrSupportProbe|DkjrPlatformProbe|DkjrNativeWorldBuild)\b',code):
                outside.append((str(path.relative_to(P.B.R)),number,code.strip()))
    assert not outside,outside
    return dict(passed=True,frozen_source_SHA256=H.T.FROZEN_SHA,assembled_exact_current_fragments=checks,
        signed_terrain_repack_source_SHA256=sha256(ref_path.read_bytes()).hexdigest(),
        query_kinds=dict(vine=0,hand=1,wall=2,support=3,platform=4),
        current_support_JSR_sites=support,current_standalone_kind4_callers=[],
        current_native_named_probe_consumers=outside,
        source3_support_dominated_by_age_ge3=True,
        all_original_directions_share_gravity_before_horizontal_direction_branch=True,
        constructor_native_bounce_and_age_wrap_do_not_bypass_query_gate=True),labels


def view(m):
    r=m.ram[2];acc=r[0x82]+256*r[0x83];imp=r[0x86]+256*r[0x87]
    delta=(acc-imp)&65535
    return dict(source=r[0x6b],prior=r[0x6c],age=r[0x7e],acceleration=acc,impulse=imp,
        signed_velocity=delta-65536 if delta&32768 else delta,kind=r[0x8db],
        direction=r[0x54],facing=r[0x6d],fraction=r[0x7f],source_y=r[0x210],
        x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'))


def run():
    parent,raw=F.load_inputs();proof,labels=closure(raw)
    e73=T.Old.reverse(parent);_,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    rows=[];counts=Counter();stale=[]
    for facing,pad_prepare in((0,2),(1,1)):
        for name,direction in(('neutral',0),('up',8),('down',4),('left',2),('right',1)):
            m=Q.mounted(seed,raw)
            # The retained cold constructor deliberately stops during the
            # original entrance hop. Finish it through ordinary Main frames.
            for _ in range(120):
                Q.frame(m,0)
                if m.ram[2][0x6b]==m.ram[2][0x6c]==1:break
            else:raise AssertionError(('Opening hop did not settle',view(m)))
            for _ in range(16):
                Q.frame(m,pad_prepare)
                if m.ram[2][0x6d]==facing and m.ram[2][0x6b]==m.ram[2][0x6c]==1:break
            for _ in range(2):Q.frame(m,0)
            assert m.ram[2][0x6b]==m.ram[2][0x6c]==1 and m.ram[2][0x6d]==facing,('Legal facing preparation',facing,name,view(m),P.B.state(m))
            # The real manager must have installed the current typed payload,
            # rather than leaving the cold precursor mounted after rebinding.
            cookie=raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16]
            assert all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3))
            events=[];platforms=[];first=None;round_index=0;step=0
            def observe(memory,c):
                nonlocal first
                if c.pc<0x8000 or memory.rawtags[(c.pc-0x8000)//8192]!=3:return
                if c.pc==labels['DkjrNativeWorldBuild']:
                    s=view(memory);counts['world_queries']+=1
                    if s['source']==3 and s['age']==0:
                        assert s['kind']in(0,1,2),'Age0 source3 unexpectedly asks platform kind'
                        counts['legal_age0_nonplatform_queries']+=1
                        if len(events)<8:events.append(dict(round=round_index,step=step,query=s))
                        if s['signed_velocity']>=0 and len(stale)<8:stale.append(dict(facing=facing,direction=name,round=round_index,state=s))
                if c.pc==labels['Platforms']:
                    s=view(memory);counts['platform_queries']+=1
                    assert s['kind']in(3,4)
                    if s['source']==3:
                        assert s['age']>=3,('Legal source3 Platform age0/1/2',s)
                        counts['source3_platform_queries']+=1
                        if first is None:first=dict(round=round_index,step=step,state=s)
                        if len(platforms)<6:platforms.append(dict(round=round_index,step=step,state=s))
            rounds=[]
            for round_index in(1,2):
                launched=False;landed=False;before=view(m)
                for step in range(1,100):
                    Q.frame(m,(128|direction)if step<=8 else 0,observe)
                    s=view(m)
                    launched|=s['source']==3
                    assert N.get(m,'NumberofLives')==2 and s['source']!=5,('Legal opening jump unexpectedly died',name,facing,step,s)
                    if launched and s['source']==s['prior']==1 and step>4:
                        landed=True;rounds.append(dict(round=round_index,steps=step,before=before,after=s));break
                assert launched and landed,('Ordinary static-floor jump bound',name,facing,view(m))
                for _ in range(2):Q.frame(m,0,observe)
            assert first and events
            expected_direction=dict(neutral=0,up=1,down=2,left=3,right=4)[name]
            assert {e['round']for e in events}=={1,2}
            assert all(e['query']['direction']==expected_direction for e in events)
            rows.append(dict(facing=facing,requested_direction=name,rounds=rounds,
                age0_queries=events,first_source3_platform_query=first,platform_query_examples=platforms))
            print(json.dumps(dict(progress_direction=name,facing=facing,counts=dict(counts))),flush=True)
    assert counts['source3_platform_queries']and counts['legal_age0_nonplatform_queries']and stale
    return dict(passed=True,ROM_SHA256=T.PIN,source_closure=proof,counts=dict(counts),
        two_legal_static_floor_jumps_each_direction_and_facing=rows,
        real_age0_stale_velocity_examples_outside_platforms=stale,
        conclusion='Age0 term is redundant at every legal current Platforms query. Source3 reaches kind3 only at age>=3; age0 stale velocity exists at kind0/2, which cannot enter Platforms.',
        synthetic_or_poisoned_state_seeds=0,source_controller_model_only=True,
        manually_invoked_exported_query_ABI_not_covered_by_legal_caller_invariant=True,
        ROM_composed=False,allocations_changed=False,Mesen_run=False,outputs=0)


if __name__=='__main__':
    result=run()
    # Keep the receipt aggregate. All full in-memory rows participate in this
    # digest; stdout needs only the caller proof and one witness per route.
    digest=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result['full_in_memory_receipt_SHA256']=digest
    for row in result['two_legal_static_floor_jumps_each_direction_and_facing']:
        row['age0_queries']=row['age0_queries'][:1]
        del row['platform_query_examples']
    result['real_age0_stale_velocity_examples_outside_platforms']=result['real_age0_stale_velocity_examples_outside_platforms'][:2]
    print(json.dumps(result,separators=(',',':')),flush=True)
