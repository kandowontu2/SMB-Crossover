"""Menu-index-only successor; preserve unrun v1 and all gameplay/hardware bytes."""
from pathlib import Path
import argparse,hashlib,json,sys
from current_roster_compact_11_v1 import navigation
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
R=Path(__file__).resolve().parents[2];B=R/'build';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--identity',choices=['chip','dale'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();out=a.output.resolve();assert not out.exists();old=B/f'current-bdf9-{a.identity}-earned-hard-v1';ready=json.loads((old/'prepared-not-run.json').read_text());assert all(sha(x['path'])==x['sha256']for x in ready['bindings'])
 cfg=json.loads((old/'config.json').read_text());rom=B/'cv3_life_gain_watch.nes';assert sha(rom)==cfg['ROM_sha256'];b=scoped_load(rom);raw=b['raw'];table=location(b,'X5MenuCharacters');assert raw[table+13]==14 and raw[table+14]==15
 cfg['menu']=13;cfg['navigation']=navigation(raw,lambda n:location(b,n),13);cfg['foods']={int(k):v for k,v in cfg['foods'].items()}
 routes=[]
 for start in range(19):
  i=start;nodes=[i]
  while i!=13:
   key=cfg['navigation'][i];assert key in['left','right','up','down'];i=raw[location(b,'X5Menu'+key.title())+i];assert i not in nodes;nodes.append(i)
  q=Arena(b,14);q.put(CrossoverMenuIndex=i,CdVariant=cfg['variant']);c,_=q.invoke('MenuResolveCharacter');assert c.a==14;routes.append(dict(start=start,nodes=nodes,resolved=c.a))
 q=Arena(b,14);q.put(CrossoverMenuIndex=14);c,_=q.invoke('MenuResolveCharacter');assert c.a==15
 original=(old/'fixture.lua').read_text();needle='if i~=14 then';assert original.count(needle)==1;new=original.replace(needle,'if i~=C.menu then')
 begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered";assert new[new.index(begin):new.index(end)]==original[original.index(begin):original.index(end)]
 out.mkdir(parents=True);put(out/'config.json',cfg);(out/'fixture.lua').write_text(new,encoding='utf-8',newline='\n')
 oldrun=(old/'run.lua').read_text();tail=oldrun.split('\n',1)[1];assert tail.count((old/'fixture.lua').as_posix())==1;tail=tail.replace((old/'fixture.lua').as_posix(),(out/'fixture.lua').as_posix());(out/'run.lua').write_text('CURRENT_CHIP_DALE='+lua(cfg)+'\nassert(CURRENT_CHIP_DALE.menu==13)\n'+tail,encoding='utf-8',newline='\n')
 cmd=json.loads((old/'command.json').read_text());cmd['argv']=[str(out/'native')if x==str(old/'native')else str(out/'run.lua')if x==str(old/'run.lua')else x for x in cmd['argv']];put(out/'command.json',cmd)
 proof=dict(passed=True,native_run=False,old_unrun_ready_preserved=True,old_ready_sha256=sha(old/'prepared-not-run.json'),cause='Raw character14 was mistaken for menu index14. Actual compiled table index13 resolvesChip14, index14 resolvesLittleMac15. Original v1 not launched.',exact_lua_delta={'from':needle,'to':'if i~=C.menu then'},all_other_gameplay_controller_setup_guards_caps_sourceproof_bytes_unchanged=True,source_GameLoop_proof_reused_unchanged=True,menu_index=13,actual_character=14,nineteen_compiled_BFS_and_actual_resolver_cases=routes,negative_wrong_index14_resolves15=True,source_food_wording_correction='Mushroom2->3 means one missingHP. Flower1->3 means two missingHP. Original Lua/source assertions already exact.')
 put(out/'menu-source-controls.json',proof)
 paths=[Path(x['path'])for x in ready['bindings']]+[old/'prepared-not-run.json',Path(__file__)]+[out/n for n in['config.json','fixture.lua','run.lua','command.json','menu-source-controls.json']];paths=list(dict.fromkeys(paths));ready.update(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,menu_index=13,menu_index_correction=proof,bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in paths]);put(out/'prepared-not-run.json',ready)
 print(json.dumps(dict(prepared=True,native_run=False,identity=a.identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths))))
if __name__=='__main__':main()
