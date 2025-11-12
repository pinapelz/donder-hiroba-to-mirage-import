# Importing from Donder Hiroba to Mirage
This repository contains the script to import from Donder Hiroba to [Mirage](https://github.com/pinapelz/Mirage)

# 1. Setup the script

## OPTION A - Executable File (Easy)
Coming soon...

## OPTION B - From Source (Advanced)
1. Install Python. Follow the instructions [here](https://github.com/PackeTsar/Install-Python/blob/master/README.md) if you need help.
2. Download the import [script](https://github.com/pinapelz/donder-hiroba-to-mirage-import/archive/refs/heads/main.zip)
3. Unzip and place all files in some folder
4. Right click and open terminal (Powershell) in this newly created folder
5. Run `Set-ExecutionPolicy Unrestricted -Scope Process` to allow the execution of scripts 
6. Create a virtual environment
```
python3 -m venv venv
.\venv\Scripts\activate
```
7. `pip install -r requirements.txt`

# 2. Refresh Donder Hiroba and Get Token

1. Login to [Donder Hiroba](https://donderhiroba.jp/)
2. Scroll down and navigate to the [Score Data page](https://donderhiroba.jp/score_list.php) by clicking on スコアデータ 閲覧
<img width="304" height="56" alt="image" src="https://github.com/user-attachments/assets/49f65ee8-a609-4b9c-a10c-fcd95412770f" />

3. Refresh your data by clicking on this icon:  <img width="51" height="38" alt="image" src="https://github.com/user-attachments/assets/efd9a501-6b9d-4585-bf86-15a1a4c320c7" />
 on the rop right corner

From here you need to get your token. There are 2 ways to do this

## Option 1: Use Cookie-Editor Extension (Easy)
1. Download the browser extension [Cookie-Editor](cookie-editor.com)
2. Click on the extension and click `_token_v2`, then copy the Value there. That's it!

## Option 2: Use Browser Network Tab (slightly more complicated)
1. Right click the page and click Inspect/Inspect Elements
2. Click on the "Network" tab
<img width="961" height="38" alt="image" src="https://github.com/user-attachments/assets/7a4e85b8-e577-4316-8b69-46cba12343ce" />

3. Refresh the page
4. Now a bunch of requests will show up. In the Filter input, type in `rank_list`. A single request should be left
<img width="1141" height="100" alt="image" src="https://github.com/user-attachments/assets/d7bcde26-e0b6-4383-8537-42f99f2a6f80" />

5. Click on the row and then select the Cookies tab
6. Copy the `_token_v2` value shown there without the quotes
<img width="450" height="222" alt="image" src="https://github.com/user-attachments/assets/82ba4a5c-79df-4c04-a008-d6a91ee8e073" />


# 3. Running the Script
Go back to the terminal you had open in Part 1.

If you used the Source method (Option A), you can now finally export your scores by running
```
python3 taiko_donder_hiroba_export.py --token <YOUR_TOKEN_VALUE>
```

Option B.. Coming soon....
