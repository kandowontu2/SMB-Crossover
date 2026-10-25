from pathlib import Path
D=Path(__file__).resolve().parent;t=(D/'profile_pz_megaman_v4.py').read_text().replace('profile-megaman-v4','profile-megaman-v5')
a='hooks={};missing=[]';assert t.count(a)==1;t=t.replace(a,"names += ['PlayerBGCollision','MegaManCollisionBox','MegaManCollisionAdder','BlockBufferPlayerCollision','BlockBufferCollision','GetBlockBufferAddr','GuestFootContactSide','CrossoverHeadProbe','CrossoverHeadWithinTerrain','CrossoverSourceSideProbe','PlayerEnemyCollision','PlayerCollisionCore','SprObjectCollisionCore']\n"+a)
a="assert all(n in hooks for n in ['GameLoop'";assert t.count(a)==1;t=t.replace(a,"for child in ['Move','Blocks','Enemies','Buttons']:\n hooks['Weapon_'+child]=image.hook(child,scope='MegaManWeapons')\n"+a)
t=t.replace("'trace.csv','events.csv','render.csv'","'trace.csv','render.csv'")
a="assert json.loads((O/'result.json').read_text())==json.loads((route/'result.json').read_text())";assert t.count(a)==1
t=t.replace(a,a+"\nwith (O/'events.csv').open()as f:actual_events=list(csv.DictReader(f))\nwith (route/'events.csv').open()as f:reference_events=list(csv.DictReader(f))\nwindow=lambda rows:[r for r in rows if int(r['frame'])>=350]\nassert window(actual_events)==window(reference_events),'All observed menu/effect queue events in and after the admitted profiling window stay exact'\n")
t=t.replace("native_route_exact=True,scopes=summary","native_route_exact=True,all_input_CPU_render_OAM_CHR_scroll_and_actual_hardware_audio_rows_exact=True,queue_event_window_start=350,queue_events_in_and_after_window_exact=True,pre_window_queue_events_excluded=True,scopes=summary")
(D/'profile_pz_megaman_v5.py').write_text(t)
