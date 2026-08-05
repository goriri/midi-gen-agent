# Voice Leading Reference

## Contents
- Core Principles
- Interval Rules
- Common Mistakes to Avoid
- Part Writing Guidelines
- Multi-Track Arrangement Tips

---

## Core Principles

### 1. Smooth Motion
Move each voice by the smallest interval possible.

**Good:**
```
Voice 1: C4 → B3 → C4  (stepwise)
Voice 2: E4 → D4 → E4  (stepwise)
Voice 3: G4 → G4 → G4  (common tone)
```

**Bad:**
```
Voice 1: C4 → G4 → C5  (large jumps)
Voice 2: E4 → B3 → G4  (erratic)
```

### 2. Contrary Motion
When possible, move voices in opposite directions.

**Good:**
```
Soprano: C5 → D5 → E5  (ascending)
Bass:    C3 → B2 → A2  (descending)
```

### 3. Avoid Parallel Fifths and Octaves
Never move two voices in parallel perfect fifths or octaves.

**Bad (parallel fifths):**
```
Voice 1: C4 → D4
Voice 2: G3 → A3  (both move up by step, maintaining 5th)
```

**Good (oblique motion):**
```
Voice 1: C4 → D4
Voice 2: G3 → G3  (one voice stays)
```

---

## Interval Rules

### Intervals to USE Freely

| Interval | Semitones | Quality |
|----------|-----------|---------|
| Unison | 0 | Perfect consonance |
| Minor 3rd | 3 | Imperfect consonance |
| Major 3rd | 4 | Imperfect consonance |
| Perfect 4th | 5 | Consonance (in context) |
| Perfect 5th | 7 | Perfect consonance |
| Minor 6th | 8 | Imperfect consonance |
| Major 6th | 9 | Imperfect consonance |
| Octave | 12 | Perfect consonance |

### Intervals to AVOID or Use Carefully

| Interval | Semitones | Rule |
|----------|-----------|------|
| Minor 2nd | 1 | **AVOID** - harsh dissonance |
| Major 2nd | 2 | Passing only, don't sustain |
| Tritone | 6 | Resolve immediately |
| Major 7th | 11 | Jazz only, resolve down |

---

## Common Mistakes to Avoid

### 1. Clusters (Adjacent Notes)
**Problem:** Multiple notes within 1-2 semitones
```
Bad: C4, C#4, D4 playing together
```
**Solution:** Spread notes across octaves
```
Good: C3, D4, E5
```

### 2. Unresolved Dissonance
**Problem:** Tritone or 7th left hanging
```
Bad: B3 + F4 (tritone) held for 4 beats
```
**Solution:** Resolve to consonance
```
Good: B3 + F4 → C4 + E4
```

### 3. Voice Crossing
**Problem:** Lower voice goes above higher voice
```
Bad:
  Soprano: C4 → B3
  Alto:    E4 → C4  (alto crosses above soprano)
```
**Solution:** Maintain voice order

### 4. Doubling the Leading Tone
**Problem:** Two voices on the 7th scale degree
```
Bad in C Major: Two voices on B
```
**Solution:** Double the root or fifth instead

---

## Part Writing Guidelines

### Spacing Between Voices

| Voices | Maximum Gap |
|--------|-------------|
| Soprano - Alto | Octave |
| Alto - Tenor | Octave |
| Tenor - Bass | Octave + Fifth |

### Register Recommendations

| Voice/Instrument | Comfortable Range |
|------------------|-------------------|
| Bass | C2 - E4 |
| Cello/Tenor | C3 - G4 |
| Viola/Alto | C3 - C5 |
| Violin/Soprano | G3 - E6 |
| Piano (left) | C2 - C4 |
| Piano (right) | C4 - C6 |

---

## Multi-Track Arrangement Tips

### Assigning Notes to Tracks

**For a C Major chord (C-E-G):**

| Track | Instrument | Note | Octave |
|-------|------------|------|--------|
| 1 | Bass | C | 2 |
| 2 | Piano/Pad | E, G | 3 |
| 3 | Melody/Lead | C, E, G | 4-5 |

### Avoid Frequency Masking

**Problem:** Two instruments playing same notes in same octave
```
Bad:
  Piano: C4, E4, G4
  Strings: C4, E4, G4  (exact same)
```

**Solution:** Spread across octaves
```
Good:
  Piano: C3, E3, G3
  Strings: E4, G4, C5
```

### Bass + Chord Relationship

**Rule:** Bass should play root or fifth of chord

| Chord | Preferred Bass | Avoid in Bass |
|-------|----------------|---------------|
| C Major | C or G | E (weak) |
| Am | A or E | C (inverts feel) |
| Dm7 | D or A | F (unstable) |

---

## Quick Checklist Before Generating MIDI

- [ ] No notes 1 semitone apart playing simultaneously
- [ ] Bass is playing root or fifth of chord
- [ ] No parallel fifths or octaves between tracks
- [ ] Dissonant intervals resolve to consonance
- [ ] Voices stay in comfortable ranges
- [ ] Tracks are spread across different octaves
