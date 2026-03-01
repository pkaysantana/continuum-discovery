$ErrorActionPreference = "Stop"
$BasePath = "C:\Users\Don\continuum-discovery"

# Create Directory Structure
$directories = @(
    "amina_results",
    "research_notes",
    "protocols",
    "unibase_logs",
    "biosecurity_audits"
)

foreach ($dir in $directories) {
    $fullPath = Join-Path -Path $BasePath -ChildPath $dir
    if (!(Test-Path -Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath | Out-Null
        Write-Host "Created directory: $dir"
    } else {
        Write-Host "Directory already exists: $dir"
    }
}

Write-Host "`nInstalling Amina skills for agentic automation..."
# Add Amina skills for agent integration
npx skills add AminoAnalytica/amina-skills --all

Write-Host "`nEnvironment scaffolding complete."
Write-Host "======================================================"
Write-Host "IMPORTANT: Please authenticate with Amina."
Write-Host "Run the following command with your actual API key:"
Write-Host "amina auth set-key `"ami_your_api_key`""
Write-Host "======================================================"
