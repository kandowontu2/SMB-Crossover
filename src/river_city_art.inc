; Generated from authenticated native RCR player renderer/patterns; see recipe.
.pushseg
.segment "RIVER_CITY_ART"
RcArtStart:
RcV0StandR:
 .byte 28
 .byte 0,0,0,254
 .byte 2,0,0,6
 .byte 4,64,0,14
 .byte 6,64,16,254
 .byte 8,2,16,254
 .byte 10,64,16,6
 .byte 12,66,16,6
RcV0Walk1R:
 .byte 28
 .byte 0,0,255,254
 .byte 2,0,255,6
 .byte 4,64,255,14
 .byte 14,64,15,254
 .byte 16,2,15,254
 .byte 18,64,15,6
 .byte 20,66,15,6
RcV0Walk2R:
 .byte 32
 .byte 0,0,255,254
 .byte 2,0,255,6
 .byte 4,64,255,14
 .byte 22,64,15,254
 .byte 24,2,15,254
 .byte 26,64,15,6
 .byte 28,66,15,6
 .byte 30,64,15,14
RcV0RunR:
 .byte 36
 .byte 32,0,255,253
 .byte 34,0,255,5
 .byte 36,64,255,13
 .byte 38,64,15,253
 .byte 40,2,15,253
 .byte 42,64,15,5
 .byte 44,2,15,5
 .byte 46,64,15,13
 .byte 48,66,15,13
RcV0JumpR:
 .byte 28
 .byte 0,0,1,254
 .byte 2,0,1,6
 .byte 4,64,1,14
 .byte 50,64,17,254
 .byte 52,2,17,254
 .byte 54,64,17,6
 .byte 56,2,17,6
RcV0CrouchR:
 .byte 32
 .byte 58,0,8,251
 .byte 60,0,8,3
 .byte 62,64,8,11
 .byte 64,0,24,251
 .byte 66,64,24,3
 .byte 68,66,24,3
 .byte 70,64,24,11
 .byte 72,66,24,11
RcV0HurtR:
 .byte 20
 .byte 58,0,7,251
 .byte 74,0,7,3
 .byte 62,64,7,11
 .byte 64,0,23,251
 .byte 76,64,23,11
RcV0DownR:
 .byte 20
 .byte 78,0,16,239
 .byte 80,64,16,247
 .byte 82,0,16,255
 .byte 84,2,16,255
 .byte 86,66,16,7
RcV0Punch1R:
 .byte 28
 .byte 88,0,0,250
 .byte 90,0,0,2
 .byte 92,64,0,10
 .byte 94,2,16,250
 .byte 96,2,16,2
 .byte 98,64,16,10
 .byte 100,66,16,10
RcV0Punch2R:
 .byte 28
 .byte 102,0,0,254
 .byte 104,0,0,6
 .byte 106,64,0,14
 .byte 108,2,16,254
 .byte 110,64,16,6
 .byte 28,66,16,6
 .byte 112,64,16,14
RcV0Punch3R:
 .byte 28
 .byte 114,0,0,255
 .byte 116,0,0,7
 .byte 118,64,0,15
 .byte 120,2,16,255
 .byte 122,0,16,7
 .byte 124,66,16,7
 .byte 126,64,16,15
RcV0Kick1R:
 .byte 28
 .byte 128,0,2,0
 .byte 130,64,2,8
 .byte 132,66,2,8
 .byte 134,0,18,0
 .byte 136,2,18,0
 .byte 138,64,18,8
 .byte 140,66,18,8
RcV0Kick2R:
 .byte 40
 .byte 128,0,2,2
 .byte 142,64,2,10
 .byte 144,2,2,10
 .byte 146,64,2,18
 .byte 144,66,2,18
 .byte 134,0,18,2
 .byte 136,2,18,2
 .byte 148,64,18,10
 .byte 150,2,18,10
 .byte 152,64,18,18
RcV0Kick3R:
 .byte 40
 .byte 128,0,2,5
 .byte 154,64,2,13
 .byte 156,0,2,21
 .byte 158,66,2,21
 .byte 134,0,18,5
 .byte 136,2,18,5
 .byte 148,64,18,13
 .byte 150,2,18,13
 .byte 160,0,18,21
 .byte 162,66,18,21
RcV0RunKickR:
 .byte 44
 .byte 164,0,0,248
 .byte 166,0,0,0
 .byte 168,64,0,8
 .byte 170,0,16,248
 .byte 172,2,16,248
 .byte 174,64,16,0
 .byte 176,66,16,0
 .byte 178,0,16,8
 .byte 180,2,16,8
 .byte 182,64,16,16
 .byte 184,66,16,16
