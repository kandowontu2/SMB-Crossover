"""Classify real H Ryu launch/drop receipts without promoting legacy geometry."""
from pathlib import Path
import collections,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=R/'build/roster-through-2-2/root49-h-ryu-gs-10-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
events=[json.loads(s)for s in(D/'ryu-accepted-native.jsonl').read_text().splitlines()]
counts=collections.Counter();details=[];unknown=[];fresh=None;used=set();wall=None
def tile(z,x,y):
 if y<32 or y>=240:return -1
 return bytes.fromhex(z['grid'])[(x//256)%2*208+((y-32)//16)*16+(x%256)//16]
for z in events:
 if z['event']=='FreshInput':fresh=z;wall=None;continue
 if z['event']=='WallAttempt':wall=z;continue
 if z['event']not in ['AcceptedLaunch','WallReturnNoJump']:continue
 assert fresh and fresh['cycle']<z['cycle']and fresh['x']==z['x']and fresh['y']==z['y']
 assert fresh['fresh']&128 and fresh['raw']&128 and not fresh['previous']&128
 kind=None;owner=None;qualifier=None
 if z['event']=='WallReturnNoJump':
  assert wall and wall['wall']and wall['raw']&4 and z['wall']==0 and z['wallLock']==15 and z['jumpUsed']==1
  kind='actual_source_down_A_wall_drop'
 elif fresh['wall']:
  assert wall and wall['wall']and z['wall']==0 and z['wallLock']in [12,15]and z['vy']in [0xFC6AAB,0xFD8000]
  if fresh['side']:
   assert fresh['side']==wall['side']==fresh['facing']
   assert fresh['supported']==1 and fresh['oldHeight']==25 and fresh['yHigh']==1
   edge=256*fresh['edgePage']+fresh['edge'];col=edge if fresh['side']==1 else edge-1
   rows=range(max(32,fresh['y']+7),min(239,fresh['y']+32)+1)
   touched=[dict(y=y,tile=tile(fresh,col,y))for y in rows if tile(fresh,col,y)>0]
   if touched:
    kind='actual_source_cached_terrain_wall_jump'
    qualifier='Live wall side, cached25px profile, current grid contact and source jump velocity/lock. Full old/current Q16/cache/corner fidelity remains separately qualified.'
   else:
    kind='actual_source_wall_jump_contact_review_pending';unknown.append(z)
  else:
   kind='actual_legacy_wall_fallback_jump'
   qualifier='Source explicitly retains unsupported retained-frame/attack wall fallback. Actual fresh input and existing XgWall prove native admission only; complete2.02 retained-shape geometry is not certified.'
 elif z['state']==0:
  foot=[tile(z,z['x']+2,z['y']+32),tile(z,z['x']+13,z['y']+32)]
  if z['yHigh']==1 and z['y']%16==0 and any(t>0 and t not in [0x23,0x26,0xc2,0xc3]for t in foot):kind='actual_native_terrain_top'
  else:
   for a in z['actors']:
    width=48 if a[8]in [5,6]else 32
    if a[1]and 36<=a[2]<=43 and a[7]==a[0]and a[6]==z['yHigh']==1 and z['y']+32==a[5]and z['x']+13>=a[4]and z['x']+2<a[4]+width:
     kind='actual_native_platform_owner';owner=a;break
   if kind is None:
    for a in z['actors']:
     if a[1]and a[2]==50 and 0<z['spring']<5 and a[6]==z['yHigh']==1 and z['y']+32==a[5]and z['x']+13>=a[4]and z['x']+2<a[4]+16:
      kind='actual_native_compressed_spring';owner=a;break
 if kind is None:kind='UNCLASSIFIED';unknown.append(z)
 counts[kind]+=1;used.add(fresh['cycle']);details.append(dict(frame=z['frame'],cycle=z['cycle'],kind=kind,input_cycle=fresh['cycle'],input_frame=fresh['frame'],x=z['x'],y=z['y'],yHigh=z['yHigh'],state=z['state'],wall_before=fresh['wall'],source_side_before=fresh['side'],owner=owner,qualifier=qualifier))
rejected=[z for z in events if z['event']=='FreshInput'and z['cycle']not in used]
out=V/'root49-ryu-h-support-gu.json';assert not out.exists()
receipt=dict(status='PASS_ACTUAL_SOURCE_ADMISSIONS_CLASSIFIED_WITH_EXPLICIT_LEGACY_LIMIT'if not unknown else'RETAINED_SOURCE_SUPPORT_CLASSIFICATION_PENDING',script_sha256=sha(__file__),input_file_sha256=sha(D/'ryu-accepted-native.jsonl'),counts=counts,details=details,unknown=unknown,rejected_fresh_inputs=rejected,limits=['Actual H source admission/terrain/native platforms/spring/wall/drop receipts only. Every accepted route input is paired; this does not close original source actor geometry, attack-cache, lifecycle or all-arsenal obligations.','Legacy wall fallback remains explicitly identified, never promoted to complete2.02 source geometry. Native platform-side attachment is not exercised by this route.','Above-viewport/corner/source exact current/previous Q16 shape needs dedicated review beyond contact proxies.'],goal_complete=False)
out.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(counts=counts,unknown=[{k:z[k]for k in ['frame','x','y','state']}for z in unknown],rejected=[{k:z[k]for k in ['frame','x','y','state','wall']}for z in rejected],sha256=sha(out))))
