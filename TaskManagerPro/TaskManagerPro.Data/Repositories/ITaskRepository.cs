using System.Collections.Generic;
using System.Threading.Tasks;
using TaskManagerPro.Data.Entities;

namespace TaskManagerPro.Data.Repositories;

public interface ITaskRepository
{
    Task<IEnumerable<TaskItem>> GetAllAsync();
    Task<TaskItem?> GetByIdAsync(int id);
    Task AddAsync(TaskItem task);
    Task UpdateAsync(TaskItem task);
    Task DeleteAsync(int id);
}
