<<<<<<< HEAD
import io
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(
 page_title="Social Media vs Productivity",
 page_icon="📱",
 layout="wide",
)

sns.set_theme(style="whitegrid")

RAW_PATH = "data/raw/social_media_vs_productivity.csv"


### WEEK 2 LOADING AND CLEANING
@st.cache_data
def load_raw_data():
 """
 Loads the raw dataset and captures the exact 'Required Code Areas'
 outputs (head, tail, shape, info, describe, missing values, duplicates)
 so they can be displayed as-is on the Data Understanding page.
 """
 df = pd.read_csv(RAW_PATH)
 head = df.head()
 tail = df.tail()
 shape = df.shape
 buffer = io.StringIO()
 df.info(buf=buffer)
 info_str = buffer.getvalue()

 describe = df.describe()
 nulls = df.isnull().sum()
 duplicates = df.duplicated().sum()

 summary = {
  "head": head,
  "tail": tail,
  "shape": shape,
  "info": info_str,
  "describe": describe,
  "nulls": nulls,
  "duplicates": duplicates,
 }

 return df, summary


@st.cache_data
def clean_raw_data(df_raw):
 """
 Performs the required cleaning steps and returns a cleaned dataframe
 """
 # Create a copy to prevent mutating the cached raw data
 df = df_raw.copy()
 log = []

 # Step 1: Remove duplicate rows
 before = len(df)
 df = df.drop_duplicates()
 log.append(
  f"Removed duplicate rows: {before - len(df)} duplicates found and dropped."
 )

 # Step 2: Handle missing values
 # Replace missing numerical metrics with their median
 if "daily_social_media_time" in df.columns:
  df["daily_social_media_time"] = df[
   "daily_social_media_time"
  ].fillna(df["daily_social_media_time"].median())
 if "job_satisfaction_score" in df.columns:
  df["job_satisfaction_score"] = df[
   "job_satisfaction_score"
  ].fillna(df["job_satisfaction_score"].median())
 log.append("Replaced missing values in numerical columns with their medians.")

 # Step 3: Round continuous floating-point metrics to 2 decimal places safely
 cols_to_round = [
  "daily_social_media_time",
  "work_hours_per_day",
  "actual_productivity_score",
  "weekly_offline_hours",
 ]
 existing_cols = [col for col in cols_to_round if col in df.columns]
 df[existing_cols] = df[existing_cols].round(2)

 # Step 4: Correct logical inconsistencies
 # If a person is Unemployed, set their work hours to 0
 if "job_type" in df.columns and "work_hours_per_day" in df.columns:
  df.loc[df["job_type"] == "Unemployed", "work_hours_per_day"] = 0

 # Step 5: Feature Engineering: Create calculated column
 if (
  "number_of_notifications" in df.columns
  and "actual_productivity_score" in df.columns
 ):
  df["Notification_Intensity"] = df["number_of_notifications"] / (
   df["actual_productivity_score"] + 1
  )
  log.append("Created 'Notification_Intensity' feature.")

 # Step 6: Remove outliers using IQR method for 'daily_social_media_time'
 if "daily_social_media_time" in df.columns:
  Q1 = df["daily_social_media_time"].quantile(0.25)
  Q3 = df["daily_social_media_time"].quantile(0.75)
  IQR = Q3 - Q1
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  df = df[
   (df["daily_social_media_time"] >= lower_bound)
   & (df["daily_social_media_time"] <= upper_bound)
  ]
  log.append(
   "Removed outliers from 'daily_social_media_time' using IQR method."
  )

 return df, log


df_raw, raw_summary = load_raw_data()
df, cleaning_log = clean_raw_data(df_raw)

PROCESSED_PATH = "data/processed/social_media_vs_productivity_cleaned.csv"
os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
df.to_csv(PROCESSED_PATH, index=False)

# ------------------------------------------------------------------
# PAGE RENDERING
# ------------------------------------------------------------------
st.title("📱 Social Media vs Productivity Analysis")
st.write("KAZI & BRADLEY: The Best Group Presentation")
st.markdown("---")

page=st.sidebar.radio("Navigate App",["Data Understanding", "Data Cleaning", "Analysis 1 & 2",
  "Analysis 3", "Analysis 4", "Analysis 5", "Analysis 6", "Analysis 7", "Analysis 8"])

if page == "Data Understanding":
 st.header("🔍 Data Understanding (Raw Dataset)")

 col1, col2 = st.columns(2)
 with col1:
  st.metric("Total Rows", raw_summary["shape"][0])
 with col2:
  st.metric("Total Columns", raw_summary["shape"][1])

 st.subheader("Data Preview (First 5 Rows)")
 st.dataframe(raw_summary["head"])

 st.subheader("Data Preview (Last 5 Rows)")
 st.dataframe(raw_summary["tail"])

 st.subheader("Dataset Information (dtypes & non-null counts)")
 st.code(raw_summary["info"])

 st.subheader("Descriptive Statistics")
 st.dataframe(raw_summary["describe"])

 st.header("📊 Productivity Comparison")
 st.markdown("---")
   # Scatter Plot: Perceived vs Actual Productivity
 st.subheader("Perceived vs Actual Productivity")

 fig3,ax3=plt.subplots(figsize=(8,6))

 sns.scatterplot(data=df,x="perceived_productivity_score",y="actual_productivity_score",s=35,alpha=0.6,edgecolor="black",linewidth=0.3,ax=ax3)

 sns.regplot(data=df,x="perceived_productivity_score",y="actual_productivity_score",scatter=False,color="red",ax=ax3)

 ax3.set_title("How Productive Are We Actually?")
 ax3.set_xlabel("Perceived Productivity")
 ax3.set_ylabel("Actual Productivity")
 ax3.grid(True)

 st.pyplot(fig3)
 st.write("Turns out, we may not be as productive as we may seem.")

 st.markdown("---")

