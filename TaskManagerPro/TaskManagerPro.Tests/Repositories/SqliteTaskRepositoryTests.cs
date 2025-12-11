using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using TaskManagerPro.Data.Context;
using TaskManagerPro.Data.Entities;
using TaskManagerPro.Data.Repositories;
using Xunit;

namespace TaskManagerPro.Tests.Repositories;

public class SqliteTaskRepositoryTests
{
    private AppDbContext CreateContext()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString()) // Unique DB per test
            .Options;
        
        var context = new AppDbContext(options);
        context.Database.EnsureCreated();
        return context;
    }

    [Fact]
    public async Task AddAsync_AddsTaskToDatabase()
    {
        // Arrange
        using var context = CreateContext();
        var repo = new SqliteTaskRepository(context);
        var task = new TaskItem { Title = "Test Task" };

        // Act
        await repo.AddAsync(task);

        // Assert
        Assert.Equal(1, await context.Tasks.CountAsync());
        Assert.True(task.Id > 0);
    }

    [Fact]
    public async Task GetAllAsync_ReturnsTasks_OrderedByPriority()
    {
        // Arrange
        using var context = CreateContext();
        var repo = new SqliteTaskRepository(context);

        await repo.AddAsync(new TaskItem { Title = "Low", PriorityScore = 10, CategoryId = 1 });
        await repo.AddAsync(new TaskItem { Title = "High", PriorityScore = 100, CategoryId = 1 });
        await repo.AddAsync(new TaskItem { Title = "Mid", PriorityScore = 50, CategoryId = 1 });

        // Act
        var results = (await repo.GetAllAsync()).ToList();

        // Assert
        Assert.Equal(3, results.Count);
        Assert.Equal("High", results[0].Title);
        Assert.Equal("Mid", results[1].Title);
        Assert.Equal("Low", results[2].Title);
    }
}
