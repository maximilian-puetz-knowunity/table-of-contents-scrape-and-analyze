# Input to the script

- Country (mandatory)
- Grade (mandatory)
- Subject
- Desired max. depth (e.g. 3 levels = topic and two levels of abstraction down)
- Directory with Screenshots of Table of Contents

E.g.

```json
{
    "country": "DE", // ISO
    "grade": "9", // mandatory
    // "region": "Germany", // localized, optional
    // "schoolType": "Liceum Ogólnokształcące",
    "subject": "Mathematics", // normalized
    "dir_path": "toc_Mathematik_9_Arbeitsheft_Mathematik_9_978-3-12-746815-1"
}
```

# Output from the script

```json
{
    "country": "DE", // ISO
    "grade": "9", // mandatory
    "subject": "Mathematik", // normalized
    "ISBN": "978-3-12-746815-1",
    "taxonomy": [ // this is an ordered list
        {
            "name": "Algebra",
            "keyterms": ["differentiation", "equations", "functions", "variables", "coefficients"],
            "level": 0, // 0-indexed
            "children": [{
                "name": "Calculus",
                "keyterms": ["derivatives", "integrals", "limits", "chain rule", "product rule"],
                "level": 1,
                "children": []
            }]
        },
        {
            "name": "Geometry",
            "keyterms": ["shapes", "angles", "area", "perimeter", "coordinates"],
            "level": 0,
            "children": [
                {
                    "name": "Triangles",
                    "keyterms": ["sides", "angles", "congruent", "similar", "vertices"],
                    "level": 1,
                    "children": [
                        {
                            "name": "Pythagorean Theorem",
                            "keyterms": ["hypotenuse", "right triangle", "a² + b² = c²", "legs"],
                            "level": 2,
                            "children": []
                        }
                    ]
                }
            ]
        }
    ]
}
```