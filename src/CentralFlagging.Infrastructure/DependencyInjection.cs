using CentralFlagging.Application.Abstractions;
using CentralFlagging.Domain.Entities;
using CentralFlagging.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;

namespace CentralFlagging.Infrastructure;

public sealed class NamespaceRepository(FlaggingDbContext db) : INamespaceRepository
{
    public Task<ProjectNamespace?> GetByNameAsync(string name, CancellationToken ct = default)
    {
        var normalized = ProjectNamespace.Normalize(name);
        return db.Namespaces.FirstOrDefaultAsync(x => x.Name == normalized, ct);
    }

    public async Task<IReadOnlyList<ProjectNamespace>> ListAsync(CancellationToken ct = default) =>
        await db.Namespaces.OrderBy(x => x.Name).ToListAsync(ct);

    public async Task AddAsync(ProjectNamespace ns, CancellationToken ct = default) =>
        await db.Namespaces.AddAsync(ns, ct);
}

public sealed class FlagRepository(FlaggingDbContext db) : IFlagRepository
{
    public async Task<FeatureFlag?> GetAsync(string namespaceName, string flagKey, CancellationToken ct = default)
    {
        var ns = ProjectNamespace.Normalize(namespaceName);
        var key = flagKey.Trim().ToLowerInvariant();
        var project = await db.Namespaces.AsNoTracking().FirstOrDefaultAsync(x => x.Name == ns, ct);
        if (project is null) return null;

        return await db.Flags
            .Include(f => f.Environments)
            .FirstOrDefaultAsync(f => f.NamespaceId == project.Id && f.Key == key, ct);
    }

    public async Task<IReadOnlyList<FeatureFlag>> ListByNamespaceAsync(string namespaceName, CancellationToken ct = default)
    {
        var ns = ProjectNamespace.Normalize(namespaceName);
        var project = await db.Namespaces.AsNoTracking().FirstOrDefaultAsync(x => x.Name == ns, ct);
        if (project is null) return [];

        return await db.Flags
            .Include(f => f.Environments)
            .Where(f => f.NamespaceId == project.Id)
            .OrderBy(f => f.Key)
            .ToListAsync(ct);
    }

    public async Task AddAsync(FeatureFlag flag, CancellationToken ct = default) =>
        await db.Flags.AddAsync(flag, ct);

    public Task SaveChangesAsync(CancellationToken ct = default) => db.SaveChangesAsync(ct);
}

public sealed class AuditRepository(FlaggingDbContext db) : IAuditRepository
{
    public async Task AddAsync(AuditEntry entry, CancellationToken ct = default) =>
        await db.AuditEntries.AddAsync(entry, ct);

    public async Task<IReadOnlyList<AuditEntry>> ListAsync(string? namespaceName, int take = 100, CancellationToken ct = default)
    {
        var q = db.AuditEntries.AsNoTracking().AsQueryable();
        if (!string.IsNullOrWhiteSpace(namespaceName))
        {
            var ns = ProjectNamespace.Normalize(namespaceName);
            q = q.Where(x => x.NamespaceName == ns);
        }

        return await q.OrderByDescending(x => x.OccurredAt).Take(take).ToListAsync(ct);
    }
}

public sealed class UnitOfWork(FlaggingDbContext db) : IUnitOfWork
{
    public Task<int> SaveChangesAsync(CancellationToken ct = default) => db.SaveChangesAsync(ct);
}

public static class InfrastructureServiceCollectionExtensions
{
    public static IServiceCollection AddCentralFlaggingInfrastructure(
        this IServiceCollection services,
        string connectionString)
    {
        services.AddDbContext<FlaggingDbContext>(opt => opt.UseSqlite(connectionString));
        services.AddScoped<INamespaceRepository, NamespaceRepository>();
        services.AddScoped<IFlagRepository, FlagRepository>();
        services.AddScoped<IAuditRepository, AuditRepository>();
        services.AddScoped<IUnitOfWork, UnitOfWork>();
        return services;
    }
}
