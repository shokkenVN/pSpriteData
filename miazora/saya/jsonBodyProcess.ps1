# CleanAndAdd.ps1
# Cleans unwanted keys and adds "type": 1 and "outfit": "" at the top of each JSON file

# Keys to remove
$removeKeys = @("Unknown00", "FileId", "Unknown24", "Transparency", "DataLen")

Get-ChildItem -Filter *.json | ForEach-Object {
    Write-Host "Processing $($_.Name)..."

    # Read JSON
    $json = Get-Content $_.FullName | ConvertFrom-Json

    # Remove unwanted properties
    $cleaned = $json | Select-Object * -ExcludeProperty $removeKeys

    # Ensure type and outfit exist
    if (-not $cleaned.PSObject.Properties.Name.Contains("type")) {
        $cleaned | Add-Member -NotePropertyName "type" -NotePropertyValue 0
    }
    if (-not $cleaned.PSObject.Properties.Name.Contains("outfit")) {
        $cleaned | Add-Member -NotePropertyName "outfit" -NotePropertyValue ""
    }

    # Reorder so "type" then "outfit" come first
    $ordered = [PSCustomObject]@{
        type       = 0
        outfit = ""
    }

    foreach ($prop in $cleaned.PSObject.Properties.Name) {
        if ($prop -ne "type" -and $prop -ne "outfit") {
            $ordered | Add-Member -NotePropertyName $prop -NotePropertyValue $cleaned.$prop
        }
    }

    # Write back to file (overwrite)
    $ordered | ConvertTo-Json -Depth 10 | Set-Content $_.FullName -Encoding UTF8
}

Write-Host "All JSON files processed successfully!"
