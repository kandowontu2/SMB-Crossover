; Authenticated RCR pixels; palette2 belongs to world objects.
; Player palette0 visible colors=white30,skin26,blue11.
; Black is optional ink: palette3 visible color1 must be native0F.
.pushseg
.segment "RIVER_CITY_ART"
RcArtStart:
RcV0Body0R:
 .byte 16
 .byte 2,0,0,254
 .byte 4,64,0,6
 .byte 0,0,16,254
 .byte 6,64,16,6
RcV0Ink0R:
 .byte 20
 .byte 94,3,0,254
 .byte 100,3,0,6
 .byte 92,67,0,14
 .byte 96,67,16,254
 .byte 98,67,16,6
RcV0Body0L:
 .byte 16
 .byte 2,64,0,9
 .byte 4,0,0,1
 .byte 0,64,16,9
 .byte 6,0,16,1
RcV0Ink0L:
 .byte 20
 .byte 94,67,0,9
 .byte 100,67,0,1
 .byte 92,3,0,249
 .byte 96,3,16,9
 .byte 98,3,16,1
RcV0Body1R:
 .byte 16
 .byte 2,0,255,254
 .byte 4,64,255,6
 .byte 8,0,15,254
 .byte 10,64,15,6
RcV0Ink1R:
 .byte 20
 .byte 94,3,255,254
 .byte 100,3,255,6
 .byte 92,67,255,14
 .byte 102,67,15,254
 .byte 104,67,15,6
RcV0Body1L:
 .byte 16
 .byte 2,64,255,9
 .byte 4,0,255,1
 .byte 8,64,15,9
 .byte 10,0,15,1
RcV0Ink1L:
 .byte 20
 .byte 94,67,255,9
 .byte 100,67,255,1
 .byte 92,3,255,249
 .byte 102,3,15,9
 .byte 104,3,15,1
RcV0Body2R:
 .byte 16
 .byte 2,0,255,254
 .byte 4,64,255,6
 .byte 12,0,15,254
 .byte 14,64,15,6
RcV0Ink2R:
 .byte 24
 .byte 102,3,255,254
 .byte 108,3,255,6
 .byte 100,67,255,14
 .byte 104,67,15,254
 .byte 106,67,15,6
 .byte 98,67,15,14
RcV0Body2L:
 .byte 16
 .byte 2,64,255,9
 .byte 4,0,255,1
 .byte 12,64,15,9
 .byte 14,0,15,1
RcV0Ink2L:
 .byte 24
 .byte 102,67,255,9
 .byte 108,67,255,1
 .byte 100,3,255,249
 .byte 104,3,15,9
 .byte 106,3,15,1
 .byte 98,3,15,249
RcV0Body3R:
 .byte 24
 .byte 30,0,255,253
 .byte 36,64,255,5
 .byte 28,64,255,13
 .byte 34,0,15,253
 .byte 38,64,15,5
 .byte 32,64,15,13
RcV0Ink3R:
 .byte 24
 .byte 114,3,255,253
 .byte 120,3,255,5
 .byte 112,67,255,13
 .byte 116,67,15,253
 .byte 118,67,15,5
 .byte 110,67,15,13
RcV0Body3L:
 .byte 24
 .byte 30,64,255,10
 .byte 36,0,255,2
 .byte 28,0,255,250
 .byte 34,64,15,10
 .byte 38,0,15,2
 .byte 32,0,15,250
RcV0Ink3L:
 .byte 24
 .byte 114,67,255,10
 .byte 120,67,255,2
 .byte 112,3,255,250
 .byte 116,3,15,10
 .byte 118,3,15,2
 .byte 110,3,15,250
RcV0Body4R:
 .byte 16
 .byte 2,0,1,254
 .byte 4,64,1,6
 .byte 18,0,17,254
 .byte 16,0,17,6
RcV0Ink4R:
 .byte 20
 .byte 94,3,1,254
 .byte 100,3,1,6
 .byte 92,67,1,14
 .byte 106,67,17,254
 .byte 108,67,17,6
RcV0Body4L:
 .byte 16
 .byte 2,64,1,9
 .byte 4,0,1,1
 .byte 18,64,17,9
 .byte 16,64,17,1
RcV0Ink4L:
 .byte 20
 .byte 94,67,1,9
 .byte 100,67,1,1
 .byte 92,3,1,249
 .byte 106,3,17,9
 .byte 108,3,17,1
RcV0Body5R:
 .byte 24
 .byte 40,0,8,251
 .byte 46,64,8,3
 .byte 44,64,8,11
 .byte 42,64,24,251
 .byte 50,64,24,3
 .byte 48,64,24,11
RcV0Ink5R:
 .byte 24
 .byte 64,3,8,251
 .byte 74,3,8,3
 .byte 66,67,8,11
 .byte 72,3,24,251
 .byte 70,67,24,3
 .byte 68,67,24,11
RcV0Body5L:
 .byte 24
 .byte 40,64,8,12
 .byte 46,0,8,4
 .byte 44,0,8,252
 .byte 42,0,24,12
 .byte 50,0,24,4
 .byte 48,0,24,252
