# CleanAndAdd.ps1
# Cleans unwanted keys and adds "type": 1 and "expression": "" at the top of each JSON file
# Expression value is extracted from the last 3-digit number in the filename

# Keys to remove
$removeKeys = @("Unknown00", "FileId", "Unknown24", "Transparency", "DataLen")

Get-ChildItem -Filter *.json | ForEach-Object {
    Write-Host "Processing $($_.Name)..."

    # Extract the last 3-digit number from filename (without extension)
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    $expressionValue = ""
    
    # Use regex to find the last 3-digit number in the filename
    if ($baseName -match '(\d{3})(?!.*\d{3})') {
        $expressionValue = $matches[1]
        Write-Host "  Found expression value: $expressionValue"
    } else {
        Write-Host "  Warning: No 3-digit number found in filename, using empty string"
    }

    # Read JSON
    $json = Get-Content $_.FullName | ConvertFrom-Json

    # Remove unwanted properties
    $cleaned = $json | Select-Object * -ExcludeProperty $removeKeys

    # Ensure type and expression exist with appropriate values
    if (-not $cleaned.PSObject.Properties.Name.Contains("type")) {
        $cleaned | Add-Member -NotePropertyName "type" -NotePropertyValue 1
    }
    if (-not $cleaned.PSObject.Properties.Name.Contains("expression")) {
        $cleaned | Add-Member -NotePropertyName "expression" -NotePropertyValue $expressionValue
    } else {
        # Update existing expression value
        $cleaned.expression = $expressionValue
    }

    # Reorder so "type" then "expression" come first
    $ordered = [PSCustomObject]@{
        type       = 1
        expression = $expressionValue
    }

    foreach ($prop in $cleaned.PSObject.Properties.Name) {
        if ($prop -ne "type" -and $prop -ne "expression") {
            $ordered | Add-Member -NotePropertyName $prop -NotePropertyValue $cleaned.$prop
        }
    }

    # Write back to file (overwrite)
    $ordered | ConvertTo-Json -Depth 10 | Set-Content $_.FullName -Encoding UTF8
}

Write-Host "All JSON files processed successfully!"