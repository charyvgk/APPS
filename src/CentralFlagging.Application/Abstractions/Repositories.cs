using CentralFlagging.Domain.Entities;
using CentralFlagging.Domain.Enums;
using CentralFlagging.Domain.Evaluation;

namespace CentralFlagging.Application.Abstractions;

public interface INamespaceRepository
{
    Task<ProjectNamespace?> GetByNameAsync(string name, CancellationToken ct = default);
    Task<IReadOnlyList<ProjectNamespace>> ListAsync(CancellationToken ct = default);
    Task AddAsync(ProjectNamespace ns, CancellationToken ct = default);
}

public interface IFlagRepository
{
    Task<FeatureFlag?> GetAsync(string namespaceName, string flagKey, CancellationToken ct = default);
    Task<IReadOnlyList<FeatureFlag>> ListByNamespaceAsync(string namespaceName, CancellationToken ct = default);
    Task AddAsync(FeatureFlag flag, CancellationToken ct = default);
    Task SaveChangesAsync(CancellationToken ct = default);
}

public interface IAuditRepository
{
    Task AddAsync(AuditEntry entry, CancellationToken ct = default);
    Task<IReadOnlyList<AuditEntry>> ListAsync(string? namespaceName, int take = 100, CancellationToken ct = default);
}

public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}

public interface IFlagEvaluationService
{
    Task<FlagDecision> EvaluateAsync(
        string namespaceName,
        string flagKey,
        EnvironmentKind environment,
        string? subjectKey = null,
        CancellationToken ct = default);
}