RcV0Ink5L:
 .byte 24
 .byte 64,67,8,12
 .byte 74,67,8,4
 .byte 66,3,8,252
 .byte 72,67,24,12
 .byte 70,3,24,4
 .byte 68,3,24,252
RcV0Body6R:
 .byte 20
 .byte 24,0,7,251
 .byte 30,64,7,3
 .byte 28,64,7,11
 .byte 26,64,23,251
 .byte 32,64,23,11
RcV0Ink6R:
 .byte 20
 .byte 110,3,7,251
 .byte 118,3,7,3
 .byte 112,67,7,11
 .byte 116,3,23,251
 .byte 114,67,23,11
RcV0Body6L:
 .byte 20
 .byte 24,64,7,12
 .byte 30,0,7,4
 .byte 28,0,7,252
 .byte 26,0,23,12
 .byte 32,0,23,252
RcV0Ink6L:
 .byte 20
 .byte 110,67,7,12
 .byte 118,67,7,4
 .byte 112,3,7,252
 .byte 116,67,23,12
 .byte 114,3,23,252
RcV0Body7R:
 .byte 16
 .byte 20,0,16,239
 .byte 22,0,16,247
 .byte 24,0,16,255
 .byte 26,64,16,7
RcV0Ink7R:
 .byte 16
 .byte 80,3,16,239
 .byte 78,67,16,247
 .byte 74,3,16,255
 .byte 76,67,16,7
RcV0Body7L:
 .byte 16
 .byte 20,64,16,24
 .byte 22,64,16,16
 .byte 24,64,16,8
 .byte 26,0,16,0
RcV0Ink7L:
 .byte 16
 .byte 80,67,16,24
 .byte 78,3,16,16
 .byte 74,67,16,8
 .byte 76,3,16,0
RcV0Body8R:
 .byte 24
 .byte 52,0,0,250
 .byte 56,0,0,2
 .byte 54,64,0,10
 .byte 60,0,16,250
 .byte 62,0,16,2
 .byte 58,64,16,10
RcV0Ink8R:
 .byte 24
 .byte 76,3,0,250
 .byte 86,3,0,2
 .byte 84,67,0,10
 .byte 80,3,16,250
 .byte 82,67,16,2
 .byte 78,67,16,10
RcV0Body8L:
 .byte 24
 .byte 52,64,0,13
 .byte 56,64,0,5
 .byte 54,0,0,253
 .byte 60,64,16,13
 .byte 62,64,16,5
 .byte 58,0,16,253
RcV0Ink8L:
 .byte 24
 .byte 76,67,0,13
 .byte 86,67,0,5
 .byte 84,3,0,253
 .byte 80,67,16,13
 .byte 82,3,16,5
 .byte 78,3,16,253
RcV0Body9R:
 .byte 20
 .byte 34,0,0,254
 .byte 38,64,0,6
 .byte 40,0,16,254
 .byte 42,64,16,6
 .byte 36,64,16,14
RcV0Ink9R:
 .byte 24
 .byte 92,3,0,254
 .byte 98,3,0,6
 .byte 90,67,0,14
 .byte 96,3,16,254
 .byte 94,3,16,6
 .byte 88,67,16,14
RcV0Body9L:
 .byte 20
 .byte 34,64,0,9
 .byte 38,0,0,1
 .byte 40,64,16,9
 .byte 42,0,16,1
 .byte 36,0,16,249
RcV0Ink9L:
 .byte 24
 .byte 92,67,0,9
 .byte 98,67,0,1
 .byte 90,3,0,249
 .byte 96,67,16,9
 .byte 94,67,16,1
 .byte 88,3,16,249
RcV0Body10R:
 .byte 20
 .byte 46,0,0,255
 .byte 48,64,0,7
 .byte 44,64,0,15
 .byte 52,0,16,255
 .byte 50,64,16,7
RcV0Ink10R:
 .byte 24
 .byte 102,3,0,255
 .byte 110,3,0,7
 .byte 100,67,0,15
 .byte 104,67,16,255
 .byte 108,3,16,7
 .byte 106,67,16,15
RcV0Body10L:
 .byte 20
 .byte 46,64,0,8
 .byte 48,0,0,0
 .byte 44,0,0,248
 .byte 52,64,16,8
 .byte 50,0,16,0
RcV0Ink10L:
 .byte 24
 .byte 102,67,0,8
 .byte 110,67,0,0
 .byte 100,3,0,248
 .byte 104,3,16,8
 .byte 108,67,16,0
 .byte 106,3,16,248
RcV0Body11R:
 .byte 16
 .byte 28,0,2,0
 .byte 30,64,2,8
 .byte 34,64,18,0
 .byte 32,64,18,8
RcV0Ink11R:
 .byte 16
 .byte 84,3,2,0
 .byte 82,67,2,8
 .byte 88,3,18,0
 .byte 86,67,18,8
RcV0Body11L:
 .byte 16
 .byte 28,64,2,7
 .byte 30,0,2,255
 .byte 34,0,18,7
 .byte 32,0,18,255
RcV0Ink11L:
 .byte 16
 .byte 84,67,2,7
 .byte 82,3,2,255
 .byte 88,67,18,7
 .byte 86,3,18,255
