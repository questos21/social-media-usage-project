import io
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    log.append(f"Removed duplicate rows: {before - len(df)} duplicates found and dropped.")

    # Step 2: Handle missing values
    # Replace missing numerical metrics with their median
    if 'daily_social_media_time' in df.columns:
        df['daily_social_media_time'] = df['daily_social_media_time'].fillna(df['daily_social_media_time'].median())
    if 'job_satisfaction_score' in df.columns:
        df['job_satisfaction_score'] = df['job_satisfaction_score'].fillna(df['job_satisfaction_score'].median())
    log.append("Replaced missing values in numerical columns with their medians.")

    # Step 3: Round continuous floating-point metrics to 2 decimal places safely
    cols_to_round = ['daily_social_media_time', 'work_hours_per_day', 
                     'actual_productivity_score', 'weekly_offline_hours']
    existing_cols = [col for col in cols_to_round if col in df.columns]
    df[existing_cols] = df[existing_cols].round(2)

    # Step 4: Correct logical inconsistencies
    # If a person is Unemployed, set their work hours to 0
    if 'job_type' in df.columns and 'work_hours_per_day' in df.columns:
        df.loc[df['job_type'] == 'Unemployed', 'work_hours_per_day'] = 0

    # Step 5: Feature Engineering: Create calculated column
    if 'number_of_notifications' in df.columns and 'actual_productivity_score' in df.columns:
        df["Notification_Intensity"] = df["number_of_notifications"] / (df["actual_productivity_score"] + 1)
        log.append("Created 'Notification_Intensity' feature.")

    # Step 6: Remove outliers using IQR method for 'daily_social_media_time'
    if 'daily_social_media_time' in df.columns:
        Q1 = df['daily_social_media_time'].quantile(0.25)
        Q3 = df['daily_social_media_time'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df = df[(df['daily_social_media_time'] >= lower_bound) & (df['daily_social_media_time'] <= upper_bound)]
        log.append("Removed outliers from 'daily_social_media_time' using IQR method.")

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
st.markdown("---")

page = st.sidebar.radio("Navigate App", ["Data Understanding", "Data Cleaning Results"])

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

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Missing Value Counts")
        st.write(raw_summary["nulls"])
    with col4:
        st.subheader("Duplicate Check")
        st.write(f"Number of duplicate rows in raw data: **{raw_summary['duplicates']}**")

elif page == "Data Cleaning Results":
    st.header("🧼 Data Cleaning & Feature Engineering")

    st.subheader("Cleaning Pipeline Log Steps")
    for step in cleaning_log:
        st.success(step)

    st.subheader("Cleaned Dataset Preview")
    st.dataframe(df.head(10))

    if "Notification_Intensity" in df.columns:
        st.subheader("Engineered Feature: Notification Intensity Preview")
        st.dataframe(df[["number_of_notifications", "actual_productivity_score",
                          "Notification_Intensity"]].head())