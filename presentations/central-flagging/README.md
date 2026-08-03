# Central Flagging Mechanism — Presentation

Architecture briefing for a **new .NET central flagging management application**, including honest **pros & cons of single-app flagging**.

## Artifacts

| File | Description |
|------|-------------|
| [`Central_Flagging_Mechanism.pdf`](./Central_Flagging_Mechanism.pdf) | Landscape PDF deck |
| [`interactive-diagrams.html`](./interactive-diagrams.html) | Interactive Mermaid diagrams + single-app pros/cons |
| [`scripts/generate_presentation.py`](./scripts/generate_presentation.py) | Regenerates the PDF |

## Related .NET solution

See [`../../src/ARCHITECTURE.md`](../../src/ARCHITECTURE.md) and [`../../src/CentralFlagging.sln`](../../src/CentralFlagging.sln).

## Deck outline

1. Title
2. Agenda
3. Current state — individual / single-app flags
4. **Single-app flagging: pros & cons**
5. Sequence — individual flagging + drawbacks
6. Drawbacks of isolated stores
7. Drawbacks of duplicated flags across projects
8. Central solution overview
9. Central namespaced sequence
10. Namespace = project name model
11. Target architecture
12. Closing every drawback
13. Pros of central application
14. Recommendation

## Regenerate PDF

```bash
pip install reportlab
python3 presentations/central-flagging/scripts/generate_presentation.py
```