RcV0Body12R:
 .byte 24
 .byte 4,0,2,2
 .byte 6,64,2,10
 .byte 0,64,2,18
 .byte 10,64,18,2
 .byte 8,0,18,10
 .byte 2,64,18,18
RcV0Ink12R:
 .byte 24
 .byte 118,3,2,2
 .byte 116,67,2,10
 .byte 112,67,2,18
 .byte 122,3,18,2
 .byte 120,67,18,10
 .byte 114,67,18,18
RcV0Body12L:
 .byte 24
 .byte 4,64,2,5
 .byte 6,0,2,253
 .byte 0,0,2,245
 .byte 10,0,18,5
 .byte 8,64,18,253
 .byte 2,0,18,245
RcV0Ink12L:
 .byte 24
 .byte 118,67,2,5
 .byte 116,3,2,253
 .byte 112,3,2,245
 .byte 122,67,18,5
 .byte 120,3,18,253
 .byte 114,3,18,245
RcV0Body13R:
 .byte 24
 .byte 4,0,2,5
 .byte 14,64,2,13
 .byte 12,64,2,21
 .byte 10,64,18,5
 .byte 8,0,18,13
 .byte 16,64,18,21
RcV0Ink13R:
 .byte 24
 .byte 70,3,2,5
 .byte 68,67,2,13
 .byte 64,3,2,21
 .byte 74,3,18,5
 .byte 72,67,18,13
 .byte 66,3,18,21
RcV0Body13L:
 .byte 24
 .byte 4,64,2,2
 .byte 14,0,2,250
 .byte 12,0,2,242
 .byte 10,0,18,2
 .byte 8,64,18,250
 .byte 16,0,18,242
RcV0Ink13L:
 .byte 24
 .byte 70,67,2,2
 .byte 68,3,2,250
 .byte 64,67,2,242
 .byte 74,67,18,2
 .byte 72,3,18,250
 .byte 66,67,18,242
RcV0Body14R:
 .byte 28
 .byte 0,0,0,248
 .byte 4,64,0,0
 .byte 2,64,0,8
 .byte 10,0,16,248
 .byte 12,64,16,0
 .byte 8,0,16,8
 .byte 6,64,16,16
RcV0Ink14R:
 .byte 28
 .byte 66,3,0,248
 .byte 76,3,0,0
 .byte 68,67,0,8
 .byte 74,3,16,248
 .byte 72,67,16,0
 .byte 70,3,16,8
 .byte 64,67,16,16
RcV0Body14L:
 .byte 28
 .byte 0,64,0,15
 .byte 4,0,0,7
 .byte 2,0,0,255
 .byte 10,64,16,15
 .byte 12,0,16,7
 .byte 8,64,16,255
 .byte 6,0,16,247
RcV0Ink14L:
 .byte 28
 .byte 66,67,0,15
 .byte 76,67,0,7
 .byte 68,3,0,255
 .byte 74,67,16,15
 .byte 72,3,16,7
 .byte 70,67,16,255
 .byte 64,3,16,247
RcV0Body15R:
 .byte 24
 .byte 18,0,0,250
 .byte 22,64,0,2
 .byte 20,64,0,10
 .byte 26,0,16,250
 .byte 28,64,16,2
 .byte 24,64,16,10
RcV0Ink15R:
 .byte 24
 .byte 84,3,0,250
 .byte 86,3,0,2
 .byte 80,67,0,10
 .byte 82,67,16,250
 .byte 78,3,16,2
 .byte 76,67,16,10
RcV0Body15L:
 .byte 24
 .byte 18,64,0,13
 .byte 22,0,0,5
 .byte 20,0,0,253
 .byte 26,64,16,13
 .byte 28,0,16,5
 .byte 24,0,16,253
RcV0Ink15L:
 .byte 24
 .byte 84,67,0,13
 .byte 86,67,0,5
 .byte 80,3,0,253
 .byte 82,3,16,13
 .byte 78,67,16,5
 .byte 76,3,16,253
RcV0Body16R:
 .byte 24
 .byte 32,0,0,255
 .byte 36,64,0,7
 .byte 30,64,0,15
 .byte 40,0,16,255
 .byte 38,64,16,7
 .byte 34,0,16,15
RcV0Ink16R:
 .byte 24
 .byte 102,3,0,255
 .byte 110,3,0,7
 .byte 124,67,0,15
 .byte 104,67,16,255
 .byte 108,3,16,7
 .byte 126,67,16,15
RcV0Body16L:
 .byte 24
 .byte 32,64,0,8
 .byte 36,0,0,0
 .byte 30,0,0,248
 .byte 40,64,16,8
 .byte 38,0,16,0
 .byte 34,64,16,248
RcV0Ink16L:
 .byte 24
 .byte 102,67,0,8
 .byte 110,67,0,0
 .byte 124,3,0,248
 .byte 104,3,16,8
 .byte 108,67,16,0
 .byte 126,3,16,248
RcV0Body17R:
 .byte 24
 .byte 46,0,0,249
 .byte 48,64,0,1
 .byte 42,64,0,9
 .byte 44,0,16,249
 .byte 50,0,16,1
 .byte 52,64,16,9
