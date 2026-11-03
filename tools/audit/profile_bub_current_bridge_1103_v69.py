"""Exact delivered cf7 idle/walk bridge and native costs, without ROM edits."""
from collections import Counter,defaultdict
import hashlib,json,re
from pathlib import Path
import check_bub_head_projection_1102_v56 as H
import check_bub_original_upgrades_1102_v49 as Base
from prepare_selected_native_packet_v1 import sha
from check_tmnt_render_oa import location
O,R,N,Q,address=H.O,H.R,H.N,H.Q,H.address
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'


def bundle():
    baseline=O/'combined-current-landing.nes'
    assert sha(baseline)=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    original=Base.Path
    Base.Path=lambda value:baseline if str(value).replace('\\','/').lower()=='c:/users/kando/downloads/smb-crossover-latest-wip-mmc5.nes'else original(value)
    try:_,parent,route,q,p,_=H.bundle()
    finally:Base.Path=original
    manifest=R/'build/bub-initial-tier-1103-v87/proposal.json';init=json.loads(manifest.read_text())
    rom=R/init['candidate'];assert sha(rom)==PIN==init['ROM_SHA256']
    for name,digest in init['bindings'].items():assert sha(R/name)==digest,name
    raw=rom.read_bytes();image=b''.join(raw[1048592+page*1024:1048592+(page+1)*1024]for page in H.H.H.PAGES)
    assert image==(rom.parent/'private-image.bin').read_bytes()
    assert image[0xa01e-0xa000:0xa021-0xa000]==bytes.fromhex('4cceb2')
    return dict(parent,raw=raw),route,q,p,manifest,rom