elif page == "Data Cleaning":
 st.header("🧼 Data Cleaning & Feature Engineering")

 st.subheader("Cleaning Pipeline Log Steps")
 for step in cleaning_log:
  st.success(step)

 st.subheader("Cleaned Dataset Preview")
 st.dataframe(df.head(10))
 col3, col4 = st.columns(2)
 with col3:
  st.subheader("Missing Value Counts")
  st.write(raw_summary["nulls"])
 with col4:
  st.subheader("Duplicate Check")
  st.write(
   f"Number of duplicate rows in raw data: **{raw_summary['duplicates']}**"
  )

 if "Notification_Intensity" in df.columns:
  st.subheader("Engineered Feature: Notification Intensity Preview")
  st.dataframe(
   df[
    [
     "number_of_notifications",
     "actual_productivity_score",
     "Notification_Intensity",
    ]
   ].head()
  )

elif page=="Analysis 1 & 2":

 st.subheader("📊 Visualizations & Analysis")


 # Analysis Question 1
 overFive=df[df["daily_social_media_time"] > 5]

 st.write("### Analysis Question 1")
 st.write("What is the productivity of participants spending more than 5 hours per day on social media?")

 col1,col2=st.columns(2)

 with col1:
  st.metric("Participants",len(overFive))
  st.metric("Average Productivity",round(overFive["actual_productivity_score"].mean(),2))
  st.metric("Average Social Media Time",round(overFive["daily_social_media_time"].mean(),2))

  st.write("Descriptive Statistics")
  st.dataframe(overFive[["daily_social_media_time","actual_productivity_score"]].describe())

 with col2:
  fig1,ax1=plt.subplots(figsize=(8,6))

  sns.scatterplot(data=overFive,x="daily_social_media_time",y="actual_productivity_score",s=35,alpha=0.6,edgecolor="black",linewidth=0.3,ax=ax1)

  sns.regplot(data=overFive,x="daily_social_media_time",y="actual_productivity_score",scatter=False,color="red",ax=ax1)

  ax1.set_xlim(df["daily_social_media_time"].min(),df["daily_social_media_time"].max())
  ax1.set_ylim(df["actual_productivity_score"].min(),df["actual_productivity_score"].max())

  ax1.set_title("Participants Spending More Than 5 Hours on Social Media")
  ax1.set_xlabel("Daily Social Media Time (Hours)")
  ax1.set_ylabel("Actual Productivity Score")
  ax1.grid(True)

  st.pyplot(fig1)

 st.markdown("---")

 # Analysis Question 2
 underFive=df[df["daily_social_media_time"] <=5]

 st.write("### Analysis Question 2")
 st.write("What is the productivity of participants spending 5 hours or less per day on social media?")

 col3,col4=st.columns(2)

 with col3:
  st.metric("Participants",len(underFive))
  st.metric("Average Productivity",round(underFive["actual_productivity_score"].mean(),2))
  st.metric("Average Social Media Time",round(underFive["daily_social_media_time"].mean(),2))

  st.write("Descriptive Statistics")
  st.dataframe(underFive[["daily_social_media_time","actual_productivity_score"]].describe())

 with col4:
  fig2,ax2=plt.subplots(figsize=(8,6))

  sns.scatterplot(data=underFive,x="daily_social_media_time",y="actual_productivity_score",s=35,alpha=0.6,edgecolor="black",linewidth=0.3,ax=ax2)

  sns.regplot(data=underFive,x="daily_social_media_time",y="actual_productivity_score",scatter=False,color="red",ax=ax2)

  ax2.set_xlim(df["daily_social_media_time"].min(),df["daily_social_media_time"].max())
  ax2.set_ylim(df["actual_productivity_score"].min(),df["actual_productivity_score"].max())

  ax2.set_title("Participants Spending 5 Hours or Less on Social Media")
  ax2.set_xlabel("Daily Social Media Time (Hours)")
  ax2.set_ylabel("Actual Productivity Score")
  ax2.grid(True)

  st.pyplot(fig2)
  st.markdown("---")

 st.markdown("---")
 st.subheader("Conclusion")

 st.info("The average productivity scores of the two groups were similar. Based on this dataset, there is little evidence that spending more than five hours on social media is associated with a substantial decrease in productivity.")
