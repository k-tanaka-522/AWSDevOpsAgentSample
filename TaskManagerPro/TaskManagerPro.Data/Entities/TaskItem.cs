using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace TaskManagerPro.Data.Entities;

[Table("Tasks")]
public class TaskItem
{
    [Key]
    public int Id { get; set; }

    [Required]
    public string Title { get; set; } = string.Empty;

    public string Description { get; set; } = string.Empty;

    public DateTime? DueDate { get; set; }

    [ForeignKey(nameof(Category))]
    public int CategoryId { get; set; }

    public virtual Category? Category { get; set; }

    public decimal EffortHours { get; set; } = 1.0m;

    public int ImpactScore { get; set; } = 5;

    public int UrgencyScore { get; set; } = 5;

    public decimal PriorityScore { get; set; } = 0.0m;

    public bool IsCompleted { get; set; } = false;

    public DateTime CreatedAt { get; set; } = DateTime.Now;

    public DateTime UpdatedAt { get; set; } = DateTime.Now;
}
