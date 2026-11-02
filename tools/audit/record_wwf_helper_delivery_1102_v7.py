"""Record actual Downloads verification and compact native evidence."""
import json,zipfile,hashlib
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    result=json.loads((O/'downloads-helper/capture/result.json').read_text())
    binding=json.loads((O/'downloads-helper/capture/binding.json').read_text())
    delivery=json.loads((O/'delivery.json').read_text())
    assert result['passed'] and binding['exit_code']==0
    assert sha(delivery['destination'])==binding['ROM_sha256']==delivery['ROM_sha256']
    delivery['downloads_launch_verified']=True
    delivery['downloads_result']={k:v for k,v in result.items() if k!='trace'}
    (O/'delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
    note=R/'docs/qa/continuation-current.json';q=json.loads(note.read_text())
    q['installed_nightly']=delivery
    q['wwf_helper_delivery_1102']=dict(qualified=['Hulk Hogan','Ted DiBiase','Bam Bam Bigelow','Honky Tonk Man','Randy Savage'],remaining='Andre loses a life at X1194 before helper; all-roster/powerup qualification incomplete.',stage='1-1',initial_center_x=1400,initial_left_x=1376,initial_y=208,width=48,actor=40)
    note.write_text(json.dumps(q,indent=2)+'\n')
    files=[O/'delivery.json']
    for name in ['native-hogan3',*[f'native-wwf-{i}' for i in range(1,6)],'native-andre2','native-karnov-regression','downloads-helper']:
        p=O/name
        files.extend(x for x in p.rglob('*') if x.is_file() and x.suffix in ['.json','.lua','.png','.csv'])
    archive=O/'native-roster-delivery-v7.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(set(files)):z.write(p,p.relative_to(R).as_posix())
    print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,SHA256=sha(archive),native_files=len(set(files)),installed=delivery['ROM_sha256'])))
if __name__=='__main__':main()
