"""Read-only classification of actual H Simon source-consumed jump receipts."""
from pathlib import Path
import collections,hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=R/'build/roster-through-2-2/root49-h-simon-gn-5-v0-mmc3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
events=[json.loads(s)for s in(D/'simon-accepted-native.jsonl').read_text().splitlines()]
counts=collections.Counter();details=[];unknown=[];last=None
for z in events:
 if z['event']=='FreshInput':last=z;continue
 if z['event']!='AcceptedLaunch':continue
 assert last and last['cycle']<z['cycle'] and last['x']==z['x']and last['y']==z['y']and last['state']==z['state']
 assert z['AB']&128 and not z['previousAB']&128 and z['raw']&128
 owner=None;kind=None
 if z['state']!=0:
  assert last['airAvailable']==1 and z['airAvailable']==0
  kind='actual_source_available_secondary_air_jump'
 elif z['yHigh']==1 and z['y']%16==0 and any(t>0 and t not in [0x23,0x26,0xc2,0xc3]for t in [z['footL'],z['footR']]):kind='actual_native_terrain_top'
 else:
  for a in z['actors']:
   width=48 if a[8]in [5,6]else 32
   if a[1]and 36<=a[2]<=43 and a[7]==a[0]and a[6]==z['yHigh']==1 and z['y']+32==a[5]and z['x']+13>=a[4]and z['x']+2<a[4]+width:
    kind='actual_native_platform_owner';owner=a;break
  if kind is None:
   for a in z['actors']:
    if a[1]and a[2]==50 and 0<z['spring']<5 and a[6]==z['yHigh']==1 and z['y']+32==a[5]and z['x']+13>=a[4]and z['x']+2<a[4]+16:
     kind='actual_native_compressed_spring';owner=a;break
 if kind is None:unknown.append(z);kind='UNCLASSIFIED'
 counts[kind]+=1;details.append(dict(frame=z['frame'],cycle=z['cycle'],x=z['x'],y=z['y'],yHigh=z['yHigh'],state=z['state'],kind=kind,owner=owner,input_frame=last['frame'],input_cycle=last['cycle'],before_available=last['airAvailable'],accepted_available=z['airAvailable']))
out=V/'root49-simon-h-support-go.json';assert not out.exists()
out.write_text(json.dumps(dict(status='PASS_ACTUAL_SOURCE_JUMPS_CLASSIFIED'if not unknown else'RETAINED_SOURCE_SUPPORT_CLASSIFICATION_PENDING',input_file_sha256=sha(D/'simon-accepted-native.jsonl'),script_sha256=sha(__file__),counts=counts,details=details,unknown=unknown,secondary_above_viewport=sum(z['kind']=='actual_source_available_secondary_air_jump'and z['yHigh']==0 for z in details),scope='Exact accepted native source launch paired with its actual prior fresh input. Source secondary jump consumes a real available bit even after walking off; does not require ground or highY1. Grounded terrain/platform/spring support checked separately. No whole source/glitchless or final media claim.'),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(counts=counts,unknown=unknown,sha256=sha(out))))