RcV0Ink17R:
 .byte 28
 .byte 90,3,0,249
 .byte 86,67,0,1
 .byte 78,67,0,9
 .byte 84,67,16,249
 .byte 88,3,16,1
 .byte 82,67,16,9
 .byte 80,67,16,17
RcV0Body17L:
 .byte 24
 .byte 46,64,0,14
 .byte 48,0,0,6
 .byte 42,0,0,254
 .byte 44,64,16,14
 .byte 50,64,16,6
 .byte 52,0,16,254
RcV0Ink17L:
 .byte 28
 .byte 90,67,0,14
 .byte 86,3,0,6
 .byte 78,3,0,254
 .byte 84,3,16,14
 .byte 88,67,16,6
 .byte 82,3,16,254
 .byte 80,3,16,246
RcV1Body0R:
 .byte 16
 .byte 38,0,0,254
 .byte 40,0,0,6
 .byte 36,0,16,254
 .byte 42,64,16,6
RcV1Ink0R:
 .byte 20
 .byte 122,3,0,254
 .byte 124,67,0,6
 .byte 120,67,0,14
 .byte 96,67,16,254
 .byte 98,67,16,6
RcV1Body0L:
 .byte 16
 .byte 38,64,0,9
 .byte 40,64,0,1
 .byte 36,64,16,9
 .byte 42,0,16,1
RcV1Ink0L:
 .byte 20
 .byte 122,67,0,9
 .byte 124,3,0,1
 .byte 120,3,0,249
 .byte 96,3,16,9
 .byte 98,3,16,1
RcV1Body1R:
 .byte 16
 .byte 38,0,255,254
 .byte 40,0,255,6
 .byte 44,0,15,254
 .byte 46,64,15,6
RcV1Ink1R:
 .byte 20
 .byte 122,3,255,254
 .byte 124,67,255,6
 .byte 120,67,255,14
 .byte 102,67,15,254
 .byte 104,67,15,6
RcV1Body1L:
 .byte 16
 .byte 38,64,255,9
 .byte 40,64,255,1
 .byte 44,64,15,9
 .byte 46,0,15,1
RcV1Ink1L:
 .byte 20
 .byte 122,67,255,9
 .byte 124,3,255,1
 .byte 120,3,255,249
 .byte 102,3,15,9
 .byte 104,3,15,1
RcV1Body2R:
 .byte 16
 .byte 38,0,255,254
 .byte 40,0,255,6
 .byte 48,0,15,254
 .byte 50,64,15,6
RcV1Ink2R:
 .byte 24
 .byte 124,3,255,254
 .byte 126,67,255,6
 .byte 122,67,255,14
 .byte 104,67,15,254
 .byte 106,67,15,6
 .byte 98,67,15,14
RcV1Body2L:
 .byte 16
 .byte 38,64,255,9
 .byte 40,64,255,1
 .byte 48,64,15,9
 .byte 50,0,15,1
RcV1Ink2L:
 .byte 24
 .byte 124,67,255,9
 .byte 126,3,255,1
 .byte 122,3,255,249
 .byte 104,3,15,9
 .byte 106,3,15,1
 .byte 98,3,15,249
RcV1Body3R:
 .byte 24
 .byte 2,0,255,253
 .byte 8,0,255,5
 .byte 0,64,255,13
 .byte 6,0,15,253
 .byte 10,64,15,5
 .byte 4,64,15,13
RcV1Ink3R:
 .byte 24
 .byte 92,3,255,253
 .byte 98,67,255,5
 .byte 90,67,255,13
 .byte 94,67,15,253
 .byte 96,67,15,5
 .byte 88,67,15,13
RcV1Body3L:
 .byte 24
 .byte 2,64,255,10
 .byte 8,64,255,2
 .byte 0,0,255,250
 .byte 6,64,15,10
 .byte 10,0,15,2
 .byte 4,0,15,250
RcV1Ink3L:
 .byte 24
 .byte 92,67,255,10
 .byte 98,3,255,2
 .byte 90,3,255,250
 .byte 94,3,15,10
 .byte 96,3,15,2
 .byte 88,3,15,250
RcV1Body4R:
 .byte 16
 .byte 38,0,1,254
 .byte 40,0,1,6
 .byte 54,0,17,254
 .byte 52,0,17,6
RcV1Ink4R:
 .byte 20
 .byte 122,3,1,254
 .byte 124,67,1,6
 .byte 120,67,1,14
 .byte 106,67,17,254
 .byte 108,67,17,6
RcV1Body4L:
 .byte 16
 .byte 38,64,1,9
 .byte 40,64,1,1
 .byte 54,64,17,9
 .byte 52,64,17,1
RcV1Ink4L:
 .byte 20
 .byte 122,67,1,9
 .byte 124,3,1,1
 .byte 120,3,1,249
 .byte 106,3,17,9
 .byte 108,3,17,1
RcV1Body5R:
 .byte 24
 .byte 12,0,8,251
 .byte 16,64,8,3
 .byte 20,64,8,11
 .byte 14,64,24,251
 .byte 22,64,24,3
 .byte 18,64,24,11