RcV0CarryR:
 .byte 32
 .byte 186,0,0,250
 .byte 188,0,0,2
 .byte 190,64,0,10
 .byte 192,2,16,250
 .byte 194,64,16,2
 .byte 196,66,16,2
 .byte 198,64,16,10
 .byte 200,66,16,10
RcV0ThrowR:
 .byte 28
 .byte 114,0,0,255
 .byte 116,0,0,7
 .byte 202,64,0,15
 .byte 120,2,16,255
 .byte 122,0,16,7
 .byte 124,66,16,7
 .byte 204,64,16,15
RcV0AirKickR:
 .byte 40
 .byte 206,0,0,249
 .byte 208,64,0,1
 .byte 210,64,0,9
 .byte 212,64,16,249
 .byte 214,2,16,249
 .byte 216,0,16,1
 .byte 218,2,16,1
 .byte 220,64,16,9
 .byte 222,66,16,9
 .byte 224,64,16,17
RcV0StandL:
 .byte 28
 .byte 0,64,0,9
 .byte 2,64,0,1
 .byte 4,0,0,249
 .byte 6,0,16,9
 .byte 8,66,16,9
 .byte 10,0,16,1
 .byte 12,2,16,1
RcV0Walk1L:
 .byte 28
 .byte 0,64,255,9
 .byte 2,64,255,1
 .byte 4,0,255,249
 .byte 14,0,15,9
 .byte 16,66,15,9
 .byte 18,0,15,1
 .byte 20,2,15,1
RcV0Walk2L:
 .byte 32
 .byte 0,64,255,9
 .byte 2,64,255,1
 .byte 4,0,255,249
 .byte 22,0,15,9
 .byte 24,66,15,9
 .byte 26,0,15,1
 .byte 28,2,15,1
 .byte 30,0,15,249
RcV0RunL:
 .byte 36
 .byte 32,64,255,10
 .byte 34,64,255,2
 .byte 36,0,255,250
 .byte 38,0,15,10
 .byte 40,66,15,10
 .byte 42,0,15,2
 .byte 44,66,15,2
 .byte 46,0,15,250
 .byte 48,2,15,250
RcV0JumpL:
 .byte 28
 .byte 0,64,1,9
 .byte 2,64,1,1
 .byte 4,0,1,249
 .byte 50,0,17,9
 .byte 52,66,17,9
 .byte 54,0,17,1
 .byte 56,66,17,1
RcV0CrouchL:
 .byte 32
 .byte 58,64,8,12
 .byte 60,64,8,4
 .byte 62,0,8,252
 .byte 64,64,24,12
 .byte 66,0,24,4
 .byte 68,2,24,4
 .byte 70,0,24,252
 .byte 72,2,24,252
RcV0HurtL:
 .byte 20
 .byte 58,64,7,12
 .byte 74,64,7,4
 .byte 62,0,7,252
 .byte 64,64,23,12
 .byte 76,0,23,252
RcV0DownL:
 .byte 20
 .byte 78,64,16,24
 .byte 80,0,16,16
 .byte 82,64,16,8
 .byte 84,66,16,8
 .byte 86,2,16,0
RcV0Punch1L:
 .byte 28
 .byte 88,64,0,13
 .byte 90,64,0,5
 .byte 92,0,0,253
 .byte 94,66,16,13
 .byte 96,66,16,5
 .byte 98,0,16,253
 .byte 100,2,16,253
RcV0Punch2L:
 .byte 28
 .byte 102,64,0,9
 .byte 104,64,0,1
 .byte 106,0,0,249
 .byte 108,66,16,9
 .byte 110,0,16,1
 .byte 28,2,16,1
 .byte 112,0,16,249
RcV0Punch3L:
 .byte 28
 .byte 114,64,0,8
 .byte 116,64,0,0
 .byte 118,0,0,248
 .byte 120,66,16,8
 .byte 122,64,16,0
 .byte 124,2,16,0
 .byte 126,0,16,248
RcV0Kick1L:
 .byte 28
 .byte 128,64,2,7
 .byte 130,0,2,255
 .byte 132,2,2,255
 .byte 134,64,18,7
 .byte 136,66,18,7
 .byte 138,0,18,255
 .byte 140,2,18,255
