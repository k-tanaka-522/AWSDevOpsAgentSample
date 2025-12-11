using System;
using TaskManagerPro.Data.Entities;

namespace TaskManagerPro.Data.Services;

public static class TaskPriorityService
{
    private const decimal WeightUrgency = 2.0m;
    private const decimal WeightImpact = 1.5m;
    private const double MaxBonus = 20.0;
    private const double BonusThresholdDays = 3.0;
    private const double DecayRate = 0.5;

    /// <summary>
    /// Calculates the priority score for a task.
    /// Formula: P = ((U * Wu) + (I * Wi)) / E + Bonus
    /// </summary>
    public static decimal Calculate(TaskItem task)
    {
        if (task == null) return 0;
        return Calculate(task.EffortHours, task.ImpactScore, task.UrgencyScore, task.DueDate);
    }

    public static decimal Calculate(decimal effort, int impact, int urgency, DateTime? dueDate)
    {
        // 1. Validate Effort (prevent division by zero)
        decimal safeEffort = effort <= 0 ? 0.1m : effort;

        // 2. Base Score
        decimal numerator = (urgency * WeightUrgency) + (impact * WeightImpact);
        decimal baseScore = numerator / safeEffort;

        // 3. Date Bonus
        decimal bonus = 0;
        if (dueDate.HasValue)
        {
            double remainingDays = (dueDate.Value - DateTime.Now).TotalDays;
            
            // If strictly less than threshold
            if (remainingDays <= BonusThresholdDays)
            {
                // If overdue, max bonus
                if (remainingDays < 0)
                {
                    bonus = (decimal)MaxBonus;
                }
                else
                {
                    // Exponential decay from 0 days (MaxBonus) to 3 days (small)
                    // Formula: MaxBonus * e^(-k * t)
                    bonus = (decimal)(MaxBonus * Math.Exp(-DecayRate * remainingDays));
                }
            }
        }

        return baseScore + bonus;
    }
}
