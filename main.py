import PySimpleGUI as sg
import sqlite3
from datetime import datetime, timedelta


#branch deneme


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

            # Validate all inputs are provided

            if not tname or not stdate or not endate or not price or not itinerary or not maxcap:
                sg.popup('All fields must be filled out.', font=('Helvetica', 14))
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


#Hotel Assignment
    
# Hotel Assignment
def show_add_hotel():
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    cur.execute("SELECT tid, tname, stdate, endate FROM Tour")
    tours = cur.fetchall()

    cur.execute("SELECT hid, city, brand FROM Hotel")
    hotels = cur.fetchall()

    layout = [
        [sg.Text("Assign Hotels for Tours", font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text("Select a Tour", font=('Helvetica', 12), background_color='navyblue', text_color='white')],
        [sg.Listbox(tours, size=(50, 5), key="selected_tour", select_mode="single", background_color='white', text_color='black', enable_events=True)],
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

    def filter_hotels(hotels, city_filter, selected_start_date, selected_end_date):
        available_hotels = []
        for hotel in hotels:
            if city_filter != "All" and hotel[1] != city_filter:
                continue
            cur.execute("""
                SELECT COUNT(*)
                FROM reservation
                WHERE hid = ? AND sdate <= ? AND edate >= ?
            """, (hotel[0], selected_end_date, selected_start_date))
            if cur.fetchone()[0] == 0:
                available_hotels.append(hotel)
        return available_hotels

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        if event == 'Back':
            window.close()
            show_admin_page(username)
            break

        if event == 'OK':
            window.close()
            show_admin_page(username)
            break

        # Update hotel list based on selected tour
        if event == "selected_tour":
            selected_tour = values["selected_tour"]
            if selected_tour:
                tour_start_date = selected_tour[0][2]
                tour_end_date = selected_tour[0][3]
                filtered_hotels = filter_hotels(hotels, values["city_filter"], tour_start_date, tour_end_date)
                window["hotel_list"].update(filtered_hotels)

        # Filter hotels by city and availability
        if event == "city_filter":
            selected_tour = values["selected_tour"]
            if selected_tour:
                tour_start_date = selected_tour[0][2]
                tour_end_date = selected_tour[0][3]
                filtered_hotels = filter_hotels(hotels, values["city_filter"], tour_start_date, tour_end_date)
                window["hotel_list"].update(filtered_hotels)
            else:
                sg.popup("Please select a tour first.", font=('Helvetica', 14))

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
                [sg.Text(f"Day interval of the chosen tour is {start_date_obj} - {end_date_obj}", font=('Helvetica', 16))],
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
                [sg.Button("Back", font=('Helvetica', 16))],
                [sg.Button("Go to Admin Page", font=('Helvetica', 16))]

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

        if event == "Go to Admin Page":
            window.close()
            show_admin_page(username)
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
                sg.popup(f"Selected dates must be within the available dates range: {', '.join(available_dates)}", font=('Helvetica', 14))
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
                # Check for existing assignments for the selected dates
                cur.execute("SELECT COUNT(*) FROM Assign WHERE tid = ? AND sdate <= ? AND edate >= ?", (tid, selected_end_date, selected_start_date))
                result = cur.fetchone()
                if result[0] > 0:
                    sg.popup("Transportation already assigned for the selected dates.", font=('Helvetica', 14))
                    continue

                # Fetch the tcode from the Transportation table
                cur.execute("SELECT tcode FROM Transportation WHERE type = ? AND starting_point = ? AND destination = ?", (t_type, t_start, t_destination))
                result = cur.fetchone()
                if result is None:
                    sg.popup("Transportation option not found in the database.", font=('Helvetica', 14))
                    continue
                t_code = result[0]

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
        [sg.Text(f'Welcome {name}! (Admin)', font=('Helvetica', 14), justification='center', background_color='navyblue', text_color='white')],
        [sg.Button('Create New Tour', button_color=('white', 'navyblue'))],
        [sg.Button('Add Transportation', button_color=('white', 'navyblue'))],
        [sg.Button('Add Hotel', button_color=('white', 'navyblue'))],
        [sg.Button('Insert Tourguide', button_color=('white', 'navyblue'))],
        [sg.Button('Display All Tours', button_color=('white', 'navyblue'))],  # New button added
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
            show_add_transportation_page()
            break
        if event == 'Add Hotel':
            window.close()
            show_add_hotel()
            break
        if event == 'Insert Tourguide':
            window.close()
            show_tourguide_selection_page()
            break
        if event == 'Display All Tours':  # Handle the new button event
            window.close()
            display_all_tours_page(username)
            break
    window.close()





def filter_tourguides(selected_start_date, selected_end_date):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Convert the selected start and end dates to datetime objects
    selected_start_date = datetime.strptime(selected_start_date, '%Y-%m-%d')
    selected_end_date = datetime.strptime(selected_end_date, '%Y-%m-%d')

    # Fetch all tour guides
    cur.execute("SELECT tgusername, name, surname FROM TourGuide JOIN User ON TourGuide.tgusername = User.username")
    all_tour_guides = cur.fetchall()

    available_tour_guides = []

    for guide in all_tour_guides:
        tgusername = guide[0]
        # Fetch the assigned tours for the tour guide
        cur.execute("SELECT t.stdate, t.endate FROM Has h JOIN Tour t ON h.tid = t.tid WHERE h.tgusername = ?", (tgusername,))
        assigned_tours = cur.fetchall()

        # Check if the tour guide is available during the selected tour's dates
        is_available = True
        for tour in assigned_tours:
            tour_start_date = datetime.strptime(tour[0], '%Y-%m-%d')
            tour_end_date = datetime.strptime(tour[1], '%Y-%m-%d')
            if not (selected_end_date < tour_start_date or selected_start_date > tour_end_date):
                is_available = False
                break

        if is_available:
            available_tour_guides.append(f"{guide[1]} {guide[2]}")

    con.close()
    return available_tour_guides

def assign_tour_guides(tid, chosen_tourguides):
    try:
        with sqlite3.connect('Project.db') as con:  # Use context manager to manage the connection
            cur = con.cursor()
            for guide in chosen_tourguides:
                # Fetch the username based on the name and surname
                cur.execute("SELECT username FROM User WHERE name || ' ' || surname = ?", (guide,))
                guide_username = cur.fetchone()
                if guide_username:
                    guide_username = guide_username[0]
                    # Check if the tour guide is already assigned to this tour
                    cur.execute("SELECT 1 FROM Has WHERE tid = ? AND tgusername = ?", (tid, guide_username))
                    if cur.fetchone():
                        sg.popup(f"Tour guide '{guide}' is already assigned to this tour. Select another one.")
                    else:
                        cur.execute('INSERT INTO Has (tid, tgusername) VALUES (?, ?)', (tid, guide_username))
            con.commit()
    except sqlite3.IntegrityError as e:
        sg.popup(f"Integrity error occurred: {e}")
    except Exception as e:
        sg.popup(f"Error occurred: {e}")
    finally:
        print("Database connection closed")










def show_tourguide_selection_page():
 
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Get the tours from the database
    cur.execute("SELECT tid, tname, stdate, endate FROM Tour")
    tours = cur.fetchall()
    con.close()


    layout = [
        [sg.Text("Select a Tour to assign tourguides", font=('Helvetica', 16))],
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
                sg.popup("Please select a tour", font=('Helvetica', 14))
                continue

            tid = selected_tour[0][0]
            stdate = selected_tour[0][2]
            endate = selected_tour[0][3]
            window.close()

            # Convert the start and end dates to datetime objects
            start_date_obj = datetime.strptime(stdate, '%Y-%m-%d')
            end_date_obj = datetime.strptime(endate, '%Y-%m-%d')

            available_tourguides = filter_tourguides(stdate, endate)

            #BU KOD PİECE GEREKSİZ OLABİLİR
            # Generate a list of dates between start_date_obj and end_date_obj
            available_dates = []
            current_date = start_date_obj
            while current_date <= end_date_obj:
                available_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
            assigned_tourguides = {date: None for date in available_dates}




            # get tourguides from the database
            con = sqlite3.connect('Project.db')
            cur = con.cursor()
            cur.execute("""
                SELECT u.name || ' ' || u.surname 
                FROM User u 
                JOIN Tourguide t ON t.tgusername = u.username
            """)
            tourguides = [row[0] for row in cur.fetchall()]
            #all_tourguide_names = list(set(option[0] for option in tourguides))
            con.close()

            layout = [
                [sg.Text("Choose Tourguides of Tour", font=('Helvetica', 16))],
                [sg.Text(f"Day interval of the chosen tour is {start_date_obj} - {end_date_obj}", font=('Helvetica', 16))],
                #[sg.Text("Filter by availability", font=('Helvetica', 16))],
                #[sg.Combo(assigned_tourguides, key= "chosen_tourguide", enable_events=True)],
                [sg.Text("Available Tourguides", font=('Helvetica', 16))],
                [sg.Listbox(available_tourguides, key="chosen_tourguide", size=(15, len(tourguides)), select_mode='multiple', background_color='white', text_color='black', enable_events=True)],
                [sg.Button("Assign Tourguides", font=('Helvetica', 16))],
                [sg.Button("Back", font=('Helvetica', 16))]
            ]

            layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))]]
            window = sg.Window('Tourguide_Page', layout, background_color='navyblue')
            break

 
    
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "Back":
            window.close()
            show_tourguide_selection_page()
            break
        
        if event == 'Assign Tourguides':
            chosen_tourguides = values['chosen_tourguide']
            print(f"Chosen tour guides: {chosen_tourguides}", flush=True)
            if chosen_tourguides and len(chosen_tourguides) >= 1:
                assign_tour_guides(tid, chosen_tourguides)
            
                window.close()
                display_all_tours_page(username)  # Navigate to display_all_tours_page
                break
            if not chosen_tourguides:
                sg.popup("No tour guides selected! Please select.")
                continue
            


