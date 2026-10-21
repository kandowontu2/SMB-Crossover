"""Verify the later actual beam defeats, pipe jump, and current-F water entry."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-current-f-samus-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
    with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
    out=V/'root49-samus-f-later-review-bg.json';assert not out.exists()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json';c=json.loads(cp.read_text())
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    packets={};traces={};actors={}
    for tag in ['q','r','s','t']:
        p=R/f'build/roster-through-2-2/root49-f-samus-route-{tag}-2-v0-mmc3';m=json.loads((p/'manifest.json').read_text());r=json.loads((H/f'native-result-{tag}.json').read_text())
        assert sha(p/'manifest.json')==r['manifest_sha256']and sha(H/f'native-{tag}.log')==r['host_log_sha256']
        assert m['controller_only']and m['full_frame_audit']and not m['memory_or_register_writes']and not m['config']['record']
        assert m['config']['character']==2 and m['config']['mapper']=='mmc3'and m['rom_sha256']==sha(p/'smb-crossover-mmc3.nes')=='ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'
        assert json.loads((p/'current-c-identity.json').read_text())==dict(character=2,behavior=0,marioVariant=0,billVariant=0,outlinesOff=1)
        tr=rows(p/'trace.csv');traces[tag]=tr;actors[tag]=rows(p/'actual-injury-b.csv')
        packets[tag]=dict(result=m.get('result'),last_pose=tr[-1],files={f.name:dict(bytes=f.stat().st_size,sha256=sha(f))for f in p.iterdir()if f.is_file()},preparation_sha256=sha(H/f'preparation-{tag}.json'))
    prefixes=[]
    for a,b,count in [('q','r',25020),('r','s',25380),('s','t',26730)]:
        assert traces[a][:count]==traces[b][:count];prefixes.append(dict(parent=a,child=b,physical_rows=count))
    def defeat(tag,slot,start,x):
        z=next(z for z in actors[tag]if z['event']=='EndFrame'and z['slot']==str(slot)and int(z['frame'])>start and int(z['ex'])==x and int(z['estate'])&32)
        assert z['id']=='13';return z
    defeated=[defeat('q',2,24820,1848),defeat('r',3,25020,1960),defeat('s',0,25453,2088),defeat('t',4,26730,2824)]
    assert defeated[0]['frame']=='24915'and defeated[1]['frame']=='25275'
    p=R/'build/roster-through-2-2/root49-f-samus-route-s-2-v0-mmc3'
    jump=next(z for z in rows(p/'pipe-step-s.csv')if int(z['mask'])&128)
    assert jump['x']=='1937'and jump['y']=='176'and jump['state']=='0'and int(jump['previousAB'])&128==0
    assert int(jump['leftFoot'])or int(jump['rightFoot']);assert int(jump['front'])
    t=packets['t']['result'];assert t['all_six_stages']and not t['cleared']and t['stage_entries']['1-1']==28513 and t['frames']==29733 and t['failure']=='death'
    fatal=next(z for z in actors['t']if z['event']=='InjurePlayer'and z['slot']==z['owner']and z['frame']=='29733')
    assert fatal['id']=='10'and fatal['slot']=='1'and fatal['ex']=='1229'and fatal['ey']=='72'
    transitions=[];old=None
    for z in traces['t']:
        if z['power']!=old:transitions.append({k:z[k]for k in ['frame','world','level','x','y','power','engine']});old=z['power']
    components=V/'root49-current-f-samus-components-bd';review=components/'review.json';assert sha(review)=='d4e84bc213e5b327ae833559eda5b0d0e1afb9ee22e20fe9d0b97c75df2047e3'
    cr=json.loads(review.read_text());prep=json.loads((components/'preparation.json').read_text());assert sha(components/'preparation.json')==cr['preparation_sha256']
    for n,h in prep['dependencies'].items():assert sha(R/n)==h,n
    for g in cr['groups']:
        assert g['exit']==0
        assert sha(components/f"{g['mapper']}-{g['fixture']}-host.log")==g['host_log_sha256']
        for n,info in g['files'].items():assert sha(components/n)==info['sha256']and(components/n).stat().st_size==info['bytes']
    result=dict(status='PASS_ROOT_SAMUS_F_FIVE_CLEARED_STAGES_WATER_ENTRY_AND_COMPONENTS',script_sha256=sha(__file__),checkpoint_sha256=sha(cp),packets=packets,
      literal_prefixes=prefixes,actual_plant_defeats=defeated,actual_supported_pipe_jump=jump,natural_route_power_transitions=transitions,water_death_actual_owner=fatal,
      component_review_sha256=sha(review),components_rehashed=len(cr['groups']),component_scopes=cr['assertion_scopes'],
      retained_controller_negatives=['R pose-reference guard at1937/Y176 after third plant defeat; resolved by ordinary supported S jump.',
        'S later stationary combat2748..2750 versus2824 is outside starting-beam reach: zero target damage in899 polls; T uses demonstrated56px range and defeats target.',
        'Q and T are actual game deaths; R/S are controller-bound stops. All raw failures/preparations retained.'],
      limits=['T reaches all six stages but has not cleared2-2. This is not a full route, arsenal, audiovisual/source-perfect geometry or final recording.',
        'Seeded component fixture scopes remain distinct from the ordinary Easy route. Historical73 suite failures have not been reclassified as passing.'],
      goal_complete=False,production_ROM_changed=False)
    out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],sha(out),[(z['frame'],z['ex'])for z in defeated],flush=True)
if __name__=='__main__':main()
