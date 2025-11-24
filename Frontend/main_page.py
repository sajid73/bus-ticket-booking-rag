import streamlit as st
import pandas as pd
from datetime import datetime
from utils import api_request

DISTRICTS = ["Dhaka", "Chattogram", "Rajshahi", "Sylhet", "Barishal", "Khulna"]
st.set_page_config(layout="wide", page_title="Bus Booking System")

st.header("🚌 Search & Book Tickets")

if 'search_results' not in st.session_state:
    st.session_state['search_results'] = None
if 'search_performed' not in st.session_state:
    st.session_state['search_performed'] = False
if 'search_origin' not in st.session_state:
    st.session_state['search_origin'] = None
if 'search_destination' not in st.session_state:
    st.session_state['search_destination'] = None
# ----------------------------------

def search_buses_callback(origin, destination):
    """Callback function to run when the search form is submitted."""
    st.session_state['search_origin'] = origin
    st.session_state['search_destination'] = destination
    st.session_state['search_performed'] = True
    
    # 1. Search Buses (Calls FastAPI SQL Endpoint)
    results = api_request('GET', 'routes', params={'origin': origin, 'destination': destination})

    if results:
        # Save the raw results to session state
        st.session_state['search_results'] = results
    else:
        st.session_state['search_results'] = []

with st.form("search_form"):
    col1, col2, col3 = st.columns(3)
    origin = col1.selectbox("Origin", options=DISTRICTS, index=0, key="origin_select")
    destination = col2.selectbox("Destination", options=[d for d in DISTRICTS if d != origin], index=1, key="dest_select")
    search_date = col3.date_input("Travel Date", min_value=datetime.now().date(), key="date_select")
    
    st.form_submit_button(
        "Search Buses", 
        type="primary",
        # Pass the selected values to the callback
        on_click=search_buses_callback,
        args=(origin, destination)
    )

if st.session_state['search_performed']:
    origin = st.session_state['search_origin']
    destination = st.session_state['search_destination']
    st.subheader(f"Available Routes from **{origin}** to **{destination}**")
    
    results = st.session_state['search_results']

    if results:
        df = pd.DataFrame(results)
        df['Available Seats'] = df['total_seats'] - df.index.map(lambda x: x % 10) # Mock seat calculation
        
        # Format DataFrame
        df = df[['id', 'provider_name', 'departure_time', 'dropping_point', 'fare', 'Available Seats']]
        df.columns = ['Route ID', 'Provider', 'Time', 'Dropping Point', 'Fare (Taka)', 'Seats']
        df['Time'] = df['Time'].fillna('N/A (Schedule not set)') 

        st.dataframe(df, width='stretch', hide_index=True)

        # Booking Form (Placed below search results)
        st.markdown("---")
        st.subheader("Book a Seat")
        with st.form("booking_form"):
            col_id, col_seat = st.columns(2)
            # Use value derived from the Route ID column in the DataFrame
            route_id = col_id.number_input("Enter Route ID to Book", min_value=1, step=1, format="%d", key="book_route_id")
            seat_number = col_seat.text_input("Seat Number (e.g., A1, B3)", value="A1", key="book_seat_num")
            
            name = st.text_input("Your Full Name", max_chars=100, key="book_name")
            phone = st.text_input("Your Phone Number", max_chars=20, key="book_phone")
            
            booked = st.form_submit_button("Confirm Booking", type="secondary")
            
            if booked:
                if not all([route_id, name, phone, seat_number]):
                    st.warning("Please fill in all booking details.")
                else:
                    # 2. Book Ticket (Calls FastAPI SQL Endpoint)
                    booking_data = {
                        "route_id": int(route_id),
                        "user_name": name,
                        "user_phone": phone,
                        "seat_number": seat_number,
                    }
                    booking_result = api_request('POST', 'book_ticket', data=booking_data)
                    
                    if booking_result:
                        st.success(f"Booking Successful! Your Booking ID is **{booking_result['id']}**. Please check the 'My Bookings' tab.")
                        st.session_state.current_phone = phone # Save phone for easy lookup
                        st.balloons()
                    else:
                        st.error("Booking failed. Please try again.")
    else:
        st.error("No buses found for this route on this date.")