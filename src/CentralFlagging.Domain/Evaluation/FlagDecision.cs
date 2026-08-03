using CentralFlagging.Domain.Enums;

namespace CentralFlagging.Domain.Evaluation;

/// <summary>
/// Deterministic evaluation result returned to SDKs / services.
/// </summary>
public sealed record FlagDecision(
    string Namespace,
    string FlagKey,
    EnvironmentKind Environment,
    bool Enabled,
    string Value,
    string Reason,
    int? RolloutPercent = null);
