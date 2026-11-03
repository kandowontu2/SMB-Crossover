"""Root WIP delivery: qualified Bub full stage, explicit Bob partial scope."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check
O=R/'build/bub-root-delivery-1102-v43'
C=R/'build/bub-menu-candidate-1102-v2'
D=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
PARENT='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
read=lambda p:json.loads(Path(p).read_text())


def proof(p):
    ready=read(p/'ready.json');b=read(p/'capture/binding.json');q=read(p/'capture/full11.json');obs=read(p/'capture/bub-observer.json')
    assert ready['ROM_sha256']==b['ROM_sha256']==obs['ROM_sha256']==PIN
    assert b['exit_code']==0 and b['ready_sha256']==sha(p/'ready.json')
    assert q['passed']and q['full_stage']and q['why']=='actual-active1-2-all-four-pipes-three-pits'
    assert(q['world'],q['level'],q['engine'])==(0,1,8)and q['initial_lives']==q['final_lives']==2
    assert obs['passed']and obs['failures']==0 and obs['checks']>0 and not q['helpers_added']
    assert[(v['kind'],v['left'],v['right_exclusive'])for v in q['clears']]==[
        ('pipe',448,480),('pipe',608,640),('pipe',736,768),('pipe',912,944),('pit',1104,1136),('pit',1376,1424),('pit',2448,2480)]
    assert len(q['actual_normal_pit_jump_entries'])==2
    for e in q['actual_normal_pit_jump_entries']+q['actual_stair_jump_entries']:
        assert e['native_state']==0 and(e['foot'][1]['solid']or e['foot'][3]['solid'])and not e['support_marker']and e['source_held']&128
    for name,h in ready['bindings'].items():assert sha(name)==h,name
    return dict(passed=True,full1_1=True,active1_2=True,frames=read(p/'capture/result.json')['frames'],completed_Main=obs['completed_Main'],checks=obs['checks'],failures=obs['failures'],original_rides=obs['source_bubble_ride_restarts'],native_pops=obs['pops'],initial_lives=2,final_lives=2,helpers_added=False,path=p.relative_to(R).as_posix())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['install','finalize']);a=ap.parse_args()
    rom=C/'combined-current-landing.nes';manifest=C/'combined-current-landing.json';assert sha(rom)==PIN
    m=read(manifest);assert m['expected_rebased_ROM_sha256']==PIN and m['delivered_parent_sha256']==PARENT and m['actual_changed_bytes_over_delivered_parent']==370
    assert m['exact_Sunny_five_patches_preserved']and m['patch_intervals_disjoint']
    for name,h in m['bindings'].items():assert sha(R/name)==h,name
    sunny=R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9/receipt.json';s=read(sunny);raw=rom.read_bytes()
    assert s['installed']and s['ROM_sha256']==PARENT and len(s['patches'])==5
    for p in s['patches']:assert raw[p['offset']:p['offset']+len(bytes.fromhex(p['new']))]==bytes.fromhex(p['new'])
    candidate=C/'native-current-landing-bub-full11-castle-stairs';qualified=proof(candidate)
    O.mkdir(exist_ok=True);packet=O/'downloads-bub-full11'
    if a.action=='install':
        assert not(O/'delivery.json').exists()and not packet.exists()
        before=check(D);assert before['passed']and before['ROM_sha256']in[PARENT,PIN]
        controller=(candidate/'controller.lua').read_text();labels={}
        for line in rom.with_suffix('.lbl').read_text().splitlines():
            match=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line)
            if match:labels[match[2]]=int(match[1],16)
        explicit={name:int(value)for name,value in re.findall(r'L\["(\w+)"\]=(\d+)',controller)}
        # The earlier physical observer has its own r() reading C.ram.
        # Only the later controller r() reads labels from L.
        label_reader=controller.index('local function r(n)return emu.read(assert(L[n],n)')
        needed=set(re.findall(r'\bL\.(\w+)',controller))|set(re.findall(r"\br\(['\"](\w+)['\"]",controller[label_reader:]))
        assert not re.search(r'\bB[.\[]',controller)and'getLabelAddress'not in controller
        prefix=['L=L or{}','B=B or{}']
        for name in sorted(needed):
            assert name in labels or name in explicit,name
            value=labels.get(name,explicit.get(name));assert name not in explicit or explicit[name]==value,name
            prefix.append(f'L["{name}"]={value}')
        controller='\n'.join(prefix)+'\n'+controller
        sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
        assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(controller)
        D.write_bytes(raw);after=check(D);assert after['passed']and sha(D)==PIN
        assert not any(D.with_suffix(ext).exists()for ext in['.lbl','.dbg','.dbg.gz'])
        refs=[Path(__file__),candidate/'controller.lua',candidate/'ready.json',candidate/'capture/binding.json',candidate/'capture/full11.json',candidate/'capture/bub-observer.json',manifest,sunny,D]
        prepare(packet,rom,controller,refs,expected=PIN,timeout=240,allow_interactive=True,scope='Actual Downloads Bub cold Hard non-shortcut1-1 replay. Explicit labels embedded; no Downloads debug/patch sidecars. All four pipes/three pits, supported stair retreats/two final pit source jumps, natural bubble combat, life/source/hardware guards retained. Bob has partial current9cf scope only; no Bob full-stage claim, no source physics changes or helper additions.')
        q=read(packet/'ready.json');q['ROM']=str(D);(packet/'ready.json').write_text(json.dumps(q,indent=2)+'\n')
        result=dict(installed=True,ROM_sha256=PIN,previous_ROM_sha256=before['ROM_sha256'],destination=str(D),backup_created=False,before=before,after=after,candidate_Bub_full11=qualified,downloads_launch_verified=False,Bob_scope='Current9cf natural close pop and first two pipes pass; thirdpipe shot rearm controller pending. Prior Bob source/cold/facing/ride proofs retain their original hashes. No current full-stage claim.',remaining='Idle/walk bridge performance, Bob full-stage route, broader roster/all-powerup/audio qualification remain incomplete.')
        (O/'delivery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return
    delivery=read(O/'delivery.json');assert delivery['ROM_sha256']==PIN and sha(D)==PIN
    downloads=proof(packet);guard=check(D);assert guard['passed']
    assert downloads['frames']==qualified['frames']and downloads['completed_Main']==qualified['completed_Main']
    base=Path('C:/NES/Super Mario Bros. (World).nes');basebytes=base.read_bytes()
    assert len(basebytes)==40976 and sha(base)=='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
    patch=bytearray(b'PATCH');i=0
    while i<len(raw):
        if i<len(basebytes)and basebytes[i]==raw[i]:i+=1;continue
        start=i
        if start==0x454f46:start-=1
        i=max(i,start+1)
        while i<len(raw)and i-start<65535 and(i>=len(basebytes)or basebytes[i]!=raw[i]):i+=1
        patch+=start.to_bytes(3,'big')+(i-start).to_bytes(2,'big')+raw[start:i]
    patch+=b'EOF'+len(raw).to_bytes(3,'big');rebuilt=bytearray(basebytes);pos=5
    while patch[pos:pos+3]!=b'EOF':
        at=int.from_bytes(patch[pos:pos+3],'big');n=int.from_bytes(patch[pos+3:pos+5],'big');pos+=5;assert n>0
        if len(rebuilt)<at+n:rebuilt.extend(bytes(at+n-len(rebuilt)))
        rebuilt[at:at+n]=patch[pos:pos+n];pos+=n
    rebuilt=rebuilt[:int.from_bytes(patch[pos+3:pos+6],'big')];assert rebuilt==raw
    ips=O/'SMB-Crossover-Latest-WIP-MMC5.ips';ips.write_bytes(patch)
    delivery.update(downloads_launch_verified=True,downloads_Bub_full11=downloads,post_downloads_guard=guard,IPS_SHA256=sha(ips),IPS_roundtrip=True,base_SHA256=sha(base),base=str(base),IPS_bytes=len(patch))
    (O/'verified-delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
    (O/'release-notes.txt').write_text('Current MMC5 work-in-progress nightly.\n\nApply the sole IPS to a clean, headered Super Mario Bros. (World) ROM.\nBase SHA-256: '+sha(base)+'\nPatched ROM SHA-256: '+PIN+'\n\nNovember 2: Bub/Bob landing adapter resets original jump state after actual supported landings. Bub clears non-shortcut 1-1 into active 1-2, all four pipes and three gaps, no life loss or new helper platforms; tested candidate and actual Downloads launch match. Source physics are retained. Bob full-stage route is still under test; current partial route and source checks are recorded separately. Sunny growth palette deadline fix and earned mushroom/flower progression retained.\n\nExpanded roster, severe-lag reduction, all-character/all-powerup and audio qualification remain in progress. Prince of Persia and Donkey Kong Jr. are private integrations and are not newly unlocked here.\n')
    print(json.dumps(delivery))

if __name__=='__main__':main()
