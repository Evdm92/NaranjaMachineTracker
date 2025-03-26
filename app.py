import streamlit as st
import pandas as pd
import datetime
import os
import io
import base64
from PIL import Image
from NaranjaMachineTracker.data_handler import DataHandler
from utils import calculate_utilization, get_machine_capacity, get_machine_type
from visualization import plot_daily_utilization, plot_inventory_impact

# Page configuration
st.set_page_config(
    page_title="Naranja Automation - Machine Utilization Tracker",
    page_icon="🏭",
    layout="centered" # Changed to centered for better mobile view
)

# Initialize data handler
data_handler = DataHandler()

# Add custom CSS for mobile responsiveness (especially for Samsung devices)
st.markdown("""
<style>
    /* Mobile-optimized styles */
    @media screen and (max-width: 640px) {
        /* Reduce padding and margin for mobile */
        .stButton>button {
            width: 100%;
            margin-bottom: 10px;
            height: 3em;
        }
        
        /* Makes inputs bigger and more finger-friendly */
        input, select, button {
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        /* Make headings slightly smaller on mobile */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.4rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        /* Adjust sidebar for mobile */
        .css-1d391kg, .css-12oz5g7 {
            padding-top: 1rem;
        }
        
        /* Adjust expander padding */
        .streamlit-expanderHeader {
            padding: 12px !important;
        }
        
        /* More space for data entry forms */
        .stNumberInput, .stSelectbox {
            margin-bottom: 15px;
        }
        
        /* Better looking download buttons */
        a[download] {
            display: inline-block;
            background-color: #F63366;
            color: white !important;
            padding: 12px 20px;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
            margin: 10px 0;
            font-weight: bold;
        }
    }
    
    /* Highlight underperforming machines for better visibility */
    .red-highlight {
        color: red;
        font-weight: bold;
    }
    
    /* General app improvements */
    .stDataFrame {
        overflow-x: auto;
    }
    
    /* Light touchable UI for Samsung devices */
    .stButton>button:active {
        transform: scale(0.97);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to create a downloadable image
def get_image_download_link(img, filename, text):
    """
    Generate a link to download an image, optimized for mobile devices.
    
    Args:
        img: PIL Image object
        filename: Name of the download file
        text: Text to display in the download link
        
    Returns:
        str: HTML link for download
    """
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Create a mobile-friendly download link with styling
    href = f'''
    <a href="data:image/png;base64,{img_str}" 
       download="{filename}" 
       style="display: inline-block; 
              padding: 0.75em 1.5em; 
              background-color: #4CAF50; 
              color: white; 
              text-decoration: none; 
              border-radius: 8px; 
              margin-top: 12px; 
              font-weight: bold; 
              font-size: 16px;
              text-align: center;">
        {text}
    </a>
    '''
    return href

# Function to create a summary image of hourly data
def create_hourly_data_image(machine_data, date, hour, username):
    """
    Create an image showing the hourly data summary.
    
    Args:
        machine_data: Dictionary of machine data
        date: Date of data collection
        hour: Hour of data collection
        username: Username of the data collector
        
    Returns:
        PIL.Image: Image with summary data
    """
    # Create a white image with text
    width, height = 800, 1000  # Good size for mobile screens
    img = Image.new('RGB', (width, height), color='white')
    
    # Import ImageDraw for text
    from PIL import ImageDraw, ImageFont
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font_title = ImageFont.truetype("DejaVuSans.ttf", 32)
        font_subtitle = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 20)
    except IOError:
        # If font file not found, use default font
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Draw title
    draw.text((20, 20), f"Naranja Automation", fill="black", font=font_title)
    draw.text((20, 60), f"Machine Utilization Report", fill="black", font=font_subtitle)
    draw.text((20, 100), f"Date: {date} | Hour: {hour}:00", fill="black", font=font_text)
    draw.text((20, 130), f"Recorded by: {username}", fill="black", font=font_text)
    
    # Draw separator line
    draw.line([(20, 160), (width-20, 160)], fill="black", width=2)
    
    # Draw data table headers
    headers = ["Machine", "Type", "Carton", "Packers", "Cartons", "Util%", "Cartons/Packer"]
    header_positions = [20, 110, 200, 290, 370, 470, 580]
    
    for i, header in enumerate(headers):
        draw.text((header_positions[i], 180), header, fill="black", font=font_text)
    
    # Draw separator line
    draw.line([(20, 210), (width-20, 210)], fill="black", width=2)
    
    # Draw data rows
    y_position = 230
    for machine_number in range(9, 21):
        machine_name = f"Machine {machine_number}"
        if machine_name in machine_data:
            data = machine_data[machine_name]
            machine_type = "SpeedPacker" if machine_number <= 14 else "JumbleFiller"
            
            # Set text color based on utilization
            text_color = "red" if data['utilization'] < 70 else "black"
            
            # Draw machine data
            draw.text((header_positions[0], y_position), machine_name, fill=text_color, font=font_text)
            draw.text((header_positions[1], y_position), machine_type, fill=text_color, font=font_text)
            draw.text((header_positions[2], y_position), data['carton_type'], fill=text_color, font=font_text)
            draw.text((header_positions[3], y_position), str(data['packers']), fill=text_color, font=font_text)
            draw.text((header_positions[4], y_position), str(data['cartons_packed']), fill=text_color, font=font_text)
            draw.text((header_positions[5], y_position), f"{data['utilization']:.1f}%", fill=text_color, font=font_text)
            
            # Draw cartons per packer
            per_packer_color = "red" if data['cartons_per_packer'] < 11 and data['packers'] > 0 else "black"
            draw.text((header_positions[6], y_position), f"{data['cartons_per_packer']:.1f}", fill=per_packer_color, font=font_text)
            
            y_position += 40
    
    # Draw separator line
    draw.line([(20, y_position+10), (width-20, y_position+10)], fill="black", width=2)
    
    # Add inventory status summary
    draw.text((20, y_position+30), "Inventory Status Summary:", fill="black", font=font_subtitle)
    
    # Count machines by inventory status
    inventory_counts = {}
    for machine, data in machine_data.items():
        if data['inventory'] not in inventory_counts:
            inventory_counts[data['inventory']] = 0
        inventory_counts[data['inventory']] += 1
    
    # Draw inventory summary
    y_pos = y_position + 70
    for status, count in inventory_counts.items():
        draw.text((40, y_pos), f"{status}: {count} machines", fill="black", font=font_text)
        y_pos += 30
    
    # Add current date/time stamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    draw.text((20, height-40), f"Report generated: {current_time}", fill="gray", font=ImageFont.load_default())
    
    return img

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_data' not in st.session_state:
    st.session_state.current_data = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "data_entry"
if 'last_saved_data' not in st.session_state:
    st.session_state.last_saved_data = None

# Password hashing function
def verify_password(password, hashed_passwords):
    """
    Verify if the provided password matches any of the stored hashed passwords
    """
    # In a real production app, use proper password hashing like bcrypt
    # This is a simple implementation for demonstration purposes
    return password in hashed_passwords

# Company approved passwords - in production, store hashed passwords
APPROVED_PASSWORDS = ["naranja2025", "automation123", "packingUnit5"] 

# Login screen
if not st.session_state.authenticated:
    st.title("Welcome to Naranja Automation")
    st.subheader("Machine Utilization Tracker")
    
    with st.form("login_form"):
        username = st.text_input("Enter your username:")
        password = st.text_input("Enter your password:", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and verify_password(password, APPROVED_PASSWORDS):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

# Main application
else:
    # Sidebar navigation
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    
    # Add link to install as app on Samsung
    st.sidebar.markdown("""
    <a href="/.streamlit/custom_app_install.html" target="_blank" 
       style="display:inline-block; padding:8px 16px; background-color:#F63366; 
              color:white; text-decoration:none; border-radius:5px; margin-bottom:15px;
              font-size:14px; text-align:center;">
        📱 Install on Samsung Device
    </a>
    """, unsafe_allow_html=True)
    
    # Date and time selection
    current_date = datetime.date.today()
    selected_date = st.sidebar.date_input("Select Date", current_date)
    current_hour = datetime.datetime.now().hour
    selected_hour = st.sidebar.selectbox(
        "Select Hour", 
        list(range(0, 24)), 
        index=current_hour
    )
    
    # Navigation
    view_options = ["Data Entry", "Daily Report", "Trend Analysis"]
    selected_view = st.sidebar.radio("View", view_options)
    
    if selected_view == "Data Entry":
        st.session_state.view_mode = "data_entry"
    elif selected_view == "Daily Report":
        st.session_state.view_mode = "daily_report"
    else:
        st.session_state.view_mode = "trend_analysis"
    
    # Load existing data for the selected date and hour if available
    timestamp = f"{selected_date}_{selected_hour}"
    existing_data = data_handler.load_data(timestamp)
    
    if st.session_state.view_mode == "data_entry":
        st.title("Machine Utilization Data Entry")
        st.subheader(f"Date: {selected_date} | Hour: {selected_hour}:00")
        
        # Initialize form data with existing data or empty values
        form_data = {}
        if existing_data is not None:
            form_data = existing_data
        
        with st.form("data_entry_form", clear_on_submit=False):
            # Create columns for better layout
            col1, col2, col3 = st.columns(3)
            
            # Container for machine data inputs
            machine_data = {}
            
            # Create input fields for each machine
            for machine_number in range(9, 21):
                machine_name = f"Machine {machine_number}"
                machine_type = get_machine_type(machine_number)
                
                with st.expander(f"{machine_name} ({machine_type})"):
                    # Default values from existing data if available
                    default_carton_type = form_data.get(machine_name, {}).get('carton_type', 'A02D')
                    default_packers = form_data.get(machine_name, {}).get('packers', 1)
                    default_cartons_packed = form_data.get(machine_name, {}).get('cartons_packed', 0)
                    default_inventory = form_data.get(machine_name, {}).get('inventory', 'Wrapped')
                    
                    # Input fields
                    carton_type = st.selectbox(
                        "Carton Type", 
                        ["A02D", "A07D", "E10D", "A11D", "E15D", "A15C"],
                        key=f"{machine_name}_carton_type",
                        index=["A02D", "A07D", "E10D", "A11D", "E15D", "A15C"].index(default_carton_type)
                    )
                    
                    packers = st.number_input(
                        "Number of Packers", 
                        min_value=0, 
                        max_value=10, 
                        value=default_packers,
                        key=f"{machine_name}_packers"
                    )
                    
                    cartons_packed = st.number_input(
                        "Cartons Packed This Hour", 
                        min_value=0, 
                        value=default_cartons_packed,
                        key=f"{machine_name}_cartons_packed"
                    )
                    
                    inventory = st.selectbox(
                        "Inventory Status", 
                        ["Wrapped", "Labelled", "Wrapped and Labelled", "Unlabelled", "Other"],
                        key=f"{machine_name}_inventory",
                        index=["Wrapped", "Labelled", "Wrapped and Labelled", "Unlabelled", "Other"].index(default_inventory)
                    )
                    
                    # Calculate utilization metrics
                    capacity = get_machine_capacity(machine_number, carton_type)
                    utilization = calculate_utilization(cartons_packed, capacity)
                    cartons_per_packer = cartons_packed / packers if packers > 0 else 0
                    
                    # Display metrics with color coding
                    col1, col2 = st.columns(2)
                    with col1:
                        if utilization < 70:
                            st.markdown(f"<div class='red-highlight'>Utilization: {utilization:.1f}%</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"Utilization: {utilization:.1f}%")
                    
                    with col2:
                        if cartons_per_packer < 11 and packers > 0:
                            st.markdown(f"<div class='red-highlight'>Cartons per Packer: {cartons_per_packer:.1f}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"Cartons per Packer: {cartons_per_packer:.1f}")
                    
                    # Store machine data
                    machine_data[machine_name] = {
                        'carton_type': carton_type,
                        'packers': packers,
                        'cartons_packed': cartons_packed,
                        'inventory': inventory,
                        'capacity': capacity,
                        'utilization': utilization,
                        'cartons_per_packer': cartons_per_packer
                    }
            
            # Submit button
            submitted = st.form_submit_button("Save Data")
            
            if submitted:
                # Add metadata to the data
                data_to_save = {
                    'timestamp': timestamp,
                    'date': str(selected_date),
                    'hour': selected_hour,
                    'username': st.session_state.username,
                    'machines': machine_data
                }
                
                # Save the data
                data_handler.save_data(timestamp, data_to_save)
                st.success(f"Data saved successfully for {selected_date} at {selected_hour}:00")
                
                # Store the saved data in session state for export
                st.session_state.last_saved_data = {
                    'machine_data': machine_data,
                    'date': str(selected_date),
                    'hour': selected_hour,
                    'username': st.session_state.username
                }
        
        # Export image section (outside of form)
        if st.session_state.last_saved_data is not None:
            st.subheader("Export Data as Image")
            st.write("Create a downloadable image snapshot of the current hour's data:")
            
            if st.button("Generate Image for Download"):
                # Create an image with the hourly data
                saved_data = st.session_state.last_saved_data
                img = create_hourly_data_image(
                    saved_data['machine_data'], 
                    saved_data['date'], 
                    saved_data['hour'], 
                    saved_data['username']
                )
                
                # Generate download link
                filename = f"machine_data_{saved_data['date']}_{saved_data['hour']}.png"
                download_link = get_image_download_link(img, filename, "📥 Download Image")
                
                # Display download link
                st.markdown(download_link, unsafe_allow_html=True)
                st.info("Tap the green download button above to save the image to your device.")
    
    elif st.session_state.view_mode == "daily_report":
        st.title("Daily Machine Utilization Report")
        st.subheader(f"Date: {selected_date}")
        
        # Load all data for the selected date
        daily_data = data_handler.load_daily_data(str(selected_date))
        
        if not daily_data:
            st.warning(f"No data available for {selected_date}")
        else:
            # Display summary statistics
            st.subheader("Summary Statistics")
            
            # Calculate daily averages per machine
            machine_averages = {}
            for machine_number in range(9, 21):
                machine_name = f"Machine {machine_number}"
                machine_type = get_machine_type(machine_number)
                
                # Initialize counters
                total_utilization = 0
                total_cartons_per_packer = 0
                total_cartons = 0
                data_points = 0
                
                # Collect data from all hours
                for data in daily_data:
                    if machine_name in data['machines']:
                        machine_data = data['machines'][machine_name]
                        total_utilization += machine_data['utilization']
                        total_cartons += machine_data['cartons_packed']
                        if machine_data['packers'] > 0:
                            total_cartons_per_packer += machine_data['cartons_per_packer']
                        data_points += 1
                
                # Calculate averages
                if data_points > 0:
                    avg_utilization = total_utilization / data_points
                    avg_cartons_per_packer = total_cartons_per_packer / data_points
                    
                    machine_averages[machine_name] = {
                        'type': machine_type,
                        'avg_utilization': avg_utilization,
                        'avg_cartons_per_packer': avg_cartons_per_packer,
                        'total_cartons': total_cartons
                    }
            
            # Display machine averages in a table
            if machine_averages:
                df_averages = pd.DataFrame.from_dict(machine_averages, orient='index')
                df_averages = df_averages.reset_index().rename(columns={'index': 'Machine'})
                
                # Format columns
                df_averages['avg_utilization'] = df_averages['avg_utilization'].map('{:.1f}%'.format)
                df_averages['avg_cartons_per_packer'] = df_averages['avg_cartons_per_packer'].map('{:.1f}'.format)
                
                # Rename columns for display
                df_averages.columns = ['Machine', 'Type', 'Avg. Utilization', 'Avg. Cartons per Packer', 'Total Cartons']
                
                st.dataframe(df_averages)
            
            # Visualize daily utilization
            st.subheader("Hourly Utilization")
            fig = plot_daily_utilization(daily_data)
            st.plotly_chart(fig, use_container_width=True)
            
            # Visualize inventory impact
            st.subheader("Inventory Impact Analysis")
            fig_inventory = plot_inventory_impact(daily_data)
            st.plotly_chart(fig_inventory, use_container_width=True)
            
            # Add option to export hourly data as image
            st.subheader("Export Hourly Data as Image")
            
            # Select which hour to export
            hours_with_data = sorted(list(set([d['hour'] for d in daily_data])))
            if hours_with_data:
                selected_export_hour = st.selectbox(
                    "Select hour to export:", 
                    hours_with_data,
                    format_func=lambda h: f"{h}:00"
                )
                
                if st.button("Generate Image for Selected Hour"):
                    # Find the data for the selected hour
                    hour_data = next((d for d in daily_data if d['hour'] == selected_export_hour), None)
                    
                    if hour_data:
                        # Create an image with the hourly data
                        img = create_hourly_data_image(
                            hour_data['machines'], 
                            str(selected_date), 
                            selected_export_hour, 
                            hour_data['username']
                        )
                        
                        # Generate download link
                        filename = f"machine_data_{selected_date}_{selected_export_hour}.png"
                        download_link = get_image_download_link(img, filename, "📥 Download Image")
                        
                        # Display download link
                        st.markdown(download_link, unsafe_allow_html=True)
                        st.info("Tap the green download button above to save the image to your device.")
    
    elif st.session_state.view_mode == "trend_analysis":
        st.title("Trend Analysis")
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=current_date - datetime.timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=current_date)
        
        if start_date > end_date:
            st.error("Start date cannot be after end date")
        else:
            # Load data for the selected date range
            all_data = data_handler.load_date_range_data(str(start_date), str(end_date))
            
            if not all_data:
                st.warning(f"No data available for the selected date range")
            else:
                # Aggregate data by date
                dates = []
                daily_avg_utilization = []
                
                current = start_date
                while current <= end_date:
                    daily_data = [d for d in all_data if d['date'] == str(current)]
                    
                    if daily_data:
                        # Calculate average utilization across all machines for this day
                        total_utilization = 0
                        data_points = 0
                        
                        for data in daily_data:
                            for machine_name, machine_data in data['machines'].items():
                                total_utilization += machine_data['utilization']
                                data_points += 1
                        
                        if data_points > 0:
                            avg_utilization = total_utilization / data_points
                            dates.append(current)
                            daily_avg_utilization.append(avg_utilization)
                    
                    current += datetime.timedelta(days=1)
                
                # Plot trend
                if dates:
                    import plotly.graph_objects as go
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates, 
                        y=daily_avg_utilization,
                        mode='lines+markers',
                        name='Average Utilization'
                    ))
                    
                    # Add reference line at 70%
                    fig.add_shape(
                        type="line",
                        x0=min(dates),
                        y0=70,
                        x1=max(dates),
                        y1=70,
                        line=dict(
                            color="red",
                            width=2,
                            dash="dash",
                        )
                    )
                    
                    fig.update_layout(
                        title="Average Daily Machine Utilization",
                        xaxis_title="Date",
                        yaxis_title="Utilization (%)",
                        yaxis=dict(range=[0, 100]),
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Inventory impact over time
                    st.subheader("Inventory Impact Over Time")
                    
                    # Collect data for inventory analysis
                    inventory_types = ["Wrapped", "Labelled", "Wrapped and Labelled", "Unlabelled", "Other"]
                    inventory_data = {inv_type: [] for inv_type in inventory_types}
                    inventory_dates = []
                    
                    current = start_date
                    while current <= end_date:
                        daily_data = [d for d in all_data if d['date'] == str(current)]
                        
                        if daily_data:
                            inventory_dates.append(current)
                            
                            # Initialize counters for this date
                            inv_utilization = {inv_type: {'total': 0, 'count': 0} for inv_type in inventory_types}
                            
                            # Collect data for each inventory type
                            for data in daily_data:
                                for machine_name, machine_data in data['machines'].items():
                                    inv_type = machine_data['inventory']
                                    inv_utilization[inv_type]['total'] += machine_data['utilization']
                                    inv_utilization[inv_type]['count'] += 1
                            
                            # Calculate averages and append to data
                            for inv_type in inventory_types:
                                if inv_utilization[inv_type]['count'] > 0:
                                    avg = inv_utilization[inv_type]['total'] / inv_utilization[inv_type]['count']
                                else:
                                    avg = None
                                inventory_data[inv_type].append(avg)
                        
                        current += datetime.timedelta(days=1)
                    
                    # Plot inventory impact trend
                    if inventory_dates:
                        fig = go.Figure()
                        
                        for inv_type in inventory_types:
                            # Filter out None values
                            valid_indices = [i for i, val in enumerate(inventory_data[inv_type]) if val is not None]
                            valid_dates = [inventory_dates[i] for i in valid_indices]
                            valid_data = [inventory_data[inv_type][i] for i in valid_indices]
                            
                            if valid_data:
                                fig.add_trace(go.Scatter(
                                    x=valid_dates, 
                                    y=valid_data,
                                    mode='lines+markers',
                                    name=inv_type
                                ))
                        
                        fig.update_layout(
                            title="Inventory Impact on Machine Utilization",
                            xaxis_title="Date",
                            yaxis_title="Utilization (%)",
                            yaxis=dict(range=[0, 100]),
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Insufficient data to generate trend analysis")

# Logout button
if st.session_state.authenticated:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