def display_all_tours_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # SQL query to fetch tours and their assigned tour guides using subqueries
    query = """
    SELECT 
        t.tid, 
        t.tname, 
        t.stdate, 
        t.endate, 
        t.maxcap, 
        t.itinerary, 
        t.price,
        (SELECT GROUP_CONCAT(u.name || ' ' || u.surname, ', ') 
         FROM Has h, User u
         WHERE h.tgusername = u.username AND h.tid = t.tid) AS tourguides
    FROM Tour t
    """
    cur.execute(query)
    tours = cur.fetchall()
    con.close()

    layout = [
        [sg.Text("All Tours in the System", font=('Helvetica', 16))],
        [sg.Table(
            values=tours, 
            headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Maximum Capacity", "Itinerary", "Price", "Tourguides"], 
            col_widths=[10, 20, 15, 15, 20, 30, 10, 50],  # Adjust the column widths as needed
            justification='center', 
            auto_size_columns=False, 
            num_rows=min(len(tours), 20)
        )],
        [sg.Button("Log Out")], 
        [sg.Button("Back")]
    ]

    window = sg.Window('All Tours', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Log Out':
            window.close()
            show_login_page()
            break

        if event == "Back":
            window.close()
            show_admin_page(username)
            break

    window.close()

#TOURGUIDE PAGES  

def show_tourguide_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    
    # Fetch the tour guide's name
    cur.execute("SELECT name, surname FROM User u JOIN Has h ON u.username = h.tgusername WHERE u.username = ?", (username,))
    guide = cur.fetchone()
    guide_name = f"{guide[0]} {guide[1]}" if guide else "Unknown Guide"

    # Fetch the assigned tours for the tour guide
    cur.execute("SELECT tid FROM Has WHERE tgusername = ?", (username,))
    assigned_tours = cur.fetchall()

    tours = []
    for tid_tuple in assigned_tours:
        tid = tid_tuple[0]
        cur.execute("SELECT tid, tname, stdate, endate, maxcap, itinerary, price FROM Tour WHERE tid = ?", (tid,))
        tour = cur.fetchone()
        if tour:
            tours.append(tour)

    layout = [
        [sg.Text('Tour Guide Page')],
        [sg.Text(f"Welcome, {guide_name}!", font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text("Your Scheduled Tours:", font=('Helvetica', 14))],
        [sg.Table(
            values=tours,
            headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Max Capacity", "Itinerary", "Price"],
            justification='center',
            auto_size_columns=False,
            num_rows=min(len(tours), 10),
        )],
        [sg.Button('Log Out', button_color=('white', 'navyblue'))]
    ]

    # Create the tour guide window
    window = sg.Window('Tour Guide Page', layout, background_color='navyblue')
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Log Out':
            break
    
    window.close()

# Example login function to call show_tourguide_page
def login(username, password):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    cur.execute("SELECT role FROM User WHERE username = ? AND password = ?", (username, password))
    result = cur.fetchone()
    con.close()

    if result:
        role = result[0]
        if role == 'tourguide':
            show_tourguide_page(username)
        elif role == 'admin':
            show_admin_page(username)
        else:
            sg.popup("Unknown role", font=('Helvetica', 14))
    else:
        sg.popup("Invalid username or password", font=('Helvetica', 14))

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
                show_tourguide_page(username)
                break
            elif role == 'traveler':
                window.close()
                show_traveler_page()
                break
            else:
                sg.popup('Invalid username or password')

window.close()




    


    

    

    
