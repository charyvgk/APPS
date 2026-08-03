using CentralFlagging.Api.Contracts;
using CentralFlagging.Application.Abstractions;
using CentralFlagging.Application.Services;
using CentralFlagging.Domain.Entities;
using CentralFlagging.Domain.Enums;
using CentralFlagging.Infrastructure;
using CentralFlagging.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.Converters.Add(new JsonStringEnumConverter());
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new()
    {
        Title = "Central Flagging API",
        Version = "v1",
        Description = "Namespaced feature-flag control plane for .NET microservices / apps."
    });
});

var connectionString = builder.Configuration.GetConnectionString("Flagging")
    ?? "Data Source=central-flagging.db";

builder.Services.AddCentralFlaggingInfrastructure(connectionString);
builder.Services.AddCentralFlaggingApplication();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<FlaggingDbContext>();
    await db.Database.EnsureCreatedAsync();
    await SeedAsync(scope.ServiceProvider);
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.MapGet("/", () => Results.Redirect("/swagger"));

app.MapGet("/api/namespaces", async (FlagManagementService mgr, CancellationToken ct) =>
{
    var items = await mgr.ListNamespacesAsync(ct);
    return Results.Ok(items.Select(MapNamespace));
});

app.MapPost("/api/namespaces", async (CreateNamespaceRequest req, FlagManagementService mgr, CancellationToken ct) =>
{
    try
    {
        var ns = await mgr.CreateNamespaceAsync(
            req.Name,
            req.DisplayName ?? req.Name,
            req.OwnerTeam,
            req.Actor ?? "api",
            ct);
        return Results.Created($"/api/namespaces/{ns.Name}", MapNamespace(ns));
    }
    catch (InvalidOperationException ex)
    {
        return Results.Conflict(new { error = ex.Message });
    }
});

app.MapGet("/api/namespaces/{ns}/flags", async (string ns, FlagManagementService mgr, CancellationToken ct) =>
{
    var flags = await mgr.ListFlagsAsync(ns, ct);
    return Results.Ok(flags.Select(MapFlag));
});

app.MapPost("/api/namespaces/{ns}/flags", async (string ns, CreateFlagRequest req, FlagManagementService mgr, CancellationToken ct) =>
{
    try
    {
        var flag = await mgr.CreateFlagAsync(ns, req.Key, req.Description ?? "", req.Type, req.Actor ?? "api", ct);
        return Results.Created($"/api/namespaces/{ns}/flags/{flag.Key}", MapFlag(flag));
    }
    catch (InvalidOperationException ex)
    {
        return Results.Conflict(new { error = ex.Message });
    }
});

app.MapPost("/api/namespaces/{ns}/flags/{key}/toggle", async (
    string ns,
    string key,
    ToggleFlagRequest req,
    FlagManagementService mgr,
    CancellationToken ct) =>
{
    try
    {
        var flag = await mgr.ToggleAsync(
            ns,
            key,
            req.Environment,
            req.Enabled,
            req.DefaultValue,
            req.Actor ?? "api",
            req.RolloutPercent,
            ct);
        return Results.Ok(MapFlag(flag));
    }
    catch (InvalidOperationException ex)
    {
        return Results.NotFound(new { error = ex.Message });
    }
});

app.MapPost("/api/evaluate", async (EvaluateRequest req, IFlagEvaluationService eval, CancellationToken ct) =>
{
    var decision = await eval.EvaluateAsync(req.Namespace, req.FlagKey, req.Environment, req.SubjectKey, ct);
    return Results.Ok(new DecisionDto(
        decision.Namespace,
        decision.FlagKey,
        decision.Environment,
        decision.Enabled,
        decision.Value,
        decision.Reason,
        decision.RolloutPercent));
});

app.MapGet("/api/audit", async (string? ns, IAuditRepository audit, CancellationToken ct) =>
{
    var items = await audit.ListAsync(ns, 100, ct);
    return Results.Ok(items.Select(a => new AuditDto(
        a.Id, a.NamespaceName, a.FlagKey, a.Action.ToString(), a.Actor, a.Details, a.OccurredAt)));
});

app.Run();

static NamespaceDto MapNamespace(ProjectNamespace ns) =>
    new(ns.Id, ns.Name, ns.DisplayName, ns.OwnerTeam, ns.CreatedAt);

static FlagDto MapFlag(FeatureFlag f) =>
    new(
        f.Id,
        f.Key,
        f.Description,
        f.Type,
        f.IsArchived,
        f.Environments.Select(e => new FlagEnvironmentDto(e.Environment, e.Enabled, e.DefaultValue, e.RolloutPercent)).ToList(),
        f.UpdatedAt);

static async Task SeedAsync(IServiceProvider sp)
{
    var mgr = sp.GetRequiredService<FlagManagementService>();
    var existing = await mgr.ListNamespacesAsync();
    if (existing.Count > 0) return;

    await mgr.CreateNamespaceAsync("payments", "Payments", "payments-team", "seed");
    await mgr.CreateNamespaceAsync("lending", "Lending", "lending-team", "seed");
    await mgr.CreateNamespaceAsync("global", "Global", "platform-team", "seed");

    await mgr.CreateFlagAsync("payments", "checkout_v2", "New checkout experience", FlagType.Boolean, "seed");
    await mgr.CreateFlagAsync("payments", "kill.gateway", "Emergency gateway kill switch", FlagType.Boolean, "seed");
    await mgr.CreateFlagAsync("lending", "risk_model_b", "Alternate risk model", FlagType.Boolean, "seed");
    await mgr.CreateFlagAsync("global", "maintenance_mode", "Estate-wide maintenance", FlagType.Boolean, "seed");

    await mgr.ToggleAsync("payments", "checkout_v2", EnvironmentKind.Development, true, "true", "seed");
}

public partial class Program;
