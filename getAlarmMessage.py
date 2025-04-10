import os
import re
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# -------------------------------
# Step 1: Parse log files
# -------------------------------

log_directory = "./Logs"

alarm_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - INFO - <<ALARM%(\d+)%(.+?)>>")
sot_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - INFO - <<(\d+)%SOT>>")

alarm_data = []

for robot_folder in os.listdir(log_directory):
    robot_path = os.path.join(log_directory, robot_folder)
    if not os.path.isdir(robot_path) or not robot_folder.startswith("Robot"):
        continue

    for date_folder in os.listdir(robot_path):
        date_path = os.path.join(robot_path, date_folder)
        if not os.path.isdir(date_path):
            continue

        for log_file in os.listdir(date_path):
            log_path = os.path.join(date_path, log_file)
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        match_alarm = alarm_pattern.search(line)
                        if match_alarm:
                            date, alarm_code, alarm_msg = match_alarm.groups()
                            alarm_data.append([date, f"<<ALARM%{alarm_code}%{alarm_msg}>>", alarm_code, alarm_msg])
                            continue

                        match_sot = sot_pattern.search(line)
                        if match_sot:
                            date, site_no = match_sot.groups()
                            alarm_data.append([date, f"<<{site_no}%SOT>>", "SOT", f"SLT1 Site{site_no} Insertion"])
            except Exception as e:
                print(f"Error reading {log_path}: {e}")

df = pd.DataFrame(alarm_data, columns=["Date", "Alarm", "Alarm Code", "Alarm Message"])
df.to_csv("extracted_alarm_logs.csv", index=False)
print("Saved: extracted_alarm_logs.csv")

# -------------------------------
# Step 2: Process and group by 3 days
# -------------------------------

df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d %H:%M:%S,%f")
df['Day'] = df['Date'].dt.date

# Filter alarm types
ic_jams = [
    "SLT1 Site1 IC Jam",
    "SLT1 Site2 IC Jam",
    "SLT1 Site3 IC Jam",
    "SLT1 Site4 IC Jam"
]
insertions = [
    "SLT1 Site1 Insertion",
    "SLT1 Site2 Insertion",
    "SLT1 Site3 Insertion",
    "SLT1 Site4 Insertion"
]

df_alarm = df[df['Alarm Message'].isin(ic_jams)].copy()
df_insert = df[df['Alarm Message'].isin(insertions)].copy()

df_alarm['Day'] = pd.to_datetime(df_alarm['Day'])
df_insert['Day'] = pd.to_datetime(df_insert['Day'])

# Daily counts
daily_alarms = df_alarm.groupby(['Day', 'Alarm Message']).size().unstack(fill_value=0)
daily_insertions = df_insert.groupby('Day').size()

# Align full range
start = min(daily_alarms.index.min(), daily_insertions.index.min())
end = max(daily_alarms.index.max(), daily_insertions.index.max())
full_range = pd.date_range(start=start, end=end, freq='D')

daily_alarms = daily_alarms.reindex(full_range, fill_value=0)
daily_insertions = daily_insertions.reindex(full_range, fill_value=0)

# Group into 5-day bins
alarms_5d = daily_alarms.groupby(pd.Grouper(freq='5D')).sum()
insertions_5d = daily_insertions.groupby(pd.Grouper(freq='5D')).sum()

print(alarms_5d)
print(insertions_5d)

# -------------------------------
# Step 3: Plot bar + line overlay
# -------------------------------

# Reset index to get 'Date' column
alarms_5d_reset = alarms_5d.reset_index().rename(columns={alarms_5d.index.name or 'index': 'Interval'})
insertions_5d_reset = insertions_5d.reset_index().rename(columns={insertions_5d.index.name or 'index': 'Interval'})

# Plot using manual axes
fig, ax = plt.subplots(figsize=(14, 6))

# Plot bars per alarm type
bar_width = 3  # Width of each 5-day bar
x = alarms_5d_reset['Interval']

bottom = None
for column in alarms_5d.columns:
    if bottom is None:
        bars = ax.bar(x, alarms_5d_reset[column], width=bar_width, label=column)
        bottom = alarms_5d_reset[column].copy()
    else:
        bars = ax.bar(x, alarms_5d_reset[column], width=bar_width, bottom=bottom, label=column)
        bottom += alarms_5d_reset[column]

# Overlay insertion line
ax.plot(insertions_5d_reset['Interval'], insertions_5d_reset.iloc[:, 1],
        color='black', linestyle='--', marker='o', linewidth=1, label='Total Insertions')

# Formatting
ax.set_title("5-Day Alarm Occurrences with Insertions")
ax.set_xlabel("5-Day Interval")
ax.set_ylabel("Count")
ax.legend(title="Alarm Type + Insertions", bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig("5-Day_Alarm_With_Insertions_FIXED.png", dpi=300)
print("Saved: 5-Day_Alarm_With_Insertions_FIXED.png")
