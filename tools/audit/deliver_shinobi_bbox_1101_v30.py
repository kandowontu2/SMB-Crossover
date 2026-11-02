"""Deliver exact native-verified original-pose Shinobi body bounds."""
import json,re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from nightly_patch_guard_v1 import check
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=R/'build/shinobi-bbox-candidate-1101-v30'
PIN='6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428'
def main():
 rom=O/'candidate.nes';assert sha(rom)==PIN
 for name in ['native-full','profile','arthur-route','metal-idle']:
  c=O/name/'capture';r=json.loads((c/'result.json').read_text());b=json.loads((c/'binding.json').read_text())
  assert r['passed']and b['exit_code']==0 and b['ROM_sha256']==PIN,(name,r)
 for name in ['CPU-design.json','seams-CPU.json']:
  q=json.loads((O/name).read_text());assert q['passed']and q['ROM_sha256']==PIN
 perf=json.loads((O/'profile/capture/performance.json').read_text());old=json.loads((O/'profile-baseline/capture/performance.json').read_text())
 assert all(perf[k]['completed_updates']==old[k]['completed_updates']for k in ['idle','walk'])
 dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');previous=sha(dest)
 assert previous in ['c3dd03031faaef7faf12f865b7a5cdfd363835e2179eca22fe2eef8180553157',PIN]
 if previous==PIN and (O/'delivery.json').exists():previous=json.loads((O/'delivery.json').read_text())['previous_sha256']
 before=check(dest);dest.write_bytes(rom.read_bytes());after=check(dest);assert sha(dest)==PIN
 q=dict(installed=True,ROM_sha256=PIN,previous_sha256=previous,backup_created=False,before=before,after=after,downloads_launch_verified=False,performance=perf,
  scope='Shinobi original pose rectangles own native enemy/contact bbox. Exact full1-1 toactive1-2 in8924frames,lives2to2,nohelpers. Arthur full1-1 regression and Metalidle/walk pass. Idle/walk80/78 updates per120physicalframes unchanged; meanCPU+1523/update. Originalhead/sideprofiles, audio/melee/magic/powerups stillrequirefollowup. Fullroster/everypowerup notcomplete.')
 (O/'delivery.json').write_text(json.dumps(q,indent=2)+'\n')
 ref=R/'build/roster-combined-1101-v1/native/controller.lua';t=ref.read_text();b=scoped_load(rom)
 names=set(re.findall(r"\br\('([^']+)'",t))|set(re.findall(r'\bL\.(\w+)',t))|{'RgOamFirst','RgOamUsed','RgOamRotation','CurrentOAMOffset','CurrentCHRBank','X5ChrMode','SsChrActive','X5WideChrActive','ReloadCHRBank','Mirror_PPUCTRL','CurrentBank','CurrentBankC'}
 t='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in sorted(names))+'\n'+t
 prepare(O/'downloads',rom,t,[Path(__file__),ref,dest],expected=PIN,timeout=90,allow_interactive=True,scope='Actual Downloads coldShinobi Select/Start/idle/walk and OAM-count/rotation alignment. Isolated testRunner may coexist with a plain user ROM session; existing automated runs stillblock. Explicitsymboladdresses, threePNGs, noRAMwrites/backups.')
 p=O/'downloads/ready.json';q=json.loads(p.read_text());q['ROM']=str(dest);p.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(installed=True,ROM_sha256=PIN,backup=False,downloads_launch_pending=True)))
if __name__=='__main__':main()