elif page=="Analysis 3":
 st.write("If not, who are the most and least productive people?")
 st.markdown("---")
 st.subheader("📊 Productivity Ranking")

 left,right=st.columns(2)

 with left:
  st.markdown("### Most Productive Participants")

  highest=df.sort_values(by="actual_productivity_score",ascending=False)

  st.dataframe(highest[["actual_productivity_score","daily_social_media_time","uses_focus_apps"]].head(10))

  st.metric("Highest Productivity Score",round(highest["actual_productivity_score"].max(),2))
  st.metric("Average Social Media Time",round(highest.head(10)["daily_social_media_time"].mean(),2))

  fig4,ax4=plt.subplots(figsize=(7,5))
  sns.scatterplot(data=highest.head(10),x="daily_social_media_time",y="actual_productivity_score",s=120,alpha=0.8,ax=ax4)
  ax4.set_title("Top 10 Most Productive")
  ax4.set_xlabel("Daily Social Media Time (Hours)")
  ax4.set_ylabel("Actual Productivity Score")
  st.pyplot(fig4)

 with right:
  st.markdown("### Least Productive Participants")

  lowest=df.sort_values(by="actual_productivity_score",ascending=True)

  st.dataframe(lowest[["actual_productivity_score","daily_social_media_time","uses_focus_apps"]].head(10))

  st.metric("Lowest Productivity Score",round(lowest["actual_productivity_score"].min(),2))
  st.metric("Average Social Media Time",round(lowest.head(10)["daily_social_media_time"].mean(),2))

  fig5,ax5=plt.subplots(figsize=(7,5))
  sns.scatterplot(data=lowest.head(10),x="daily_social_media_time",y="actual_productivity_score",s=120,alpha=0.8,ax=ax5)
  ax5.set_title("Bottom 10 Least Productive")
  ax5.set_xlabel("Daily Social Media Time (Hours)")
  ax5.set_ylabel("Actual Productivity Score")
  st.pyplot(fig5)

 st.info("Conclusion: The participants with the highest productivity scores did not consistently spend less time on social media than the least productive participants. This suggests that factors other than social media usage may have a greater influence on productivity.")
elif page=="Analysis 4":
 st.write("Could focus apps explain productivity instead?")
 st.subheader("📊 Analysis Question 4")
 focusApps=df.groupby("uses_focus_apps")["actual_productivity_score"].mean().reset_index()
 st.dataframe(focusApps)
 yesAverage=focusApps.loc[focusApps["uses_focus_apps"]==True,"actual_productivity_score"].values[0]
 noAverage=focusApps.loc[focusApps["uses_focus_apps"]==False,"actual_productivity_score"].values[0]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Uses Focus Apps",
   round(yesAverage,2)
  )

 with col2:
  st.metric(
   "Does Not Use Focus Apps",
   round(noAverage,2)
  )
 fig,ax=plt.subplots(figsize=(8,5))

 sns.boxplot(
  data=df,
  x="uses_focus_apps",
  y="actual_productivity_score",
  ax=ax
 )

 ax.set_title("Actual Productivity by Focus App Usage")
 ax.set_xlabel("Uses Focus Apps")
 ax.set_ylabel("Actual Productivity Score")

 st.pyplot(fig)
 difference=abs(yesAverage-noAverage)

 if difference<2:
  st.success(
   "Conclusion: The average productivity scores of users with and without focus apps were very similar. Based on this dataset, focus apps do not appear to have a strong relationship with productivity."
  )
 else:
  st.success(
   "Conclusion: Users of focus apps had a noticeably different average productivity score, suggesting that focus apps may be associated with productivity."
  )
elif page=="Analysis 5":
 st.write("Does occupation make a difference?")
 st.subheader("📊 Analysis Question 5")

 occupationProductivity=df.groupby("job_type")["actual_productivity_score"].mean().reset_index()
 occupationProductivity=occupationProductivity.sort_values(by="actual_productivity_score",ascending=False)

 st.dataframe(occupationProductivity)

 highestOccupation=occupationProductivity.iloc[0]
 lowestOccupation=occupationProductivity.iloc[-1]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Most Productive Occupation",
   highestOccupation["job_type"],
   )

  st.metric(
   "Average Productivity",
   round(highestOccupation["actual_productivity_score"],2)
   )

 with col2:
  st.metric(
   "Least Productive Occupation",
   lowestOccupation["job_type"],
   )

  st.metric(
   "Average Productivity",
   round(lowestOccupation["actual_productivity_score"],2)
   )

 fig,ax=plt.subplots(figsize=(10,5))

 sns.barplot(
  data=occupationProductivity,
  x="job_type",
  y="actual_productivity_score",
  ax=ax
 )

 ax.set_title("Average Productivity by Occupation")
 ax.set_xlabel("Occupation")
 ax.set_ylabel("Average Productivity Score")
 plt.xticks(rotation=20)

 st.pyplot(fig)

 st.success("Conclusion: Productivity is not reallyy affected by Occupation.")
elif page=="Analysis 6":
 st.write("How common are focus apps?")
 st.subheader("📊 Analysis Question 6")

 focusCounts=df["uses_focus_apps"].value_counts().reset_index()
 focusCounts.columns=["uses_focus_apps","count"]

 st.dataframe(focusCounts)

 yesCount=focusCounts.loc[focusCounts["uses_focus_apps"]==True,"count"].values[0]
 noCount=focusCounts.loc[focusCounts["uses_focus_apps"]==False,"count"].values[0]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Uses Focus Apps",
   yesCount
  )

 with col2:
  st.metric(
   "Does Not Use Focus Apps",
   noCount
  )

 fig,ax=plt.subplots(figsize=(7,5))

 sns.countplot(
  data=df,
  x="uses_focus_apps",
  ax=ax
 )

 ax.set_title("Number of Participants Using Focus Apps")
 ax.set_xlabel("Uses Focus Apps")
 ax.set_ylabel("Number of Participants")

 st.pyplot(fig)

 percentage=(yesCount/len(df))*100

 st.success(
  f"Conclusion: {percentage:.1f}% of participants use focus apps. This helps us understand how common focus apps are before deciding whether they are likely to influence overall productivity."
 ) 
