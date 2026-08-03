# Central Flagging Mechanism — Presentation

Architecture briefing on moving from per-project feature flags to a **central flagging application** with **project-name namespaces**.

## Artifacts

| File | Description |
|------|-------------|
| [`Central_Flagging_Mechanism.pdf`](./Central_Flagging_Mechanism.pdf) | Full landscape PDF deck (13 slides) |
| [`interactive-diagrams.html`](./interactive-diagrams.html) | Interactive Mermaid sequence & architecture diagrams |
| [`scripts/generate_presentation.py`](./scripts/generate_presentation.py) | Regenerates the PDF |

## Deck outline

1. Title — Central Flagging Mechanism  
2. Agenda  
3. Current state — individual project flags  
4. Sequence — individual flagging + visible drawbacks  
5. Drawbacks of isolated flag stores  
6. Drawbacks of the same flags copied across projects  
7. Solution overview — central control plane  
8. Sequence — central namespaced evaluation  
9. Data model — namespaces = project names  
10. Target architecture (logical view)  
11. Closing every drawback (problem → capability map)  
12. Pros of the central application  
13. Recommendation / conclusion  

## Regenerate PDF

```bash
pip install reportlab
python3 presentations/central-flagging/scripts/generate_presentation.py
```

## Interactive diagrams

Open `interactive-diagrams.html` in a browser (Mermaid loads from CDN). Tabs cover:

- Individual flags sequence + drawbacks  
- Duplicated-flag drift flowchart  
- Central solution sequence + expandable pros  
- Namespace model  
- Drawback → capability coverage table  
