import streamlit as st
import datetime
import pandas as pd
from utils import api_request

DISTRICTS = ["Dhaka", "Chattogram", "Rajshahi", "Sylhet", "Barishal", "Khulna"]

# --- Initialize Session State for Persistence ---
if 'current_bookings' not in st.session_state:
    st.session_state['current_bookings'] = None
if 'searched_phone' not in st.session_state:
    st.session_state['searched_phone'] = ""

st.header("🎫 My Bookings")

def load_bookings(phone_number):
    """Function to fetch and store bookings in session state."""
    if phone_number:
        # 3. View Bookings (Calls FastAPI SQL Endpoint)
        bookings = api_request('GET', f'bookings/{phone_number}')
        st.session_state['current_bookings'] = bookings
        st.session_state['searched_phone'] = phone_number
    else:
        st.session_state['current_bookings'] = None
        st.session_state['searched_phone'] = ""

# Use the saved phone number as the default value if available
initial_phone = st.session_state.get('current_phone', '') # Retrieve phone from successful booking in other tab
phone_to_search = st.text_input("Enter your Phone Number to view bookings:", 
                                value=st.session_state.get('searched_phone', initial_phone), # Use searched phone or initial phone
                                key="manage_phone_input")

st.button(
    "Load Bookings",
    on_click=load_bookings,
    args=(phone_to_search,)
)

bookings = st.session_state['current_bookings']
phone_number = st.session_state['searched_phone']

if bookings is not None and phone_number:
    if bookings:
        st.subheader(f"Bookings for **{phone_number}**")
        
        booking_list = []
        for b in bookings:
            booking_list.append({
                "ID": b['id'],
                "Route ID": b['route_id'],
                "Seat": b.get('seat_number', 'N/A'), # Added Seat number for better clarity
                "Status": b['status'],
                "Booked Time": b['booking_time'][:10] # Show only date
            })
        
        df_bookings = pd.DataFrame(booking_list)
        st.dataframe(df_bookings, width='stretch', hide_index=True)

        # Cancellation Form
        st.markdown("---")
        st.subheader("Cancel a Booking")
        with st.form("cancel_form"):
            cancel_id = st.number_input("Enter Booking ID to Cancel", min_value=1, step=1, format="%d", key="cancel_id_input")
            cancel_button = st.form_submit_button("Confirm Cancellation", type="secondary")
            
            if cancel_button:
                # 4. Cancel Ticket (Calls FastAPI SQL Endpoint)
                cancel_result = api_request('POST', f'cancel_booking/{int(cancel_id)}')
                
                if cancel_result and cancel_result.get('status') == 'Canceled':
                    st.success(f"Booking ID **{cancel_id}** has been successfully Canceled. Refreshing list...")
                    # Rerun the load function to update the list immediately
                    load_bookings(phone_number) 
                    st.rerun() # Use st.rerun() to force the script to re-execute and display the updated state
                elif cancel_result:
                    st.warning(f"Cancellation failed or status was not updated for ID {cancel_id}.")
                else:
                    st.error(f"Error communicating with service for ID {cancel_id}.")

    else:
        st.info(f"No bookings found for phone number {phone_number}.")

elif st.session_state['searched_phone']:
    st.info(f"No bookings found for phone number {phone_number}.")