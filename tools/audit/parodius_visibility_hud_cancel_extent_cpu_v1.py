"""Exercise every owned-removal extent within the existing84-byte Buffer1."""
from pathlib import Path
import argparse,hashlib,json
from parodius_visibility_hud_cancel_cpu_v2 import setup,execute
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def packet(n):
 if n==0:return[]
 assert n>=4
 if n>66:return packet(8)+packet(n-8)
 return[0x20,0x80,n-3]+[(i*37+11)&255 for i in range(n-3)]


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.rom)=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631';b=scoped_load(a.rom);rows=[];case=None
 try:
  for family,offset,length in [('full',0,42)]+[('attr',i,11)for i in [0]+list(range(4,32))]:
   available=83-offset-length
   for n in [0]+list(range(4,available+1)):
    case=dict(family=family,offset=offset,tail=n,old_extent=offset+length+n);q=setup(b,active=3)
    if family=='full':q.put(InvHudActive=0,InvHudPhysical=0);q.invoke('PnHud');owned=[q.get('VRAM_Buffer1',i)for i in range(42)];upper=0x85
    else:owned=[0x23,0xc0,8]+[170]*8;upper=0x81+offset*4
    prefix=packet(offset);tail=packet(n);original=prefix+owned+tail+[0];q.array('VRAM_Buffer1',original);q.put(VRAM_Buffer1_Offset=len(original)-1,X5HudChrUpper=upper)
    out=execute(q,'PnHudNewLife');expected=prefix+tail+[0]
    assert q.get('VRAM_Buffer1_Offset')==len(expected)-1 and[q.get('VRAM_Buffer1',i)for i in range(len(expected))]==expected
    assert q.get('X5HudChrUpper')==1 and q.get('InvHudActive')==0 and q.get('VvHudDirty')==1
    rows.append(dict(case,cycles=out['cycles'],original_native_prefix_tail_and_terminator_exact=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),case=case,completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');q=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),cases=len(rows),max_old_extent=max(x['old_extent']for x in rows),
          foreground_PnHudNewLife_CPU_min=min(x['cycles']for x in rows),foreground_PnHudNewLife_CPU_max=max(x['cycles']for x in rows),
          tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),
          limits='Every syntactically valid prefix/tail encoded length within the existing83-byte extent; synthetic isolated CPU packets, not claims that every shape is naturally produced/reachable or fits native vblank. Queue removals preserve all non-HUD commands; rare foreground cancellation cost is explicit. No native run or adoption.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
