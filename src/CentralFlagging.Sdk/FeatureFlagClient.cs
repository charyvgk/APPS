using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using CentralFlagging.Domain.Enums;
using CentralFlagging.Domain.Evaluation;
using Microsoft.Extensions.DependencyInjection;

namespace CentralFlagging.Sdk;

public sealed class CentralFlaggingOptions
{
    /// <summary>Base URL of the central flagging API, e.g. https://flags.company.internal</summary>
    public string BaseUrl { get; set; } = "http://localhost:5080";

    /// <summary>Project namespace bound to this consuming application.</summary>
    public string Namespace { get; set; } = string.Empty;

    public EnvironmentKind Environment { get; set; } = EnvironmentKind.Production;
}

public interface IFeatureFlagClient
{
    Task<FlagDecision> EvaluateAsync(string flagKey, string? subjectKey = null, CancellationToken ct = default);
    Task<bool> IsEnabledAsync(string flagKey, string? subjectKey = null, CancellationToken ct = default);
}

public sealed class FeatureFlagClient(HttpClient http, CentralFlaggingOptions options) : IFeatureFlagClient
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        Converters = { new JsonStringEnumConverter() }
    };

    public async Task<FlagDecision> EvaluateAsync(string flagKey, string? subjectKey = null, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(options.Namespace))
            throw new InvalidOperationException("CentralFlagging:Namespace must be configured for this application.");

        var payload = new
        {
            Namespace = options.Namespace,
            FlagKey = flagKey,
            Environment = options.Environment.ToString(),
            SubjectKey = subjectKey
        };

        using var response = await http.PostAsJsonAsync("api/evaluate", payload, ct);
        response.EnsureSuccessStatusCode();
        var dto = await response.Content.ReadFromJsonAsync<DecisionResponse>(JsonOptions, ct)
            ?? throw new InvalidOperationException("Empty evaluation response.");

        return new FlagDecision(
            dto.Namespace,
            dto.FlagKey,
            dto.Environment,
            dto.Enabled,
            dto.Value,
            dto.Reason,
            dto.RolloutPercent);
    }

    public async Task<bool> IsEnabledAsync(string flagKey, string? subjectKey = null, CancellationToken ct = default)
    {
        var decision = await EvaluateAsync(flagKey, subjectKey, ct);
        return decision.Enabled;
    }

    private sealed record DecisionResponse(
        string Namespace,
        string FlagKey,
        EnvironmentKind Environment,
        bool Enabled,
        string Value,
        string Reason,
        int? RolloutPercent);
}

public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddCentralFlaggingSdk(
        this IServiceCollection services,
        Action<CentralFlaggingOptions> configure)
    {
        var options = new CentralFlaggingOptions();
        configure(options);
        services.AddSingleton(options);
        services.AddHttpClient<IFeatureFlagClient, FeatureFlagClient>(client =>
        {
            client.BaseAddress = new Uri(options.BaseUrl.TrimEnd('/') + "/");
            client.Timeout = TimeSpan.FromSeconds(3);
        });
        return services;
    }
}
