"""Sparse two-platform composition on genuine4cbd RCR; no shared edits."""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ov=B/'celeste-platform-rcr-overlay';assert not ov.exists()
 old=json.loads((B/'celeste_platform_two_handoff_v1.json').read_text())
 for name in['src/celeste_platform_two.s','src/celeste_mario_host.s']:
  p=B/'celeste-platform-two-overlay'/name;assert sha(p)==old['bindings'][str(p.resolve())]
 parent=B/'roster-shared-rcr-adopted-v8.nes';assert sha(parent)=='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
 assert parent.read_bytes()[16+26*8192+0x1140:16+26*8192+0x1600]==bytes([255])*1216
 host=(R/'src/celeste_mario_host.s').read_text();before='.proc CmHostDashTail\n farcall CmWeapons\n';after='.proc CmHostDashTail\n farcall CmPlatformWeapons\n';assert host.count(before)==1
 (ov/'src').mkdir(parents=True)
 (ov/'smb1base-mmc5-expanded.cfg').write_bytes((R/'smb1base-mmc5-expanded.cfg').read_bytes())
 (ov/'src/celeste_mario_host.s').write_text(host.replace(before,after),encoding='utf-8',newline='\n')
 (ov/'src/celeste_platform_two.s').write_bytes((B/'celeste-platform-two-overlay/src/celeste_platform_two.s').read_bytes())
 (ov/'src/entrypoint.s').write_text('.include "build/roster-shared-rcr-adopted-v8-objects/entrypoint.s"\n.include "celeste_platform_two.s"\n',encoding='utf-8')
 (B/'celeste_platform_rcr_v1.patch').write_text(''.join(difflib.unified_diff(host.splitlines(True),host.replace(before,after).splitlines(True),fromfile='a/src/celeste_mario_host.s',tofile='b/src/celeste_mario_host.s')),encoding='utf-8')
 cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(ov),'--output',str(B/'celeste-platform-rcr-v1.nes')]
 q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_platform_rcr_build_v1.json').write_text(json.dumps(dict(command=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr),indent=2)+'\n');print(q.stdout,q.stderr);assert q.returncode==0
if __name__=='__main__':main()
