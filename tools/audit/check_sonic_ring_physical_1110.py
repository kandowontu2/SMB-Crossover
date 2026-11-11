"""Replay ring damage and the full Sonic route in the shared Mesen queue."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from run_stdout_mesen_1110 import R, run


RING = R / 'tools/playthroughs/sonic_ring_feedback_stdout_1110_v3.lua'
PIN = '36e9a6a8b2f8dfb79447c8d9e74633245dd412ede0a408d075e3df2db01b85ca'
STAGE = R / 'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
STAGE_PIN = '2c2ee3f821affcff8c8748a35918fd7c9531760332a3e6d0b5d392f4154fa4ee'
POWER = R / 'tools/playthroughs/sonic_earned_injury_stdout_1110_v2.lua'
POWER_PIN = 'a6e1dc5caf708a6d7fbe21bc7d7d18207061befc5e9bb1972bedb2e7125b182c'
OLD_COOKIE = b'a72b01c0f80210577f684adf9ea78ed5'
RING_COOKIE = b'a72b018c2e04635376b3ef263b330c8f'
CANDIDATE = R / 'build/sonic-ring-native-1110/candidate.nes'


def run_rings(rom, output, images=False):
    env = {'SMB_STDOUT_IMAGES': '1' if images else '0', 'SMB_SONIC_COOKIE': RING_COOKIE.decode()}
    return run(RING, rom, output, PIN, 200, extra_env=env)


def run_stage(rom, output):
    original = STAGE.read_bytes()
    assert sha256(original).hexdigest() == STAGE_PIN
    assert original.count(OLD_COOKIE) == 1
    return run_adapted(STAGE, original.replace(OLD_COOKIE, RING_COOKIE), rom, output)


def run_power(rom, output):
    return run_adapted(POWER, power_controller(PIN, RING_COOKIE).encode(), rom, output)


def power_controller(pin, cookie):
    original = POWER.read_bytes()
    assert sha256(original).hexdigest() == POWER_PIN
    script = original.decode('utf-8').replace('\r\n', '\n')
    former_pin = '49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7'
    former_cookie = 'a72b0194a989064ae62ef75a04986523'
    assert script.count(former_pin) == script.count(former_cookie) == 1
    script = script.replace(former_pin, pin).replace(former_cookie, cookie.decode())
    first = script.index(' if injury then\n')
    last = script.index(' local bits=0\n', first)
    script = script[:first] + ''' if injury then
  assert(#stores==0 and s.status==1 and s.engine==8 and s.timer==0 and s.injury_timer==0,
         'Original ring damage preserves the earned mushroom tier')
  if not injury.after then
   assert(source(0x340)==0 and source(0x34f)&0x40~=0 and source(0x35e)==0x55,
          'Authentic ring loss and thrown-ring record')
   assert(s.vx==-512 and s.vy==-1024,'Original ring knockback')
   injury.after=s
  elseif not recovered and source(0x34f)&0x40==0 then
   assert(s.source_flags&0x80~=0 and s.vx==0 and s.vy>=0,'Grounded ring stun release')
   recovered=s;phase='resume'
  end
  if recovered and s.x>=recovered.x+16 then
   requestedFinish={ok=true,why='Earned mushroom, original ring loss and tier-one recovery'}
   setPad(0);return
  end
 end
''' + script[last:]
    contact = "  injury={actor=enemy,player=player};queueImage('Sonic_powered_Goomba_contact')"
    assert script.count(contact) == 1
    script = script.replace(contact, "  assert(source(0x340)==5,'Five earned rings before powered contact')\n" + contact)
    return script


def run_adapted(source, content, rom, output):
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output) as directory:
        script = Path(directory) / source.name
        script.write_bytes(content)
        return run(script, rom, output, PIN, 240,
                   extra_env={'SMB_STDOUT_IMAGES': '0'})


def gameplay_digest(result):
    receipt = dict(result['receipt'])
    receipt.pop('image_tags', None)
    return sha256(json.dumps(receipt, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('route', choices=('rings', 'stage', 'mushroom'))
    parser.add_argument('--rom', type=Path, default=CANDIDATE)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--images', action='store_true')
    args = parser.parse_args()
    assert args.route == 'rings' or not args.images
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    if args.route == 'rings':
        result = run_rings(args.rom.resolve(), output, args.images)
    elif args.route == 'stage':
        result = run_stage(args.rom.resolve(), output)
    else:
        result = run_power(args.rom.resolve(), output)
    result['gameplay_SHA256'] = gameplay_digest(result)
    print(json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
