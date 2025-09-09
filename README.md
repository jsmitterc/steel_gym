# Profile Manager Script

This Python script reads names from a CSV file and automatically activates/deactivates face recognition profiles via the API.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your API key:**
   - Go to your face recognition web app
   - Navigate to the "API Keys" tab
   - Create a new API key and copy it

3. **Configure the script:**
   - Open `profile_manager.py`
   - Replace `YOUR_API_KEY_HERE` with your actual API key
   - Update `API_BASE_URL` if using deployed version (not localhost)

4. **Prepare your CSV file:**
   - Rename your `active.csv` file or update the `CSV_FILE` variable
   - CSV should have names in the first column
   - Can have a header row (script auto-detects)

## CSV Format

The script supports these CSV formats:

**With header:**
```csv
name
John Doe
Jane Smith
Mike Johnson
```

**Without header:**
```csv
John Doe
Jane Smith
Mike Johnson
```

## Usage

```bash
python profile_manager.py
```

## What it does

1. **Reads** all names from the CSV file (case-insensitive)
2. **Fetches** all profiles from your account via API
3. **Compares** each profile name against the CSV list:
   - If name is in CSV → **Activates** the profile
   - If name is NOT in CSV → **Deactivates** the profile
   - If name not found → **Skips** (no error)
4. **Reports** summary of changes made

## Example Output

```
=== Profile Status Sync ===
Read 5 names from active.csv
Found 10 profiles in account

Processing: John Doe
  Current status: Inactive
  Should be: Active
  ✓ Successfully activated

Processing: Old Employee
  Current status: Active  
  Should be: Inactive
  ✓ Successfully deactivated

=== Summary ===
Profiles activated: 3
Profiles deactivated: 2
Profiles skipped (already correct): 5
Errors: 0
Total processed: 10
```

## Troubleshooting

- **"Invalid API key"**: Check your API key is correct and active
- **"CSV file not found"**: Make sure the file exists and path is correct
- **Network errors**: Check if your face recognition app is running
- **Permission errors**: Make sure your API key has the right permissions