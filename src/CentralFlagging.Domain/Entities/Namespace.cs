namespace CentralFlagging.Domain.Entities;

/// <summary>
/// Isolation boundary keyed by consuming project name (e.g. "payments", "lending").
/// </summary>
public sealed class ProjectNamespace
{
    public Guid Id { get; private set; } = Guid.NewGuid();
    public string Name { get; private set; } = string.Empty;
    public string DisplayName { get; private set; } = string.Empty;
    public string? OwnerTeam { get; private set; }
    public DateTimeOffset CreatedAt { get; private set; } = DateTimeOffset.UtcNow;

    private readonly List<FeatureFlag> _flags = [];
    public IReadOnlyCollection<FeatureFlag> Flags => _flags;

    private ProjectNamespace() { }

    public static ProjectNamespace Create(string name, string displayName, string? ownerTeam = null)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Namespace name is required.", nameof(name));

        return new ProjectNamespace
        {
            Name = Normalize(name),
            DisplayName = string.IsNullOrWhiteSpace(displayName) ? name : displayName.Trim(),
            OwnerTeam = ownerTeam?.Trim()
        };
    }

    public static string Normalize(string name) => name.Trim().ToLowerInvariant();
}