RcV0Kick2L:
 .byte 40
 .byte 128,64,2,5
 .byte 142,0,2,253
 .byte 144,66,2,253
 .byte 146,0,2,245
 .byte 144,2,2,245
 .byte 134,64,18,5
 .byte 136,66,18,5
 .byte 148,0,18,253
 .byte 150,66,18,253
 .byte 152,0,18,245
RcV0Kick3L:
 .byte 40
 .byte 128,64,2,2
 .byte 154,0,2,250
 .byte 156,64,2,242
 .byte 158,2,2,242
 .byte 134,64,18,2
 .byte 136,66,18,2
 .byte 148,0,18,250
 .byte 150,66,18,250
 .byte 160,64,18,242
 .byte 162,2,18,242
RcV0RunKickL:
 .byte 44
 .byte 164,64,0,15
 .byte 166,64,0,7
 .byte 168,0,0,255
 .byte 170,64,16,15
 .byte 172,66,16,15
 .byte 174,0,16,7
 .byte 176,2,16,7
 .byte 178,64,16,255
 .byte 180,66,16,255
 .byte 182,0,16,247
 .byte 184,2,16,247
RcV0CarryL:
 .byte 32
 .byte 186,64,0,13
 .byte 188,64,0,5
 .byte 190,0,0,253
 .byte 192,66,16,13
 .byte 194,0,16,5
 .byte 196,2,16,5
 .byte 198,0,16,253
 .byte 200,2,16,253
RcV0ThrowL:
 .byte 28
 .byte 114,64,0,8
 .byte 116,64,0,0
 .byte 202,0,0,248
 .byte 120,66,16,8
 .byte 122,64,16,0
 .byte 124,2,16,0
 .byte 204,0,16,248
RcV0AirKickL:
 .byte 40
 .byte 206,64,0,14
 .byte 208,0,0,6
 .byte 210,0,0,254
 .byte 212,0,16,14
 .byte 214,66,16,14
 .byte 216,64,16,6
 .byte 218,66,16,6
 .byte 220,0,16,254
 .byte 222,2,16,254
 .byte 224,0,16,246
RcV0PoseRLo:
 .byte <RcV0StandR,<RcV0Walk1R,<RcV0Walk2R,<RcV0RunR,<RcV0JumpR,<RcV0CrouchR,<RcV0HurtR,<RcV0DownR,<RcV0Punch1R,<RcV0Punch2R,<RcV0Punch3R,<RcV0Kick1R,<RcV0Kick2R,<RcV0Kick3R,<RcV0RunKickR,<RcV0CarryR,<RcV0ThrowR,<RcV0AirKickR
RcV0PoseRHi:
 .byte >RcV0StandR,>RcV0Walk1R,>RcV0Walk2R,>RcV0RunR,>RcV0JumpR,>RcV0CrouchR,>RcV0HurtR,>RcV0DownR,>RcV0Punch1R,>RcV0Punch2R,>RcV0Punch3R,>RcV0Kick1R,>RcV0Kick2R,>RcV0Kick3R,>RcV0RunKickR,>RcV0CarryR,>RcV0ThrowR,>RcV0AirKickR
RcV0PoseLLo:
 .byte <RcV0StandL,<RcV0Walk1L,<RcV0Walk2L,<RcV0RunL,<RcV0JumpL,<RcV0CrouchL,<RcV0HurtL,<RcV0DownL,<RcV0Punch1L,<RcV0Punch2L,<RcV0Punch3L,<RcV0Kick1L,<RcV0Kick2L,<RcV0Kick3L,<RcV0RunKickL,<RcV0CarryL,<RcV0ThrowL,<RcV0AirKickL
RcV0PoseLHi:
 .byte >RcV0StandL,>RcV0Walk1L,>RcV0Walk2L,>RcV0RunL,>RcV0JumpL,>RcV0CrouchL,>RcV0HurtL,>RcV0DownL,>RcV0Punch1L,>RcV0Punch2L,>RcV0Punch3L,>RcV0Kick1L,>RcV0Kick2L,>RcV0Kick3L,>RcV0RunKickL,>RcV0CarryL,>RcV0ThrowL,>RcV0AirKickL
RcV1StandR:
 .byte 32
 .byte 0,0,0,254
 .byte 2,2,0,254
 .byte 4,64,0,6
 .byte 6,2,0,6
 .byte 8,64,0,14
 .byte 10,64,16,254
 .byte 12,64,16,6
 .byte 14,66,16,6
