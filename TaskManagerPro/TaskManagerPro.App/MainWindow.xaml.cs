using System.Windows;
using TaskManagerPro.App.ViewModels;
using System.Windows.Controls;

namespace TaskManagerPro.App;

public partial class MainWindow : Window
{
    public MainWindow(MainWindowViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        
        // Auto-load data on startup
        Loaded += async (s, e) => 
        {
            try
            {
                await viewModel.LoadCommand.ExecuteAsync(null);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Load Error: {ex.Message}", "Error");
            }
        };
    }
}