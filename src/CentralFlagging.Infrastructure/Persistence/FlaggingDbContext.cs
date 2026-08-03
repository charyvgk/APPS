using CentralFlagging.Domain.Entities;
using CentralFlagging.Domain.Enums;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace CentralFlagging.Infrastructure.Persistence;

public sealed class FlaggingDbContext(DbContextOptions<FlaggingDbContext> options) : DbContext(options)
{
    public DbSet<ProjectNamespace> Namespaces => Set<ProjectNamespace>();
    public DbSet<FeatureFlag> Flags => Set<FeatureFlag>();
    public DbSet<FlagEnvironmentState> FlagEnvironments => Set<FlagEnvironmentState>();
    public DbSet<AuditEntry> AuditEntries => Set<AuditEntry>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfiguration(new NamespaceConfig());
        modelBuilder.ApplyConfiguration(new FeatureFlagConfig());
        modelBuilder.ApplyConfiguration(new FlagEnvironmentConfig());
        modelBuilder.ApplyConfiguration(new AuditEntryConfig());
    }
}

file sealed class NamespaceConfig : IEntityTypeConfiguration<ProjectNamespace>
{
    public void Configure(EntityTypeBuilder<ProjectNamespace> b)
    {
        b.ToTable("namespaces");
        b.HasKey(x => x.Id);
        b.Property(x => x.Name).HasMaxLength(128).IsRequired();
        b.HasIndex(x => x.Name).IsUnique();
        b.Property(x => x.DisplayName).HasMaxLength(256).IsRequired();
        b.Property(x => x.OwnerTeam).HasMaxLength(256);
        b.Ignore(x => x.Flags);
    }
}

file sealed class FeatureFlagConfig : IEntityTypeConfiguration<FeatureFlag>
{
    public void Configure(EntityTypeBuilder<FeatureFlag> b)
    {
        b.ToTable("flags");
        b.HasKey(x => x.Id);
        b.Property(x => x.Key).HasMaxLength(128).IsRequired();
        b.Property(x => x.Description).HasMaxLength(1024);
        b.Property(x => x.Type).HasConversion<string>().HasMaxLength(32);
        b.HasIndex(x => new { x.NamespaceId, x.Key }).IsUnique();
        b.HasMany(x => x.Environments)
            .WithOne()
            .HasForeignKey(x => x.FlagId)
            .OnDelete(DeleteBehavior.Cascade);
        b.Navigation(x => x.Environments).UsePropertyAccessMode(PropertyAccessMode.Field);
    }
}

file sealed class FlagEnvironmentConfig : IEntityTypeConfiguration<FlagEnvironmentState>
{
    public void Configure(EntityTypeBuilder<FlagEnvironmentState> b)
    {
        b.ToTable("flag_environments");
        b.HasKey(x => x.Id);
        b.Property(x => x.Environment).HasConversion<string>().HasMaxLength(32);
        b.Property(x => x.DefaultValue).HasMaxLength(4096);
        b.HasIndex(x => new { x.FlagId, x.Environment }).IsUnique();
    }
}

file sealed class AuditEntryConfig : IEntityTypeConfiguration<AuditEntry>
{
    public void Configure(EntityTypeBuilder<AuditEntry> b)
    {
        b.ToTable("audit_entries");
        b.HasKey(x => x.Id);
        b.Property(x => x.NamespaceName).HasMaxLength(128).IsRequired();
        b.Property(x => x.FlagKey).HasMaxLength(128);
        b.Property(x => x.Action).HasConversion<string>().HasMaxLength(32);
        b.Property(x => x.Actor).HasMaxLength(256);
        b.Property(x => x.Details).HasMaxLength(2048);
        b.HasIndex(x => x.OccurredAt);
    }
}
