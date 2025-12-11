using System;
using TaskManagerPro.Data.Services;
using Xunit;

namespace TaskManagerPro.Tests.Services;

public class TaskPriorityServiceTests
{
    [Fact]
    public void Calculate_StandardCase_ReturnsCorrectScore()
    {
        // Arrange
        decimal effort = 1.0m;
        int impact = 5;
        int urgency = 5;
        DateTime? due = null;

        // Act
        // Numerator = (5 * 2.0) + (5 * 1.5) = 10 + 7.5 = 17.5
        // Score = 17.5 / 1.0 = 17.5
        decimal score = TaskPriorityService.Calculate(effort, impact, urgency, due);

        // Assert
        Assert.Equal(17.5m, score);
    }

    [Fact]
    public void Calculate_HighUrgency_ReturnsHigherScore()
    {
        // Arrange
        var scoreNormal = TaskPriorityService.Calculate(1.0m, 5, 5, null);
        var scoreUrgent = TaskPriorityService.Calculate(1.0m, 5, 10, null);

        // Assert
        Assert.True(scoreUrgent > scoreNormal);
    }

    [Fact]
    public void Calculate_ZeroEffort_TreatsAsSmallEffort()
    {
        // Arrange
        decimal effort = 0m; 

        // Act
        // treated as 0.1
        // (10 + 7.5) / 0.1 = 175.0
        decimal score = TaskPriorityService.Calculate(effort, 5, 5, null);

        // Assert
        Assert.Equal(175.0m, score);
    }

    [Fact]
    public void Calculate_WithDueDateBonus_AddsBonus()
    {
        // Arrange
        var due = DateTime.Now; // Today (0 days remaining)
        // Base = 17.5
        // Bonus (0 days) = 20 * e^0 = 20.0 (approx, depends on exact time diff logic)
        // If remainingDays calculated as near 0 (positive or slightly negative if passed), bonus is ~20.
        
        // Act
        decimal score = TaskPriorityService.Calculate(1.0m, 5, 5, due);

        // Assert
        Assert.True(score > 30.0m); // Should have significant bonus
    }
}