RcV1Walk1R:
 .byte 32
 .byte 0,0,255,254
 .byte 2,2,255,254
 .byte 4,64,255,6
 .byte 6,2,255,6
 .byte 8,64,255,14
 .byte 16,64,15,254
 .byte 18,64,15,6
 .byte 14,66,15,6
RcV1Walk2R:
 .byte 36
 .byte 0,0,255,254
 .byte 2,2,255,254
 .byte 4,64,255,6
 .byte 6,2,255,6
 .byte 8,64,255,14
 .byte 20,64,15,254
 .byte 22,64,15,6
 .byte 14,66,15,6
 .byte 24,64,15,14
RcV1RunR:
 .byte 40
 .byte 26,0,255,253
 .byte 28,2,255,253
 .byte 30,64,255,5
 .byte 32,2,255,5
 .byte 34,64,255,13
 .byte 36,66,255,13
 .byte 38,64,15,253
 .byte 40,64,15,5
 .byte 42,66,15,5
 .byte 44,64,15,13
RcV1JumpR:
 .byte 28
 .byte 0,0,1,254
 .byte 2,2,1,254
 .byte 4,64,1,6
 .byte 6,2,1,6
 .byte 8,64,1,14
 .byte 46,64,17,254
 .byte 48,64,17,6
RcV1CrouchR:
 .byte 36
 .byte 50,0,8,251
 .byte 52,2,8,251
 .byte 54,64,8,3
 .byte 56,66,8,3
 .byte 58,64,8,11
 .byte 60,66,8,11
 .byte 62,0,24,251
 .byte 64,64,24,3
 .byte 66,64,24,11
RcV1HurtR:
 .byte 32
 .byte 50,0,7,251
 .byte 52,2,7,251
 .byte 68,64,7,3
 .byte 58,64,7,11
 .byte 60,66,7,11
 .byte 62,0,23,251
 .byte 70,64,23,11
 .byte 72,66,23,11
RcV1DownR:
 .byte 20
 .byte 74,0,16,239
 .byte 76,64,16,247
 .byte 78,2,16,247
 .byte 80,0,16,255
 .byte 82,64,16,7
RcV1Punch1R:
 .byte 36
 .byte 84,0,0,250
 .byte 86,0,0,2
 .byte 88,2,0,2
 .byte 90,64,0,10
 .byte 92,66,0,10
 .byte 94,2,16,250
 .byte 96,66,16,2
 .byte 98,64,16,10
 .byte 100,66,16,10
RcV1Punch2R:
 .byte 32
 .byte 102,0,0,254
 .byte 104,64,0,6
 .byte 36,2,0,6
 .byte 106,64,0,14
 .byte 108,2,16,254
 .byte 110,0,16,6
 .byte 112,66,16,6
 .byte 114,64,16,14
RcV1Punch3R:
 .byte 36
 .byte 116,0,0,255
 .byte 118,2,0,255
 .byte 120,64,0,7
 .byte 122,66,0,7
 .byte 124,64,0,15
 .byte 126,66,16,255
 .byte 128,0,16,7
 .byte 130,66,16,7
 .byte 132,64,16,15
RcV1Kick1R:
 .byte 28
 .byte 134,0,2,0
 .byte 136,2,2,0
 .byte 138,64,2,8
 .byte 140,66,2,8
 .byte 142,0,18,0
 .byte 144,66,18,0
 .byte 146,64,18,8
RcV1Kick2R:
 .byte 36
 .byte 134,0,2,2
 .byte 136,2,2,2
 .byte 148,64,2,10
 .byte 140,66,2,10
 .byte 150,64,2,18
 .byte 142,0,18,2
 .byte 144,66,18,2
 .byte 152,0,18,10
 .byte 154,64,18,18
RcV1Kick3R:
 .byte 36
 .byte 134,0,2,5
 .byte 136,2,2,5
 .byte 156,64,2,13
 .byte 140,66,2,13
 .byte 158,64,2,21
 .byte 142,0,18,5
 .byte 144,66,18,5
 .byte 152,0,18,13
 .byte 160,64,18,21
RcV1RunKickR:
 .byte 40
 .byte 162,0,0,248
 .byte 164,2,0,248
 .byte 166,0,0,0
 .byte 168,66,0,0
 .byte 170,64,0,8
 .byte 172,66,0,8
 .byte 174,0,16,248
 .byte 176,64,16,0
 .byte 178,0,16,8
 .byte 180,64,16,16
