import PySimpleGUI as sg
import sqlite3
from datetime import datetime, timedelta

def get_user_role(username, password):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    
    # Check if the user is an admin
    cur.execute("SELECT * FROM Admin WHERE adusername = ?", (username,))
    if cur.fetchone():
        cur.execute("SELECT * FROM User WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        if user:
            con.close()
            return 'admin', user[1]  # Assuming user[1] is the name of the user
    # Check if the user is a tour guide
    cur.execute("SELECT * FROM TourGuide WHERE tgusername = ?", (username,))
    if cur.fetchone():
        cur.execute("SELECT * FROM User WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        if user:
            con.close()
            return 'tourguide', user[1]
    
    # Check if the user is a traveler
    cur.execute("SELECT * FROM Traveler WHERE trusername = ?", (username,))
    if cur.fetchone():
        cur.execute("SELECT * FROM User WHERE username = ? AND password = ?", (username, password))
        user = cur.fetchone()
        if user:
            con.close()
            return 'traveler', user[1]
    
    con.close()
    return None, None



#ADMIN PAGES


def show_create_tour_form():
    today = datetime.today()
    today_str = today.strftime('%Y-%m-%d')
    layout = [
        [sg.Text('Create a New Tour', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Tour Name', background_color='navyblue', text_color='white'), sg.InputText(key='tname')],
        [sg.Text('Starting Date', background_color='navyblue', text_color='white'), sg.Input(key='stdate', size=(20, 1)), sg.CalendarButton("Choose Starting Date", target="stdate", format="%Y-%m-%d", default_date_m_d_y=(today.month, today.day, today.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text('Ending Date', background_color='navyblue', text_color='white'), sg.Input(key='endate', size=(20, 1)), sg.CalendarButton("Choose Ending Date", target="endate", format="%Y-%m-%d", close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text('Price', background_color='navyblue', text_color='white'), sg.InputText(key='price')],
        [sg.Text('Itinerary', background_color='navyblue', text_color='white'), sg.InputText(key='itinerary')],
        [sg.Text('Maximum Capacity', background_color='navyblue', text_color='white'), sg.InputText(key='maxcap')],
        [sg.Button('Create Tour', button_color=('white', 'navyblue'))],
        [sg.Button('Back', button_color=('white', 'navyblue'))]
    ]
    
    window = sg.Window('Create Tour', layout, background_color='navyblue')
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED :
            break
        if  event == 'Back':
            window.close()
            show_admin_page(username)
            break
        if event == 'Create Tour':
            tname = values['tname']
            stdate = values['stdate']
            endate = values['endate']
            price = values['price']
            itinerary = values['itinerary']
            maxcap = values['maxcap']

            # Validate dates
            if not stdate or not endate:
                sg.popup('Please choose both starting and ending dates.', font=('Helvetica', 14))
                continue

            stdate_obj = datetime.strptime(stdate, '%Y-%m-%d')
            endate_obj = datetime.strptime(endate, '%Y-%m-%d')

            if stdate_obj < today:
                sg.popup('Starting date cannot be earlier than today.', font=('Helvetica', 14))
                continue

            if endate_obj < stdate_obj:
                sg.popup('Ending date cannot be earlier than starting date.', font=('Helvetica', 14))
                continue

            try:
                print("Starting Create Tour logic", flush=True)
                tname = values['tname']
                stdate = values['stdate']
                endate = values['endate']
                price = values['price']
                itinerary = values['itinerary']
                maxcap = values['maxcap']

                print(f"Inserting: {tname}, {stdate}, {endate}, {price}, {itinerary}, {maxcap}", flush=True)
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                cur.execute("SELECT MAX(tid) FROM Tour")
                result = cur.fetchone()
                next_tid = (result[0] or 0) + 1
                print(f"Next tid determined: {next_tid}", flush=True)
                cur.execute("INSERT INTO Tour (tid, tname, stdate, endate, price, itinerary, maxcap) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (next_tid, tname, stdate, endate, price, itinerary, maxcap))
                con.commit()
                print("Insert committed successfully", flush=True)
                sg.popup(f'Tour created successfully with ID {next_tid}', font=('Helvetica', 14))
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)
            finally:
                con.close()
                print("Database connection closed", flush=True)
            window.close()
            show_admin_page(username)
            break

    
    window.close()
    


#Transportation
#deneme
def show_add_transportation():
    

    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Get the transportation options from the database
    cur.execute("SELECT type, starting_point, destination FROM Transportation")
    transportation_options= cur.fetchall()

    # Get the tour code from the database
    cur.execute("SELECT MAX(tid) FROM Tour")
    result1 = cur.fetchone()
    tid = result1[0]

    # Get the starting and end dates of the tour
    cur.execute("SELECT stdate,endate FROM Tour WHERE tid = ?",  (tid,))
    result2 = cur.fetchone()
    stdate = result2[0]
    endate = result2[1]
    con.close()

    # Convert the start and end dates to datetime objects
    start_date_obj = datetime.strptime(stdate, '%Y-%m-%d')
    end_date_obj = datetime.strptime(endate, '%Y-%m-%d')

    # Generate a list of dates between start_date_obj and end_date_obj
    available_dates = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        available_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    assigned_transportation = {date: None for date in available_dates}

    layout = [
        [sg.Text("Choose Transportation of Tour", font=('Helvetica', 16))],
        [sg.Text('Starting Date', background_color='navyblue', text_color='white'), sg.Input(key='stdate', size=(20, 1)), sg.CalendarButton("Choose Starting Date", target="stdate", format="%Y-%m-%d", default_date_m_d_y=(start_date_obj.month, start_date_obj.day, start_date_obj.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text('Ending Date', background_color='navyblue', text_color='white'), sg.Input(key='endate', size=(20, 1)), sg.CalendarButton("Choose Ending Date", target="endate", format="%Y-%m-%d", close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Combo(["All", "Plane", "Train", "Boat", "Bus"], key="t_filter", default_value="All", enable_events=True)],
        [sg.Text("Filter by starting point", font=('Helvetica', 16))],
        [sg.Combo(["All", "Istanbul", "Moscow", "Berlin", "Athens", "New York", "Tokyo", "London", "Madrid", "Naples", "Los Angeles", "Dubai", "Zurich", "Helsinki", "Tallinn", "Bangkok", "Munich", "Brussels", "Sydney", "Warsaw", "Oslo"], key= "s_filter", default_value="All", enable_events=True)],
        [sg.Text("Filter by destination", font=('Helvetica', 16))],
        [sg.Combo(["All",'Rome', 'Paris', 'Prague', 'Santorini', 'Boston', 'Seoul', 'Edinburgh', 'Barcelona', 'Palermo', 'San Francisco', 'Cairo', 'Geneva', 'Stockholm', 'Helsinki', 'Singapore', 'Vienna', 'Amsterdam', 'Melbourne', 'Krakow', 'Copenhagen'], key= "d_filter", default_value="All", enable_events=True)],
        [sg.Text("Available Transportation Options", font=('Helvetica', 16))],
        [sg.Listbox(transportation_options, key="transportation_options", size=(30, len(transportation_options)), select_mode='single', enable_events=True)],
        [sg.Button("Assign Transportation", font=('Helvetica', 16))],
        [sg.Button("Close", font=('Helvetica', 16))]]
        
    layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))]]
    window = sg.Window('Transportation_Page', layout)

    def filter_transportation(options, t_filter, s_filter, d_filter):
        filtered_options = []
        for option in options:
            if (t_filter == "All" or option[0] == t_filter) and \
               (s_filter == "All" or option[1] == s_filter) and \
               (d_filter == "All" or option[2] == d_filter):
                filtered_options.append(option)
        return filtered_options

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "Close":
            break
        
        # Filter Process
        if event in ("t_filter", "s_filter", "d_filter"):
            filtered_options = filter_transportation(transportation_options, values["t_filter"], values["s_filter"], values["d_filter"])
            window["transportation_options"].update(filtered_options)

        # Date arrangements
        if event == "Assign Transportation":
            selected_start_date = values["stdate"]
            selected_end_date = values["endate"]
            t_transportation = values['transportation_options']
            
            if not selected_start_date or not selected_end_date:
                sg.popup("Please select both start and end dates.", font=('Helvetica', 14))
                continue
            
            if selected_start_date not in available_dates or selected_end_date not in available_dates:
                sg.popup("Selected dates must be within the available dates range.", font=('Helvetica', 14))
                continue
            
            if selected_end_date < selected_start_date:
                sg.popup("End date cannot be earlier than start date.", font=('Helvetica', 14))
                continue
            
            if not t_transportation or len(t_transportation[0]) < 3:
                sg.popup("Please select a valid transportation option.", font=('Helvetica', 14))
                continue
            
            try:
                print("Starting choose tour options", flush=True)
                t_type = t_transportation[0][0]
                t_start = t_transportation[0][1]
                t_destination = t_transportation[0][2]

                print(f"Inserting: {t_type}, {t_start}, {t_destination}", flush=True)
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                

                # Fetch the tcode from the Transportation table
                cur.execute("SELECT tcode FROM Transportation WHERE type = ? AND starting_point = ? AND destination = ?", (t_type, t_start, t_destination))
                result = cur.fetchone()
                if result is None:
                    sg.popup("Transportation option not found in the database.", font=('Helvetica', 14))
                    continue
                t_code = result[0]

                                # Check for existing assignments for the selected dates
                cur.execute("SELECT COUNT(*) FROM Assign WHERE sdate <= ? AND edate >= ? AND tid = ?", (selected_end_date, selected_start_date, tid))
                result = cur.fetchone()
                if result[0] > 0:
                    sg.popup("Transportation already assigned for the selected dates.", font=('Helvetica', 14))
                    continue

                # Ensure dates are in the correct format
                try:
                    selected_start_date = datetime.strptime(selected_start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                    selected_end_date = datetime.strptime(selected_end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    sg.popup("Invalid date format. Please use YYYY-MM-DD.", font=('Helvetica', 14))
                    continue

                # Insert the new assignment
                cur.execute("INSERT INTO Assign (tid, tcode, sdate, edate) VALUES (?, ?, ?, ?)",
                            (tid, t_code, selected_start_date, selected_end_date))
                con.commit()
                print("Insert committed successfully", flush=True)
                sg.popup('Transportation created successfully', font=('Helvetica', 14))

                # Check if all dates have transportation assigned
                cur.execute("SELECT sdate, edate FROM Assign WHERE tid = ?", (tid,))
                assigned_dates = cur.fetchall()
                assigned_dates_set = set()
                for sdate, edate in assigned_dates:
                    current_date = datetime.strptime(sdate, '%Y-%m-%d')
                    end_date = datetime.strptime(edate, '%Y-%m-%d')
                    while current_date <= end_date:
                        assigned_dates_set.add(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)

                unassigned_dates = set(available_dates) - assigned_dates_set
                if not unassigned_dates:
                    sg.popup("All dates have transportation assigned.", font=('Helvetica', 14))
                    window.close()
                else:
                    unassigned_dates_list = list(unassigned_dates)
                    unassigned_dates_list.sort()
                    sg.popup(f"Some dates are still unassigned: {', '.join(unassigned_dates_list)}", font=('Helvetica', 14))
                    available_dates = unassigned_dates_list
                    assigned_transportation = {date: None for date in available_dates}
                    window["stdate"].update("")
                    window["endate"].update("")
                    window["transportation_options"].update(filtered_options)
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)
            finally:
                con.close()
                print("Database connection closed", flush=True)

    window.close()


def show_admin_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    cur.execute("SELECT name FROM User WHERE username = ?", (username,))
    user = cur.fetchone()
    con.close()
    
    name = user[0]
    
 # Define the layout of the admin window
    layout = [
        [sg.Text(f'Welcome {name}', font=('Helvetica', 14), justification='center', background_color='navyblue', text_color='white')],
        [sg.Button('Create New Tour', button_color=('white', 'navyblue'))],
        [sg.Button('Add Transportation', button_color=('white', 'navyblue'))],
        [sg.Button('Add Hotel', button_color=('white', 'navyblue'))],
        [sg.Button('Logout', button_color=('white', 'navyblue'))]
    ]
    
    
    # Create the admin window
    window = sg.Window('Admin Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Logout':
            break
        if event == 'Create New Tour':
            window.close()
            show_create_tour_form()
            break
        if event == 'Add Transportation':
            window.close()
            show_add_transportation_form(username)
            break
        if event == 'Add Hotel':
            window.close()
            show_add_hotel_form(username)
            break

    window.close()




#TOURGUIDE PAGES  



def show_tourguide_page():
    # Define the layout of the tour guide window
    layout = [
        [sg.Text('Tour Guide Page')],
        [sg.Button('Logout')]
    ]
    
    # Create the tour guide window
    window = sg.Window('Tour Guide Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Logout':
            break
    
    window.close()




#TRAVELER PAGES



def show_traveler_page():
    # Define the layout of the traveler window
    layout = [
        [sg.Text('Traveler Page')],
        [sg.Button('Logout')]
    ]
    
    # Create the traveler window
    window = sg.Window('Traveler Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Logout':
            break
    
    window.close()




#LOGIN PAGES


# Define the layout of the login window
layout = [
    [sg.Text('Welcome to Orange Travel Agency Platform, please enter your information', font=('Helvetica', 12), justification='center', background_color='navyblue', text_color='white')],
    [sg.Text('Username'), sg.InputText(key='username')],
    [sg.Text('Password'), sg.InputText(key='password', password_char='*')],
    [sg.Button('Login')]
]

# Create the login window
window = sg.Window('Login', layout, background_color='navyblue')

# Event loop to process events and get values of inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Login':
        username = values['username']
        password = values['password']
        if not username:
            sg.popup('Username must be entered')
        elif not password:
            sg.popup('Password must be entered')
        else:
            role, name = get_user_role(username, password)
            if role == 'admin':
                window.close()
                show_admin_page(username)
                break
            elif role == 'tourguide':
                window.close()
                show_tourguide_page()
                break
            elif role == 'traveler':
                window.close()
                show_traveler_page()
                break
            else:
                sg.popup('Invalid username or password')

window.close()