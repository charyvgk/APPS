namespace CentralFlagging.Domain.Enums;

public enum FlagType
{
    Boolean = 0,
    String = 1,
    Number = 2,
    Json = 3
}

public enum EnvironmentKind
{
    Development = 0,
    Staging = 1,
    Production = 2
}

public enum AuditAction
{
    Created = 0,
    Updated = 1,
    Toggled = 2,
    Archived = 3,
    Evaluated = 4
}