RcV1CarryR:
 .byte 44
 .byte 182,0,0,250
 .byte 184,66,0,250
 .byte 186,64,0,2
 .byte 188,66,0,2
 .byte 190,64,0,10
 .byte 192,66,0,10
 .byte 194,66,16,250
 .byte 196,0,16,2
 .byte 198,66,16,2
 .byte 200,64,16,10
 .byte 202,66,16,10
RcV1ThrowR:
 .byte 36
 .byte 116,0,0,255
 .byte 118,2,0,255
 .byte 120,64,0,7
 .byte 122,66,0,7
 .byte 204,64,0,15
 .byte 126,66,16,255
 .byte 128,0,16,7
 .byte 130,66,16,7
 .byte 206,64,16,15
RcV1AirKickR:
 .byte 36
 .byte 208,0,0,249
 .byte 210,66,0,249
 .byte 212,64,0,1
 .byte 214,2,0,1
 .byte 216,64,0,9
 .byte 218,64,16,249
 .byte 220,0,16,1
 .byte 222,64,16,9
 .byte 224,64,16,17
RcV1StandL:
 .byte 32
 .byte 0,64,0,9
 .byte 2,66,0,9
 .byte 4,0,0,1
 .byte 6,66,0,1
 .byte 8,0,0,249
 .byte 10,0,16,9
 .byte 12,0,16,1
 .byte 14,2,16,1
RcV1Walk1L:
 .byte 32
 .byte 0,64,255,9
 .byte 2,66,255,9
 .byte 4,0,255,1
 .byte 6,66,255,1
 .byte 8,0,255,249
 .byte 16,0,15,9
 .byte 18,0,15,1
 .byte 14,2,15,1
RcV1Walk2L:
 .byte 36
 .byte 0,64,255,9
 .byte 2,66,255,9
 .byte 4,0,255,1
 .byte 6,66,255,1
 .byte 8,0,255,249
 .byte 20,0,15,9
 .byte 22,0,15,1
 .byte 14,2,15,1
 .byte 24,0,15,249
RcV1RunL:
 .byte 40
 .byte 26,64,255,10
 .byte 28,66,255,10
 .byte 30,0,255,2
 .byte 32,66,255,2
 .byte 34,0,255,250
 .byte 36,2,255,250
 .byte 38,0,15,10
 .byte 40,0,15,2
 .byte 42,2,15,2
 .byte 44,0,15,250
RcV1JumpL:
 .byte 28
 .byte 0,64,1,9
 .byte 2,66,1,9
 .byte 4,0,1,1
 .byte 6,66,1,1
 .byte 8,0,1,249
 .byte 46,0,17,9
 .byte 48,0,17,1
RcV1CrouchL:
 .byte 36
 .byte 50,64,8,12
 .byte 52,66,8,12
 .byte 54,0,8,4
 .byte 56,2,8,4
 .byte 58,0,8,252
 .byte 60,2,8,252
 .byte 62,64,24,12
 .byte 64,0,24,4
 .byte 66,0,24,252
RcV1HurtL:
 .byte 32
 .byte 50,64,7,12
 .byte 52,66,7,12
 .byte 68,0,7,4
 .byte 58,0,7,252
 .byte 60,2,7,252
 .byte 62,64,23,12
 .byte 70,0,23,252
 .byte 72,2,23,252
RcV1DownL:
 .byte 20
 .byte 74,64,16,24
 .byte 76,0,16,16
 .byte 78,66,16,16
 .byte 80,64,16,8
 .byte 82,0,16,0
RcV1Punch1L:
 .byte 36
 .byte 84,64,0,13
 .byte 86,64,0,5
 .byte 88,66,0,5
 .byte 90,0,0,253
 .byte 92,2,0,253
 .byte 94,66,16,13
 .byte 96,2,16,5
 .byte 98,0,16,253
 .byte 100,2,16,253
RcV1Punch2L:
 .byte 32
 .byte 102,64,0,9
 .byte 104,0,0,1
 .byte 36,66,0,1
 .byte 106,0,0,249
 .byte 108,66,16,9
 .byte 110,64,16,1
 .byte 112,2,16,1
 .byte 114,0,16,249
RcV1Punch3L:
 .byte 36
 .byte 116,64,0,8
 .byte 118,66,0,8
 .byte 120,0,0,0
 .byte 122,2,0,0
 .byte 124,0,0,248
 .byte 126,2,16,8
 .byte 128,64,16,0
 .byte 130,2,16,0
 .byte 132,0,16,248