RcV1Ink5R:
 .byte 24
 .byte 100,3,8,251
 .byte 110,67,8,3
 .byte 102,67,8,11
 .byte 108,3,24,251
 .byte 106,67,24,3
 .byte 104,67,24,11
RcV1Body5L:
 .byte 24
 .byte 12,64,8,12
 .byte 16,0,8,4
 .byte 20,0,8,252
 .byte 14,0,24,12
 .byte 22,0,24,4
 .byte 18,0,24,252
RcV1Ink5L:
 .byte 24
 .byte 100,67,8,12
 .byte 110,3,8,4
 .byte 102,3,8,252
 .byte 108,67,24,12
 .byte 106,3,24,4
 .byte 104,3,24,252
RcV1Body6R:
 .byte 20
 .byte 12,0,7,251
 .byte 60,64,7,3
 .byte 20,64,7,11
 .byte 14,64,23,251
 .byte 62,64,23,11
RcV1Ink6R:
 .byte 20
 .byte 64,3,7,251
 .byte 72,67,7,3
 .byte 66,67,7,11
 .byte 70,3,23,251
 .byte 68,67,23,11
RcV1Body6L:
 .byte 20
 .byte 12,64,7,12
 .byte 60,0,7,4
 .byte 20,0,7,252
 .byte 14,0,23,12
 .byte 62,0,23,252
RcV1Ink6L:
 .byte 20
 .byte 64,67,7,12
 .byte 72,3,7,4
 .byte 66,3,7,252
 .byte 70,67,23,12
 .byte 68,3,23,252
RcV1Body7R:
 .byte 16
 .byte 58,64,16,239
 .byte 56,0,16,247
 .byte 60,0,16,255
 .byte 62,64,16,7
RcV1Ink7R:
 .byte 16
 .byte 90,3,16,239
 .byte 78,67,16,247
 .byte 74,3,16,255
 .byte 76,67,16,7
RcV1Body7L:
 .byte 16
 .byte 58,0,16,24
 .byte 56,64,16,16
 .byte 60,64,16,8
 .byte 62,0,16,0
RcV1Ink7L:
 .byte 16
 .byte 90,67,16,24
 .byte 78,3,16,16
 .byte 74,67,16,8
 .byte 76,3,16,0
RcV1Body8R:
 .byte 24
 .byte 24,0,0,250
 .byte 26,0,0,2
 .byte 32,64,0,10
 .byte 30,0,16,250
 .byte 34,0,16,2
 .byte 28,64,16,10
RcV1Ink8R:
 .byte 24
 .byte 112,3,0,250
 .byte 122,3,0,2
 .byte 120,67,0,10
 .byte 116,3,16,250
 .byte 118,67,16,2
 .byte 114,67,16,10
RcV1Body8L:
 .byte 24
 .byte 24,64,0,13
 .byte 26,64,0,5
 .byte 32,0,0,253
 .byte 30,64,16,13
 .byte 34,64,16,5
 .byte 28,0,16,253
RcV1Ink8L:
 .byte 24
 .byte 112,67,0,13
 .byte 122,67,0,5
 .byte 120,3,0,253
 .byte 116,67,16,13
 .byte 118,3,16,5
 .byte 114,3,16,253
RcV1Body9R:
 .byte 20
 .byte 54,0,0,254
 .byte 56,0,0,6
 .byte 58,0,16,254
 .byte 60,64,16,6
 .byte 36,64,16,14
RcV1Ink9R:
 .byte 24
 .byte 68,3,0,254
 .byte 74,67,0,6
 .byte 66,67,0,14
 .byte 72,3,16,254
 .byte 70,3,16,6
 .byte 64,67,16,14
RcV1Body9L:
 .byte 20
 .byte 54,64,0,9
 .byte 56,64,0,1
 .byte 58,64,16,9
 .byte 60,0,16,1
 .byte 36,0,16,249
RcV1Ink9L:
 .byte 24
 .byte 68,67,0,9
 .byte 74,3,0,1
 .byte 66,3,0,249
 .byte 72,67,16,9
 .byte 70,67,16,1
 .byte 64,3,16,249
RcV1Body10R:
 .byte 20
 .byte 2,0,0,255
 .byte 6,0,0,7
 .byte 44,64,0,15
 .byte 10,0,16,255
 .byte 8,64,16,7
RcV1Ink10R:
 .byte 24
 .byte 78,3,0,255
 .byte 86,67,0,7
 .byte 76,67,0,15
 .byte 80,67,16,255
 .byte 84,3,16,7
 .byte 82,67,16,15
RcV1Body10L:
 .byte 20
 .byte 2,64,0,8
 .byte 6,64,0,0
 .byte 44,0,0,248
 .byte 10,64,16,8
 .byte 8,0,16,0
RcV1Ink10L:
 .byte 24
 .byte 78,67,0,8
 .byte 86,3,0,0
 .byte 76,3,0,248
 .byte 80,3,16,8
 .byte 84,67,16,0
 .byte 82,3,16,248
RcV1Body11R:
 .byte 16
 .byte 0,0,2,0
 .byte 2,64,2,8
 .byte 6,64,18,0
 .byte 4,64,18,8
