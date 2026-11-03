"""Deliver tested block/tier fixes; retain explicit pending flower/perf scope."""
import argparse,json,re,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
from nightly_patch_guard_v1 import check
O=R/'build/bub-earned-delivery-1103-v98'
C=R/'build/bub-initial-tier-native-1103-v88'
D=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
PARENT='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
read=lambda p:json.loads(Path(p).read_text())

def bound(path):
    q=read(path);assert q['passed']
    for name,h in q.get('bindings',{}).items():
        f=Path(name);f=f if f.is_absolute()else R/f
        assert sha(f)==h,str(f)
    return q

def proof(packet,identity,task):
    ready=read(packet/'ready.json');binding=read(packet/'capture/binding.json');result=read(packet/'capture/result.json')
    assert ready['ROM_sha256']==binding['ROM_sha256']==PIN
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(packet/'ready.json')
    for name,h in ready['bindings'].items():assert sha(name)==h,name
    assert result['passed']and result['controller_only']and result['active_data_writes']==result['late_enables']==0
    q=read(packet/'capture'/('earned-mushroom.json'if task=='mushroom'else'full11.json'))
    assert q['passed']
    if task=='mushroom':
        obs=q['observer'];assert q['identity']==identity and q['source_flags']==q['native_status']==1 and q['lives']==2
        assert q['observed_immature']and q['observed_mature']
    else:
        obs=read(packet/'capture/bub-observer.json')
        assert q['full_stage']and(q['world'],q['level'],q['engine'])==(0,1,8)
        assert q['initial_lives']==q['final_lives']==2 and not q['helpers_added']
        assert[(v['kind'],v['left'],v['right_exclusive'])for v in q['clears']]==[
            ('pipe',448,480),('pipe',608,640),('pipe',736,768),('pipe',912,944),('pit',1104,1136),('pit',1376,1424),('pit',2448,2480)]
        assert obs['pops']==17 and obs['source_bubble_ride_restarts']==6
    assert obs['passed']and obs['identity']==identity and obs['failures']==0
    return dict(identity=identity,task=task,frames=result['frames'],completed_Main=obs['completed_Main'],checks=obs['checks'],failures=0,lives=[2,2],helpers_added=False,packet=packet.relative_to(R).as_posix())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['install','finalize']);args=ap.parse_args()
    rom=R/'build/bub-initial-tier-1103-v87/bub-initial-tier.nes';assert sha(rom)==PIN
    cpu=R/'build/bub-current-cold-1103-v97/receipt.json';cold=bound(cpu)
    assert cold['ROM_SHA256']==PIN and cold['paired_Main_updates']==250 and cold['header_poison_rejections']==32
    head=R/'build/bub-menu-candidate-1102-v2';refs=[cpu,R/'docs/qa/checkpoints/2026-11-03/bub-earned-native-v90/receipt.json']
    for name in['head-projection-v64-nested.json','head-projection-v68-brick-nested-small.json','head-projection-v68-brick-nested-powered.json']:
        path=head/name;q=bound(path);assert q['memory_ROM_SHA256']==cold['parent_ROM_SHA256'];refs.append(path)
        assert q.get('minimum_nested_IRQ_SP',0)>=122
    bound(refs[1]);rows=[];packets=[]
    for identity,name in[(0,'bub'),(1,'bob')]:
        for task in['mushroom','full11']:
            packet=C/f'{name}-{task}';rows.append(proof(packet,identity,task));packets.append((identity,name,task,packet))
    O.mkdir(exist_ok=True)
    if args.action=='install':
        assert not(O/'delivery.json').exists()
        before=check(D);assert before['ROM_sha256']==PARENT
        labels={}
        for line in rom.with_suffix('.lbl').read_text().splitlines():
            m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line)
            if m:labels[m[2]]=int(m[1],16)
        sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
        prepared=[]
        for identity,name,task,packet in packets:
            text=(packet/'controller.lua').read_text();explicit={n:int(v)for n,v in re.findall(r'L\["(\w+)"\]=(\d+)',text)}
            reader=text.index('local function r(n)return emu.read(assert(L[n],n)')
            needed=set(re.findall(r'\bL\.(\w+)',text))|set(re.findall(r"\br\(['\"](\w+)['\"]",text[reader:]))
            assert not re.search(r'\bB[.\[]',text)and'getLabelAddress'not in text
            prefix=['L=L or{}','B=B or{}']
            for n in sorted(needed):
                assert n in labels or n in explicit,n
                v=labels.get(n,explicit.get(n));assert n not in explicit or explicit[n]==v,n
                prefix.append(f'L["{n}"]={v}')
            text='\n'.join(prefix)+'\n'+text
            assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
            prepared.append((identity,name,task,packet,text))
        assert not any(D.with_suffix(ext).exists()for ext in['.lbl','.dbg','.dbg.gz'])
        D.write_bytes(rom.read_bytes());after=check(D);assert sha(D)==PIN
        for identity,name,task,packet,text in prepared:
            target=O/f'downloads-{name}-{task}'
            prepare(target,rom,text,[Path(__file__),D,packet/'controller.lua',packet/'ready.json',packet/'capture/binding.json',*refs],expected=PIN,timeout=180 if task=='mushroom'else 240,allow_interactive=True,scope='Actual Downloads launch with explicit embedded labels and no debug/patch sidecars. Both original mushroom emergence/maturity/collection/60-update transformation and separate fullnonshortcut1-1 actual native controller-only replays. No all-powerup, flower-route, acoustic-fidelity or lag-reduction claim. Parent head IRQ receipts retain their cc7 hash; exact cf7 initialization delta/cold250pairedMain and20new-instruction IRQ/FF checks bound separately.')
            ready=read(target/'ready.json');ready['ROM']=str(D);(target/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
        out=dict(installed=True,ROM_sha256=PIN,previous_ROM_sha256=PARENT,destination=str(D),backup_created=False,before=before,after=after,downloads_launch_verified=False,candidate_rows=rows,source_scope='Deferred actual ceiling contact and own native initial tier; donor physics retained. No new helpers. Source shoes/quick-bubble upgrades are implemented, but the later earned flower controller is not yet passing.',remaining='Flower route, original audio fidelity, idle/walk lag reduction, Prince/DK Jr and remaining roster integrations remain in progress.')
        (O/'delivery.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));return
    delivery=read(O/'delivery.json');assert delivery['ROM_sha256']==PIN==sha(D)
    actual=[]
    for identity,name,task,packet in packets:
        row=proof(O/f'downloads-{name}-{task}',identity,task);assert read(O/f'downloads-{name}-{task}'/'ready.json')['ROM']==str(D)
        expected=next(r for r in rows if r['identity']==identity and r['task']==task)
        assert all(row[k]==expected[k]for k in['frames','completed_Main','checks','failures','lives'])
        actual.append(row)
    base=Path('C:/NES/Super Mario Bros. (World).nes');assert sha(base)=='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
    original=base.read_bytes();raw=rom.read_bytes();patch=bytearray(b'PATCH');i=0
    while i<len(raw):
        if i<len(original)and original[i]==raw[i]:i+=1;continue
        start=i
        if start==0x454f46:start-=1
        i=max(i,start+1)
        while i<len(raw)and i-start<65535 and(i>=len(original)or original[i]!=raw[i]):i+=1
        patch+=start.to_bytes(3,'big')+(i-start).to_bytes(2,'big')+raw[start:i]
    patch+=b'EOF'+len(raw).to_bytes(3,'big');rebuilt=bytearray(original);at=5
    while patch[at:at+3]!=b'EOF':
        pos=int.from_bytes(patch[at:at+3],'big');n=int.from_bytes(patch[at+3:at+5],'big');at+=5;assert n
        if len(rebuilt)<pos+n:rebuilt.extend(bytes(pos+n-len(rebuilt)))
        rebuilt[pos:pos+n]=patch[at:at+n];at+=n
    assert rebuilt[:int.from_bytes(patch[at+3:at+6],'big')]==raw
    ips=O/'SMB-Crossover-Latest-WIP-MMC5.ips';ips.write_bytes(patch)
    delivery.update(downloads_launch_verified=True,downloads_rows=actual,post_downloads_guard=check(D),IPS_SHA256=sha(ips),IPS_roundtrip=True,base_SHA256=sha(base),IPS_bytes=len(patch))
    (O/'verified-delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
    (O/'release-notes.txt').write_text('Current MMC5 work-in-progress nightly.\n\nApply the sole IPS to a clean, headered Super Mario Bros. (World) ROM.\nBase SHA-256: '+sha(base)+'\nPatched ROM SHA-256: '+PIN+'\n\nNovember 3: Bub/Bob head contacts now reach the real native block routine after their resident movement callback returns. Their own cold/new-life initialization clears inherited Mario power status, restoring actual mushroom emergence and source shoes progression. Both characters collect the first mushroom and independently clear non-shortcut 1-1 into active 1-2 without life loss or new helper platforms. All four replays pass from the actual Downloads path. Original donor physics retained.\n\nThe later earned flower route, original audio fidelity, idle/walk lag reduction and remaining roster integrations are still under test. Prince of Persia and Donkey Kong Jr. remain private integrations; they are not newly unlocked in this build.\n')
    print(json.dumps(delivery))

if __name__=='__main__':main()
