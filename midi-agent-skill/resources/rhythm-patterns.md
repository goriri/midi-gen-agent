# Rhythm Patterns Reference

## Contents
- Time Signatures
- Basic Beat Patterns
- Syncopation
- Polyrhythms
- Genre-Specific Patterns
- Note Duration Reference

---

## Time Signatures

### Common Time Signatures

| Signature | Beats/Bar | Feel | Common Use |
|-----------|-----------|------|------------|
| 4/4 | 4 | Strong-weak-medium-weak | Pop, rock, most music |
| 3/4 | 3 | Strong-weak-weak | Waltz, ballads |
| 2/4 | 2 | Strong-weak | March, polka |
| 6/8 | 6 (or 2) | Compound duple | Folk, ballads, jigs |
| 12/8 | 12 (or 4) | Compound quadruple | Blues, slow rock |
| 5/4 | 5 | Asymmetric | Progressive, jazz |
| 7/8 | 7 | Asymmetric | Progressive, Balkan |

### Beat Emphasis in 4/4

```
Beat:     1       2       3       4
Emphasis: STRONG  weak    medium  weak
```

---

## Basic Beat Patterns

### 4/4 Rock Beat
```
Beat:    1   +   2   +   3   +   4   +
Kick:    X       .       X       .
Snare:   .       X       .       X
HiHat:   X   X   X   X   X   X   X   X
```

### 4/4 Pop Beat
```
Beat:    1   +   2   +   3   +   4   +
Kick:    X       .   X   .       X   .
Snare:   .       X       .       X
HiHat:   X   X   X   X   X   X   X   X
```

### 3/4 Waltz
```
Beat:    1       2       3
Bass:    X       .       .
Chord:   .       X       X
```

### 6/8 Feel
```
Beat:    1   2   3   4   5   6
Accent:  X   .   .   X   .   .
```

---

## Syncopation

Syncopation emphasizes off-beats or weak beats.

### Basic Syncopation Pattern
```
Normal:     1   +   2   +   3   +   4   +
            X       X       X       X

Syncopated: 1   +   2   +   3   +   4   +
            X   X       X   X       X
```

### Anticipation (Playing Before the Beat)
```
Beat:       1   +   2   +   3   +   4   +
Normal:     .   .   X   .   .   .   X   .
Anticipated:.   X   .   .   .   X   .   .
```

### Common Syncopation Types

| Type | Pattern | Effect |
|------|---------|--------|
| Backbeat | Accent 2 & 4 | Rock/pop groove |
| Offbeat | Accent +'s | Reggae feel |
| Anticipation | Before beat | Jazz/funk |
| Delayed | After beat | Laid-back feel |

---

## Polyrhythms

Two or more conflicting rhythms played simultaneously.

### 3 Against 2 (3:2)
```
Voice 1:  X   .   X   .   X   .  (3 notes)
Voice 2:  X   .   .   X   .   .  (2 notes)
Combined: X   .   X   X   X   .
```

### 4 Against 3 (4:3)
```
Voice 1:  X   .   .   X   .   .   X   .   .   X   .   .  (4 notes)
Voice 2:  X   .   .   .   X   .   .   .   X   .   .   .  (3 notes)
```

### Hemiola (3 in the Space of 2)
```
Normal 6/8:  X   .   .   X   .   .
Hemiola:     X   .   X   .   X   .
```

---

## Genre-Specific Patterns

### Rock
```
Straight 8ths, strong 2 & 4
BPM: 100-140
```

### Jazz Swing
```
"Triplet feel" - long-short pattern
Beat:    1     +     2     +     3     +     4     +
Feel:    X     .  x  X     .  x  X     .  x  X     .  x
BPM: 120-200
```

### Funk
```
Heavy syncopation, 16th note emphasis
Beat:    1 e + a 2 e + a 3 e + a 4 e + a
Accent:  X . . X . X . . X . . X . X . .
BPM: 90-120
```

### Bossa Nova
```
2-bar pattern with syncopation
Bar 1:   X . . X . . X . . X . . X . . .
Bar 2:   X . . X . . X . . . X . . X . .
BPM: 120-145
```

### Reggae
```
Offbeat emphasis (One Drop)
Beat:    1   +   2   +   3   +   4   +
Kick:    .       .       X       .
Guitar:  .   X   .   X   .   X   .   X
BPM: 60-90
```

### Electronic (Four-on-the-Floor)
```
Kick on every beat
Beat:    1   +   2   +   3   +   4   +
Kick:    X       X       X       X
HiHat:   .   X   .   X   .   X   .   X
BPM: 120-140
```

### Hip Hop
```
Boom-bap pattern
Beat:    1   +   2   +   3   +   4   +
Kick:    X       .       .   X   .
Snare:   .       X       .       X
BPM: 85-115
```

---

## Note Duration Reference

### MIDI Duration Values

| Name | Symbol | Beats (4/4) | MIDI Duration |
|------|--------|-------------|---------------|
| Whole | 𝅝 | 4 | "1" |
| Half | 𝅗𝅥 | 2 | "2" |
| Quarter | ♩ | 1 | "4" |
| Eighth | ♪ | 0.5 | "8" |
| Sixteenth | 𝅘𝅥𝅯 | 0.25 | "16" |
| Dotted Half | 𝅗𝅥. | 3 | "d2" |
| Dotted Quarter | ♩. | 1.5 | "d4" |
| Dotted Eighth | ♪. | 0.75 | "d8" |
| Triplet Quarter | ♩³ | 0.67 | "4t" |
| Triplet Eighth | ♪³ | 0.33 | "8t" |

### Duration Combinations

```json
{
  "notes": [
    {"pitch": "C4", "duration": "4"},   // Quarter note
    {"pitch": "D4", "duration": "8"},   // Eighth note
    {"pitch": "E4", "duration": "8"},   // Eighth note
    {"pitch": "F4", "duration": "2"}    // Half note
  ]
}
```

---

## Rhythm Tips for MIDI

### Creating Groove
1. Vary velocity (loudness) slightly
2. Add subtle timing variations
3. Use syncopation sparingly
4. Match rhythm to genre conventions

### Common Mistakes
- ✗ All notes same velocity
- ✗ Everything perfectly on-grid
- ✗ Ignoring genre conventions
- ✗ Too much syncopation

### Tempo Guidelines by Genre

| Genre | BPM Range |
|-------|-----------|
| Ballad | 60-80 |
| Hip Hop | 85-115 |
| Pop | 100-130 |
| Rock | 110-140 |
| Dance/EDM | 120-140 |
| Drum & Bass | 160-180 |