RcV1Ink11R:
 .byte 16
 .byte 84,3,2,0
 .byte 82,67,2,8
 .byte 88,3,18,0
 .byte 86,67,18,8
RcV1Body11L:
 .byte 16
 .byte 0,64,2,7
 .byte 2,0,2,255
 .byte 6,0,18,7
 .byte 4,0,18,255
RcV1Ink11L:
 .byte 16
 .byte 84,67,2,7
 .byte 82,3,2,255
 .byte 88,67,18,7
 .byte 86,3,18,255
RcV1Body12R:
 .byte 24
 .byte 56,0,2,2
 .byte 58,64,2,10
 .byte 54,64,2,18
 .byte 62,64,18,2
 .byte 60,0,18,10
 .byte 2,64,18,18
RcV1Ink12R:
 .byte 24
 .byte 118,3,2,2
 .byte 116,67,2,10
 .byte 112,67,2,18
 .byte 122,3,18,2
 .byte 120,67,18,10
 .byte 114,67,18,18
RcV1Body12L:
 .byte 24
 .byte 56,64,2,5
 .byte 58,0,2,253
 .byte 54,0,2,245
 .byte 62,0,18,5
 .byte 60,64,18,253
 .byte 2,0,18,245
RcV1Ink12L:
 .byte 24
 .byte 118,67,2,5
 .byte 116,3,2,253
 .byte 112,3,2,245
 .byte 122,67,18,5
 .byte 120,3,18,253
 .byte 114,3,18,245
RcV1Body13R:
 .byte 24
 .byte 38,0,2,5
 .byte 40,64,2,13
 .byte 36,64,2,21
 .byte 44,64,18,5
 .byte 42,0,18,13
 .byte 46,64,18,21
RcV1Ink13R:
 .byte 24
 .byte 70,3,2,5
 .byte 68,67,2,13
 .byte 64,3,2,21
 .byte 74,3,18,5
 .byte 72,67,18,13
 .byte 66,3,18,21
RcV1Body13L:
 .byte 24
 .byte 38,64,2,2
 .byte 40,0,2,250
 .byte 36,0,2,242
 .byte 44,0,18,2
 .byte 42,64,18,250
 .byte 46,0,18,242
RcV1Ink13L:
 .byte 24
 .byte 70,67,2,2
 .byte 68,3,2,250
 .byte 64,67,2,242
 .byte 74,67,18,2
 .byte 72,3,18,250
 .byte 66,67,18,242
RcV1Body14R:
 .byte 28
 .byte 14,0,0,248
 .byte 16,64,0,0
 .byte 22,64,0,8
 .byte 24,0,16,248
 .byte 26,64,16,0
 .byte 20,0,16,8
 .byte 18,64,16,16
RcV1Ink14R:
 .byte 28
 .byte 92,3,0,248
 .byte 96,3,0,0
 .byte 94,67,0,8
 .byte 74,3,16,248
 .byte 72,67,16,0
 .byte 70,3,16,8
 .byte 64,67,16,16
RcV1Body14L:
 .byte 28
 .byte 14,64,0,15
 .byte 16,0,0,7
 .byte 22,0,0,255
 .byte 24,64,16,15
 .byte 26,0,16,7
 .byte 20,64,16,255
 .byte 18,0,16,247
RcV1Ink14L:
 .byte 28
 .byte 92,67,0,15
 .byte 96,67,0,7
 .byte 94,3,0,255
 .byte 74,67,16,15
 .byte 72,3,16,7
 .byte 70,67,16,255
 .byte 64,3,16,247
RcV1Body15R:
 .byte 24
 .byte 48,0,0,250
 .byte 50,0,0,2
 .byte 54,64,0,10
 .byte 56,0,16,250
 .byte 58,64,16,2
 .byte 52,64,16,10
RcV1Ink15R:
 .byte 24
 .byte 84,3,0,250
 .byte 126,67,0,2
 .byte 124,67,0,10
 .byte 82,67,16,250
 .byte 78,3,16,2
 .byte 76,67,16,10
RcV1Body15L:
 .byte 24
 .byte 48,64,0,13
 .byte 50,64,0,5
 .byte 54,0,0,253
 .byte 56,64,16,13
 .byte 58,0,16,5
 .byte 52,0,16,253
RcV1Ink15L:
 .byte 24
 .byte 84,67,0,13
 .byte 126,3,0,5
 .byte 124,3,0,253
 .byte 82,3,16,13
 .byte 78,67,16,5
 .byte 76,3,16,253
RcV1Body16R:
 .byte 24
 .byte 2,0,0,255
 .byte 6,0,0,7
 .byte 0,64,0,15
 .byte 10,0,16,255
 .byte 8,64,16,7
 .byte 4,0,16,15
RcV1Ink16R:
 .byte 24
 .byte 78,3,0,255
 .byte 86,67,0,7
 .byte 88,67,0,15
 .byte 80,67,16,255
 .byte 84,3,16,7
 .byte 90,67,16,15
