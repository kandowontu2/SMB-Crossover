"""Correct obsolete A-bank-only observer guards in a private Easy wall matrix."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-head-axis-actual-wall-bv'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not H.exists();H.mkdir();groups=[]
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('actual_wall',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 original=R/'tests/samus-zero-wall-contact.lua';base=original.read_text()
 for rev,folder in [('F',R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f'),('G',V/'root49-samus-head-axis-g2/source/build')]:
  for mp in ['mmc3','mmc5']:
   image=im.Image(folder/f'smb-crossover-{mp}.nes');out=H/f'{rev}-{mp}';out.mkdir()
   names=['PlayerBGCollision','PlayerHeadCollision','SamusStopAtWall','SpawnBrickChunks','SetupPowerUp','MegaMan202AfterBG']
   hooks={n:image.hook(n)for n in names}
   text=base
   replacements={
    "if frame<550 or not bank(1)then return end":"if frame<550 or not actual('PlayerBGCollision')then return end",
    "if not current or not bank(1)or current.kind~='head' then return end":"if not current or not actual('PlayerHeadCollision')or current.kind~='head' then return end",
    "if current and bank(1)then current.walls=current.walls+1 end":"if current and actual('SamusStopAtWall')then current.walls=current.walls+1 end",
    "if not o or not bank(1)then return end\n assert(wx":"if not o or not actual('SpawnBrickChunks')then return end\n assert(wx",
    "if not o or not bank(1)then return end\n local slot":"if not o or not actual('SetupPowerUp')then return end\n local slot",
    "if not current or not bank(1)then return end":"if not current or not actual('MegaMan202AfterBG')then return end",
    "w('SelectedCharacter',2);w('PlayerStatus',c.power)":"w('SelectedCharacter',2);w('CrossoverBehaviorVersion',0);w('PlayerStatus',c.power)"}
   for a,b in replacements.items():assert text.count(a)==1,a;text=text.replace(a,b)
   marker="local log=assert(io.open(OUTPUT..ROM_NAME..'-samus-zero-wall-contact.csv','w'))"
   helper_lua='''local function actual(n)
 if depth~=0 then return false end
 local h=WALL_HOOKS[n];local p=emu.convertAddress(h.address)
 if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return false end
 for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual wall/effect hook8 '..n)end
 return true
end
'''
   assert text.count(marker)==1;text=text.replace(marker,helper_lua+marker)
   core=out/'actual-core.lua';core.write_text(text)
   wrapper=out/'actual-wrapper.lua';wrapper.write_text('WALL_HOOKS='+im.lua(hooks)+'\nTEST_DIR='+im.lua((R/'tests').as_posix()+'/')+'\ndofile(TEST_DIR.."menu-bootstrap.lua")\ndofile('+im.lua(core.as_posix())+')\n')
   q=subprocess.run([sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(wrapper),str(image.path),'--timeout','180'],cwd=R,capture_output=True,text=True)
   log=out/'host.log';log.write_text(q.stdout+q.stderr)
   groups.append(dict(revision=rev,mapper=mp,exit=q.returncode,ROM_sha256=sha(image.path),parent_sha256=sha(original),hooks=hooks,changes=replacements,files={str(p.relative_to(H)):sha(p)for p in out.rglob('*')if p.is_file()}))
   (H/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(rev,mp,'actual-wall',q.returncode,flush=True)
 (H/'review.json').write_text(json.dumps(dict(script_sha256=sha(__file__),groups=groups,scope='Explicit Easy0 native wall/head/effect matrix. Old CurrentBank==1 guard skipped fixed-bank SpawnBrickChunks/SetupPowerUp when rare native head body maps A-bank9. New observer binds exact actual CPU physical bank and8bytes; no outcomes/expectations weakened. No shared fixture changes or ordinary route claim.',main_changed=False),indent=2)+'\n')
 print('ACTUAL_WALL_REVIEW',sha(H/'review.json'),flush=True)
if __name__=='__main__':main()
