import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Daily Reminder App", layout="centered")
st.title("📅 Daily Reminder Dashboard")

uploaded_file = st.file_uploader("Upload Reminder CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Check if Device-ID column exists
    if "Device-ID/User-ID" not in df.columns:
        st.error("CSV file must contain a 'Device-ID/User-ID' column.")
    else:
        # Ask user to enter Device-ID
        device_id = st.text_input("Enter your Device-ID to view your reminders:")

        if device_id:
            # Filter based on Device-ID
            df_user = df[df["Device-ID/User-ID"].astype(str) == device_id]

            if df_user.empty:
                st.warning("No reminders found for this Device-ID.")
            else:
                # Clean and parse
                df_user['Timestamp'] = pd.to_datetime(df_user['Timestamp'], errors='coerce')
                df_user = df_user.dropna(subset=['Timestamp'])

                # Date selector
                selected_date = st.date_input("Select a date to view reminders:", datetime.now().date())
                st.subheader(f"Reminders for {selected_date.strftime('%B %d, %Y')}")

                # Filter for selected date
                df_today = df_user[df_user['Timestamp'].dt.date == selected_date]

                if df_today.empty:
                    st.info("No reminders for selected date.")
                else:
                    # Filters
                    with st.expander("🔍 Filter Reminders"):
                        reminder_types = df_today['Reminder Type'].dropna().unique()
                        selected_types = st.multiselect("Reminder Type", reminder_types, default=list(reminder_types))

                        sent_status = st.radio("Reminder Sent?", ["All", "Yes", "No"])
                        ack_status = st.radio("Acknowledged?", ["All", "Yes", "No"])

                        filtered_df = df_today[df_today['Reminder Type'].isin(selected_types)]

                        if sent_status != "All":
                            filtered_df = filtered_df[filtered_df['Reminder Sent (Yes/No)'] == sent_status]
                        if ack_status != "All":
                            filtered_df = filtered_df[filtered_df['Acknowledged (Yes/No)'] == ack_status]

                    st.success(f"Showing {len(filtered_df)} reminder(s).")

                    # --- Display reminders with acknowledge buttons ---
                    updated = False
                    for idx, row in filtered_df.iterrows():
                        with st.container():
                            st.markdown(f"### ⏰ {row['Reminder Type']}")
                            st.markdown(f"**Time:** {row['Timestamp'].strftime('%I:%M %p')}")
                            st.markdown(f"**Message:** {row['Reminder Type']}")
                            st.markdown(f"**Acknowledged:** {row['Acknowledged (Yes/No)']}")

                            if row['Acknowledged (Yes/No)'] == "No":
                                if st.button(f"Acknowledge Reminder #{idx}", key=f"ack_{idx}"):
                                    df.loc[row.name, 'Acknowledged (Yes/No)'] = "Yes"
                                    updated = True
                                    st.success("✅ Reminder acknowledged!")

                            st.markdown("---")

                    if updated:
                        st.download_button(
                            "⬇️ Download Updated Reminders",
                            df.to_csv(index=False),
                            file_name="updated_reminders.csv",
                            mime="text/csv"
                        )
