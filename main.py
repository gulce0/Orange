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
    layout = [
        [sg.Text('Create a New Tour', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Tour Name', background_color='navyblue', text_color='white'), sg.InputText(key='tname')],
        [sg.Text('Starting Date', background_color='navyblue', text_color='white'), sg.InputText(key='stdate')],
        [sg.Text('Ending Date', background_color='navyblue', text_color='white'), sg.InputText(key='endate')],
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
<<<<<<< HEAD
                sg.popup('Tour created successfully', font=('Helvetica', 14))
<<<<<<< Updated upstream
=======
                sg.popup(f'Tour created successfully with ID {next_tid}', font=('Helvetica', 14))
=======
                
>>>>>>> Stashed changes
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)
            finally:
                con.close()
                print("Database connection closed", flush=True)
            window.close()
<<<<<<< Updated upstream
            show_admin_page(username)
            break

    
    window.close()


#Hotel Assignment
    
def show_add_hotel():
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    cur.execute("SELECT tid, tname, stdate, endate FROM Tour")
    tours = cur.fetchall()

    cur.execute("SELECT hid, city, brand FROM Hotel")
    hotels = cur.fetchall()
    con.close()

    layout = [
        [sg.Text("Assign Hotels for Tours", font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text("Select a Tour", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Listbox(tours, size=(50, 5), key="selected_tour", select_mode="single", background_color='white', text_color='black')],
        [sg.Text("Starting Date", font=('Helvetica', 12), background_color='navyblue', text_color='white'),
         sg.Input(key="stdate", background_color='white', text_color='black'),
         sg.CalendarButton("Pick Start Date", target="stdate", format="%Y-%m-%d", button_color=('white', 'navyblue'))],
        [sg.Text("Ending Date", font=('Helvetica', 12), background_color='navyblue', text_color='white'),
         sg.Input(key="endate", background_color='white', text_color='black'),
         sg.CalendarButton("Pick End Date", target="endate", format="%Y-%m-%d", button_color=('white', 'navyblue'))],
        [sg.Text("Filter by City", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Combo(["All"] + list(set(hotel[1] for hotel in hotels)), key="city_filter", default_value="All", enable_events=True,
                  background_color='white', text_color='black')],
        [sg.Text("Available Hotels", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Listbox(hotels, size=(50, len(hotels)), key="hotel_list", select_mode="single", background_color='white', text_color='black')],
        [sg.Button("Assign Hotel", button_color=('white', 'navyblue')), sg.Button("Close", button_color=('white', 'navyblue')), sg.Button("Back", button_color=('white','navyblue'))]
    ]

    window = sg.Window("Hotel Assignment", layout, background_color='navyblue')

    def filter_hotels(hotels, city_filter):
        if city_filter == "All":
            return hotels
        return [hotel for hotel in hotels if hotel[1] == city_filter]

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Close"):
            break


        if  event == 'Back':
            window.close()
            show_admin_page(username)
            break

        if  event == 'OK':
            window.close()
            show_admin_page(username)
            break
        
        # Filter hotels by city
        if event == "city_filter":
            filtered_hotels = filter_hotels(hotels, values["city_filter"])
            window["hotel_list"].update(filtered_hotels)

        # Assign a hotel to a tour
        if event == "Assign Hotel":
            selected_tour = values["selected_tour"]
            selected_start_date = values["stdate"]
            selected_end_date = values["endate"]
            selected_hotel = values["hotel_list"]

            if not selected_tour:
                sg.popup("Please select a tour.", font=('Helvetica', 14))
                continue

            if not selected_start_date or not selected_end_date:
                sg.popup("Please select both start and end dates.", font=('Helvetica', 14))
                continue

            if not selected_hotel:
                sg.popup("Please select a hotel.", font=('Helvetica', 14))
                continue

        

            tour_id = selected_tour[0][0]  
            selected_hotel_id = selected_hotel[0][0]  
            tour_start_date = selected_tour[0][2] 
            tour_end_date = selected_tour[0][3] 

            # Dates should be matching with the tour dates
            if selected_start_date < tour_start_date or selected_end_date > tour_end_date:
                sg.popup("Selected dates must be matching with the tour dates.", font=('Helvetica', 14))
                continue

            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()

                # Check the availability of the hotel
                cur.execute("""
                    SELECT COUNT(*)
                    FROM reservation
                    WHERE hid = ? AND sdate <= ? AND edate >= ?
                """, (selected_hotel_id, selected_end_date, selected_start_date))
                if cur.fetchone()[0] > 0:
                    sg.popup("This hotel is already assigned for the selected dates.", font=('Helvetica', 14))
                    continue

                # Insert the hotel assignment into the reservation table
                cur.execute("""
                    INSERT INTO reservation (tid, hid, sdate, edate)
                    VALUES (?, ?, ?, ?)
                """, (tour_id, selected_hotel_id, selected_start_date, selected_end_date))
                con.commit()

                sg.popup("Hotel successfully assigned to the tour.", font=('Helvetica', 14))

                window.close()  
                show_admin_page(username)  
                break

            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
            finally:
                con.close()

    window.close()

#Transportation Assignment

def show_add_transportation_page():
    

    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Get the tours from the database
    cur.execute("SELECT tid, tname, stdate, endate FROM Tour")
    tours = cur.fetchall()
    con.close()

    # Layout for selecting a tour
    layout = [
        [sg.Text("Select a Tour to assign transportation", font=('Helvetica', 16))],
        [sg.Listbox(tours, size=(50, 5), key="selected_tour", select_mode="single", background_color='white', text_color='black')],
        [sg.Button("Next", font=('Helvetica', 16)), sg.Button("Back", font=('Helvetica', 16))]
    ]

    window = sg.Window('Select Tour', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            window.close()
            return
        if event == "Back":
            window.close()
            show_admin_page(username)
            break
        
        if event == "Next":
            selected_tour = values["selected_tour"]
            if not selected_tour:
                sg.popup("Please select a tour.", font=('Helvetica', 14))
                continue

            tid = selected_tour[0][0]
            stdate = selected_tour[0][2]
            endate = selected_tour[0][3]
            window.close()

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

            # Get the transportation options from the database
            con = sqlite3.connect('Project.db')
            cur = con.cursor()
            cur.execute("SELECT type, starting_point, destination FROM Transportation")
            transportation_options = cur.fetchall()
            types = list(set(option[0] for option in transportation_options))
            starting_points = list(set(option[1] for option in transportation_options))
            destinations = list(set(option[2] for option in transportation_options))

            con.close()

            layout = [
                [sg.Text("Choose Transportation of Tour", font=('Helvetica', 16))],
                [sg.Text('Starting Date', background_color='navyblue', text_color='white'), sg.Input(key='stdate', size=(20, 1)), sg.CalendarButton("Choose Starting Date", target="stdate", format="%Y-%m-%d", default_date_m_d_y=(start_date_obj.month, start_date_obj.day, start_date_obj.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
                [sg.Text('Ending Date', background_color='navyblue', text_color='white'), sg.Input(key='endate', size=(20, 1)), sg.CalendarButton("Choose Ending Date", target="endate", format="%Y-%m-%d", default_date_m_d_y=(end_date_obj.month, end_date_obj.day, end_date_obj.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
                [sg.Combo(["All"]+ types, key="t_filter", default_value="All", enable_events=True)],
                [sg.Text("Filter by starting point", font=('Helvetica', 16))],
                [sg.Combo(["All"]+ starting_points, key= "s_filter", default_value="All", enable_events=True)],
                [sg.Text("Filter by destination", font=('Helvetica', 16))],
                [sg.Combo(["All"]+ destinations, key= "d_filter", default_value="All", enable_events=True)],
                [sg.Text("Available Transportation Options", font=('Helvetica', 16))],
                [sg.Listbox(transportation_options, key="transportation_options", size=(30, len(transportation_options)), select_mode='single', enable_events=True)],
                [sg.Button("Assign Transportation", font=('Helvetica', 16))],
                [sg.Button("Back", font=('Helvetica', 16))]
            ]

            layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))]]
            window = sg.Window('Transportation_Page', layout, background_color='navyblue')
            break
        

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
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Back":
            window.close()
            show_add_transportation_page()
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
>>>>>>> 5df53925000a1b41e1b08ec51e0c8d5c6bd5d139
                
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)
            finally:
                con.close()
                print("Database connection closed", flush=True)
            window.close()
=======
>>>>>>> Stashed changes
            show_tourguide_selection_page()
            break

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
        [sg.Text(f'Welcome {name}', font=('Helvetica', 16), justification='center', background_color='navyblue', text_color='white')],
        [sg.Button('Create New Tour', button_color=('white', 'navyblue'))],
        [sg.Button('Exit', button_color=('white', 'navyblue'))]
    ]
    
    # Create the admin window
    window = sg.Window('Admin Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Create New Tour':
            window.close()
            show_create_tour_form()
            break

    window.close()

def show_tourguide_selection_page():

    tourguides = ('Chris Adams', 'Susan Clark', 'David Martin', 'Linda White', 'Robert King' )

    
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    cur.execute("SELECT MAX(tid) FROM Tour")
    result1 = cur.fetchone()
    tour_code = result1[0]

    cur.execute("SELECT stdate,endate FROM Tour WHERE tid = ?",  (tour_code,))
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
    assigned_tourguide = {date: None for date in available_dates}


    layout = [
        [sg.Text("Choose Tourguides of Tour", font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text("Available Dates", font=('Helvetica', 16))], 
        [sg.Listbox(available_dates, key="selected_dates", size=(10, 10))],
        [sg.Text("Available Tourguides", font=('Helvetica', 16))],
        [sg.Listbox(tourguides, size=(15, len(tourguides)), key='chosen_tourguide', select_mode='multiple', enable_events=True)],
        [sg.Button("Assign Tourguides", font=('Helvetica', 16))],
        [sg.Button("Close", font=('Helvetica', 16))]
    ]


    
    # Create the tour guide window
    window = sg.Window('Touruide Page', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Close':
            break
        elif event == 'Assign Tourguides':
            chosen_tourguides = values['chosen_tourguide']
            if chosen_tourguides and len(chosen_tourguides) == 2:
                sg.popup(f"Tourguides '{chosen_tourguides[0]}' and '{chosen_tourguides[1]}' Assigned Successfully!")
                assign_tour_guides(tour_code, chosen_tourguides)
                break
            elif not chosen_tourguides:
                sg.popup("No tour guides selected! Please select exactly two.")
            elif len(chosen_tourguides) < 2:
                sg.popup("You have selected fewer than two tour guides. Please select two.")
            elif len(chosen_tourguides) > 2:
                sg.popup("Too many selections! Please select only two tour guides.")    
<<<<<<< Updated upstream
    
    window.close()
    display_all_tours_page()
=======
            window.close()
            display_all_tours_page()
    window.close()

>>>>>>> Stashed changes

def filter_tourguides(available_dates):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Create a set of all tour guides to start with
    cur.execute("SELECT tgusername FROM Tourguide")
    all_tour_guides = {row[0] for row in cur.fetchall()}

    for date in available_dates:
        cur.execute("SELECT tgusername FROM Has h Tour t WHERE t.stdate <= ? AND t.endate >= ?", (date, date))
        
        # Remove guides who are unavailable on this date
        unavailable_guides = {row[0] for row in cur.fetchall()}
        all_tour_guides -= unavailable_guides

    con.close()
    return list(all_tour_guides)

def assign_tour_guides(t_code, chosen_tourguides):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    for guide in chosen_tourguides:
        cur.execute('INSERT INTO Has (tid, tgusername) VALUES (?, ?)', (t_code, guide))

    con.commit()
    print(f"Assigned tour guides: {chosen_tourguides[0]} and {chosen_tourguides[1]} to tour ID {t_code}.")
    con.close()

def display_all_tours_page():
    con = sqlite3.connect('Project.db')
    cur = con.cursor() 

    cur.execute("SELECT * FROM Tour")
    tours = cur.fetchall()
    con.close()

    layout = [
<<<<<<< Updated upstream
        [sg.Text("All Tours in the System", font=('Helvetica', 16), background_color='navyblue', text_color='white' )],
        [sg.Table(values=tours, headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Maximum Capacity", "Itinerary", "Price"],justification='center', auto_size_columns=False, num_rows=min(len(tours), 10))],
        [sg.Button("Log Out")]
=======
        [sg.Text("All Tours in the System", font=('Helvetica', 16))],
        [sg.Table(values=tours, headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Maximum Capacity", "Itinerary", "Price"],justification='center', auto_size_columns=False, num_rows=min(len(tours), 10))],
        [sg.Button("Log Out")], [sg.Button("Back")]
>>>>>>> Stashed changes
    ]


    window = sg.Window('All Tours', layout, background_color='navyblue')

    while True:
<<<<<<< Updated upstream
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED or event == "Log Out":
            sg.popup("Logged out successfully!")
            break

=======
        event = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Back':
            break
        if event == "Log Out":
          sg.popup("Logged out successfully!")
          break
    
>>>>>>> Stashed changes
    window.close()


#TOURGUIDE PAGES  


def show_tourguide_page():
    # Define the layout of the tour guide window
    layout = [
        [sg.Text('Tour Guide Page')],
        [sg.Button('Exit')]
    ]
    
    # Create the tour guide window
    window = sg.Window('Tour Guide Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    
    window.close()



#TRAVELER PAGES



def show_traveler_page():
    # Define the layout of the traveler window
    layout = [
        [sg.Text('Traveler Page')],
        [sg.Button('Exit')]
    ]
    
    # Create the traveler window
    window = sg.Window('Traveler Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
    
    window.close()




#LOGIN PAGES


# Define the layout of the login window
layout = [
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





    


    

    

    