RcV1Body16L:
 .byte 24
 .byte 2,64,0,8
 .byte 6,64,0,0
 .byte 0,0,0,248
 .byte 10,64,16,8
 .byte 8,0,16,0
 .byte 4,64,16,248
RcV1Ink16L:
 .byte 24
 .byte 78,67,0,8
 .byte 86,3,0,0
 .byte 88,3,0,248
 .byte 80,3,16,8
 .byte 84,67,16,0
 .byte 90,3,16,248
RcV1Body17R:
 .byte 24
 .byte 16,0,0,249
 .byte 18,64,0,1
 .byte 12,64,0,9
 .byte 14,0,16,249
 .byte 20,0,16,1
 .byte 22,64,16,9
RcV1Ink17R:
 .byte 28
 .byte 90,3,0,249
 .byte 86,67,0,1
 .byte 78,67,0,9
 .byte 84,67,16,249
 .byte 88,3,16,1
 .byte 82,67,16,9
 .byte 80,67,16,17
RcV1Body17L:
 .byte 24
 .byte 16,64,0,14
 .byte 18,0,0,6
 .byte 12,0,0,254
 .byte 14,64,16,14
 .byte 20,64,16,6
 .byte 22,0,16,254
RcV1Ink17L:
 .byte 28
 .byte 90,67,0,14
 .byte 86,3,0,6
 .byte 78,3,0,254
 .byte 84,3,16,14
 .byte 88,67,16,6
 .byte 82,3,16,254
 .byte 80,3,16,246
RcV0PoseRLo:
 .byte <RcV0Body0R,<RcV0Body1R,<RcV0Body2R,<RcV0Body3R,<RcV0Body4R,<RcV0Body5R,<RcV0Body6R,<RcV0Body7R,<RcV0Body8R,<RcV0Body9R,<RcV0Body10R,<RcV0Body11R,<RcV0Body12R,<RcV0Body13R,<RcV0Body14R,<RcV0Body15R,<RcV0Body16R,<RcV0Body17R
RcV0PoseRHi:
 .byte >RcV0Body0R,>RcV0Body1R,>RcV0Body2R,>RcV0Body3R,>RcV0Body4R,>RcV0Body5R,>RcV0Body6R,>RcV0Body7R,>RcV0Body8R,>RcV0Body9R,>RcV0Body10R,>RcV0Body11R,>RcV0Body12R,>RcV0Body13R,>RcV0Body14R,>RcV0Body15R,>RcV0Body16R,>RcV0Body17R
RcV0InkRLo:
 .byte <RcV0Ink0R,<RcV0Ink1R,<RcV0Ink2R,<RcV0Ink3R,<RcV0Ink4R,<RcV0Ink5R,<RcV0Ink6R,<RcV0Ink7R,<RcV0Ink8R,<RcV0Ink9R,<RcV0Ink10R,<RcV0Ink11R,<RcV0Ink12R,<RcV0Ink13R,<RcV0Ink14R,<RcV0Ink15R,<RcV0Ink16R,<RcV0Ink17R
RcV0InkRHi:
 .byte >RcV0Ink0R,>RcV0Ink1R,>RcV0Ink2R,>RcV0Ink3R,>RcV0Ink4R,>RcV0Ink5R,>RcV0Ink6R,>RcV0Ink7R,>RcV0Ink8R,>RcV0Ink9R,>RcV0Ink10R,>RcV0Ink11R,>RcV0Ink12R,>RcV0Ink13R,>RcV0Ink14R,>RcV0Ink15R,>RcV0Ink16R,>RcV0Ink17R
RcV0PoseLLo:
 .byte <RcV0Body0L,<RcV0Body1L,<RcV0Body2L,<RcV0Body3L,<RcV0Body4L,<RcV0Body5L,<RcV0Body6L,<RcV0Body7L,<RcV0Body8L,<RcV0Body9L,<RcV0Body10L,<RcV0Body11L,<RcV0Body12L,<RcV0Body13L,<RcV0Body14L,<RcV0Body15L,<RcV0Body16L,<RcV0Body17L
RcV0PoseLHi:
 .byte >RcV0Body0L,>RcV0Body1L,>RcV0Body2L,>RcV0Body3L,>RcV0Body4L,>RcV0Body5L,>RcV0Body6L,>RcV0Body7L,>RcV0Body8L,>RcV0Body9L,>RcV0Body10L,>RcV0Body11L,>RcV0Body12L,>RcV0Body13L,>RcV0Body14L,>RcV0Body15L,>RcV0Body16L,>RcV0Body17L
RcV0InkLLo:
 .byte <RcV0Ink0L,<RcV0Ink1L,<RcV0Ink2L,<RcV0Ink3L,<RcV0Ink4L,<RcV0Ink5L,<RcV0Ink6L,<RcV0Ink7L,<RcV0Ink8L,<RcV0Ink9L,<RcV0Ink10L,<RcV0Ink11L,<RcV0Ink12L,<RcV0Ink13L,<RcV0Ink14L,<RcV0Ink15L,<RcV0Ink16L,<RcV0Ink17L
