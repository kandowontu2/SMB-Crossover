"""Freeze exact recorded Darkwing hang/deep-foot cause; no emulator launch."""
from pathlib import Path
import csv,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    old=ROOT/'build/verification/compact-bdf9-darkwing-reserve-v2';new=ROOT/'build/verification/compact-bdf9-darkwing-reserve-position-v1'
    r=json.loads((new/'prepared-not-run.json').read_text());assert all(sha(Path(p))==h for p,h in r['bindings'].items())
    launch=json.loads((new/'launch.json').read_text());assert launch['exit_code']==1 and not launch['changed_inputs']and launch['settings_before']==launch['settings_after']
    result=json.loads((new/'result.json').read_text());assert not result['passed']and result['frames']==1873 and result['reason']=='Completed native world/camera step bound'
    same={}
    for n in ['trace.csv','inputs.csv','events.jsonl','darkwing-resources.csv','captures.nesppuv1','captures-index.jsonl']:
        assert(old/n).read_bytes()==(new/n).read_bytes(),n;same[n]=dict(bytes=(new/n).stat().st_size,sha256=sha(new/n))
    rows=list(csv.DictReader((new/'darkwing-position-writes.csv').open(newline='')))
    xs=[q for q in rows if q['event']=='Player_X_Position'and q['old']=='209'and q['value']=='223'];assert len(xs)==1;x=xs[0]
    assert(x['bank'],x['pc'],x['cycle'],x['R0_R7'])==('10','41709','55730272','2:84:176:84:6:222:13:3')
    ys=[q for q in rows if q['event']=='Player_Y_Position'and q['frame']==x['frame']and q['bank']=='67'and q['value']=='182'];assert len(ys)==1;y=ys[0]
    assert y['old']=='176'and y['hang']=='136'and y['scEnemy']=='0'and '8:6:0:740:183:1:191:1:4:728:185:168:255'in y['arrows']
    base=ROOT/'build/cv3-life-watch-bdf9-production.nes';current=ROOT/'build/kirby-mike-polish-production.nes';a,b=scoped_load(base),scoped_load(current)
    spans={}
    for n in ['DwHangUpdate','DwValidateArrow','DwArrowActor','DwScroogePhysics','RosterGuestFootContactSide','SamusStopAtWallBanked','PlayerBGCollision','GuestFootContactSide']:
        count=int(a['syms'][n]['size'],0)if'size'in a['syms'][n]else address(a,'AreaChangeTimerData')-address(a,n)
        newcount=int(b['syms'][n]['size'],0)if'size'in b['syms'][n]else address(b,'AreaChangeTimerData')-address(b,n)
        assert address(a,n)==address(b,n)and count==newcount and a['raw'][location(a,n):location(a,n)+count]==b['raw'][location(b,n):location(b,n)+count]
        spans[n]=dict(pc=address(a,n),bytes=count,sha256=hashlib.sha256(a['raw'][location(a,n):location(a,n)+count]).hexdigest())
    # Mesen's memory-write callback PC is after this two-byte ZP STA.
    for row,n in [(x,'Player_X_Position'),(y,'Player_Y_Position')]:
        pc=int(row['pc'])-2;bank=int(row['bank']);at=16+bank*8192+pc%8192
        assert a['raw'][at:at+2]==bytes([0x85,address(a,n)])
    z=dict(native_aggregate_passed=False,diagnostic_observation_passed=True,original_FALSEs_preserved=True,ROM_sha256=result['ROM_sha256'],current_source_parent_sha256=sha(current),
        launch=dict(path=str(new/'launch.json'),sha256=sha(new/'launch.json'),exit_code=1,settings_unchanged=True,changed_inputs=[]),
        all_original_payloads_byteexact=same,position_rows=len(rows),first_forced_Y=y,horizontal_correction=x,
        actual_writer=dict(reported_callback_PC='10:A2ED',actual_STA_PC='10:A2EB',owner='SamusStopAtWallBanked::LeftClamp',world_before=721,world_after=735,camera_before_after=[610,610],deep_foot=dict(left=84,right=84,low_nibble=6,selected_side=2),source_caller_return='Stack contains9D22, the return after StopPlayerMove JSR SamusStopAtWall at126:9D20.'),
        first_cause=dict(reported_callback_PC='67:A564',actual_STA_PC='67:A562',owner='DwHangUpdate::Freeze',player_Y_before=176,player_Y_after=182,derived_from_actual_actor_Y=185,hang=136,slot=8,shot_type=6,SsMode=1,actor_slot=4,actor_state=168,terrain_release_bit=128),
        classification='Actual hanging ignores the validated falling Arrow actor terrain-release bit, pulls body into solid terrain, then genuine deep-foot resolver clamps horizontally. Globalwall guard retained; no14pxvelocity claim.',
        exact_current_owner_spans=spans,
        bindings={str(p):sha(p)for p in [Path(__file__).resolve(),new/'prepared-not-run.json',new/'launch.json',new/'result.json',new/'darkwing-position-writes.csv',base,base.with_suffix('.dbg'),current,current.with_suffix('.dbg')]})
    out=ROOT/'build/current-bdf9-darkwing-position-cause-v1.json';assert not out.exists();out.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(path=str(out),sha256=sha(out),original_native_FALSE=True,diagnostic_observation_PASS=True,rows=len(rows))))

if __name__=='__main__':main()
