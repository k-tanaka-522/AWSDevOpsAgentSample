using System;
using CommunityToolkit.Mvvm.ComponentModel;
using TaskManagerPro.Data.Entities;

namespace TaskManagerPro.App.ViewModels;

public partial class TaskDetailViewModel : ObservableObject
{
    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private string _description = string.Empty;

    [ObservableProperty]
    private DateTime? _dueDate;

    [ObservableProperty]
    private decimal _effortHours = 1.0m;

    [ObservableProperty]
    private int _impactScore = 5;

    [ObservableProperty]
    private int _urgencyScore = 5;

    public TaskItem ToEntity()
    {
        return new TaskItem
        {
            Title = Title,
            Description = Description,
            DueDate = DueDate,
            EffortHours = EffortHours,
            ImpactScore = ImpactScore,
            UrgencyScore = UrgencyScore
        };
    }

    public void LoadFromEntity(TaskItem task)
    {
        Title = task.Title;
        Description = task.Description;
        DueDate = task.DueDate;
        EffortHours = task.EffortHours;
        ImpactScore = task.ImpactScore;
        UrgencyScore = task.UrgencyScore;
    }
}
