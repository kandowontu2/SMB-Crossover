"""Carry the delivered menu into the user's requested private86 WIP."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
O=R/'build/karnov-host-resource-base-1101-v1';M=R/'build/menu-wwf-compact-1101-v1'
sha=lambda b:hashlib.sha256(b).hexdigest()


def stripped(b,ranges):
    z=bytearray(b)
    for lo,hi in ranges:z[lo:hi]=bytes(hi-lo)
    return sha(z)


def main():
    path=O/'compact-carry-before.json'
    if path.exists():before=json.loads(path.read_text())
    else:
        b=scoped_load(O/'candidate.nes');assert sha(b['raw'])=='f1fadebcf755a5cff09f8857ed054ecff3897ed4e804e8e88e690a2669cc43ee'
        ranges=[(location(b,'DrawSelectionPreview'),location(b,'QueueVariantHint')),(location(b,'KrCookie'),location(b,'KrCookie')+16),(1048592+399*1024+8160,1048592+399*1024+8176)]
        before=dict(ROM_sha256=sha(b['raw']),ranges=ranges,outside_SHA256=stripped(b['raw'],ranges))
        path.write_text(json.dumps(before,indent=2)+'\n')
    subprocess.run([sys.executable,str(R/'tools/audit/build_karnov_gameplay_host_1101_v1.py'),'--render','--ingress','--scene','--menu','--compact-menu'],check=True,cwd=R)
    b=scoped_load(O/'candidate.nes');m=scoped_load(M/'candidate.nes');assert stripped(b['raw'],before['ranges'])==before['outside_SHA256'],'Beyond menu+authentication changed'
    lo,hi=before['ranges'][0];assert b['raw'][lo:hi]==m['raw'][lo:hi]
    q=dict(passed=True,ROM_sha256=sha(b['raw']),previous_private=before['ROM_sha256'],menu_parent=sha(m['raw']),allowed_changed_ranges=before['ranges'],all_other_private_ROM_bytes_exact=True,delivered_compact_menu_exact=True,selectable=86,existing_verified_playable=85,user_requested_WIP=True,complete_character=False,limits='Same Karnov opening component; injury/death/pickups/rebound/combat/audio still incomplete. User explicitly requests access to the current WIP.')
    (O/'compact-carry-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
