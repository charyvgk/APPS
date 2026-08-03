using CentralFlagging.Domain.Entities;
using CentralFlagging.Domain.Enums;
using CentralFlagging.Domain.Evaluation;

namespace CentralFlagging.UnitTests;

public class FlagEvaluatorTests
{
    [Fact]
    public void Disabled_flag_returns_disabled_reason()
    {
        var flag = FeatureFlag.Create(Guid.NewGuid(), "checkout_v2", "test");
        var decision = FlagEvaluator.Evaluate("payments", flag, EnvironmentKind.Production, "user-1");

        Assert.False(decision.Enabled);
        Assert.Equal("disabled", decision.Reason);
    }

    [Fact]
    public void Full_rollout_is_stable_enabled()
    {
        var flag = FeatureFlag.Create(Guid.NewGuid(), "checkout_v2", "test");
        flag.Toggle(EnvironmentKind.Production, true, "true");
        flag.GetEnvironment(EnvironmentKind.Production).SetRollout(100);

        var decision = FlagEvaluator.Evaluate("payments", flag, EnvironmentKind.Production, "user-1");

        Assert.True(decision.Enabled);
        Assert.Equal("enabled", decision.Reason);
    }

    [Fact]
    public void Partial_rollout_is_deterministic_per_subject()
    {
        var flag = FeatureFlag.Create(Guid.NewGuid(), "checkout_v2", "test");
        flag.Toggle(EnvironmentKind.Production, true, "true");
        flag.GetEnvironment(EnvironmentKind.Production).SetRollout(50);

        var a1 = FlagEvaluator.Evaluate("payments", flag, EnvironmentKind.Production, "user-a");
        var a2 = FlagEvaluator.Evaluate("payments", flag, EnvironmentKind.Production, "user-a");
        var b1 = FlagEvaluator.Evaluate("payments", flag, EnvironmentKind.Production, "user-b");

        Assert.Equal(a1.Enabled, a2.Enabled);
        Assert.Equal(a1.Reason, a2.Reason);
        // Different subjects may differ; at least evaluate without throw.
        Assert.Contains(b1.Reason, new[] { "rollout_in", "rollout_out" });
    }

    [Fact]
    public void Namespace_normalize_is_lowercase()
    {
        var ns = ProjectNamespace.Create("Payments", "Payments App");
        Assert.Equal("payments", ns.Name);
    }
}
