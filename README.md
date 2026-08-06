SOCIAL MEDIA USAGE ANALYSIS THE MULTITASKING ILLUSION
Social Media Usage vs Productivity
Project Description

An interactive Streamlit data science app analyzing how daily social media habits relate to productivity, focus-app usage, occupation and notification frequency using a survey dataset of 30,000 respondents built as part of the DSA1080 group project by Kazi & Bradley.

Problem Statement

Social media use during work hours is widely believed to hurt focus and productivity but individuals and organizations often lack concrete data to confirm this or design better digital wellbeing habits. This project explores that relationship using real survey data, examining social media time, focus apps, occupation and notifications as possible drivers of productivity.

Dataset
Source: social_media_vs_productivity.csv (survey dataset, provided)
Number of rows: 30,000
Number of columns: 19
Key columns: daily_social_media_time, actual_productivity_score, perceived_productivity_score, job_type, number_of_notifications, uses_focus_apps, job_satisfaction_score, work_hours_per_day
Tools Used
Python
Streamlit
Pandas
NumPy
Matplotlib
Seaborn

Data Cleaning
Removed duplicate rows.
Replaced missing values in daily_social_media_time and job_satisfaction_score with their column medians.
Rounded continuous numeric columns (daily_social_media_time, work_hours_per_day, actual_productivity_score, weekly_offline_hours) to 2 decimal places.
Corrected a logical inconsistency: set work_hours_per_day to 0 for respondents with job_type = "Unemployed".
Engineered a new feature, Notification_Intensity, calculated as number_of_notifications / (actual_productivity_score + 1).
Removed outliers in daily_social_media_time using the IQR method.

Analysis Questions
What is the productivity of participants spending more than 5 hours per day on social media?
What is the productivity of participants spending 5 hours or less per day on social media?
Who are the most and least productive people, and does their social media usage differ?
Could focus apps explain differences in productivity?
Does occupation make a difference to productivity?
How common is focus-app usage among participants?
Do notifications play a role in productivity?
Putting it all together — what really influences productivity? (final cross-occupation synthesis)

Visualizations
Scatter plot with regression line — perceived vs actual productivity
Scatter plots with regression lines — productivity vs social media time (over 5 hrs / under 5 hrs groups)
Scatter plots — top 10 most and least productive participants
Box plot — productivity by focus-app usage
Bar chart — average productivity by occupation
Count plot — focus-app usage frequency
Line chart — average productivity by number of notifications
Bubble chart — productivity vs social media time by occupation, sized by notifications, colored by focus-app usage rate

Key Insights
Social media usage alone is not a strong predictor of productivity — participants above and below the 5-hour/day threshold scored similarly.
The most productive participants did not consistently use less social media than the least productive ones, pointing to other driving factors.
Focus-app usage shows only a modest relationship with productivity; users and non-users scored similarly.
Occupation shows more variation in average productivity than social media usage does, though the effect is still limited.
Notification count has only a weak correlation with productivity.
Productivity appears to result from a combination of factors — occupation, digital habits, and distraction management — rather than any single variable acting alone.

Recommendations
Avoid framing productivity policy around screen-time limits alone, since usage time alone shows little predictive power in this dataset.
Investigate occupation-specific work conditions further, since they show more variation in productivity than digital habits do.
Treat focus apps as a possible support tool rather than a guaranteed fix, given the modest effect size observed.
Consider notification management as one factor among several, not a standalone lever for improving productivity.
Take a holistic view of productivity drivers (work environment, occupation, digital habits, distraction management) rather than isolating one variable.

How to Run the Project
Clone the repository
Install requirements: pip install <requirement>
Run the app: python -m streamlit run app.py
The app opens in our browser at http://localhost:8501
KAZI  KIIRU MATHU 202604055
BRADLEY QUEST 676509
