# Central Flagging Management Application (.NET)

A **new** .NET 8 solution that acts as the **single control plane** for feature flags across many applications. Each consuming project is isolated by a **namespace = project name**.

## Why not keep flags inside each app?

### Single-app flagging — Pros

| Pro | Why it feels attractive |
|-----|-------------------------|
| **Simple to start** | A `appsettings` toggle or small DB table ships with the first service |
| **Low latency** | Evaluation is in-process; no network hop |
| **No shared dependency** | App keeps working if a central platform is down |
| **Local ownership** | Team can invent keys and lifecycle without coordinating |
| **Fast for one team / one deployable** | Perfect when there is truly only one product surface |

### Single-app flagging — Cons

| Con | What goes wrong at scale |
|-----|--------------------------|
| **Fragmented truth** | “Is `checkout_v2` on?” requires N consoles / repos |
| **Slow incident response** | Kill switches wait on app deploys or per-repo PRs |
| **Inconsistent semantics** | Different caching, defaults, and SDK behavior per service |
| **Weak governance** | No unified RBAC, approval, or audit across the estate |
| **Duplicated machinery** | Targeting, % rollout, environments reinvented everywhere |
| **Cross-app drift** | The “same” flag copied into many apps diverges in meaning and lifecycle |
| **Partial rollouts** | Feature on in Payments, forgotten in Lending → broken journeys |
| **Ownership fog** | Cross-cutting flags have no single accountable owner |

**Bottom line:** single-app flagging is fine for a lone service. It becomes an operational liability as soon as multiple projects must move together.

## Central flagging — how this solution covers the gaps

| Single-app pain | Central capability |
|-----------------|--------------------|
| Fragmented truth | One API + store; namespaces partition by project |
| Slow kills | Toggle via Admin/API without redeploying consumers |
| Inconsistent eval | Shared evaluator + `CentralFlagging.Sdk` |
| Weak governance | Audit log on every management mutation |
| Duplicated machinery | Environments, rollout %, types built once |
| Cross-app drift | One definition per `namespace/key`; optional `global` namespace |
| Ownership fog | Namespace `OwnerTeam` + audit actor |

## Solution layout

```
src/
  CentralFlagging.sln
  CentralFlagging.Domain/          # Namespace, Flag, Environment state, Evaluator
  CentralFlagging.Application/     # Management + evaluation services
  CentralFlagging.Infrastructure/  # EF Core + SQLite (swap to SQL Server later)
  CentralFlagging.Api/             # ASP.NET Core Minimal API (Swagger)
  CentralFlagging.Sdk/             # HttpClient for consuming .NET apps
  CentralFlagging.UnitTests/
```

### Namespace model

```
Organization
 ├─ ns:payments      → checkout_v2, kill.gateway
 ├─ ns:lending       → risk_model_b
 ├─ ns:onboarding    → kyc_async
 └─ ns:global        → maintenance_mode   (true cross-cutting kills)
```

Consumers always evaluate with **their** project namespace. No accidental cross-project reads.

## API (management + evaluation)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/namespaces` | List project namespaces |
| POST | `/api/namespaces` | Create namespace |
| GET | `/api/namespaces/{ns}/flags` | List flags in a project |
| POST | `/api/namespaces/{ns}/flags` | Create flag |
| POST | `/api/namespaces/{ns}/flags/{key}/toggle` | Enable/disable + rollout |
| POST | `/api/evaluate` | SDK evaluation (`namespace`, `flagKey`, `environment`, `subjectKey`) |
| GET | `/api/audit?ns=` | Change audit trail |

## Consume from another .NET app

```csharp
builder.Services.AddCentralFlaggingSdk(opt =>
{
    opt.BaseUrl = "http://localhost:5080";
    opt.Namespace = "payments";           // THIS project name
    opt.Environment = EnvironmentKind.Production;
});

// later
if (await flags.IsEnabledAsync("checkout_v2", userId))
{
    // new path
}
```

## Run locally

```bash
export PATH="$PATH:$HOME/.dotnet"
cd src
dotnet restore CentralFlagging.sln
dotnet test CentralFlagging.sln
dotnet run --project CentralFlagging.Api
# Swagger → http://localhost:5080/swagger
```

## Suggested next increments

1. SQL Server / PostgreSQL provider + EF migrations  
2. Redis / edge snapshot cache for SDK (local-first eval)  
3. OIDC + RBAC scoped to namespaces  
4. Admin Blazor/React UI on top of the same API  
5. Webhooks / Outbox for config-changed fan-out  

## Presentation companions

- `presentations/central-flagging/Central_Flagging_Mechanism.pdf`  
- `presentations/central-flagging/interactive-diagrams.html`  
