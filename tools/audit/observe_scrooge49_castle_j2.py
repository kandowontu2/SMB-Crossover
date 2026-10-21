"""Fresh current-P full-fixed I2 replay with rebound passive castle telemetry."""
from pathlib import Path
import csv,hashlib,importlib.util,json,re,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/root49p-scrooge-castle-observer-j2'
V=ROOT/'build/verification/mm49n-scrooge-castle-observer-v'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
OLD=ROOT/'build/roster-through-2-2/root49p-scrooge-phase-i2-12-v0-mmc3'
REF=ROOT/'build/verification/root49p-three-fixed-a/current-p-mmc3-reference.json'
U=ROOT/'build/verification/mm48-private-reference-runner-u/roster_run_reference.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    cat=json.loads((CP/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    old=json.loads((OLD/'manifest.json').read_text());assert old['result']['frames']==11484
    assert sha(OLD/'inputs.csv')==old['inputs_sha256']
    pins={p.relative_to(ROOT).as_posix():sha(p)for p in [V/'metadata.json',V/'observer.lua',OLD/'inputs.csv',OLD/'manifest.json',REF,U]}
    image_path=ROOT/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(image_path)=='54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec=importlib.util.spec_from_file_location('current_P_scoped_image',image_path)
    image=importlib.util.module_from_spec(spec);spec.loader.exec_module(image)
    im=image.Image(CP/'smb-crossover-mmc3.nes')
    c=json.loads((V/'metadata.json').read_text());c['rom']=im.metadata();c['ram']=im.ram
    c['hooks']={n:im.hook(h['label'],h.get('scope'),h['delta'])for n,h in c['hooks'].items()}
    for name,w in c['writers'].items():
        w['target']=im.ram[w['field']];h=c['hooks'][name];b=h['bytes']
        assert w['register']=='A' and b[0]in(0x85,0x8d)
        assert int.from_bytes(bytes(b[1:w['instructionBytes']]),'little')==w['target'],name
    c['watched']={n:im.ram[n]for n in c['watched']}
    for key,name in [('xAdders','BlockBuffer_X_Adder'),('yAdders','BlockBuffer_Y_Adder')]:
        h=im.hook(name);n=len(c[key]);c[key]=list(im.raw[h['rom_offset']:h['rom_offset']+n])
    guards=c['adder_guards']
    if isinstance(guards,dict):c['adder_guards']={n:im.hook(h['label'],h.get('scope'),h['delta'])for n,h in guards.items()}
    else:c['adder_guards']=[im.hook(h['label'],h.get('scope'),h['delta'])for h in guards]
    c['FirebarYPos_guard']=im.hook('FirebarYPos');assert c['FirebarYPos_guard']['bytes'][:2]==[12,24]
    h=c['hooks']['FirebarInjuryCall'];target=im.sym('InjurePlayer')['val']
    assert h['bytes'][:3]==[0x20,target&255,target>>8]
    c['firebar_injury_return']=h['address']+3
    text=(V/'observer.lua').read_text()
    oldwindow='x>=900 and x<=1100 and frame+1>=10450 and frame+1<=11300'
    assert text.count(oldwindow)==1
    text=text.replace(oldwindow,'x>=1296 and x<=1408 and frame+1>=11200 and frame+1<=11500')
    assert text.count('relative,firebars\\n')==1
    text=text.replace('relative,firebars\\n','relative,firebars,gridFirstX,gridFirstY,grid8x11hex\\n')
    marker=' local scrooge=table.concat('
    assert text.count(marker)==1
    text=text.replace(marker," local gx=(x//16-2)*16;local grid={}\n for gy=32,192,16 do for dx=0,112,16 do grid[#grid+1]=string.format('%02x',block(gx+dx,gy))end end\n"+marker)
    marker="table.concat(firebars,';')},',')"
    assert text.count(marker)==1
    text=text.replace(marker,"table.concat(firebars,';'),gx,32,table.concat(grid)},',')")
    assert not re.search(r'emu\.(?:write|setState|setInput|saveState|loadState)\s*\(',text)
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+575_000_000<50_000_000_000
    OUT.mkdir();(OUT/'metadata.json').write_text(json.dumps(c,indent=2)+'\n')
    (OUT/'metadata.lua').write_text('return '+image.lua(c)+'\n')
    bound=text.replace('@METADATA@',(OUT/'metadata.lua').as_posix())
    (OUT/'observer.lua').write_text(bound)
    (OUT/'policy.lua').write_text('return assert(dofile('+json.dumps((OUT/'observer.lua').as_posix())+'))\n')
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    good,error=LuaRuntime().eval("function(s)local f,e=load(s,'passive-castle-j','t');return f~=nil,e end")(bound)
    assert good,error
    command=[sys.executable,str(U),'--reference-descriptor',str(REF),'--reference-sha256',sha(REF),
             '--reference-reserve-bytes','75000000','--character','12','--mapper','mmc3','--policy',str(OUT/'policy.lua'),
             '--tag','root49p-scrooge-castle-observer-j2','--frames','11484','--timeout','300','--replay',str(OLD/'inputs.csv')]
    report=dict(status='RUNNING_FULL_FIXED_PASSIVE_J2',script_sha256=sha(Path(__file__)),input_pins=pins,command=command,
                metadata_sha256=sha(OUT/'metadata.json'),observer_sha256=sha(OUT/'observer.lua'),workspace_before=used,
                accepted_release=False,goal_complete=False,ordinary_controller_changes=0)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with (OUT/'native.log').open('wb')as f:p=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    run=ROOT/'build/roster-through-2-2/root49p-scrooge-castle-observer-j2-12-v0-mmc3'
    report.update(native_exit=p.returncode)
    comparisons={}
    for n in ['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']:
        comparisons[n]=dict(literal=(OLD/n).read_bytes()==(run/n).read_bytes(),old_sha256=sha(OLD/n),new_sha256=sha(run/n))
    report['nine_CSV_comparison']=comparisons
    if (run/'result.json').exists():report['result']=json.loads((run/'result.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in cat.items())and all(sha(ROOT/n)==h for n,h in pins.items())
    report.update(status='COMPLETE_FULL_FIXED_PASSIVE_J2_OUTCOME_RETAINED',workspace_after=workspace_bytes(ROOT),
                  qualification='Current-P physical/scoped hooks rebound; exact whole original I2 replay, no grants/prefix/tail, no CPU model or source edit. All original outcomes and observer failures retained. Actual source writer decisions require separate raw review.')
    save();print(json.dumps(dict(native_exit=p.returncode,all_nine_literal=all(v['literal']for v in comparisons.values()),report_sha256=sha(OUT/'report.json'))))

if __name__=='__main__':main()
