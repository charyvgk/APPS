using System.ComponentModel.DataAnnotations;
using CentralFlagging.Domain.Enums;

namespace CentralFlagging.Api.Contracts;

public sealed record CreateNamespaceRequest(
    [Required] string Name,
    string? DisplayName,
    string? OwnerTeam,
    string? Actor);

public sealed record CreateFlagRequest(
    [Required] string Key,
    string? Description,
    FlagType Type,
    string? Actor);

public sealed record ToggleFlagRequest(
    [Required] EnvironmentKind Environment,
    [Required] bool Enabled,
    string? DefaultValue,
    int? RolloutPercent,
    string? Actor);

public sealed record EvaluateRequest(
    [Required] string Namespace,
    [Required] string FlagKey,
    EnvironmentKind Environment = EnvironmentKind.Production,
    string? SubjectKey = null);

public sealed record NamespaceDto(Guid Id, string Name, string DisplayName, string? OwnerTeam, DateTimeOffset CreatedAt);

public sealed record FlagEnvironmentDto(
    EnvironmentKind Environment,
    bool Enabled,
    string DefaultValue,
    int RolloutPercent);

public sealed record FlagDto(
    Guid Id,
    string Key,
    string Description,
    FlagType Type,
    bool IsArchived,
    IReadOnlyList<FlagEnvironmentDto> Environments,
    DateTimeOffset UpdatedAt);

public sealed record DecisionDto(
    string Namespace,
    string FlagKey,
    EnvironmentKind Environment,
    bool Enabled,
    string Value,
    string Reason,
    int? RolloutPercent);

public sealed record AuditDto(
    Guid Id,
    string NamespaceName,
    string? FlagKey,
    string Action,
    string Actor,
    string Details,
    DateTimeOffset OccurredAt);
