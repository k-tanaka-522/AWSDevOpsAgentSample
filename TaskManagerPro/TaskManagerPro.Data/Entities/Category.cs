using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace TaskManagerPro.Data.Entities;

[Table("Categories")]
public class Category
{
    [Key]
    public int Id { get; set; }

    [Required]
    public string Name { get; set; } = string.Empty;

    public string ColorHex { get; set; } = "#FFFFFF";

    public int SortOrder { get; set; } = 0;
}
