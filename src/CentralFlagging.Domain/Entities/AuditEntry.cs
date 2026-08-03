using CentralFlagging.Domain.Enums;

namespace CentralFlagging.Domain.Entities;

public sealed class AuditEntry
{
    public Guid Id { get; private set; } = Guid.NewGuid();
    public string NamespaceName { get; private set; } = string.Empty;
    public string? FlagKey { get; private set; }
    public AuditAction Action { get; private set; }
    public string Actor { get; private set; } = "system";
    public string Details { get; private set; } = string.Empty;
    public DateTimeOffset OccurredAt { get; private set; } = DateTimeOffset.UtcNow;

    private AuditEntry() { }

    public static AuditEntry Create(
        string namespaceName,
        AuditAction action,
        string actor,
        string details,
        string? flagKey = null) =>
        new()
        {
            NamespaceName = namespaceName,
            FlagKey = flagKey,
            Action = action,
            Actor = string.IsNullOrWhiteSpace(actor) ? "system" : actor,
            Details = details
        };
}
