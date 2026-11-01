"""Reuse one frozen controller after checking the exact CF code and native ABI."""
from pathlib import Path
import argparse,re,sys,zipfile
from prepare_selected_native_packet_v1 import R,prepare,sha
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_contra_force_p1_coherent_cart_v2 import native_abi


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--expected',required=True);ap.add_argument('--variant',choices=['burns','smith','iron','beans'],required=True)
    args=ap.parse_args();joint=args.joint.resolve()
    parent=R/'build/contra-force-projectile-contact-1031-v3/joint'
    assert sha(parent/'candidate.nes')=='f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182'
    assert sha(joint/'candidate.nes')==args.expected
    old,new=[scoped_load(p/'candidate.nes')for p in [parent,joint]]
    assert native_abi(old)==native_abi(new)
    for lo,hi in [(935,959)]:
        assert old['raw'][1048592+lo*1024:1048592+hi*1024]==new['raw'][1048592+lo*1024:1048592+hi*1024]
    archive=R/'docs/qa/checkpoints/2026-10-31/ready74-cf-projectile-native-v1/native-results.zip'
    member=f'build/contra-force-shooting-native-1031-v3/{args.variant}/controller.lua'
    with zipfile.ZipFile(archive)as z:text=z.read(member).decode('utf-8')
    for name,value in re.findall(r'L\["(\w+)"\]=(\d+)',text):
        if name in new['syms']:assert address(new,name)==int(value),name
    old_sha=sha(parent/'candidate.nes');assert text.count(old_sha)==1
    text=text.replace(old_sha,args.expected,1)
    assert not any(x in text for x in ['emu.write(','emu.setState(','emu.loadSavestate('])
    prepare(args.output,joint/'candidate.nes',text,[Path(__file__),archive,parent/'candidate.nes',parent/'candidate.dbg',joint/'source-stage.json'],
            expected=args.expected,timeout=90,
            scope=f'{args.variant}: frozen controller-earned pistol defeat, native score/SFX/source impact, camera and CHR/OAM/display checks. Exact CF image and108 native imports checked before reuse. No full1-1/upgrades claim.')


if __name__=='__main__':main()
