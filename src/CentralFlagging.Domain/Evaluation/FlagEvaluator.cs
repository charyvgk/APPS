using CentralFlagging.Domain.Entities;
using CentralFlagging.Domain.Enums;
using CentralFlagging.Domain.Evaluation;

namespace CentralFlagging.Domain.Evaluation;

public static class FlagEvaluator
{
    /// <summary>
    /// Evaluates a flag for a subject. Rollout uses stable hashing so the same
    /// subject consistently falls in/out of a percentage bucket.
    /// </summary>
    public static FlagDecision Evaluate(
        string namespaceName,
        FeatureFlag flag,
        EnvironmentKind environment,
        string? subjectKey = null)
    {
        if (flag.IsArchived)
        {
            return new FlagDecision(
                namespaceName,
                flag.Key,
                environment,
                Enabled: false,
                Value: "false",
                Reason: "flag_archived");
        }

        var state = flag.GetEnvironment(environment);

        if (!state.Enabled)
        {
            return new FlagDecision(
                namespaceName,
                flag.Key,
                environment,
                Enabled: false,
                Value: state.DefaultValue,
                Reason: "disabled",
                RolloutPercent: state.RolloutPercent);
        }

        // Enabled with 0 or 100 rollout => fully on (0 means "no percentage gating").
        if (state.RolloutPercent is 0 or >= 100)
        {
            return On(namespaceName, flag, environment, state, "enabled");
        }

        if (string.IsNullOrWhiteSpace(subjectKey))
        {
            // Without a subject, treat enabled + partial rollout as on for server defaults,
            // but report reason so callers can require subject-aware evaluation.
            return On(namespaceName, flag, environment, state, "enabled_no_subject");
        }

        var bucket = StableBucket(namespaceName, flag.Key, subjectKey);
        if (bucket < state.RolloutPercent)
        {
            return On(namespaceName, flag, environment, state, "rollout_in");
        }

        return new FlagDecision(
            namespaceName,
            flag.Key,
            environment,
            Enabled: false,
            Value: "false",
            Reason: "rollout_out",
            RolloutPercent: state.RolloutPercent);
    }

    private static FlagDecision On(
        string namespaceName,
        FeatureFlag flag,
        EnvironmentKind environment,
        FlagEnvironmentState state,
        string reason) =>
        new(
            namespaceName,
            flag.Key,
            environment,
            Enabled: true,
            Value: state.DefaultValue,
            Reason: reason,
            RolloutPercent: state.RolloutPercent);

    public static int StableBucket(string ns, string key, string subject)
    {
        var input = $"{ns}:{key}:{subject}";
        unchecked
        {
            // FNV-1a 32-bit
            uint hash = 2166136261;
            foreach (var ch in input)
            {
                hash ^= ch;
                hash *= 16777619;
            }
            return (int)(hash % 100);
        }
    }
}