elif page=="Analysis 7":
 st.write("Do notifications play a role in productivity?")
 st.subheader("📊 Analysis Question 7")

 notificationProductivity=df.groupby("number_of_notifications")["actual_productivity_score"].mean().reset_index()

 st.dataframe(notificationProductivity)

 highestNotification=notificationProductivity.loc[notificationProductivity["actual_productivity_score"].idxmax()]
 lowestNotification=notificationProductivity.loc[notificationProductivity["actual_productivity_score"].idxmin()]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Highest Average Productivity",
   round(highestNotification["actual_productivity_score"],2)
  )

  st.metric(
   "Notifications",
   int(highestNotification["number_of_notifications"])
  )

 with col2:
  st.metric(
   "Lowest Average Productivity",
   round(lowestNotification["actual_productivity_score"],2)
  )

  st.metric(
   "Notifications",
   int(lowestNotification["number_of_notifications"])
  )

 fig,ax=plt.subplots(figsize=(9,5))

 sns.lineplot(
  data=notificationProductivity,
  x="number_of_notifications",
  y="actual_productivity_score",
  marker="o",
  ax=ax
 )

 ax.set_title("Average Productivity by Number of Notifications")
 ax.set_xlabel("Number of Notifications")
 ax.set_ylabel("Average Productivity Score")

 st.pyplot(fig)

 correlation=df["number_of_notifications"].corr(df["actual_productivity_score"])

 st.metric(
  "Correlation",
  round(correlation,2)
 )

 if abs(correlation)<0.3:
  st.success(
   "Conclusion: There is only a weak relationship between notifications and productivity."
  )
 elif correlation<0:
  st.success(
   "Conclusion: Productivity tends to decrease as notifications increase."
  )
 else:
  st.success(
   "Conclusion: Productivity tends to increase as notifications increase."
  )
