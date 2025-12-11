using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using TaskManagerPro.Data.Entities;
using TaskManagerPro.Data.Repositories;
using TaskManagerPro.Data.Services;

namespace TaskManagerPro.App.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    private readonly ITaskRepository _repository;

    [ObservableProperty]
    private ObservableCollection<TaskItem> _tasks = new();

    [ObservableProperty]
    private TaskItem? _selectedTask;

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private string _statusMessage = "Ready";

    public MainWindowViewModel(ITaskRepository repository)
    {
        _repository = repository;
    }

    [RelayCommand]
    public async Task LoadAsync()
    {
        try
        {
            IsLoading = true;
            StatusMessage = "Loading tasks...";
            var items = await _repository.GetAllAsync();
            Tasks = new ObservableCollection<TaskItem>(items);
            StatusMessage = $"Loaded {Tasks.Count} tasks.";
        }
        catch (System.Exception ex)
        {
            StatusMessage = $"Error: {ex.Message}";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    public async Task AddTaskAsync()
    {
        // For MVP, we'll just add a dummy task or open a dialog (which we'll implement later)
        // Here implies opening a dialog logic, which usually requires a Navigation Service or Dialog Service.
        // For now, we stub it.
        StatusMessage = "Add Task clicked (Dialog not implemented yet).";
        
        // MVP: Add a test task directly to verify end-to-end
        var newTask = new TaskItem
        {
            Title = "New Task",
            EffortHours = 1.0m,
            ImpactScore = 5,
            UrgencyScore = 5,
            DueDate = System.DateTime.Now.AddDays(3),
            CategoryId = 1 // Ensure valid FK
        };
        newTask.PriorityScore = TaskPriorityService.Calculate(newTask);

        await _repository.AddAsync(newTask);
        await LoadAsync(); // Refresh
    }

    [RelayCommand]
    public async Task CompleteTaskAsync(TaskItem? task)
    {
        if (task == null) return;

        task.IsCompleted = true;
        await _repository.UpdateAsync(task);
        await LoadAsync();
        StatusMessage = $"Completed: {task.Title}";
    }

    [RelayCommand]
    public async Task DeleteTaskAsync(TaskItem? task)
    {
         if (task == null) return;
         
         await _repository.DeleteAsync(task.Id);
         await LoadAsync();
         StatusMessage = $"Deleted: {task.Title}";
    }
}
