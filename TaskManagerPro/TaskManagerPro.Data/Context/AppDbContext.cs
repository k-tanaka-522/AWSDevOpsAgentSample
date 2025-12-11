using System;
using System.IO;
using Microsoft.EntityFrameworkCore;
using TaskManagerPro.Data.Entities;

namespace TaskManagerPro.Data.Context;

public class AppDbContext : DbContext
{
    public DbSet<TaskItem> Tasks { get; set; }
    public DbSet<Category> Categories { get; set; }

    public AppDbContext()
    {
        InitializeDbPath();
    }

    // Constructor for DI/Testing
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
        InitializeDbPath();
    }

    private void InitializeDbPath()
    {
        var folder = Environment.SpecialFolder.LocalApplicationData;
        var path = Environment.GetFolderPath(folder);
        var appFolder = Path.Join(path, "TaskManagerPro");
        Directory.CreateDirectory(appFolder);
        DbPath = Path.Join(appFolder, "tasks.db");
    }

    public string DbPath { get; private set; }

    protected override void OnConfiguring(DbContextOptionsBuilder options)
    {
        if (!options.IsConfigured)
        {
            options.UseSqlite($"Data Source={DbPath}");
        }
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Category>().HasData(
            new Category { Id = 1, Name = "Inbox", ColorHex = "#808080", SortOrder = 0 },
            new Category { Id = 2, Name = "Work", ColorHex = "#0078D4", SortOrder = 1 },
            new Category { Id = 3, Name = "Personal", ColorHex = "#107C10", SortOrder = 2 }
        );

        modelBuilder.Entity<TaskItem>()
            .HasIndex(t => new { t.IsCompleted, t.PriorityScore }); // For performant sorting
    }
}