def main():
    destination=O/'current-bridge-profile-v69.json';assert not destination.exists()
    b,route,q,head,manifest,rom=bundle()
    def labels(path):return {m[2]:int(m[1],16)for line in path.read_text().splitlines()if(m:=re.match(r'^al\s+([0-9a-fA-F]+)\s+\.(\S+)$',line))}
    owner=labels(R/'build/bubble-bobble-source-1101-v1/native-event-v9-owner.lbl')
    routes=labels(R/'build/bubble-bobble-source-1101-v1/native-proxy-routes.lbl')
    points={(193,owner[n]):n for n in['CoCheckCode','CoCheckHeaders']}
    private=['BbNativeUpdate','BbNativeInput','BbNativeIn','BbNativeOut','BbNativeBoxes',
        'BbNativeCeiling','BbNativeTile23','BbNativeTile84','BbNativeProxiesIn','BbNativeProxiesOut',
        'BbNativeShiftCamera','BbNativeDraw','BbNativeContacts','BbNativeObserve','BbSourceClock',
        'BbPlayerStep','BbBubbleStep','BbTrappedEnemyStep']
    for name in private:
        if name in q['labels']:points[(3,q['labels'][name])]=name
    for name in['BbHeadBegin','BbHeadCapture','BbDeferredHead']:
        points[(3,head['labels'][name])]=name
    native_names=['BlockBufferCollision','PlayerBGCollision','PlayerEnemyCollision','PlayerCollision',
        'AreaParserCore','CrossoverLevelColumn','RenderAreaGraphics','DrawLevelLoop',
        'DrawAllMetasprites','MetaspriteRenderLoop','BillHeadConsumer','BillSideConsumer',
        'BillFootConsumer','CrossoverHeadProbe','CrossoverSideProbe','CrossoverFootProbe']
    for name in native_names:
        if name in b['syms']:points[(((location(b,name)-16)//8192)|128,address(b,name))]=name
    original=N.NesMPU;cases=[]
    for identity in[0,1]:
        for phase,keys in[('idle',0),('walk',1)]:
            m=Q.Q.fresh(b,route,identity);Q.L.E.main_fields(m)
            buckets=Counter();rows=Counter();calls=Counter();inclusive=defaultdict(list)
            host_banks=Counter();host_pcs=Counter();ppu=Counter();stack=[];totals=[]
            class Trace(original):
                def step(self):
                    mm=self.memory;pc=self.pc;bank=mm.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                    while stack and(pc,self.sp,bank)==(stack[-1]['return'],stack[-1]['sp'],stack[-1]['bank']):
                        item=stack.pop();inclusive[item['name']].append(self.processorCycles-item['cycles'])
                    name=points.get((bank,pc))
                    if name:
                        calls[name]+=1;ret=(mm[0x100+((self.sp+1)&255)]+256*mm[0x100+((self.sp+2)&255)]+1)&65535
                        tag=mm.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                        stack.append(dict(name=name,return_=ret,sp=(self.sp+2)&255,bank=tag,cycles=self.processorCycles))
                        stack[-1]['return']=stack[-1].pop('return_')
                    if bank==193 and pc==routes['ExDispatch']:
                        target=mm[address(b,'FarcallJmpTarget_SMC')+1]+256*mm[address(b,'FarcallJmpTarget_SMC')+2]
                        assert 0xb08c<=target<=0xb0fb and(target-0xb08c)%3==0
                        rows[(target-0xb08c)//3]+=1
                    if mm[pc]in[0x8d,0x8e,0x8c]:
                        target=mm[(pc+1)&65535]+256*mm[(pc+2)&65535]
                        if target in[0x2006,0x2007]:ppu[target]+=1
                    if bank==3:bucket='original_source'if 0xa100<=pc<q['labels']['BbCodeEnd']else'private_native_bridge'
                    elif bank==2 and 0xd320<=pc<0xd400:bucket='private_helper'
                    elif bank==193 and 0xae00<=pc<0xb013:bucket='shared_owner_auth'
                    elif bank==193 and(0xa740<=pc<0xa800 or 0xb08c<=pc<0xb0fe):bucket='shared_overlay_dispatch'
                    elif bank==207:bucket='shared_high_router'
                    elif 0x15a<=pc<0x17c:bucket='RAM_farcall'
                    else:bucket='other_native_host'
                    before=self.processorCycles;result=super().step();cost=self.processorCycles-before
                    buckets[bucket]+=cost
                    if bucket=='other_native_host':host_banks[bank]+=cost;host_pcs[bank,pc]+=cost
                    return result
            N.NesMPU=Trace
            try:
                clock=m.ram[2][0x1f]
                for epoch in range(12):
                    N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    totals.append(N.invoke(m,'GameCoreRoutine',x=0,y=0)['CPU'])
            finally:N.NesMPU=original
            assert not stack and sum(totals)==sum(buckets.values())
            assert(m.ram[2][0x1f]-clock)&255==12 and N.get(m,'NumberofLives')==2
            vector_targets={str(row):int.from_bytes(b['raw'][1048592+H.H.H.PAGES[0]*1024+row*3+1:1048592+H.H.H.PAGES[0]*1024+row*3+3],'little')for row in rows}
            result=dict(identity=identity,phase=phase,Main_updates=12,source_updates=12,
                mean_CPU=sum(totals)/12,CPU_range=[min(totals),max(totals)],
                exclusive_mean_CPU={name:value/12 for name,value in buckets.items()},
                service_rows=dict(sorted(rows.items())),row_semantics={'14':'NativeSide, not pickup','24':'Pickup, absent in empty fixtures'},
                private_row_targets=vector_targets,entry_calls=dict(calls),
                inclusive={name:dict(calls=len(costs),mean=sum(costs)/len(costs),per_Main=sum(costs)/12,maximum=max(costs))for name,costs in inclusive.items()},
                other_host_bank_mean_CPU={str(bank):cost/12 for bank,cost in host_banks.items()},
                other_host_top_PC=[dict(bank=bank,PC=pc,mean_CPU=cost/12)for(bank,pc),cost in host_pcs.most_common(40)],
                direct_PPU_stores={f'{a:04X}':count for a,count in ppu.items()})
            cases.append(result)
            print(json.dumps({k:result[k]for k in['identity','phase','mean_CPU','exclusive_mean_CPU','service_rows']}),flush=True)
    result=dict(passed=True,CPU_only=True,ROM_written=False,source_mutated=False,installed=False,
        ROM_SHA256=PIN,original_cadence_reused=dict(path='build/bub-menu-candidate-1102-v2/clock-bridge-profile-v46.json',SHA256=sha(O/'clock-bridge-profile-v46.json'),scope='Original one source-player opportunity per donor NMI remains exact; no new donor scheduling test or changed subcadence.'),
        source_code_end=q['labels']['BbCodeEnd'],cases=cases,
        scope='Exact deliveredcf7 actual GameCore, both identities, legal empty ground idle/walk. Exclusive cost buckets do not overlap; inclusive nested routine costs must not be summed. Hardware stalls/IRQ/NMI are excluded from CPU totals. No auth cache/bypass, resource allocation, candidate or performance fix implied.',
        bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),rom,manifest,rom.parent/'private-image.bin',O/'head-source-v59.json',O/'clock-bridge-profile-v46.json']})
    destination.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
