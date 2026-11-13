# Prince raised-hand block reach: native validation

Private candidate `3b7990bc59b490a1c5e488133a7c65d05526944d63b7e987f0b3f44df733343d`
was composed from the installed `cebb0ae6` nightly using
`prince_pickup_reach_1112.transform`. It has not been installed or published.

Actual controller-only Mesen replay:
`replay_prince_first_pickup_1112.py --reach-candidate --runout-x 390 --face-right --hold-updates 80 --observe-updates 100`.
Use the bounded runner with output `build/prince-first-pickup-1112`.

The real native head query returned question tile C1 at X342/Y173,
upward speed FB, action14/pose78 and lowY13. The native powerup actor appeared.
At frame1976 Prince retained HP5 and both lives. This establishes emergence,
not collection or complete powerup progression.

- Receipt: `a2d9588ce46ceb195eab502bbd27a52cd78eb916e63fa0f6037dc630bb8c86cf`.
- Controller: `e2aa77ad73bc5eaebe43a83279e47dfc5a36e93260faf36adea6fb35fa2ae849`.
- No captures, videos or emulated-state writes.

The helper extends the pose78 head-query height while keeping the ordinary
native center-X convention; it is not a pixel-accurate hand collision mask.
The larger450-byte loader also needs compatible extraction/reversal support
before delivery.

## Full-stage regression

The same candidate passed the physical Mesen route through1-1, the native
flagpole and castle, into active1-2 at frame16374. Both lives remained; terminal
HP5 reflects the next-stage reset, not a damage-free route (HP2 at the flag).
No added helper platforms or controller RAM writes.

- Replay: `replay_prince_native_flag_1111.py --brake 3115 --adaptive-retreat`,
  candidate cookie `a72602ef59ee4b58b224fe37a78747a9`.
- Receipt: `7e0c5e0b240534db58fd7085ae1157205128bc16333c98ccd60b9120b73a442b`.
- Controller: `9ca6e81186d62096b7d818fd14986dd23c435bc2fabb70d9261fe3e1c15d1037`.

The first-item replay and full-stage replay are separate runs; this does not
establish natural collection of every powerup in a single full-stage run.

## Natural mushroom collection

The first-item replay with `--collect` also passed. Kind0 emerged at X336,
advanced through rising states1..17 to mature state80, walked right and fell
into Prince. Native item flag cleared and status became1 at frame2159,
X417/Y176, HP5/lives2/sword0. Receipt
`18c9539b5e514daefee470a677e9cdd95f45578f256aac2cbb41bac25f33c1db`,
controller `700a13aa79ea500b86cdbfb139b56f3fd35a635f9196b2849bd0846650a7c6f9`.
An initial controller-only failure inserted a trace into the wrong callback;
the anchored replacement was corrected before this passing run.

Root independently reran the full CPU/interrupt audit: receipt
`880febb14a36b53d4bb5d1ecf03a76218bf03171d5a02a5284dbedc6e3e854e6`.
Both loader formats round-trip; reverse reconstructs the exact parentcebb ROM.
193 changed-cold forced-blank NMI cuts and15IRQ/15lag-NMI head-query cuts pass.

User additionally requested sword drawing and use. Flower acquisition, drawing,
attack and sheathing checks are now required before this candidate's delivery.
No Downloads overwrite or Current release update has occurred yet.

## Sword acquisition route in progress

`--flower` joins the successful mushroom acquisition to the existing native
four-pipe route, then tries the block at X1248. Current baseline reaches it,
but HP5→4 at X846/Y177 after the third-pipe jump also loses native power status.
Consequently the block produces kind0 (another mushroom), not a flower.
Receipt `5a5c5da7d1b0a49e93807f2efbfe33f0a58f1998c252eb3ea3cc289f729304ce`;
controller `137381376487caf7db7ff1fc634c924c1bf2d8e8216b7342b71e715297e9de63`.
This is not a flower-reward failure. A changed third-pipe enemy-wait threshold
of800 instead of848 is prepared but untested; storage preflight stopped it.

