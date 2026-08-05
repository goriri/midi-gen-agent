# Orchestration Reference

## Contents
- Instrument Families
- Instrument Ranges
- Combining Instruments
- Arrangement Techniques
- Genre-Specific Guidelines

---

## Instrument Families

### Strings
| Instrument | GM Program | Range | Character |
|------------|------------|-------|-----------|
| Violin | 40 | G3-E7 | Bright, expressive |
| Viola | 41 | C3-C6 | Warm, middle voice |
| Cello | 42 | C2-G5 | Rich, emotional |
| Contrabass | 43 | E1-G4 | Deep, foundational |
| String Ensemble | 48-49 | Wide | Lush, cinematic |

### Woodwinds
| Instrument | GM Program | Range | Character |
|------------|------------|-------|-----------|
| Flute | 73 | C4-C7 | Airy, bright |
| Oboe | 68 | B♭3-G6 | Nasal, pastoral |
| Clarinet | 71 | D3-B♭6 | Warm, versatile |
| Bassoon | 70 | B♭1-E5 | Dark, comedic |
| Alto Sax | 65 | D♭3-A5 | Smooth, jazzy |

### Brass
| Instrument | GM Program | Range | Character |
|------------|------------|-------|-----------|
| Trumpet | 56 | E3-C6 | Bright, heroic |
| Trombone | 57 | E2-B♭4 | Bold, powerful |
| French Horn | 60 | F2-C6 | Noble, warm |
| Tuba | 58 | D1-F4 | Deep, grounding |
| Brass Section | 61 | Wide | Majestic |

### Keyboards
| Instrument | GM Program | Range | Character |
|------------|------------|-------|-----------|
| Grand Piano | 0 | A0-C8 | Versatile, rich |
| Electric Piano | 4-5 | Wide | Warm, vintage |
| Harpsichord | 6 | Wide | Baroque, bright |
| Organ | 16-19 | Wide | Sustained, full |

### Plucked
| Instrument | GM Program | Range | Character |
|------------|------------|-------|-----------|
| Acoustic Guitar | 24-25 | E2-E6 | Warm, intimate |
| Electric Guitar | 26-30 | E2-E6 | Versatile |
| Acoustic Bass | 32 | E1-G4 | Round, warm |
| Electric Bass | 33-34 | E1-G4 | Punchy, defined |
| Harp | 46 | C1-G7 | Ethereal, flowing |

---

## Register and Roles

### Four-Part Texture

| Role | Register | Typical Instruments |
|------|----------|---------------------|
| Soprano | C4-C6 | Violin, Flute, Trumpet |
| Alto | G3-G5 | Viola, Clarinet, French Horn |
| Tenor | C3-C5 | Cello, Trombone, Tenor Sax |
| Bass | C1-C4 | Contrabass, Tuba, Bass Guitar |

### Spacing Guidelines

```
Good:  Soprano  C5
       Alto     G4  (Perfect 4th below)
       Tenor    C4  (Perfect 5th below)
       Bass     C3  (Octave below)

Bad:   Soprano  C5
       Alto     B4  (Too close - minor 2nd)
       Tenor    A4  (Cluttered)
       Bass     G4  (Not enough space)
```

---

## Combining Instruments

### Doubling (Same Notes)

| Combination | Effect |
|-------------|--------|
| Violin + Flute | Bright, clear |
| Cello + Bassoon | Dark, rich |
| Trumpet + Violin | Heroic melody |
| Strings + Brass | Epic, full |
| Piano + Strings | Warm, cinematic |

### Layering (Different Notes)

```
Example: C Major Chord

Flute:    G5 (5th, high)
Violin:   E4 (3rd, mid)
Viola:    C4 (root, mid)
Cello:    G3 (5th, low)
Bass:     C2 (root, foundation)
```

### Timbral Blend

| Blend Type | Instruments | Result |
|------------|-------------|--------|
| Homogeneous | All strings | Unified sound |
| Heterogeneous | Strings + Winds | Varied color |
| Contrast | Solo vs Tutti | Dramatic effect |

---

## Dynamic Layering

### Building Intensity

| Level | Instruments | Dynamic |
|-------|-------------|---------|
| 1 (Quiet) | Solo piano or strings | pp-p |
| 2 (Soft) | Strings + woodwinds | p-mp |
| 3 (Medium) | Full strings + light brass | mp-mf |
| 4 (Loud) | Full orchestra | mf-f |
| 5 (Climax) | Full orchestra + percussion | f-ff |

### Crescendo Build

```
Bar 1-2:  Strings only (p)
Bar 3-4:  + Woodwinds (mp)
Bar 5-6:  + French Horns (mf)
Bar 7-8:  + Trumpets + Timpani (f)
```

---

## Genre-Specific Arrangements

### Classical/Orchestral
```
Melody:     Violin I / Flute
Harmony:    Violin II / Viola / Horns
Bass:       Cello / Contrabass
Accents:    Timpani / Brass stabs
```

### Jazz Combo
```
Melody:     Saxophone / Trumpet
Harmony:    Piano (chord voicings)
Bass:       Upright Bass (walking)
Rhythm:     Drums / Piano comping
```

### Rock Band
```
Melody:     Vocals / Lead Guitar
Harmony:    Rhythm Guitar / Keys
Bass:       Electric Bass
Rhythm:     Drums
```

### Pop/Electronic
```
Melody:     Synth Lead / Vocal
Harmony:    Synth Pad / Piano
Bass:       Synth Bass / 808
Rhythm:     Drum Machine / Percussion
```

### Film Score (Epic)
```
Foundation: Low Strings + Brass
Middle:     Full Strings + Horns
Top:        Choir + High Strings + Trumpets
Rhythm:     Taiko Drums + Timpani
```

---

## Frequency Considerations

### Avoid Frequency Clashing

| Register | Instruments to Separate |
|----------|-------------------------|
| Low (C1-C3) | Bass, Tuba, Cello, Left hand piano |
| Low-Mid (C3-C4) | Tenor Sax, Trombone, Viola |
| Mid (C4-C5) | Voice, Guitar, Piano, Violin |
| High (C5-C7) | Flute, Piccolo, High Strings |

### EQ Space by Instrument Role

```
Bass:     50-250 Hz  (foundation)
Rhythm:   250-500 Hz (body)
Harmony:  500-2000 Hz (warmth)
Melody:   2000-8000 Hz (presence)
Air:      8000+ Hz (brilliance)
```

---

## Track Assignment Tips for MIDI

### Minimal Arrangement (3-4 tracks)
```json
{
  "tracks": [
    {"instrument": "acoustic-grand-piano", "role": "melody + harmony"},
    {"instrument": "acoustic-bass", "role": "bass"},
    {"instrument": "string-ensemble-1", "role": "pad"}
  ]
}
```

### Full Arrangement (6-8 tracks)
```json
{
  "tracks": [
    {"instrument": "violin", "role": "melody"},
    {"instrument": "viola", "role": "counter-melody"},
    {"instrument": "cello", "role": "harmony"},
    {"instrument": "contrabass", "role": "bass"},
    {"instrument": "french-horn", "role": "sustained harmony"},
    {"instrument": "timpani", "role": "accents"}
  ]
}
```

---

## Quick Checklist

- [ ] Each instrument in its comfortable range
- [ ] Bass and melody clearly separated (2+ octaves)
- [ ] No frequency clashing in same octave
- [ ] Dynamics appropriate for genre
- [ ] Instrument choices match style
- [ ] Lead instrument clearly audible
