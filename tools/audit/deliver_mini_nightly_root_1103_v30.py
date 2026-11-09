"""Install only a passing Mini candidate; verify actual Downloads and IPS."""
from pathlib import Path
import argparse,json
from prepare_selected_native_packet_v1 import R,sha,prepare
from nightly_patch_guard_v1 import check
O=R/'build/mini-mario-delivery-root-1103-v30'
D=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PREVIOUS='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
read=lambda p:json.loads(Path(p).read_text())

def proof(packet,pin):
    q=read(packet/'ready.json');b=read(packet/'capture/binding.json');p=read(packet/'capture/result.json')
    assert q['ROM_sha256']==b['ROM_sha256']==p['ROM_sha256']==pin
    assert b['exit_code']==0 and b['ready_sha256']==sha(packet/'ready.json')
    assert p['passed'] and p['controller_only'] and not p['script_RAM_writes']
    for name,h in q['bindings'].items():assert sha(name)==h,name
    return p

def main():
    a=argparse.ArgumentParser();a.add_argument('action',choices=['install','finalize'])
    a.add_argument('--rom',type=Path,required=True);a.add_argument('--packet',type=Path,required=True)
    a.add_argument('--candidate',type=Path,required=True)
    a.add_argument('--symbols-from',type=Path);args=a.parse_args()
    rom=args.rom.resolve();packet=args.packet.resolve();pin=sha(rom)
    candidate=read(args.candidate);assert candidate['candidate_SHA256']==pin
    p=proof(packet,pin);O.mkdir(exist_ok=True)
    if args.action=='install':
        assert not(O/'delivery.json').exists()
        before=check(D);assert before['ROM_sha256']==PREVIOUS
        assert not any(D.with_suffix(ext).exists()for ext in['.lbl','.dbg','.dbg.gz'])
        D.write_bytes(rom.read_bytes());after=check(D);assert sha(D)==pin
        out=O/'downloads-smoke'
        symbols=(args.symbols_from.with_suffix('.lbl'),args.symbols_from.with_suffix('.dbg')) if args.symbols_from else None
        prepare(out,rom,(packet/'controller.lua').read_text(),
            [Path(__file__),D,args.candidate,packet/'ready.json',packet/'capture/binding.json'],
            expected=pin,timeout=180,allow_interactive=True,rom_symbols=symbols,
            scope='Exact passing Mini controller smoke from actual Downloads launch. Embedded labels, no Downloads debug or patch sidecars. No videos, RAM seeds, full-stage or full-powerup inference.')
        q=read(out/'ready.json');q['ROM']=str(D);(out/'ready.json').write_text(json.dumps(q,indent=2)+'\n')
        receipt=dict(installed=True,Downloads_launch_verified=False,ROM_SHA256=pin,
            previous_ROM_SHA256=PREVIOUS,destination=str(D),backup_created=False,
            before=before,after=after,candidate_smoke=p,verification_scope='Candidate actual selection, idle, walking, turning, jump, landing, native source art/bbox/CHR/OAM checks.')
        (O/'delivery.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return
    receipt=read(O/'delivery.json');assert receipt['ROM_SHA256']==pin==sha(D)
    q=proof(O/'downloads-smoke',pin)
    assert read(O/'downloads-smoke/ready.json')['ROM']==str(D)
    base=Path('C:/NES/Super Mario Bros. (World).nes')
    assert sha(base)=='0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea'
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
    receipt.update(Downloads_launch_verified=True,downloads_smoke=q,post_guard=check(D),
        IPS_SHA256=sha(ips),IPS_roundtrip=True,base_SHA256=sha(base),IPS_bytes=len(patch))
    (O/'verified-delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (O/'release-notes.txt').write_text('Current MMC5 work-in-progress nightly.\n\nApply this sole IPS to clean, headered Super Mario Bros. (World).\nBase SHA-256: '+sha(base)+'\nPatched ROM SHA-256: '+pin+'\n\nMini Mario is now an unlocked Mario alternate: highlight Mario and press Select until MINI MARIO. Original miniature art and source ground/jump/fall/crouch/skid movement, with wall cling/jump adapted for SMB terrain. A jumps; hold against a wall and press A again to climb it. Native selection, movement, jump, landing and source sprite checks pass from the actual Downloads path. This is an initial playable integration, not a completed powerup/audio/campaign audit. Prince of Persia and Donkey Kong Jr. remain private/locked integrations.\n')
    print(json.dumps(dict(verified=True,ROM_SHA256=pin,IPS_SHA256=sha(ips),IPS_roundtrip=True)))

if __name__=='__main__':main()