Both root-owned private candidates (Prince3b7990 and Metal1595c7f) were removed
after exact hash checks to free file slots. Their source transforms reconstruct
them; do not assume the old build paths remain populated. Downloads stayscebb.
The Prince helper is separately checking whether source opponent import's
box3-only admission prevents real Goomba box9 from triggering sword draw.

Further route diagnosis confirms original fall damage: live HP write at A291,
frame4251/X844/Y176, action20/pose106, fall counterC6C6=3, HP5→4 and returnA2C7.
Receipt `71144165f1c7d1e0662fc7160ec3afe7354c192661345159cda5a4660614b629`.
The trace also captured two cold-initialization writes; the observer is now
restricted to active engine8. Changing walker timing to800 still incurred the
same fall loss and later died; simply walking off instead encountered a Goomba
at X804. Both experiments were controller changes only and are reverted.
The natural sword route needs a safe original descent, not a fall-damage bypass.

`--descent 4` (Down) crouches on the cap at X758/Y112 without damage; it does
not descend (receipt59175396). `--descent 5` (Down+Right) walks off and lands
with fall counter0, but contacts a Goomba at X804. Current A345 debits all five
HP through the unarmed defender, with successive returns AB5C/5F/62/65/68.
Receipt `419539227df5df1013e742770aa97b33b52a2e50b417d676ef7f9f6e7df33b9f`.
This distinguishes a safe-height descent from a safe enemy-crossing route;
the latter remains unresolved. The optional descent replay retains both probes.

### Sword candidate regression

The composed reach/sword candidate
`a0dc025be05d1a9e697bb47f1affaea9d33f70be3d7fbee240b520e433f12327`
passed a fresh controller-only Mesen first-mushroom collection at frame2160,
X417/Y176, HP5 and both lives. Receipt:
`50413ea06514f78e09061467af402e33273140882822120995cfeb72bdb31b4c`;
controller SHA256:
`e823ac3e7f8c12250641f45cc19c135b9e66259aa0c6420907459b8c81787f9a`.
No captures or emulated-state writes were used. This proves pickup regression
only, not a naturally earned sword demonstration or the full-stage route.

Root also independently composed the menu-facing patch over that candidate:
`c5ce8c1557f6eb27c97f1fb1b0404c7854f59feb18717f27171d7dcb890efbbd`.
All445 menu edit bytes matched their exact preimages; reversing sword and
reach recovered the installedcebb parent exactly. This check wrote no ROM.
The sword support publication observer must useD746, not the previousD74B.
Neither private candidate has been installed in Downloads or published.

The combinedc5ce8c candidate then passed the actual controller-only full1-1
route and entered active underground1-2 at frame16379 with both lives.
Receipt `60479ff4e2bda39d132807db13310ba272cf68d5eebbb6f98a21ddd75d21491f`;
controller `018f23db7dd7a1482c10f861db2f3c3ad546417cbdc189e56e0c1c98bdefd65e`.
The route used theD746 observer, brake3115 and adaptive retreat. No added
helpers, captures or state writes. TerminalHP5 is the next-stage reset;
this is not a no-injury claim or proof of sword combat. Existing external
Mesen sessions were left untouched. The combined candidate is retained only
at `build/prince-first-pickup-1112/candidate.nes` pending remaining gates.

Prepared delivery recipe: `tools/audit/deliver_prince_menu_1112.py`, using
`compose_prince_menu_1112.py`. Root verified exact forward/reverse composition,
matching native controller bytes and in-memory IPS reconstruction. Proposed
IPS SHA256 `fd0c11b7745c1a3e4f62d46272b0540316d5ab2861667bd65749050f131357a4`,
2,099,506 bytes. Installation and release publication have not been run;
the pending sword regression gates remain mandatory before either action.
