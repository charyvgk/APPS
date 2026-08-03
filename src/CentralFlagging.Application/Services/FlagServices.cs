using CentralFlagging.Application.Abstractions;
using CentralFlagging.Domain.Entities;
using CentralFlagging.Domain.Enums;
using CentralFlagging.Domain.Evaluation;
using Microsoft.Extensions.DependencyInjection;

namespace CentralFlagging.Application.Services;

public sealed class FlagEvaluationService(IFlagRepository flags) : IFlagEvaluationService
{
    public async Task<FlagDecision> EvaluateAsync(
        string namespaceName,
        string flagKey,
        EnvironmentKind environment,
        string? subjectKey = null,
        CancellationToken ct = default)
    {
        var ns = ProjectNamespace.Normalize(namespaceName);
        var flag = await flags.GetAsync(ns, flagKey, ct);
        if (flag is null)
        {
            return new FlagDecision(ns, flagKey.ToLowerInvariant(), environment, false, "false", "flag_not_found");
        }

        // Change/audit trail is recorded on management mutations, not on hot-path evaluation.
        return FlagEvaluator.Evaluate(ns, flag, environment, subjectKey);
    }
}

public sealed class FlagManagementService(
    INamespaceRepository namespaces,
    IFlagRepository flags,
    IAuditRepository audit,
    IUnitOfWork uow)
{
    public async Task<ProjectNamespace> CreateNamespaceAsync(string name, string displayName, string? ownerTeam, string actor, CancellationToken ct = default)
    {
        var existing = await namespaces.GetByNameAsync(name, ct);
        if (existing is not null)
            throw new InvalidOperationException($"Namespace '{ProjectNamespace.Normalize(name)}' already exists.");

        var ns = ProjectNamespace.Create(name, displayName, ownerTeam);
        await namespaces.AddAsync(ns, ct);
        await audit.AddAsync(AuditEntry.Create(ns.Name, AuditAction.Created, actor, $"Created namespace {ns.DisplayName}"), ct);
        await uow.SaveChangesAsync(ct);
        return ns;
    }

    public Task<IReadOnlyList<ProjectNamespace>> ListNamespacesAsync(CancellationToken ct = default) =>
        namespaces.ListAsync(ct);

    public async Task<FeatureFlag> CreateFlagAsync(
        string namespaceName,
        string key,
        string description,
        FlagType type,
        string actor,
        CancellationToken ct = default)
    {
        var ns = await namespaces.GetByNameAsync(namespaceName, ct)
            ?? throw new InvalidOperationException($"Namespace '{namespaceName}' not found.");

        var existing = await flags.GetAsync(ns.Name, key, ct);
        if (existing is not null)
            throw new InvalidOperationException($"Flag '{key}' already exists in '{ns.Name}'.");

        var flag = FeatureFlag.Create(ns.Id, key, description, type);
        await flags.AddAsync(flag, ct);
        await audit.AddAsync(AuditEntry.Create(ns.Name, AuditAction.Created, actor, $"Created flag {flag.Key}", flag.Key), ct);
        await uow.SaveChangesAsync(ct);
        return flag;
    }

    public async Task<FeatureFlag> ToggleAsync(
        string namespaceName,
        string flagKey,
        EnvironmentKind environment,
        bool enabled,
        string? defaultValue,
        string actor,
        int? rolloutPercent = null,
        CancellationToken ct = default)
    {
        var flag = await flags.GetAsync(namespaceName, flagKey, ct)
            ?? throw new InvalidOperationException($"Flag '{flagKey}' not found in '{namespaceName}'.");

        flag.Toggle(environment, enabled, defaultValue ?? (enabled ? "true" : "false"));
        if (rolloutPercent is int pct)
            flag.GetEnvironment(environment).SetRollout(pct);
        else if (enabled)
            flag.GetEnvironment(environment).SetRollout(100);
        else
            flag.GetEnvironment(environment).SetRollout(0);

        await audit.AddAsync(
            AuditEntry.Create(
                ProjectNamespace.Normalize(namespaceName),
                AuditAction.Toggled,
                actor,
                $"{environment} => enabled={enabled}, value={defaultValue}, rollout={rolloutPercent}",
                flag.Key),
            ct);
        await uow.SaveChangesAsync(ct);
        return flag;
    }

    public Task<IReadOnlyList<FeatureFlag>> ListFlagsAsync(string namespaceName, CancellationToken ct = default) =>
        flags.ListByNamespaceAsync(namespaceName, ct);
}

public static class ApplicationServiceCollectionExtensions
{
    public static IServiceCollection AddCentralFlaggingApplication(this IServiceCollection services)
    {
        services.AddScoped<IFlagEvaluationService, FlagEvaluationService>();
        services.AddScoped<FlagManagementService>();
        return services;
    }
}
