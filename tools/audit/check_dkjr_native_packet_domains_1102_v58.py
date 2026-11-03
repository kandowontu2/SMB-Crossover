"""Compiled source point multiplicity and private packet address domains.

Follows the declared38 native entries plus typed world-fruit APIs. Internal
exported donor labels are not arbitrary-call native APIs.
"""
import collections, functools, json, re, sys
from pathlib import Path
import check_dkjr_native_score_tail_1102_v55 as S
A,R,O,W,N=S.A,S.R,S.O,S.W,S.N
sys.setrecursionlimit(30000)


def main():
    q=json.loads((O/'native-scoretail-v54-layout.json').read_text());L=q['labels']
    source=(O/'native-scoretail-v54.s').read_text();mem={}
    hidden=sorted(set(re.findall(r'^(DIndirect_[0-9a-f]{4}):',source,re.M)))
    assert hidden
    cfg=(O/'native-scoretail-v54.cfg').read_text().replace('native-scoretail-','native-domains-').replace('-v54.bin','-v58.bin')
    linked,extra=A.assemble('native-domains-v58',source+'\n.export '+','.join(hidden)+'\n',cfg)
    assert linked==(O/'native-scoretail-v54.bin').read_bytes()
    L=dict(L);L.update(extra)
    for name,start in [('native-scoretail-v54.bin',0xa000),('native-scoretail-pause-v54.bin',0xd540),('native-scoretail-main-v54.bin',0xd65e),('native-scoretail-ports-v54.bin',0xd6a7)]:
        mem.update({start+i:v for i,v in enumerate((O/name).read_bytes())})
    modes={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3}
    reached=set();calls=collections.Counter();opaque=set();memo={};active=[]
    def instruction(pc):
        op=mem[pc];name,mode=N.NesMPU.disassemble[op];assert name!='???',(hex(pc),hex(op))
        size=modes[mode];operand=mem.get(pc+1,0)+(256*mem.get(pc+2,0)if size==3 else 0)
        return name,mode,size,operand
    def summary(entry):
        if entry==L['DkjrNativeAwardSourcePoints']:return 1
        if entry not in mem:opaque.add(entry);return 0
        if entry in memo:return memo[entry]
        assert entry not in active,('recursive private service',list(map(hex,active)),hex(entry))
        active.append(entry);graph={};weight={};todo=[entry]
        while todo:
            pc=todo.pop()
            if pc in graph:continue
            if pc not in mem:opaque.add(pc);continue
            reached.add(pc);name,mode,size,operand=instruction(pc);nxt=pc+size;edges=[];cost=0
            if name=='JSR':
                calls[pc,operand]+=1;cost=summary(operand);edges=[nxt]
            elif name=='JMP':
                assert mode=='abs',('unbounded native indirect jump',hex(pc))
                if operand in mem:edges=[operand]
                else:opaque.add(operand)
            elif mode=='rel':
                delta=operand-(256 if operand&128 else 0);edges=[nxt,nxt+delta]
            elif name not in ['RTS','RTI','BRK']:edges=[nxt]
            else:assert name!='BRK',('reachable private BRK',hex(pc))
            graph[pc]=edges;weight[pc]=cost;todo.extend(z for z in edges if z not in graph)
        # Collapse branch/scan loops. A positive-weight cycle would allow
        # multiple point publications and reject the one-byte pending design.
        index={};low={};stack=[];on=set();components=[]
        def visit(v):
            index[v]=low[v]=len(index);stack.append(v);on.add(v)
            for w in graph[v]:
                if w not in graph:continue
                if w not in index:visit(w);low[v]=min(low[v],low[w])
                elif w in on:low[v]=min(low[v],index[w])
            if low[v]==index[v]:
                group=[]
                while True:
                    w=stack.pop();on.remove(w);group.append(w)
                    if w==v:break
                components.append(group)
        for pc in graph:
            if pc not in index:visit(pc)
        owner={pc:i for i,g in enumerate(components)for pc in g};dag={i:set()for i in range(len(components))};cost={}
        for i,g in enumerate(components):
            cycle=len(g)>1 or any(pc in graph[pc]for pc in g)
            cost[i]=sum(weight[pc]for pc in g)
            assert not cycle or cost[i]==0,('point-producing loop',hex(entry),list(map(hex,g)))
            for pc in g:
                dag[i].update(owner[z]for z in graph[pc]if z in owner and owner[z]!=i)
        @functools.lru_cache(None)
        def longest(i):return cost[i]+max([longest(z)for z in dag[i]]or[0])
        answer=longest(owner[entry]);memo[entry]=answer;active.pop();return answer
    roots=[L['DkServices']+3*i for i in range(38)]+[L[n]for n in ['DkjrNativeFruitSet','DkjrNativeFruitReset','DkjrNativeFruitProject','DkjrNativeFruitRemove']]
    max_publications={str(i):summary(pc)for i,pc in enumerate(roots)}
    assert max_publications['0']==1 and max(max_publications.values())==1
    # The score staging leaf was deliberately summarized as one publication;
    # still include its complete compiled read/write instructions in domains.
    pc=L['DkjrNativeAwardSourcePoints']
    while pc<L['DkScoreFlush']:
        reached.add(pc);pc+=instruction(pc)[2]
    packet_access=[];nearby=[];dynamic=[]
    frame_bases={0xc460:7,0xc468:32,0xc48a:7,0xc492:32}
    typed_x={0xc420:3,0xc424:3,0xc428:3,0xc42c:3,0xc430:3,0xc445:5,0xc44b:5,0xc451:5}
    indirect={name:pc for name,pc in L.items()if re.fullmatch(r'DIndirect_[0-9a-f]{4}',name)}
    for pc in sorted(reached):
        name,mode,size,operand=instruction(pc)
        if mode not in ['abs','abx','aby']:continue
        if pc in indirect.values():
            dynamic.append(dict(PC=pc,name=next(n for n,z in indirect.items()if z==pc),operation=name));continue
        maximum=operand+(255 if mode in ['abx','aby']else 0)
        if not(operand<0xc4bb and maximum>=0xc460):continue
        if operand>=0xc460:
            assert operand<0xc4bb
            bound=frame_bases[operand]if mode=='abx'else 0
            assert mode=='abs' or mode=='abx'and operand in frame_bases,(hex(pc),name,mode,hex(operand))
            assert operand+bound<0xc4bb
            packet_access.append(dict(PC=pc,operation=name,mode=mode,base=operand,index_maximum=bound))
        else:
            if mode=='aby':assert 0xc400<=operand<=0xc406;bound=22
            else:assert mode=='abx'and operand in typed_x;bound=typed_x[operand]
            assert operand+bound<0xc460
            nearby.append(dict(PC=pc,operation=name,mode=mode,base=operand,index_maximum=bound,last_address=operand+bound))
    assert len(indirect)==len(dynamic),(len(indirect),len(dynamic),[n for n,p in indirect.items()if p not in reached])
    fruit={'d973','d978','d9b6','d9c7'}
    descriptor={'eb96','eb9f','eba4','eba9','ebd0','ebd9'}
    render={'ea95','eaa5','eaac','eab0','eac4','ead0','eaf6','eaf9','eaff','eb2a','eb2d','eb33','eb54'}
    assert {n[-4:]for n in indirect}==fruit|descriptor|render
    # Fixed producer/dominance clauses, bound to complete assembled source.
    assert source.count(' sta $c091\n')==1 and source.count(' sta $c092\n')==1
    assert ' lda #0\n sta $c091\n lda #4\n sta $c092' in source
    assert 'DkjrNativeFruitProject:\n ldx FruitCount\n cpx #5\n bcs FruitProjectReject' in source
    assert ' ldx #0\n ldy #1\nFruitProjectLoop:' in source
    assert ' adc #7\n tay\n inx\n cpx #4\n bne FruitProjectLoop' in source
    assert 'D_ea24: ; original $EA24: lda #$02\n lda #$02\nD_ea26: ; original $EA26: sta $05\n sta $c005' in source
    assert source.count(' jsr DkjrNativeAwardSourcePoints\n')==1
    assert ' jsr DkPauseMain\n jsr DkScoreFlush\n bcc DkMainNo' in source
    assert ' sta LifeCommitted\n sta ScoreAmount\n rts' in source
    # Actual native continuation binds reentrancy as well as final snapshots.
    prior=json.loads((O/'native-scoretail-v55-CPU.json').read_text());assert prior['passed']
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        compiled_reachable_instructions=len(reached),declared_native_and_world_API_roots=len(roots),
        conservative_score_publications_per_call=max_publications,
        packet_extent=[0xc460,0xc4bb],packet_read_write_sites=packet_access,nearby_bounded_sites=nearby,
        complete_original_indirect_sites=dynamic,
        indirect_domains=dict(fruit=dict(pointer=[0xc091,0xc092],only_typed_producer=0xc400,Y_maximum=28,half_open=[0xc400,0xc41d]),
            render=dict(pointer=[0xc004,0xc005],dominant_high=2,low_and_Y_8bit_maximum_last=0xc3fe),
            descriptor=dict(pointer=[0xc002,0xc003],typed_domains=['immutable relocated original bounds/contact descriptors','validated source-format terrain/vine listsC800..C8D8'])) ,
        synchronous_lifetime=dict(source_publication_maximum=1,flush_once_after_source_phase=True,
            pending_consumed_before_actual_Main_return=248,constructor_clears_pending=True,
            score_and_victim_frames_disjoint=True,interrupt_actor_reentry=False,
            async_evidence='v56 direct725IRQ+725FF; v57 complete nested audio cohort receipt separately. IRQ/audio never alter private arrays, including both packets. Latest owner replacement must authenticate, retire and invalidate before reuse.'),
        scope='Compiled control-flow follows every declared38 native vector plus4typed world-fruit APIs; branch loops collapse only when zero point-weight. Conservative maximumone original point publication proves one-byte existing pending lifetime without controller-dependent assumptions. Every reachable direct/indexed possible packet alias is classified;23original translated-indirect sites have source-backed fruit/OAM/descriptor domains. No arbitrary internal-label or poisoned private-pointer API is admitted. Final native public gates/latest-owner cold/retire and allunfinishedrows remain outside this private proof.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-scoretail-v54.s',O/'native-scoretail-v54.bin',O/'native-scoretail-v54-layout.json',O/'native-scoretail-v55-CPU.json',O/'native-scoretail-v56-direct.json',R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json']})
    (O/'native-packet-domains-v58.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in['passed','compiled_reachable_instructions','declared_native_and_world_API_roots','packet_extent']}))


if __name__=='__main__':main()
