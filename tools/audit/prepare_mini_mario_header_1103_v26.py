"""Distinct exact native7-byte status-name repair; frozen4923B unchanged."""
from pathlib import Path
import json,re,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_host_1103_v22 as H
W=H.W;R,O=H.R,H.O

def main():
    old=(O/'mini-host-v22.bin').read_bytes();prior=json.loads((O/'mini-host-v22.json').read_text());assert W.sha(old)==prior['SHA256']
    src=(O/'mini-host-v22.s').read_text()
    needle=' ldy #8\n@hud:\n lda MiniName,y';assert src.count(needle)==1
    src=src.replace(needle,' ldy #6\n@hud:\n lda MiniName,y')
    needle='MiniName: .byte $16,$12,$17,$12,$16,$0A,$1B,$12,$18';assert src.count(needle)==1
    # Retain exact code/data size and all entry addresses. Final2 bytes are
    # unreachable historical name suffix, not an allocation or live string.
    src=src.replace(needle,'MiniName: .byte $16,$12,$17,$12,$24,$24,$24,$12,$18')
    p=O/'mini-host-v26';p.with_suffix('.s').write_text(src);p.with_suffix('.cfg').write_bytes((O/'mini-host-v22.cfg').read_bytes());cc=R/'tools/Windows/cc65/bin'
    for cmd in[[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
        r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert r.returncode==0,r.stderr
    data=p.with_suffix('.bin').read_bytes();L={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)};assert L==prior['labels']and len(data)==len(old)
    changes=[dict(offset=i,CPU=i+0xa000,old=a,new=b)for i,(a,b)in enumerate(zip(old,data))if a!=b];assert len(changes)==4,changes
    out=dict(passed=True,bytes=len(data),SHA256=W.sha(data),labels=L,vectors=prior['vectors'],five_1KB_pages_fit=True,CPU_qualified=False,native_admitted=False,ROM_written=False,old_SHA256=W.sha(old),exact_changes=changes,HUD_name='MINI   ',menu_name='MINIMARIO',source_authority='src/screen_render.s::TopStatusBarLine declares name length7 then WORLD/TIME packet immediately. Only payload11..17 may be changed by row30.',bindings={p.relative_to(R).as_posix():W.sha(p.read_bytes())for p in[Path(__file__),O/'mini-host-v22.s',O/'mini-host-v22.bin',O/'mini-host-v22.json',R/'src/screen_render.s']})
    (O/'mini-host-v26.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in['passed','bytes','SHA256','exact_changes']}))
if __name__=='__main__':main()