elif page=="Analysis 8":
 st.write("Putting everything together: What really influences productivity?")
 st.subheader("🏆 Kazi & Bradley Final Thesis")

 summary=df.groupby("job_type").agg(
  Average_Productivity=("actual_productivity_score","mean"),
  Average_Social_Media_Time=("daily_social_media_time","mean"),
  Average_Notifications=("number_of_notifications","mean"),
  Focus_App_Users=("uses_focus_apps","mean")
 ).reset_index()

 st.dataframe(summary.round(2))

 col1,col2,col3,col4=st.columns(4)

 with col1:
  st.metric(
   "Overall Productivity",
   round(df["actual_productivity_score"].mean(),2)
  )

 with col2:
  st.metric(
   "Average Social Media Hours",
   round(df["daily_social_media_time"].mean(),2)
  )

 with col3:
  st.metric(
   "Average Notifications",
   round(df["number_of_notifications"].mean(),0)
  )

 with col4:
  st.metric(
   "Focus App Usage",
   str(round(df["uses_focus_apps"].mean()*100,1))+"%"
  )

 fig,ax=plt.subplots(figsize=(11,7))

 scatter=ax.scatter(
  summary["Average_Social_Media_Time"],
  summary["Average_Productivity"],
  s=summary["Average_Notifications"]*3,
  c=summary["Focus_App_Users"],
  cmap="viridis",
  alpha=0.8,
  edgecolors="black"
 )

 for i,row in summary.iterrows():
  ax.text(
   row["Average_Social_Media_Time"]+0.03,
   row["Average_Productivity"]+0.03,
   row["job_type"],
   fontsize=9
  )

 cbar=plt.colorbar(scatter)
 cbar.set_label("Proportion Using Focus Apps")

 ax.set_title("Kazi's Final Thesis\nProductivity by Occupation",fontsize=15,fontweight="bold")
 ax.set_xlabel("Average Daily Social Media Time (Hours)")
 ax.set_ylabel("Average Actual Productivity Score")

 st.pyplot(fig)

 st.markdown("---")

 st.success("""
 ## 📖 Final Thesis

 After analysing the dataset from multiple perspectives, several key findings emerged.

 **1. Social media usage alone was not a strong predictor of productivity.**
 Participants spending more than five hours on social media achieved productivity scores that were remarkably similar to those spending less than five hours.

 **2. Productivity varies more across occupations than across social media usage.**
 Different job types consistently showed different average productivity scores.

 **3. Focus apps showed only a modest relationship with productivity.**
 Users and non-users recorded similar productivity levels, suggesting that simply installing a focus app does not guarantee better performance.

 **4. Notification levels may contribute to distraction, but they do not fully explain productivity differences.**
 Some occupations receive many notifications while maintaining relatively high productivity.

 **Overall Conclusion**

 This project suggests that productivity is influenced by multiple interacting factors rather than one single behaviour. Social media use, focus apps and notifications each contribute part of the picture, but occupation and work context appear to explain more variation than any single variable on its own.

 **TRADE MARK!**

 Productivity is not determined simply by the amount of time spent on social media. Instead, it appears to be the combined result of an individual's work environment, occupation, digital habits and ability to manage distractions. Looking at only one variable provides an incomplete explanation; meaningful insight comes from analysing the relationships between several factors together.
=======
import io
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# PAGE CONFIGURATION
st.set_page_config(
 page_title="Social Media vs Productivity",
 page_icon="📱",
 layout="wide",
)

sns.set_theme(style="whitegrid")

RAW_PATH = "data/raw/social_media_vs_productivity.csv"


### WEEK 2 LOADING AND CLEANING
@st.cache_data
def load_raw_data():
 """
 Loads the raw dataset and captures the exact 'Required Code Areas'
 outputs (head, tail, shape, info, describe, missing values, duplicates)
 so they can be displayed as-is on the Data Understanding page.
 """
 df = pd.read_csv(RAW_PATH)
 head = df.head()
 tail = df.tail()
 shape = df.shape
 buffer = io.StringIO()
 df.info(buf=buffer)
 info_str = buffer.getvalue()

 describe = df.describe()
 nulls = df.isnull().sum()
 duplicates = df.duplicated().sum()

 summary = {
  "head": head,
  "tail": tail,
  "shape": shape,
  "info": info_str,
  "describe": describe,
  "nulls": nulls,
  "duplicates": duplicates,
 }

 return df, summary


@st.cache_data
def clean_raw_data(df_raw):
 """
 Performs the required cleaning steps and returns a cleaned dataframe
 """
 # Create a copy to prevent mutating the cached raw data
 df = df_raw.copy()
 log = []

 # Step 1: Remove duplicate rows
 before = len(df)
 df = df.drop_duplicates()
 log.append(
  f"Removed duplicate rows: {before - len(df)} duplicates found and dropped."
 )

 # Step 2: Handle missing values
 # Replace missing numerical metrics with their median
 if "daily_social_media_time" in df.columns:
  df["daily_social_media_time"] = df[
   "daily_social_media_time"
  ].fillna(df["daily_social_media_time"].median())
 if "job_satisfaction_score" in df.columns:
  df["job_satisfaction_score"] = df[
   "job_satisfaction_score"
  ].fillna(df["job_satisfaction_score"].median())
 log.append("Replaced missing values in numerical columns with their medians.")

 # Step 3: Round continuous floating-point metrics to 2 decimal places safely
 cols_to_round = [
  "daily_social_media_time",
  "work_hours_per_day",
  "actual_productivity_score",
  "weekly_offline_hours",
 ]
 existing_cols = [col for col in cols_to_round if col in df.columns]
 df[existing_cols] = df[existing_cols].round(2)

 # Step 4: Correct logical inconsistencies
 # If a person is Unemployed, set their work hours to 0
 if "job_type" in df.columns and "work_hours_per_day" in df.columns:
  df.loc[df["job_type"] == "Unemployed", "work_hours_per_day"] = 0

 # Step 5: Feature Engineering: Create calculated column
 if (
  "number_of_notifications" in df.columns
  and "actual_productivity_score" in df.columns
 ):
  df["Notification_Intensity"] = df["number_of_notifications"] / (
   df["actual_productivity_score"] + 1
  )
  log.append("Created 'Notification_Intensity' feature.")

 # Step 6: Remove outliers using IQR method for 'daily_social_media_time'
 if "daily_social_media_time" in df.columns:
  Q1 = df["daily_social_media_time"].quantile(0.25)
  Q3 = df["daily_social_media_time"].quantile(0.75)
  IQR = Q3 - Q1
  lower_bound = Q1 - 1.5 * IQR
  upper_bound = Q3 + 1.5 * IQR
  df = df[
   (df["daily_social_media_time"] >= lower_bound)
   & (df["daily_social_media_time"] <= upper_bound)
  ]
  log.append(
   "Removed outliers from 'daily_social_media_time' using IQR method."
  )

 return df, log


df_raw, raw_summary = load_raw_data()
df, cleaning_log = clean_raw_data(df_raw)

PROCESSED_PATH = "data/processed/social_media_vs_productivity_cleaned.csv"
os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
df.to_csv(PROCESSED_PATH, index=False)

# ------------------------------------------------------------------
# PAGE RENDERING
# ------------------------------------------------------------------
st.title("📱 Social Media vs Productivity Analysis")
st.write("KAZI & BRADLEY: The Best Group Presentation")
st.markdown("---")

page=st.sidebar.radio("Navigate App",["Data Understanding", "Data Cleaning", "Analysis 1 & 2",
  "Analysis 3", "Analysis 4", "Analysis 5", "Analysis 6", "Analysis 7", "Analysis 8"])

if page == "Data Understanding":
 st.header("🔍 Data Understanding (Raw Dataset)")

 col1, col2 = st.columns(2)
 with col1:
  st.metric("Total Rows", raw_summary["shape"][0])
 with col2:
  st.metric("Total Columns", raw_summary["shape"][1])

 st.subheader("Data Preview (First 5 Rows)")
 st.dataframe(raw_summary["head"])

 st.subheader("Data Preview (Last 5 Rows)")
 st.dataframe(raw_summary["tail"])

 st.subheader("Dataset Information (dtypes & non-null counts)")
 st.code(raw_summary["info"])

 st.subheader("Descriptive Statistics")
 st.dataframe(raw_summary["describe"])

 st.header("📊 Productivity Comparison")
 st.markdown("---")
   # Scatter Plot: Perceived vs Actual Productivity
 st.subheader("Perceived vs Actual Productivity")

 fig3,ax3=plt.subplots(figsize=(8,6))

 sns.scatterplot(data=df,x="perceived_productivity_score",y="actual_productivity_score",s=35,alpha=0.6,edgecolor="black",linewidth=0.3,ax=ax3)

 sns.regplot(data=df,x="perceived_productivity_score",y="actual_productivity_score",scatter=False,color="red",ax=ax3)

 ax3.set_title("How Productive Are We Actually?")
 ax3.set_xlabel("Perceived Productivity")
 ax3.set_ylabel("Actual Productivity")
 ax3.grid(True)

 st.pyplot(fig3)
 st.write("Turns out, we may not be as productive as we may seem.")

 st.markdown("---")

elif page == "Data Cleaning":
 st.header("🧼 Data Cleaning & Feature Engineering")

 st.subheader("Cleaning Pipeline Log Steps")
 for step in cleaning_log:
  st.success(step)

 st.subheader("Cleaned Dataset Preview")
 st.dataframe(df.head(10))
 col3, col4 = st.columns(2)
 with col3:
  st.subheader("Missing Value Counts")
  st.write(raw_summary["nulls"])
 with col4:
  st.subheader("Duplicate Check")
  st.write(
   f"Number of duplicate rows in raw data: **{raw_summary['duplicates']}**"
  )

 if "Notification_Intensity" in df.columns:
  st.subheader("Engineered Feature: Notification Intensity Preview")
  st.dataframe(
   df[
    [
     "number_of_notifications",
     "actual_productivity_score",
     "Notification_Intensity",
    ]
   ].head()
  )

elif page=="Analysis 1 & 2":

 st.subheader("📊 Visualizations & Analysis")


 # Analysis Question 1
 overFive=df[df["daily_social_media_time"] > 5]

 st.write("### Analysis Question 1")
 st.write("What is the productivity of participants spending more than 5 hours per day on social media?")

 col1,col2=st.columns(2)

 with col1:
  st.metric("Participants",len(overFive))
  st.metric("Average Productivity",round(overFive["actual_productivity_score"].mean(),2))
  st.metric("Average Social Media Time",round(overFive["daily_social_media_time"].mean(),2))

  st.write("Descriptive Statistics")
  st.dataframe(overFive[["daily_social_media_time","actual_productivity_score"]].describe())

 with col2:
  fig1,ax1=plt.subplots(figsize=(8,6))

  sns.scatterplot(data=overFive,x="daily_social_media_time",y="actual_productivity_score",s=35,alpha=0.6,edgecolor="black",linewidth=0.3,ax=ax1)

  sns.regplot(data=overFive,x="daily_social_media_time",y="actual_productivity_score",scatter=False,color="red",ax=ax1)

  ax1.set_xlim(df["daily_social_media_time"].min(),df["daily_social_media_time"].max())
  ax1.set_ylim(df["actual_productivity_score"].min(),df["actual_productivity_score"].max())

  ax1.set_title("Participants Spending More Than 5 Hours on Social Media")
  ax1.set_xlabel("Daily Social Media Time (Hours)")
  ax1.set_ylabel("Actual Productivity Score")
  ax1.grid(True)

  st.pyplot(fig1)

 st.markdown("---")

 # Analysis Question 2
 underFive=df[df["daily_social_media_time"] <=5]

 st.write("### Analysis Question 2")
 st.write("What is the productivity of participants spending 5 hours or less per day on social media?")

 col3,col4=st.columns(2)

 with col3:
  st.metric("Participants",len(underFive))
  st.metric("Average Productivity",round(underFive["actual_productivity_score"].mean(),2))
  st.metric("Average Social Media Time",round(underFive["daily_social_media_time"].mean(),2))

  st.write("Descriptive Statistics")
  st.dataframe(underFive[["daily_social_media_time","actual_productivity_score"]].describe())

 with col4:
  fig2,ax2=plt.subplots(figsize=(8,6))

  sns.scatterplot(data=underFive,x="daily_social_media_time",y="actual_productivity_score",s=35,alpha=0.6,edgecolor="black",linewidth=0.3,ax=ax2)

  sns.regplot(data=underFive,x="daily_social_media_time",y="actual_productivity_score",scatter=False,color="red",ax=ax2)

  ax2.set_xlim(df["daily_social_media_time"].min(),df["daily_social_media_time"].max())
  ax2.set_ylim(df["actual_productivity_score"].min(),df["actual_productivity_score"].max())

  ax2.set_title("Participants Spending 5 Hours or Less on Social Media")
  ax2.set_xlabel("Daily Social Media Time (Hours)")
  ax2.set_ylabel("Actual Productivity Score")
  ax2.grid(True)

  st.pyplot(fig2)
  st.markdown("---")

 st.markdown("---")
 st.subheader("Conclusion")

 st.info("The average productivity scores of the two groups were similar. Based on this dataset, there is little evidence that spending more than five hours on social media is associated with a substantial decrease in productivity.")
elif page=="Analysis 3":
 st.write("If not, who are the most and least productive people?")
 st.markdown("---")
 st.subheader("📊 Productivity Ranking")

 left,right=st.columns(2)

 with left:
  st.markdown("### Most Productive Participants")

  highest=df.sort_values(by="actual_productivity_score",ascending=False)

  st.dataframe(highest[["actual_productivity_score","daily_social_media_time","uses_focus_apps"]].head(10))

  st.metric("Highest Productivity Score",round(highest["actual_productivity_score"].max(),2))
  st.metric("Average Social Media Time",round(highest.head(10)["daily_social_media_time"].mean(),2))

  fig4,ax4=plt.subplots(figsize=(7,5))
  sns.scatterplot(data=highest.head(10),x="daily_social_media_time",y="actual_productivity_score",s=120,alpha=0.8,ax=ax4)
  ax4.set_title("Top 10 Most Productive")
  ax4.set_xlabel("Daily Social Media Time (Hours)")
  ax4.set_ylabel("Actual Productivity Score")
  st.pyplot(fig4)

 with right:
  st.markdown("### Least Productive Participants")

  lowest=df.sort_values(by="actual_productivity_score",ascending=True)

  st.dataframe(lowest[["actual_productivity_score","daily_social_media_time","uses_focus_apps"]].head(10))

  st.metric("Lowest Productivity Score",round(lowest["actual_productivity_score"].min(),2))
  st.metric("Average Social Media Time",round(lowest.head(10)["daily_social_media_time"].mean(),2))

  fig5,ax5=plt.subplots(figsize=(7,5))
  sns.scatterplot(data=lowest.head(10),x="daily_social_media_time",y="actual_productivity_score",s=120,alpha=0.8,ax=ax5)
  ax5.set_title("Bottom 10 Least Productive")
  ax5.set_xlabel("Daily Social Media Time (Hours)")
  ax5.set_ylabel("Actual Productivity Score")
  st.pyplot(fig5)

 st.info("Conclusion: The participants with the highest productivity scores did not consistently spend less time on social media than the least productive participants. This suggests that factors other than social media usage may have a greater influence on productivity.")
elif page=="Analysis 4":
 st.write("Could focus apps explain productivity instead?")
 st.subheader("📊 Analysis Question 4")
 focusApps=df.groupby("uses_focus_apps")["actual_productivity_score"].mean().reset_index()
 st.dataframe(focusApps)
 yesAverage=focusApps.loc[focusApps["uses_focus_apps"]==True,"actual_productivity_score"].values[0]
 noAverage=focusApps.loc[focusApps["uses_focus_apps"]==False,"actual_productivity_score"].values[0]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Uses Focus Apps",
   round(yesAverage,2)
  )

 with col2:
  st.metric(
   "Does Not Use Focus Apps",
   round(noAverage,2)
  )
 fig,ax=plt.subplots(figsize=(8,5))

 sns.boxplot(
  data=df,
  x="uses_focus_apps",
  y="actual_productivity_score",
  ax=ax
 )

 ax.set_title("Actual Productivity by Focus App Usage")
 ax.set_xlabel("Uses Focus Apps")
 ax.set_ylabel("Actual Productivity Score")

 st.pyplot(fig)
 difference=abs(yesAverage-noAverage)

 if difference<2:
  st.success(
   "Conclusion: The average productivity scores of users with and without focus apps were very similar. Based on this dataset, focus apps do not appear to have a strong relationship with productivity."
  )
 else:
  st.success(
   "Conclusion: Users of focus apps had a noticeably different average productivity score, suggesting that focus apps may be associated with productivity."
  )
elif page=="Analysis 5":
 st.write("Does occupation make a difference?")
 st.subheader("📊 Analysis Question 5")

 occupationProductivity=df.groupby("job_type")["actual_productivity_score"].mean().reset_index()
 occupationProductivity=occupationProductivity.sort_values(by="actual_productivity_score",ascending=False)

 st.dataframe(occupationProductivity)

 highestOccupation=occupationProductivity.iloc[0]
 lowestOccupation=occupationProductivity.iloc[-1]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Most Productive Occupation",
   highestOccupation["job_type"],
   )

  st.metric(
   "Average Productivity",
   round(highestOccupation["actual_productivity_score"],2)
   )

 with col2:
  st.metric(
   "Least Productive Occupation",
   lowestOccupation["job_type"],
   )

  st.metric(
   "Average Productivity",
   round(lowestOccupation["actual_productivity_score"],2)
   )

 fig,ax=plt.subplots(figsize=(10,5))

 sns.barplot(
  data=occupationProductivity,
  x="job_type",
  y="actual_productivity_score",
  ax=ax
 )

 ax.set_title("Average Productivity by Occupation")
 ax.set_xlabel("Occupation")
 ax.set_ylabel("Average Productivity Score")
 plt.xticks(rotation=20)

 st.pyplot(fig)

 st.success("Conclusion: Productivity is not reallyy affected by Occupation.")
elif page=="Analysis 6":
 st.write("How common are focus apps?")
 st.subheader("📊 Analysis Question 6")

 focusCounts=df["uses_focus_apps"].value_counts().reset_index()
 focusCounts.columns=["uses_focus_apps","count"]

 st.dataframe(focusCounts)

 yesCount=focusCounts.loc[focusCounts["uses_focus_apps"]==True,"count"].values[0]
 noCount=focusCounts.loc[focusCounts["uses_focus_apps"]==False,"count"].values[0]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Uses Focus Apps",
   yesCount
  )

 with col2:
  st.metric(
   "Does Not Use Focus Apps",
   noCount
  )

 fig,ax=plt.subplots(figsize=(7,5))

 sns.countplot(
  data=df,
  x="uses_focus_apps",
  ax=ax
 )

 ax.set_title("Number of Participants Using Focus Apps")
 ax.set_xlabel("Uses Focus Apps")
 ax.set_ylabel("Number of Participants")

 st.pyplot(fig)

 percentage=(yesCount/len(df))*100

 st.success(
  f"Conclusion: {percentage:.1f}% of participants use focus apps. This helps us understand how common focus apps are before deciding whether they are likely to influence overall productivity."
 ) 
elif page=="Analysis 7":
 st.write("Do notifications play a role in productivity?")
 st.subheader("📊 Analysis Question 7")

 notificationProductivity=df.groupby("number_of_notifications")["actual_productivity_score"].mean().reset_index()

 st.dataframe(notificationProductivity)

 highestNotification=notificationProductivity.loc[notificationProductivity["actual_productivity_score"].idxmax()]
 lowestNotification=notificationProductivity.loc[notificationProductivity["actual_productivity_score"].idxmin()]

 col1,col2=st.columns(2)

 with col1:
  st.metric(
   "Highest Average Productivity",
   round(highestNotification["actual_productivity_score"],2)
  )

  st.metric(
   "Notifications",
   int(highestNotification["number_of_notifications"])
  )

 with col2:
  st.metric(
   "Lowest Average Productivity",
   round(lowestNotification["actual_productivity_score"],2)
  )

  st.metric(
   "Notifications",
   int(lowestNotification["number_of_notifications"])
  )

 fig,ax=plt.subplots(figsize=(9,5))

 sns.lineplot(
  data=notificationProductivity,
  x="number_of_notifications",
  y="actual_productivity_score",
  marker="o",
  ax=ax
 )

 ax.set_title("Average Productivity by Number of Notifications")
 ax.set_xlabel("Number of Notifications")
 ax.set_ylabel("Average Productivity Score")

 st.pyplot(fig)

 correlation=df["number_of_notifications"].corr(df["actual_productivity_score"])

 st.metric(
  "Correlation",
  round(correlation,2)
 )

 if abs(correlation)<0.3:
  st.success(
   "Conclusion: There is only a weak relationship between notifications and productivity."
  )
 elif correlation<0:
  st.success(
   "Conclusion: Productivity tends to decrease as notifications increase."
  )
 else:
  st.success(
   "Conclusion: Productivity tends to increase as notifications increase."
  )
elif page=="Analysis 8":
 st.write("Putting everything together: What really influences productivity?")
 st.subheader("🏆 Kazi & Bradley Final Thesis")

 summary=df.groupby("job_type").agg(
  Average_Productivity=("actual_productivity_score","mean"),
  Average_Social_Media_Time=("daily_social_media_time","mean"),
  Average_Notifications=("number_of_notifications","mean"),
  Focus_App_Users=("uses_focus_apps","mean")
 ).reset_index()

 st.dataframe(summary.round(2))

 col1,col2,col3,col4=st.columns(4)

 with col1:
  st.metric(
   "Overall Productivity",
   round(df["actual_productivity_score"].mean(),2)
  )

 with col2:
  st.metric(
   "Average Social Media Hours",
   round(df["daily_social_media_time"].mean(),2)
  )

 with col3:
  st.metric(
   "Average Notifications",
   round(df["number_of_notifications"].mean(),0)
  )

 with col4:
  st.metric(
   "Focus App Usage",
   str(round(df["uses_focus_apps"].mean()*100,1))+"%"
  )

 fig,ax=plt.subplots(figsize=(11,7))

 scatter=ax.scatter(
  summary["Average_Social_Media_Time"],
  summary["Average_Productivity"],
  s=summary["Average_Notifications"]*3,
  c=summary["Focus_App_Users"],
  cmap="viridis",
  alpha=0.8,
  edgecolors="black"
 )

 for i,row in summary.iterrows():
  ax.text(
   row["Average_Social_Media_Time"]+0.03,
   row["Average_Productivity"]+0.03,
   row["job_type"],
   fontsize=9
  )

 cbar=plt.colorbar(scatter)
 cbar.set_label("Proportion Using Focus Apps")

 ax.set_title("Kazi's Final Thesis\nProductivity by Occupation",fontsize=15,fontweight="bold")
 ax.set_xlabel("Average Daily Social Media Time (Hours)")
 ax.set_ylabel("Average Actual Productivity Score")

 st.pyplot(fig)

 st.markdown("---")

 st.success("""
 ## 📖 Final Thesis

 After analysing the dataset from multiple perspectives, several key findings emerged.

 **1. Social media usage alone was not a strong predictor of productivity.**
 Participants spending more than five hours on social media achieved productivity scores that were remarkably similar to those spending less than five hours.

 **2. Productivity varies more across occupations than across social media usage.**
 Different job types consistently showed different average productivity scores.

 **3. Focus apps showed only a modest relationship with productivity.**
 Users and non-users recorded similar productivity levels, suggesting that simply installing a focus app does not guarantee better performance.

 **4. Notification levels may contribute to distraction, but they do not fully explain productivity differences.**
 Some occupations receive many notifications while maintaining relatively high productivity.

 **Overall Conclusion**

 This project suggests that productivity is influenced by multiple interacting factors rather than one single behaviour. Social media use, focus apps and notifications each contribute part of the picture, but occupation and work context appear to explain more variation than any single variable on its own.

 **TRADE MARK!**

 Productivity is not determined simply by the amount of time spent on social media. Instead, it appears to be the combined result of an individual's work environment, occupation, digital habits and ability to manage distractions. Looking at only one variable provides an incomplete explanation; meaningful insight comes from analysing the relationships between several factors together.
>>>>>>> 7bf3137655a3150b3b57c7d9a551ce9cd095ec8d
 """)