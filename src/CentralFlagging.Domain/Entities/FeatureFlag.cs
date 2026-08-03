using CentralFlagging.Domain.Enums;

namespace CentralFlagging.Domain.Entities;

public sealed class FeatureFlag
{
    public Guid Id { get; private set; } = Guid.NewGuid();
    public Guid NamespaceId { get; private set; }
    public string Key { get; private set; } = string.Empty;
    public string Description { get; private set; } = string.Empty;
    public FlagType Type { get; private set; } = FlagType.Boolean;
    public bool IsArchived { get; private set; }
    public DateTimeOffset CreatedAt { get; private set; } = DateTimeOffset.UtcNow;
    public DateTimeOffset UpdatedAt { get; private set; } = DateTimeOffset.UtcNow;

    private readonly List<FlagEnvironmentState> _environments = [];
    public IReadOnlyCollection<FlagEnvironmentState> Environments => _environments;

    private FeatureFlag() { }

    public static FeatureFlag Create(
        Guid namespaceId,
        string key,
        string description,
        FlagType type = FlagType.Boolean)
    {
        if (namespaceId == Guid.Empty)
            throw new ArgumentException("Namespace is required.", nameof(namespaceId));
        if (string.IsNullOrWhiteSpace(key))
            throw new ArgumentException("Flag key is required.", nameof(key));

        var flag = new FeatureFlag
        {
            NamespaceId = namespaceId,
            Key = key.Trim().ToLowerInvariant(),
            Description = description?.Trim() ?? string.Empty,
            Type = type
        };

        foreach (EnvironmentKind env in Enum.GetValues<EnvironmentKind>())
        {
            flag._environments.Add(FlagEnvironmentState.CreateDefault(flag.Id, env));
        }

        return flag;
    }

    public void Toggle(EnvironmentKind environment, bool enabled, string defaultValue)
    {
        var state = _environments.Single(e => e.Environment == environment);
        state.SetEnabled(enabled, defaultValue);
        UpdatedAt = DateTimeOffset.UtcNow;
    }

    public void Archive()
    {
        IsArchived = true;
        UpdatedAt = DateTimeOffset.UtcNow;
    }

    public FlagEnvironmentState GetEnvironment(EnvironmentKind environment) =>
        _environments.Single(e => e.Environment == environment);
}

public sealed class FlagEnvironmentState
{
    public Guid Id { get; private set; } = Guid.NewGuid();
    public Guid FlagId { get; private set; }
    public EnvironmentKind Environment { get; private set; }
    public bool Enabled { get; private set; }
    public string DefaultValue { get; private set; } = "false";
    public int RolloutPercent { get; private set; }
    public DateTimeOffset UpdatedAt { get; private set; } = DateTimeOffset.UtcNow;

    private FlagEnvironmentState() { }

    public static FlagEnvironmentState CreateDefault(Guid flagId, EnvironmentKind environment) =>
        new()
        {
            FlagId = flagId,
            Environment = environment,
            Enabled = false,
            DefaultValue = "false",
            RolloutPercent = 0
        };

    public void SetEnabled(bool enabled, string defaultValue)
    {
        Enabled = enabled;
        DefaultValue = string.IsNullOrWhiteSpace(defaultValue) ? (enabled ? "true" : "false") : defaultValue;
        UpdatedAt = DateTimeOffset.UtcNow;
    }

    public void SetRollout(int percent)
    {
        if (percent is < 0 or > 100)
            throw new ArgumentOutOfRangeException(nameof(percent), "Rollout must be 0-100.");
        RolloutPercent = percent;
        UpdatedAt = DateTimeOffset.UtcNow;
    }
}
