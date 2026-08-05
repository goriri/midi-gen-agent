# Counterpoint Reference

Counterpoint is the relationship of two or more simultaneous musical lines that are harmonically dependent yet melodically independent.

## Contents
- Species Counterpoint Overview
- First Species (Note-against-note)
- Second Species (2:1)
- Third Species (4:1)
- Fourth Species (Suspensions)
- Fifth Species (Florid)
- Practical Application

---

## Species Counterpoint Overview

Based on Johann Joseph Fux's *Gradus ad Parnassum* (1725), species counterpoint teaches composition through five progressive levels of complexity.

### Consonance Classification

| Type | Intervals |
|------|-----------|
| Perfect Consonance | Unison, P5, P8 |
| Imperfect Consonance | m3, M3, m6, M6 |
| Dissonance | m2, M2, P4, tritone, m7, M7 |

---

## First Species (Note-against-note)

Each note in the counterpoint sounds against one note in the cantus firmus (the given melody).

### Rules

1. **Begin on**: Unison, P5, or P8
2. **End on**: Unison or P8
3. **Use only consonances**: P1, m3, M3, P5, m6, M6, P8
4. **FORBIDDEN**: Parallel P5ths and P8ves

### Motion Types

| Motion | Description | Example |
|--------|-------------|---------|
| Contrary | Voices move in opposite directions | ✓ Preferred |
| Oblique | One voice stays, other moves | ✓ Good |
| Similar | Same direction, different interval | Use carefully |
| Parallel | Same direction, same interval | ✗ Avoid for P5/P8 |

### First Species Example

```
Cantus:      C4  D4  E4  F4  G4  A4  G4  F4  E4  D4  C4
Counterpoint: E4  F4  G4  A4  B4  C5  B4  A4  G4  F4  E4
Interval:     3   3   3   3   3   3   3   3   3   3   3
```

---

## Second Species (2:1)

Two notes in counterpoint against each whole note in cantus firmus.

### Rules

1. **Strong beats**: Must be consonant
2. **Weak beats**: May use passing tones (dissonant)
3. **No parallel P5/P8** on adjacent strong beats
4. **Approach perfect consonances** by contrary or oblique motion

### Passing Tone Usage

```
Cantus:      C4 -------- D4 --------
Counter:     E4    F4    G4    A4
Beat:        1     2     1     2
Consonance:  ✓     pass  ✓     ✓
```

---

## Third Species (4:1)

Four notes against each cantus firmus note.

### Rules

1. **Beat 1**: Must be consonant
2. **Beats 2-4**: May use passing/neighbor tones
3. **Cambiata**: A specific melodic pattern allowed
4. **No more than 3 notes** in same direction

### Neighbor Tone Pattern

```
Main note → Step away → Return
C4 → D4 → C4 (upper neighbor)
C4 → B3 → C4 (lower neighbor)
```

---

## Fourth Species (Suspensions)

Syncopated rhythm creates tension and resolution through suspensions.

### Suspension Structure

| Phase | Description | Beat |
|-------|-------------|------|
| Preparation | Consonance | Weak beat |
| Suspension | Dissonance (held over) | Strong beat |
| Resolution | Consonance (step down) | Weak beat |

### Common Suspensions

| Type | Interval Pattern | Resolution |
|------|------------------|------------|
| 4-3 | P4 → M3 or m3 | Down by step |
| 7-6 | m7/M7 → m6/M6 | Down by step |
| 9-8 | M9/m9 → P8 | Down by step |
| 2-3 (bass) | M2/m2 → m3/M3 | Down by step |

### Fourth Species Example

```
Beat:    1    2    3    4  | 1    2    3    4
Cantus:  C4----------------|D4----------------
Counter: G4--------G4------|F#4-------F#4----
                   (prep)   (susp)    (res)
```

---

## Fifth Species (Florid Counterpoint)

Combines all previous species with varied rhythms.

### Guidelines

1. **Mix rhythms**: Whole, half, quarter notes
2. **No single species** should dominate
3. **Include suspensions** for harmonic interest
4. **Maintain melodic flow** with stepwise motion

### Florid Example Pattern

```
Bar 1: Half + 2 quarters
Bar 2: Whole with suspension
Bar 3: 4 quarters
Bar 4: Half + suspension resolution
```

---

## Practical Application for MIDI

### Two-Voice Texture

When creating a melody with bass:

```json
{
  "tracks": [
    {
      "instrument": "violin",
      "notes": [
        {"pitch": "G4", "duration": "4"},
        {"pitch": "A4", "duration": "4"},
        {"pitch": "B4", "duration": "4"},
        {"pitch": "C5", "duration": "4"}
      ]
    },
    {
      "instrument": "cello",
      "notes": [
        {"pitch": "C3", "duration": "4"},
        {"pitch": "F3", "duration": "4"},
        {"pitch": "G3", "duration": "4"},
        {"pitch": "C3", "duration": "4"}
      ]
    }
  ]
}
```

### Checklist for Counterpoint

- [ ] No parallel fifths or octaves
- [ ] Strong beats are consonant
- [ ] Voices move mostly by step
- [ ] Contrary motion preferred
- [ ] Dissonances properly prepared and resolved
- [ ] Melodic lines are singable/playable

---

## Bach-Style Considerations

Bach's counterpoint differs from strict species:
- Uses both perfect and imperfect consonances freely
- Grows from harmonic background
- Features bold independence between voices
- Incorporates more chromatic movement

For Bach-style fugues, consider adding:
- Subject (main theme)
- Answer (transposed response)
- Counter-subject (accompanying melody)
- Episodes (developmental sections)
