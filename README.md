# APPS

## Central Flagging (.NET)

New central feature-flag management application:

- Solution: [`src/CentralFlagging.sln`](src/CentralFlagging.sln)
- Architecture + **single-app pros/cons**: [`src/ARCHITECTURE.md`](src/ARCHITECTURE.md)
- Presentation PDF + interactive diagrams: [`presentations/central-flagging/`](presentations/central-flagging/)

```bash
export PATH="$PATH:$HOME/.dotnet"
dotnet test src/CentralFlagging.sln
dotnet run --project src/CentralFlagging.Api
# http://localhost:5080/swagger
```