RcV0InkLHi:
 .byte >RcV0Ink0L,>RcV0Ink1L,>RcV0Ink2L,>RcV0Ink3L,>RcV0Ink4L,>RcV0Ink5L,>RcV0Ink6L,>RcV0Ink7L,>RcV0Ink8L,>RcV0Ink9L,>RcV0Ink10L,>RcV0Ink11L,>RcV0Ink12L,>RcV0Ink13L,>RcV0Ink14L,>RcV0Ink15L,>RcV0Ink16L,>RcV0Ink17L
RcV0BodyPage:
 .byte 208,208,208,204,208,204,207,208,204,207,207,208,205,205,204,205,205,205
RcV0InkPage:
 .byte 166,166,210,210,166,211,166,167,211,211,211,167,211,165,210,165,211,210
RcV1PoseRLo:
 .byte <RcV1Body0R,<RcV1Body1R,<RcV1Body2R,<RcV1Body3R,<RcV1Body4R,<RcV1Body5R,<RcV1Body6R,<RcV1Body7R,<RcV1Body8R,<RcV1Body9R,<RcV1Body10R,<RcV1Body11R,<RcV1Body12R,<RcV1Body13R,<RcV1Body14R,<RcV1Body15R,<RcV1Body16R,<RcV1Body17R
RcV1PoseRHi:
 .byte >RcV1Body0R,>RcV1Body1R,>RcV1Body2R,>RcV1Body3R,>RcV1Body4R,>RcV1Body5R,>RcV1Body6R,>RcV1Body7R,>RcV1Body8R,>RcV1Body9R,>RcV1Body10R,>RcV1Body11R,>RcV1Body12R,>RcV1Body13R,>RcV1Body14R,>RcV1Body15R,>RcV1Body16R,>RcV1Body17R
RcV1InkRLo:
 .byte <RcV1Ink0R,<RcV1Ink1R,<RcV1Ink2R,<RcV1Ink3R,<RcV1Ink4R,<RcV1Ink5R,<RcV1Ink6R,<RcV1Ink7R,<RcV1Ink8R,<RcV1Ink9R,<RcV1Ink10R,<RcV1Ink11R,<RcV1Ink12R,<RcV1Ink13R,<RcV1Ink14R,<RcV1Ink15R,<RcV1Ink16R,<RcV1Ink17R
RcV1InkRHi:
 .byte >RcV1Ink0R,>RcV1Ink1R,>RcV1Ink2R,>RcV1Ink3R,>RcV1Ink4R,>RcV1Ink5R,>RcV1Ink6R,>RcV1Ink7R,>RcV1Ink8R,>RcV1Ink9R,>RcV1Ink10R,>RcV1Ink11R,>RcV1Ink12R,>RcV1Ink13R,>RcV1Ink14R,>RcV1Ink15R,>RcV1Ink16R,>RcV1Ink17R
RcV1PoseLLo:
 .byte <RcV1Body0L,<RcV1Body1L,<RcV1Body2L,<RcV1Body3L,<RcV1Body4L,<RcV1Body5L,<RcV1Body6L,<RcV1Body7L,<RcV1Body8L,<RcV1Body9L,<RcV1Body10L,<RcV1Body11L,<RcV1Body12L,<RcV1Body13L,<RcV1Body14L,<RcV1Body15L,<RcV1Body16L,<RcV1Body17L
RcV1PoseLHi:
 .byte >RcV1Body0L,>RcV1Body1L,>RcV1Body2L,>RcV1Body3L,>RcV1Body4L,>RcV1Body5L,>RcV1Body6L,>RcV1Body7L,>RcV1Body8L,>RcV1Body9L,>RcV1Body10L,>RcV1Body11L,>RcV1Body12L,>RcV1Body13L,>RcV1Body14L,>RcV1Body15L,>RcV1Body16L,>RcV1Body17L
RcV1InkLLo:
 .byte <RcV1Ink0L,<RcV1Ink1L,<RcV1Ink2L,<RcV1Ink3L,<RcV1Ink4L,<RcV1Ink5L,<RcV1Ink6L,<RcV1Ink7L,<RcV1Ink8L,<RcV1Ink9L,<RcV1Ink10L,<RcV1Ink11L,<RcV1Ink12L,<RcV1Ink13L,<RcV1Ink14L,<RcV1Ink15L,<RcV1Ink16L,<RcV1Ink17L
RcV1InkLHi:
 .byte >RcV1Ink0L,>RcV1Ink1L,>RcV1Ink2L,>RcV1Ink3L,>RcV1Ink4L,>RcV1Ink5L,>RcV1Ink6L,>RcV1Ink7L,>RcV1Ink8L,>RcV1Ink9L,>RcV1Ink10L,>RcV1Ink11L,>RcV1Ink12L,>RcV1Ink13L,>RcV1Ink14L,>RcV1Ink15L,>RcV1Ink16L,>RcV1Ink17L
RcV1BodyPage:
 .byte 208,208,208,206,208,206,206,208,206,207,207,209,205,206,204,206,207,207
RcV1InkPage:
 .byte 166,166,210,165,166,165,167,167,165,166,166,167,211,165,210,165,166,210
RcArtEnd:
.assert RcArtEnd-RcArtStart<=5248,error,"RCR art capacity"
.popseg