RcV1Kick1L:
 .byte 28
 .byte 134,64,2,7
 .byte 136,66,2,7
 .byte 138,0,2,255
 .byte 140,2,2,255
 .byte 142,64,18,7
 .byte 144,2,18,7
 .byte 146,0,18,255
RcV1Kick2L:
 .byte 36
 .byte 134,64,2,5
 .byte 136,66,2,5
 .byte 148,0,2,253
 .byte 140,2,2,253
 .byte 150,0,2,245
 .byte 142,64,18,5
 .byte 144,2,18,5
 .byte 152,64,18,253
 .byte 154,0,18,245
RcV1Kick3L:
 .byte 36
 .byte 134,64,2,2
 .byte 136,66,2,2
 .byte 156,0,2,250
 .byte 140,2,2,250
 .byte 158,0,2,242
 .byte 142,64,18,2
 .byte 144,2,18,2
 .byte 152,64,18,250
 .byte 160,0,18,242
RcV1RunKickL:
 .byte 40
 .byte 162,64,0,15
 .byte 164,66,0,15
 .byte 166,64,0,7
 .byte 168,2,0,7
 .byte 170,0,0,255
 .byte 172,2,0,255
 .byte 174,64,16,15
 .byte 176,0,16,7
 .byte 178,64,16,255
 .byte 180,0,16,247
RcV1CarryL:
 .byte 44
 .byte 182,64,0,13
 .byte 184,2,0,13
 .byte 186,0,0,5
 .byte 188,2,0,5
 .byte 190,0,0,253
 .byte 192,2,0,253
 .byte 194,2,16,13
 .byte 196,64,16,5
 .byte 198,2,16,5
 .byte 200,0,16,253
 .byte 202,2,16,253
RcV1ThrowL:
 .byte 36
 .byte 116,64,0,8
 .byte 118,66,0,8
 .byte 120,0,0,0
 .byte 122,2,0,0
 .byte 204,0,0,248
 .byte 126,2,16,8
 .byte 128,64,16,0
 .byte 130,2,16,0
 .byte 206,0,16,248
RcV1AirKickL:
 .byte 36
 .byte 208,64,0,14
 .byte 210,2,0,14
 .byte 212,0,0,6
 .byte 214,66,0,6
 .byte 216,0,0,254
 .byte 218,0,16,14
 .byte 220,64,16,6
 .byte 222,0,16,254
 .byte 224,0,16,246
RcV1PoseRLo:
 .byte <RcV1StandR,<RcV1Walk1R,<RcV1Walk2R,<RcV1RunR,<RcV1JumpR,<RcV1CrouchR,<RcV1HurtR,<RcV1DownR,<RcV1Punch1R,<RcV1Punch2R,<RcV1Punch3R,<RcV1Kick1R,<RcV1Kick2R,<RcV1Kick3R,<RcV1RunKickR,<RcV1CarryR,<RcV1ThrowR,<RcV1AirKickR
RcV1PoseRHi:
 .byte >RcV1StandR,>RcV1Walk1R,>RcV1Walk2R,>RcV1RunR,>RcV1JumpR,>RcV1CrouchR,>RcV1HurtR,>RcV1DownR,>RcV1Punch1R,>RcV1Punch2R,>RcV1Punch3R,>RcV1Kick1R,>RcV1Kick2R,>RcV1Kick3R,>RcV1RunKickR,>RcV1CarryR,>RcV1ThrowR,>RcV1AirKickR
RcV1PoseLLo:
 .byte <RcV1StandL,<RcV1Walk1L,<RcV1Walk2L,<RcV1RunL,<RcV1JumpL,<RcV1CrouchL,<RcV1HurtL,<RcV1DownL,<RcV1Punch1L,<RcV1Punch2L,<RcV1Punch3L,<RcV1Kick1L,<RcV1Kick2L,<RcV1Kick3L,<RcV1RunKickL,<RcV1CarryL,<RcV1ThrowL,<RcV1AirKickL
RcV1PoseLHi:
 .byte >RcV1StandL,>RcV1Walk1L,>RcV1Walk2L,>RcV1RunL,>RcV1JumpL,>RcV1CrouchL,>RcV1HurtL,>RcV1DownL,>RcV1Punch1L,>RcV1Punch2L,>RcV1Punch3L,>RcV1Kick1L,>RcV1Kick2L,>RcV1Kick3L,>RcV1RunKickL,>RcV1CarryL,>RcV1ThrowL,>RcV1AirKickL
.assert *-RcArtStart<=4096,error,"River City art allocation"
.popseg
