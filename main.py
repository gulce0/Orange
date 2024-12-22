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


def show_create_tour_form(username):
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
    
    window = sg.Window('Create Tour', layout, background_color='navyblue', size=(800, 500))
    
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


    
# Hotel Assignment


def show_add_hotel(username, tid, stdate, edate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Convert the start and end dates to datetime objects
    start_date_obj = datetime.strptime(stdate, '%Y-%m-%d')
    end_date_obj = datetime.strptime(edate, '%Y-%m-%d')

    # Generate a list of dates between start_date_obj and end_date_obj
    available_dates = []
    current_date = start_date_obj
    while current_date <= end_date_obj:
        available_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    assigned_hotels = {date: None for date in available_dates}


    cur.execute("""
    SELECT hid, city, brand FROM Hotel""")
    hotel_options = cur.fetchall()
    cities = list(set(option[1] for option in hotel_options))
    brands = list(set(option[2] for option in hotel_options))

    con.close()

    layout = [
        [sg.Text("Choose Hotel for Tour", font=('Helvetica', 16))],
        [sg.Text(f"Day interval of the chosen tour is {start_date_obj.strftime('%Y-%m-%d')} - {end_date_obj.strftime('%Y-%m-%d')}", font=('Helvetica', 16))],
    [sg.Text('Starting Date', background_color='navyblue', text_color='white'), 
     sg.Input(key='stdate', size=(20, 1), enable_events=True), 
     sg.CalendarButton("Choose Starting Date", target="stdate", format="%Y-%m-%d", 
                      default_date_m_d_y=(start_date_obj.month, start_date_obj.day, start_date_obj.year), 
                      close_when_date_chosen=True, begin_at_sunday_plus=1)],
    [sg.Text('Ending Date', background_color='navyblue', text_color='white'), 
     sg.Input(key='endate', size=(20, 1), enable_events=True), 
     sg.CalendarButton("Choose Ending Date", target="endate", format="%Y-%m-%d", 
                      default_date_m_d_y=(end_date_obj.month, end_date_obj.day, end_date_obj.year), 
                      close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text("Filter by city", font=('Helvetica', 16))],
        [sg.Combo(["All"] + cities, key="city_filter", default_value="All", enable_events=True, font=('Helvetica', 14))],
        [sg.Text("Filter by brand", font=('Helvetica', 16))],
        [sg.Combo(["All"] + brands, key="brand_filter", default_value="All", enable_events=True, font=('Helvetica', 14))],
        [sg.Text("Available Hotel Options", font=('Helvetica', 16))],
        [sg.Listbox(hotel_options, key="hotel_options", size=(50, 10), select_mode='single', enable_events=True, font=('Helvetica', 14), background_color='white', text_color='black')],
        [sg.Button("Assign Hotel", font=('Helvetica', 16))],
        [sg.Button("Back", font=('Helvetica', 16))],
        [sg.Button("Go to Admin Page", font=('Helvetica', 16))]
                        ]

    layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(800, 500))]]
    window = sg.Window('Hotel_Page', layout, background_color='navyblue')

    def filter_hotels(hotels, city_filter, brand_filter, selected_start_date, selected_end_date):
        filtered_options = []
        # Create a new connection inside the filter function
        con = sqlite3.connect('Project.db')
        cur = con.cursor()
        
        try:
            for hotel in hotels:
                if (city_filter != "All" and hotel[1] != city_filter) or (brand_filter != "All" and hotel[2] != brand_filter):
                    continue
                cur.execute("""
                    SELECT COUNT(*)
                    FROM reservation
                    WHERE hid = ? AND sdate <= ? AND edate >= ?
                """, (hotel[0], selected_end_date, selected_start_date))
                if cur.fetchone()[0] == 0:
                    filtered_options.append(hotel)
        finally:
            con.close()
            
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
            show_assigned_hotel_list(username, tid, stdate, edate)
            break
            
        # Handle date and filter changes
        if event in ("city_filter", "brand_filter", "stdate", "endate"):
            selected_start_date = values["stdate"]
            selected_end_date = values["endate"]
            
            if selected_start_date and selected_end_date:
                try:
                    selected_start_date_obj = datetime.strptime(selected_start_date, '%Y-%m-%d')
                    selected_end_date_obj = datetime.strptime(selected_end_date, '%Y-%m-%d')
                    if selected_start_date_obj <= selected_end_date_obj:
                        filtered_options = filter_hotels(
                            hotel_options, 
                            values["city_filter"], 
                            values["brand_filter"], 
                            selected_start_date, 
                            selected_end_date
                        )
                        window["hotel_options"].update(filtered_options)
                    else:
                        sg.popup("End date cannot be earlier than start date.", font=('Helvetica', 14))
                except ValueError:
                    sg.popup("Invalid date format. Please use YYYY-MM-DD.", font=('Helvetica', 14))

        if event == "Assign Hotel":
            selected_start_date = values["stdate"]
            selected_end_date = values["endate"]
            h_hotel = values['hotel_options']
            
            if not selected_start_date or not selected_end_date:
                sg.popup("Please select both start and end dates.", font=('Helvetica', 14))
                continue
            
            if selected_start_date not in available_dates or selected_end_date not in available_dates:
                sg.popup(
                    f"Selected dates must be within the available dates range: {', '.join(available_dates)}",
                    font=('Helvetica', 14)
                )
                continue
            
            if selected_end_date < selected_start_date:
                sg.popup("End date cannot be earlier than start date.", font=('Helvetica', 14))
                continue
            
            if not h_hotel or len(h_hotel[0]) < 3:
                sg.popup("Please select a valid hotel option.", font=('Helvetica', 14))
                continue
            
            try:
                h_hid = h_hotel[0][0]

                con = sqlite3.connect('Project.db')
                cur = con.cursor()

                # 1) Check if any hotel is already assigned for any overlapping day in this date range for the same tour
                cur.execute(
                    "SELECT COUNT(*) FROM reservation "
                    "WHERE tid = ? AND sdate <= ? AND edate >= ?",
                    (tid, selected_end_date, selected_start_date)
                )
                if cur.fetchone()[0] > 0:
                    sg.popup(
                        "Hotel is already assigned for this day.",
                        font=('Helvetica', 14)
                    )
                    continue
                
                # 2) Insert the new assignment
                cur.execute(
                    "INSERT INTO reservation (tid, hid, sdate, edate) VALUES (?, ?, ?, ?)",
                    (tid, h_hid, selected_start_date, selected_end_date)
                )
                con.commit()
                sg.popup('Hotel assigned successfully', font=('Helvetica', 14))

                # 3) Check if all dates have hotel assigned
                cur.execute("SELECT sdate, edate FROM reservation WHERE tid = ?", (tid,))
                assigned_dates = cur.fetchall()
                assigned_dates_set = set()
                for sdate, edate in assigned_dates:
                    current_date = datetime.strptime(sdate, '%Y-%m-%d')
                    end_date_dt = datetime.strptime(edate, '%Y-%m-%d')
                    while current_date <= end_date_dt:
                        assigned_dates_set.add(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)

                unassigned_dates = set(available_dates) - assigned_dates_set
                if not unassigned_dates:
                    sg.popup("All dates have hotel assigned.", font=('Helvetica', 14))
                else:
                    unassigned_dates_list = sorted(unassigned_dates)
                    sg.popup(
                        f"Some dates are still unassigned: {', '.join(unassigned_dates_list)}",
                        font=('Helvetica', 14)
                    )
                    available_dates = unassigned_dates_list
                    assigned_hotels = {date: None for date in available_dates}
                    window["stdate"].update("")
                    window["endate"].update("")
                    window["hotel_options"].update(filtered_options)

            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
            finally:
                con.close()

    window.close()


def show_assigned_hotel_list(username, tid, stdate, edate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    query = """
    SELECT 
        h.hid, 
        h.city, 
        h.brand, 
        r.sdate, 
        r.edate
    FROM Hotel h, Reservation r
    WHERE h.hid = r.hid AND r.tid = ?
    """
    cur.execute(query, (tid,))
    hotels = cur.fetchall()
    con.close()

    layout = [
        [sg.Text("Assigned Hotel List", font=('Helvetica', 24), justification='center', background_color='navyblue', text_color='white', pad=(0, 20))],
        [sg.Table(
            values=hotels, 
            headings=["Hid", "City", "Brand", "Start Date", "End Date"], 
            col_widths=[20, 20, 30, 15, 15],  # Adjust the column widths as needed
            justification='center',
            key='hotel_table',
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE
        )],
        [sg.Button('Add Hotel', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
         sg.Button('Delete Hotel', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
         sg.Button('Back', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10))]
    ]

    window = sg.Window('Assigned Hotel List', layout, background_color='navyblue', size=(800, 600), element_justification='center')

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Back'):
            window.close()
            show_admin_page(username)
            break
        if event == 'Add Hotel':
            window.close()
            show_add_hotel(username, tid, stdate, edate)
            break
        if event == 'Delete Hotel':
            selected_row = values['hotel_table']
            if selected_row:
                h_hid = hotels[selected_row[0]][0]
                h_city = hotels[selected_row[0]][1]
                h_brand = hotels[selected_row[0]][2]
                h_sdate = hotels[selected_row[0]][3]
                h_edate = hotels[selected_row[0]][4]
                delete_hotel(tid, h_hid, h_city, h_brand, h_sdate, h_edate)
                sg.popup("Hotel deleted successfully", font=('Helvetica', 14))
                window.close()
                show_assigned_hotel_list(username, tid, stdate, edate)
                break
            else:
                sg.popup("Please select a hotel", font=('Helvetica', 14))
    window.close()


def delete_hotel(tid, h_hid, h_city, h_brand, r_sdate, r_edate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    cur.execute("""
    DELETE FROM Reservation
    WHERE tid = ? AND hid = (
        SELECT hid FROM Hotel
        WHERE hid = ? AND city = ? AND brand = ?
    ) AND sdate = ? AND edate = ?
    """, (tid, h_hid, h_city, h_brand, r_sdate, r_edate))
    con.commit()
    con.close()

#Transportation Assignment

def show_add_transportation_page(username, tid, stdate, endate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

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
    cur.execute("SELECT tcode, type, starting_point, destination FROM Transportation")
    transportation_options = cur.fetchall()
    types = list(set(option[1] for option in transportation_options))
    starting_points = list(set(option[2] for option in transportation_options))
    destinations = list(set(option[3] for option in transportation_options))

    con.close()

    layout = [
        [sg.Text("Choose Transportation of Tour", font=('Helvetica', 16))],
        [sg.Text(f"Day interval of the chosen tour is {start_date_obj.strftime('%Y-%m-%d')} - {end_date_obj.strftime('%Y-%m-%d')}", font=('Helvetica', 16))],
        [sg.Text('Starting Date', background_color='navyblue', text_color='white'), sg.Input(key='stdate', size=(20, 1)), sg.CalendarButton("Choose Starting Date", target="stdate", format="%Y-%m-%d", default_date_m_d_y=(start_date_obj.month, start_date_obj.day, start_date_obj.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text('Ending Date', background_color='navyblue', text_color='white'), sg.Input(key='endate', size=(20, 1)), sg.CalendarButton("Choose Ending Date", target="endate", format="%Y-%m-%d", default_date_m_d_y=(end_date_obj.month, end_date_obj.day, end_date_obj.year), close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Combo(["All"] + types, key="t_filter", default_value="All", enable_events=True, font=('Helvetica', 14))],
        [sg.Text("Filter by starting point", font=('Helvetica', 16))],
        [sg.Combo(["All"] + starting_points, key= "s_filter", default_value="All", enable_events=True, font=('Helvetica', 14))],
        [sg.Text("Filter by destination", font=('Helvetica', 16))],
        [sg.Combo(["All"] + destinations, key= "d_filter", default_value="All", enable_events=True, font=('Helvetica', 14))],
        [sg.Text("Available Transportation Options", font=('Helvetica', 16))],
        [sg.Listbox(transportation_options, key="transportation_options", size=(50, 10), select_mode='single', enable_events=True, font=('Helvetica', 14), background_color='white', text_color='black')],
        [sg.Button("Assign Transportation", font=('Helvetica', 16))],
        [sg.Button("Back", font=('Helvetica', 16))]
    ]

    layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(800, 500))]]
    window = sg.Window('Transportation_Page', layout, background_color='navyblue')

    def filter_transportation(options, t_filter, s_filter, d_filter):
        filtered_options = []
        for option in options:
            if (t_filter == "All" or option[1] == t_filter) and \
                (s_filter == "All" or option[2] == s_filter) and \
                (d_filter == "All" or option[3] == d_filter):
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
            show_assigned_transportation_list(username, tid, stdate, endate)
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
                t_type = t_transportation[0][1]
                t_start = t_transportation[0][2]
                t_destination = t_transportation[0][3]

                print(f"Inserting: {t_type}, {t_start}, {t_destination}", flush=True)
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                # Check for existing assignments for the selected dates
                cur.execute("SELECT COUNT(*) FROM Assign WHERE tid = ? AND sdate <= ? AND edate > ?", (tid, selected_end_date, selected_start_date))
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
                        end_date -= timedelta(days=1)

                unassigned_dates = set(available_dates) - assigned_dates_set
                if not unassigned_dates:
                    sg.popup("All dates have transportation assigned.", font=('Helvetica', 14))
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

                
def show_assigned_transportation_list(username, tid, stdate, endate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    query = """
    SELECT 
        tr.type, 
        tr.starting_point, 
        tr.destination, 
        a.sdate, 
        a.edate
    FROM Transportation tr, Assign a
    WHERE tr.tcode = a.tcode AND a.tid = ?
    """
    cur.execute(query, (tid,))
    transportation = cur.fetchall()
    con.close()

    layout = [
        [sg.Text("Assigned Transportation List", font=('Helvetica', 24), justification='center', background_color='navyblue', text_color='white', pad=(0, 20))],
        [sg.Table(
            values=transportation, 
            headings=["Type", "Starting Point", "Destination", "Start Date", "End Date"], 
            col_widths=[15, 20, 20, 15, 15],  # Adjust the column widths as needed
            justification='center',
            key='transportation_table',
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE
        )],
        [sg.Button('Add Transportation', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
         sg.Button('Delete Transportation', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
         sg.Button('Back', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10))]
    ]

    window = sg.Window('Assigned Transportation List', layout, background_color='navyblue', size=(800, 600), element_justification='center')

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Back'):
            window.close()
            show_admin_page(username)
            break
        if event == 'Add Transportation':
            window.close()
            show_add_transportation_page(username, tid, stdate, endate)
            break
        if event == 'Delete Transportation':
            selected_row = values['transportation_table']
            if selected_row:
                tr_type = transportation[selected_row[0]][0]
                tr_starting_point = transportation[selected_row[0]][1]
                tr_destination = transportation[selected_row[0]][2]
                tr_sdate = transportation[selected_row[0]][3]
                tr_edate = transportation[selected_row[0]][4]
                delete_transportation(tid, tr_type, tr_starting_point, tr_destination, tr_sdate, tr_edate)
                sg.popup("Transportation deleted successfully", font=('Helvetica', 14))
                window.close()
                show_assigned_transportation_list(username, tid, stdate, endate)
                break
            else:
                sg.popup("Please select a transportation", font=('Helvetica', 14))
    window.close()


def delete_transportation(tid, tr_type, tr_starting_point, tr_destination, tr_sdate, tr_edate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    cur.execute("""
    DELETE FROM Assign
    WHERE tid = ? AND tcode = (
        SELECT tcode FROM Transportation
        WHERE type = ? AND starting_point = ? AND destination = ?
    ) AND sdate = ? AND edate = ?
    """, (tid, tr_type, tr_starting_point, tr_destination, tr_sdate, tr_edate))
    con.commit()
    con.close()

    
def show_admin_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    cur.execute("""
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
    """)
    tours = cur.fetchall()
    con.close()

    layout = [
        [sg.Text("Admin Dashboard", font=('Helvetica', 24), justification='center', background_color='navyblue', text_color='white', pad=(0, 20))],
        [sg.Table(
            values=tours, 
            headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Max Capacity", "Itinerary", "Price", "Tourguides"], 
            col_widths=[10, 20, 15, 15, 15, 30, 10, 30],  # Adjust the column widths as needed
            justification='center',
            key='tour_table',
            enable_events=True,
            select_mode=sg.TABLE_SELECT_MODE_BROWSE,
            auto_size_columns=False,
            display_row_numbers=False,
            num_rows=min(25, len(tours)),
            vertical_scroll_only=False
        )],
        [sg.Column([
            [sg.Button('Create New Tour', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
             sg.Button('Show Transportations', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
             sg.Button('Show Hotels', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
             sg.Button('Insert Tourguide', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10)),
             sg.Button('Logout', button_color=('white', 'navyblue'), size=(20, 2), pad=(10, 10))]
        ], justification='center', element_justification='center')]
    ]

    window = sg.Window('Admin Page', layout, background_color='navyblue', size=(800, 600), element_justification='center')

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, 'Logout'):
            break
        if event == 'Create New Tour':
            window.close()
            show_create_tour_form(username)
            break
        if event == 'Show Transportations':
            selected_row = values['tour_table']
            if selected_row:
                tid = tours[selected_row[0]][0]
                stdate = tours[selected_row[0]][2]
                edate = tours[selected_row[0]][3]
                window.close()
                show_assigned_transportation_list(username, tid, stdate, edate)
            else:
                sg.popup("Please select a tour", font=('Helvetica', 14))
            
        if event == 'Show Hotels':
            selected_row = values['tour_table']
            if selected_row:
                tid = tours[selected_row[0]][0]
                stdate = tours[selected_row[0]][2]
                edate = tours[selected_row[0]][3]
                window.close()
                show_assigned_hotel_list(username, tid, stdate, edate)
            else:
                sg.popup("Please select a tour", font=('Helvetica', 14))
            
        if event == 'Insert Tourguide':
            selected_row = values['tour_table']
            if selected_row:
                tid = tours[selected_row[0]][0]
                stdate = tours[selected_row[0]][2]
                edate = tours[selected_row[0]][3]
                window.close()
                show_tourguide_selection_page(username, tid, stdate, edate)
            else:
                sg.popup("Please select a tour", font=('Helvetica', 14))
            
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










def show_tourguide_selection_page(username, tid, stdate, edate):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Fetch available tour guides
    available_tourguides = filter_tourguides(stdate, edate)

    layout = [
        [sg.Text("Choose Tourguides for Tour", font=('Helvetica', 16))],
        [sg.Text(f"Day interval of the chosen tour is {stdate} - {edate}", font=('Helvetica', 16))],
        [sg.Text("Available Tourguides", font=('Helvetica', 16))],
        [sg.Listbox(values=available_tourguides, size=(30, 6), key='chosen_tourguide', select_mode='multiple', font=('Helvetica', 14))],
        [sg.Button('Assign Tourguides')],
        [sg.Button('Back')]
    ]

    layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))]]
    window = sg.Window('Tourguide_Page', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == 'Back':
            window.close()
            show_admin_page(username)
            break
        if event == 'Assign Tourguides':
            chosen_tourguides = values['chosen_tourguide']
            if chosen_tourguides:
                assign_tour_guides(tid, chosen_tourguides)
                sg.popup("Tourguides assigned successfully", font=('Helvetica', 14))
                window.close()
                show_admin_page(username)
                break
            else:
                sg.popup("No tour guides selected! Please select.", font=('Helvetica', 14))

    window.close()



#TOURGUIDE PAGES  

def show_tourguide_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    
    # Fetch the tour guide's name
    cur.execute("SELECT name, surname FROM User WHERE username = ?", (username,))
    guide = cur.fetchone()
    guide_name = f"{guide[0]} {guide[1]}" if guide else "Unknown Guide"

    layout = [
        [sg.Text('Tour Guide Page', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text(f"Welcome, {guide_name}!", font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Button('My Tours', button_color=('white', 'navyblue'))],
        [sg.Button('Log Out', button_color=('white', 'navyblue'))]
    ]

    # Create the tour guide window
    window = sg.Window('Tour Guide Page', layout, background_color='navyblue', size=(800, 500))
    
    # Event loop to process events and get values of inputs
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == 'Log Out':
            break
        if event == 'My Tours':
            window.close()
            show_tourguides_tours_page(username)
            break

    window.close()


def show_tourguides_tours_page(username):
    
    con = sqlite3.connect('Project.db')
    cur = con.cursor()


    # Retrieve the list of assigned tour TIDs
    cur.execute("SELECT tid FROM Has WHERE tgusername = ?", (username,))
    assigned_tours = cur.fetchall()
    print(f"Assigned tours: {assigned_tours}")  # Debug print

    # Prepare data for an SG.Table
    table_data = []

    # For each assigned tour, fetch the tour name and customers
    for row in assigned_tours:
        assigned_tid = row[0]
        # Fetch the tour name
        cur.execute("SELECT tname FROM Tour WHERE tid = ?", (assigned_tid,))
        tour_row = cur.fetchone()
        print(f"Tour info for tid {assigned_tid}: {tour_row}")  # Debug print

        if not tour_row:
            continue
        tour_name = tour_row[0]

        # Fetch usernames of booked customers
        cur.execute("SELECT trusername FROM Purchase WHERE tid = ?", (assigned_tid,))
        booked_customers = cur.fetchall()
        print(f"Processing tour {assigned_tid} - {tour_name}")
        print(f"Found booked customers: {booked_customers}")

        if booked_customers:  # Only proceed if there are customers
            for cust_row in booked_customers:
                traveler_username = cust_row[0]
                
                # Get customer name from User table first
                cur.execute("""
                    SELECT name, surname 
                    FROM User 
                    WHERE username = ?""", (traveler_username,))
                user_data = cur.fetchone()
                
                if user_data:
                    # Then get contact info from Traveler table
                    cur.execute("""
                        SELECT tr_contact_no 
                        FROM Traveler 
                        WHERE trusername = ?""", (traveler_username,))
                    traveler_data = cur.fetchone()
                    
                    if traveler_data:
                        full_name = f"{user_data[0]} {user_data[1]}"
                        phone_number = traveler_data[0]
                        table_data.append([tour_name, full_name, phone_number])
                        print(f"Added customer: {full_name} for tour: {tour_name}")
                    else:
                        print(f"No traveler data found for username: {traveler_username}")

    con.close()

    # Debugging: Print the table data to the console
    print("Table Data:", table_data)

    # Define PySimpleGUI layout
    headings = ["Tour Name", "Customer Name", "Contact Number"]
    layout = [
        [sg.Text("My Tours", font=('Helvetica', 24), background_color='navyblue', text_color='white', justification='center')],
        [sg.Table(values=table_data, headings=headings, key="my_tours_table", auto_size_columns=True, justification='left')],
        [sg.Button("Back"), sg.Button("Log Out")]
    ]

    window = sg.Window("My Tours Page", layout, background_color="navyblue", size=(800, 600))
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Log Out"):
            break
        if event == "Back":
            window.close()
            show_tourguide_page(username)
            return
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



#TRAVELER PAGES



def show_traveler_page(username):
    layout = [
        [sg.Text('Orange Travel Agency', font=('Helvetica', 16), background_color='navyblue', text_color='orange')],
        [sg.Button('Profile', button_color=('white', 'navyblue'), size=(16, 1))],
        [sg.Button('My Tours', button_color=('white', 'navyblue'), size=(16, 1))],
        [sg.Button('Tour Search', button_color=('white', 'navyblue'), size=(16, 1))],
        [sg.Button('Pay for First Tour', button_color=('white', 'navyblue'), size=(16, 1))],
        [sg.Button('Exit', button_color=('white', 'navyblue'), size=(16, 1))]
    ]
    window = sg.Window('Traveler Page', layout, background_color='navyblue', size=(200, 200))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Profile':
            window.close()
            show_profile_page(username)
            break
        if event == 'Tour Search':
            window.close()
            show_tour_search_page(username)
            break
        if event == 'My Tours':
            window.close()
            show_my_tours_page(username)
            break
        if event == 'Pay for First Tour':
            handle_customer_payment_workflow(username)
            break
    window.close()



def show_profile_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    
    # Fetch the traveler's name and surname
    cur.execute("SELECT name, surname FROM User WHERE username = ?", (username,))
    user = cur.fetchone()
    con.close()
    
    if user:
        name, surname = user
    else:
        name, surname = "Unknown", "User"

    layout = [
        [sg.Text(f'{name} {surname}', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Add New Contact Number', background_color='navyblue', text_color='white'), sg.InputText(key='contact_number')],
        [sg.Text('Add New Credit Card Information', font=('Helvetica', 13), background_color='navyblue', text_color='white')],
        [sg.Text('Card Number', background_color='navyblue', text_color='white'), sg.InputText(key='card_number')],
        [sg.Text('Bank', background_color='navyblue', text_color='white'), sg.InputText(key='bank')],
        [sg.Text('CVV', background_color='navyblue', text_color='white'), sg.InputText(key='cvv')],
        [sg.Text('Expiration Date (MM/YY)', background_color='navyblue', text_color='white'), sg.InputText(key='expiration_date')],
        [sg.Button('Save', button_color=('white', 'navyblue'))],
        [sg.Button('Back', button_color=('white', 'navyblue'))]
    ]

    window = sg.Window('Profile Page', layout, background_color='navyblue', size=(400, 400))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Back':
            window.close()
            show_traveler_page(username)
            break
        if event == 'Save':
            contact_number = values['contact_number']
            card_number = values['card_number']
            bank = values['bank']
            cvv = values['cvv']
            expiration_date = values['expiration_date']

            # Validate contact number if provided
            if contact_number and (not contact_number.isdigit() or len(contact_number) != 10):
                sg.popup('Please provide a valid contact number consisting of 10 digits.', font=('Helvetica', 14))
                continue

            # Validate credit card information if provided
            if card_number or bank or cvv or expiration_date:
                if not (card_number and bank and cvv and expiration_date):
                    sg.popup('In order to add a card, please provide complete credit card information.', font=('Helvetica', 14))
                    continue
            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                if contact_number:
                    cur.execute("UPDATE Traveler SET tr_contact_no = ? WHERE trusername = ?", (contact_number, username))
                if card_number and bank and cvv and expiration_date:
                    cur.execute("INSERT INTO CreditCard (cardnumber, bank, CVV, expirationdate, ownerusername) VALUES (?, ?, ?, ?, ?)",
                                (card_number, bank, cvv, expiration_date, username))
                con.commit()
                sg.popup('Profile information updated successfully!', font=('Helvetica', 14))
                window.close()
                show_traveler_page(username)
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
            finally:
                con.close()

    window.close()

def show_tour_search_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Fetch all tours that have not started yet
    today = datetime.today().strftime('%Y-%m-%d')
    cur.execute("SELECT tid, tname, stdate, endate FROM Tour WHERE stdate > ?", (today,))
    tours = cur.fetchall()
    con.close()

    layout = [
        [sg.Text('Tour Search Page', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Start Date', background_color='navyblue', text_color='white'), sg.Input(key='start_date', size=(20, 1)), sg.CalendarButton("Choose Start Date", target="start_date", format="%Y-%m-%d", close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Text('End Date', background_color='navyblue', text_color='white'), sg.Input(key='end_date', size=(20, 1)), sg.CalendarButton("Choose End Date", target="end_date", format="%Y-%m-%d", close_when_date_chosen=True, begin_at_sunday_plus=1)],
        [sg.Button('Filter Tours', button_color=('white', 'navyblue'))],
        [sg.Table(
            values=tours,
            headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date"],
            key='tour_table',
            justification='center',
            auto_size_columns=False,
            num_rows=min(len(tours), 10),
            enable_events=True,
            font=('Helvetica', 14)
        )],
        [sg.Text('Tour Details', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Multiline(size=(60, 10), key='tour_details', disabled=True, background_color='white', text_color='black')],
        [sg.Button('Purchase', button_color=('white', 'navyblue'))],
        [sg.Button('Back', button_color=('white', 'navyblue'))]
    ]

    scrollable_layout = [[sg.Column(layout, scrollable=True, vertical_scroll_only=True, size=(780, 580))]]
    window = sg.Window('Tour Search Page', scrollable_layout, background_color='navyblue', size=(800, 600))
    
    selected_tour_id = None
   


    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Back':
            window.close()
            show_traveler_page(username)
            break

        if event == 'Filter Tours':
            start_date = values['start_date']
            end_date = values['end_date']

            if not start_date or not end_date:
                sg.popup('Please select both start and end dates.', font=('Helvetica', 14))
                continue
            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                cur.execute("SELECT tid, tname, stdate, endate FROM Tour WHERE stdate >= ? AND endate <= ?", (start_date, end_date))
                filtered_tours = cur.fetchall()
                con.close()
                window['tour_table'].update(filtered_tours)
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))



        if event == 'tour_table':
            selected_tour_index = values['tour_table'][0]
            selected_tour = tours[selected_tour_index]
            selected_tour_id = selected_tour[0]
            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                cur.execute("SELECT maxcap, itinerary, price FROM Tour WHERE tid = ?", (selected_tour_id,))
                tour_details = cur.fetchone()
                
                if tour_details:
                    try:
                        maxcap = int(tour_details[0])
                    except ValueError:
                        sg.popup(f"Invalid maximum capacity value: {tour_details[0]}", font=('Helvetica', 14))
                        continue


                # Fetch assigned transportation
                cur.execute("SELECT type, starting_point, destination FROM Transportation t JOIN Assign a ON t.tcode = a.tcode WHERE a.tid = ?", (selected_tour_id,))
                transportation = cur.fetchall()

                # Fetch assigned hotels
                cur.execute("SELECT h.city, h.brand FROM Hotel h JOIN reservation r ON h.hid = r.hid WHERE r.tid = ?", (selected_tour_id,))
                hotels = cur.fetchall()

                # Fetch assigned tour guides
                cur.execute("SELECT u.name || ' ' || u.surname FROM User u JOIN Has h ON u.username = h.tgusername WHERE h.tid = ?", (selected_tour_id,))
                tour_guides = cur.fetchall()

                # Calculate current capacity
                cur.execute("SELECT COUNT(*) FROM Purchase WHERE tid = ?", (selected_tour_id,))
                purchased_count = cur.fetchone()[0]
                current_capacity = maxcap - purchased_count

                con.close()

                itinerary = tour_details[1]
                price = tour_details[2]
                details = f"Current Capacity: {current_capacity}\nItinerary: {itinerary}\nPrice: {price}\n\n"
                details += "Transportation:\n"
                for t in transportation:
                    details += f"Type: {t[0]}, Starting Point: {t[1]}, Destination: {t[2]}\n"
                details += "\nHotels:\n"
                for h in hotels:
                    details += f"City: {h[0]}, Brand: {h[1]}\n"
                details += "\nTour Guides:\n"
                for tg in tour_guides:
                    details += f"{tg[0]}\n"
                window['tour_details'].update(details)
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))

        if event == 'Purchase':
            if selected_tour_id:
                window.close()
                show_payment_page(username, selected_tour_id)
                break
            else:
                sg.popup('Please select a tour to purchase.', font=('Helvetica', 14))

    window.close()

def show_payment_page(username, tour_id):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Fetch existing credit card information for the customer
    cur.execute("SELECT cardnumber, bank, cvv, expirationdate FROM CreditCard WHERE ownerusername = ?", (username,))
    credit_cards = cur.fetchall()
    con.close()

    if not credit_cards:
        credit_cards = [("No card found, you can add your information from your profile.", "")]

    layout = [
        [sg.Text('Payment Page', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Select Credit Card', background_color='navyblue', text_color='white')],
        [sg.Listbox(values=[f"Bank: {card[1]}, Card Number: {card[0]}" for card in credit_cards], size=(50, len(credit_cards)), key='selected_card')],
        [sg.Text('CVV', background_color='navyblue', text_color='white'), sg.InputText(key='cvv')],
        [sg.Text('Expiration Date (MM/YY)', background_color='navyblue', text_color='white'), sg.InputText(key='expiration_date')],
        [sg.Button('Pay', button_color=('white', 'navyblue'))],
        [sg.Button('Back', button_color=('white', 'navyblue'))]
    ]


    window = sg.Window('Payment Page', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Back':
            window.close()
            show_tour_search_page(username)
            break

        if event == 'Pay':
            selected_card = values['selected_card']
            entered_cvv = values['cvv']
            entered_expiration_date = values['expiration_date']


            if not selected_card or "No card found" in selected_card[0]:
                sg.popup('Please select a credit card to proceed with the payment.', font=('Helvetica', 14))
                continue

            if not entered_cvv or not entered_expiration_date:
                sg.popup('Please enter CVV and expiration date.', font=('Helvetica', 14))
                continue

            # Get the index of the selected card
            selected_card_index = [i for i, card in enumerate(credit_cards) if f"Bank: {card[1]}, Card Number: {card[0]}" == selected_card[0]][0]
            card_info = credit_cards[selected_card_index]
            card_number = card_info[0]
            bank = card_info[1]
            correct_cvv = str(card_info[2]).strip()
            correct_expiration_date = card_info[3].strip()

            # Debugging statements
            print(f"Entered CVV: {entered_cvv}, Correct CVV: {correct_cvv}", flush=True)
            print(f"Entered Expiration Date: {entered_expiration_date}, Correct Expiration Date: {correct_expiration_date}", flush=True)
            print(f"Selected Card: {card_info}", flush=True)

            # Validate CVV and expiration date
            if entered_cvv != correct_cvv or entered_expiration_date != correct_expiration_date:
                sg.popup('Invalid CVV or expiration date. Please enter the correct information.', font=('Helvetica', 14))
                continue

            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()

                # Insert the purchase into the Purchase table
                cur.execute("INSERT INTO Purchase (tid, trusername) VALUES (?, ?)", (tour_id, username))

                con.commit()
                con.close()

                sg.popup('Payment successful! You have purchased the tour.', font=('Helvetica', 14))
                window.close()
                show_traveler_page(username)
                break
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))

    window.close()


def show_my_tours_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Fetch purchased tours for the user
    cur.execute("""
        SELECT t.tid, t.tname, t.stdate, t.endate, t.itinerary, t.price
        FROM Tour t
        JOIN Purchase p ON t.tid = p.tid
        WHERE p.trusername = ?
    """, (username,))
    purchased_tours = cur.fetchall()
    con.close()        


    layout = [
        [sg.Text('My Tours', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Table(
            values=purchased_tours,
            headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Itinerary", "Price"],
            key='purchased_tours_table',
            justification='center',
            auto_size_columns=False,
            num_rows=min(len(purchased_tours), 10),
            enable_events=True,
            font=('Helvetica', 14)
        )],
        [sg.Multiline(size=(60, 10), key='tour_details', disabled=True, background_color='white', text_color='black')],
        [sg.Button('Back', button_color=('white', 'navyblue'))],
        [sg.Button('Add review and rating', button_color=('white', 'navyblue'))]
    ]

    window = sg.Window('My Tours', layout, background_color='navyblue', size=(800, 600))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Back':
            window.close()
            show_traveler_page(username)
            break



        if event == 'purchased_tours_table':
            selected_tour_index = values['purchased_tours_table'][0]
            selected_tour = purchased_tours[selected_tour_index]
            tour_id = selected_tour[0]

            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                cur.execute("SELECT maxcap, itinerary, price FROM Tour WHERE tid = ?", (tour_id,))
                tour_details = cur.fetchone()

                if tour_details:
                    try:
                        maxcap = int(tour_details[0])
                    except ValueError:
                        sg.popup(f"Invalid maximum capacity value: {tour_details[0]}", font=('Helvetica', 14))
                        continue

                    # Calculate current capacity
                    cur.execute("SELECT COUNT(*) FROM Purchase WHERE tid = ?", (tour_id,))
                    purchased_count = cur.fetchone()[0]
                    current_capacity = maxcap - purchased_count

                    # Fetch assigned transportation
                    cur.execute("SELECT type, starting_point, destination FROM Transportation t JOIN Assign a ON t.tcode = a.tcode WHERE a.tid = ?", (tour_id,))
                    transportation = cur.fetchall()

                    # Fetch assigned hotels
                    cur.execute("SELECT h.city, h.brand FROM Hotel h JOIN reservation r ON h.hid = r.hid WHERE r.tid = ?", (tour_id,))
                    hotels = cur.fetchall()

                    # Fetch assigned tour guides
                    cur.execute("SELECT u.name || ' ' || u.surname FROM User u JOIN Has h ON u.username = h.tgusername WHERE h.tid = ?", (tour_id,))
                    tour_guides = cur.fetchall()

                    con.close()

                    itinerary = tour_details[1]
                    price = tour_details[2]
                    details = f"Current Capacity: {current_capacity}\nItinerary: {itinerary}\nPrice: {price}\n\n"
                    details += "Transportation:\n"
                    for t in transportation:
                        details += f"Type: {t[0]}, Starting Point: {t[1]}, Destination: {t[2]}\n"
                    details += "\nHotels:\n"
                    for h in hotels:
                        details += f"City: {h[0]}, Brand: {h[1]}\n"
                    details += "\nTour Guides:\n"
                    for tg in tour_guides:
                        details += f"{tg[0]}\n"
                    window['tour_details'].update(details)
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
        if event == 'Add review and rating' and tour_id:
            if tour_id is not None:
                window.close()
                show_add_review_page(username, tour_id)
                break
            else:
                sg.popup('Please select a tour before adding a review.', font=('Helvetica', 14))


    window.close()

def show_add_review_page(username, tour_id):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()
    layout = [
        [sg.Text('Write a Review', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Rating (1-5):', background_color='navyblue', text_color='white'), sg.InputText(key='rating')],
        [sg.Text('Review:', background_color='navyblue', text_color='white'), sg.InputText(key='review_text')],
        [sg.Button('Submit'), sg.Button('Cancel')]
    ]

    window = sg.Window('Add Review', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':
            window.close()
            show_my_tours_page(username)
            break
        if event == 'Submit':
            rating = values['rating'].strip()  # Trim leading/trailing spaces
            review_text = values['review_text']

            # Enhanced rating validation
            try:
                # Convert the rating to an integer and check if it's within the valid range (1-5)
                rating_int = int(rating)  
                if rating_int < 1 or rating_int > 5:
                    raise ValueError("Rating must be between 1 and 5.")  # Custom error if outside range
            except ValueError as e:
                sg.popup(f'Invalid rating: {e}', font=('Helvetica', 14))
                continue  # Go back to the form and wait for valid input

            # Try to insert the review into the database after rating validation
            try:
                # Assuming 'rid' is not auto-increment and needs to be manually inserted
                cur.execute("SELECT MAX(rid) FROM Review")
                max_rid = cur.fetchone()[0]  # Get the current maximum 'rid'
                new_rid = max_rid + 1 if max_rid is not None else 1  # Increment the 'rid' (or start from 1 if empty)

                # Insert the review with the manually calculated 'rid'
                cur.execute("INSERT INTO Review (rid, text, date, rating, ReviewTourid, ReviewTrUsername) VALUES (?, ?, date('now'), ?, ?, ?)",
                            (new_rid, review_text, rating_int, tour_id, username))
                con.commit()  # Commit the transaction

                # Show success message
                sg.popup('Review submitted successfully!', font=('Helvetica', 14))  

                # Update the layout to show additional buttons (Back and Tour Reviews)
                layout = [
                    [sg.Text('Review Submitted', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
                    [sg.Button('Back'), sg.Button('Tour Reviews')]
                ]
                
                # Update the existing window with the new layout (recreate the window)
                window.close()
                window = sg.Window('Add Review', layout, background_color='navyblue')

            except Exception as e:
                # Log the exception to understand what went wrong
                sg.popup(f"Error occurred while submitting the review: {e}", font=('Helvetica', 14))

        # Handle additional button events
        if event == 'Back':
            window.close()
            show_my_tours_page(username)
            break
        elif event == 'Tour Reviews':
            window.close()
            show_tour_reviews_page(tour_id)  # Go to the tour reviews page
            break

    window.close()  # Close the window when done




def show_tour_reviews_page(username):
    con = sqlite3.connect('Project.db')
    cur = con.cursor()

    # Fetch all tours with their average ratings
    cur.execute("""
        SELECT T.tid, T.tname, 
               IFNULL(AVG(R.rating), 0) AS avg_rating
        FROM Tour T
        LEFT JOIN Review R ON T.tid = R.ReviewTourid
        GROUP BY T.tid, T.tname
    """)
    tours = cur.fetchall()  # List of tours with their average ratings
    con.close()

    # Prepare the layout
    layout = [
        [sg.Text('Tour Reviews', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Listbox(values=[f"{tour[1]} (ID: {tour[0]}, Avg Rating: {tour[2]:.1f})" for tour in tours],
                    size=(50, 10), key='selected_tour')],
        [sg.Button('View Reviews', button_color=('white', 'navyblue'))],
        [sg.Button('Back', button_color=('white', 'navyblue'))]
    ]

    window = sg.Window('Tour Reviews', layout, background_color='navyblue')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Back':
            window.close()
            show_traveler_page(username)  # Navigate back to the traveler page
            break

        if event == 'View Reviews':
            selected_tour = values['selected_tour']
            if not selected_tour:
                sg.popup('Please select a tour to view reviews.', font=('Helvetica', 14))
                continue

            # Extract the selected tour ID
            tour_id = int(selected_tour[0].split('(ID: ')[1].split(',')[0])

            try:
                # Fetch all reviews for the selected tour
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                cur.execute("""
                    SELECT R.text, R.rating, R.ReviewTrUsername
                    FROM Review R
                    WHERE R.ReviewTourid = ?
                """, (tour_id,))
                reviews = cur.fetchall()
                con.close()

                if reviews:
                    # Format reviews to display in a popup
                    reviews_text = "\n\n".join([f"{r[2]}: {r[1]}/5 - {r[0]}" for r in reviews])
                    sg.popup_scrolled(reviews_text, title=f"Reviews for Tour ID {tour_id}", font=('Helvetica', 14))
                else:
                    sg.popup('No reviews available for this tour.', font=('Helvetica', 14))
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
                if con:
                    con.close()

    window.close()  # Close the window when done



def display_customer_tours(username):
    """Display all tours for the customer excluding invalid or non-booked ones."""
    try:
        con = sqlite3.connect('Project.db')
        cur = con.cursor()
        cur.execute("""
            SELECT t.tid, t.tname, t.stdate, t.endate, t.price 
            FROM Tour t
            JOIN Purchase p ON t.tid = p.tid
            WHERE p.trusername = ?
        """, (username,))
        tours = cur.fetchall()
        con.close()

        if tours:
            tour_list = "\n".join([f"Tour ID: {t[0]}, Name: {t[1]}, Start: {t[2]}, End: {t[3]}, Price: {t[4]}" for t in tours])
            sg.popup_scrolled(f"Your Tours:\n\n{tour_list}", title="My Tours", font=('Helvetica', 14))
        else:
            sg.popup("You currently have no tours booked.", font=('Helvetica', 14))
    except Exception as e:
        sg.popup(f"Error: {e}", font=('Helvetica', 14))

def pay_for_first_tour(username):
    """Pay for the first tour the customer booked and return to the customer page."""
    try:
        con = sqlite3.connect('Project.db')
        cur = con.cursor()
        cur.execute("""
            SELECT t.tid, t.tname, t.price 
            FROM Tour t
            JOIN Purchase p ON t.tid = p.tid
            WHERE p.trusername = ?
            LIMIT 1
        """, (username,))
        tour = cur.fetchone()
        con.close()

        if tour:
            tour_id, tour_name, price = tour
            sg.popup(f"Payment successful for Tour ID: {tour_id} ({tour_name}). Total: {price:.2f}", font=('Helvetica', 14))
        else:
            sg.popup("No eligible tours found to pay for.", font=('Helvetica', 14))
    except Exception as e:
        sg.popup(f"Error: {e}", font=('Helvetica', 14))
    finally:
        # Return to the customer page
        show_traveler_page(username)


def handle_customer_payment_workflow(username):
    """Handle the workflow for displaying and paying for a customer's first tour."""
    # Step 1: Display all tours for the customer
    display_customer_tours(username)

    # Step 2: Pay for the first tour the customer tried to book
    pay_for_first_tour(username)





                

#LOGIN PAGES


# Define the layout of the login window

def show_login_page():
    layout = [
        [sg.Text('Welcome to Orange Travel Agency Platform, please enter your information', font=('Helvetica', 12), justification='center', background_color='navyblue', text_color='white')],
        [sg.Text('Username'), sg.InputText(key='username',font=('Helvetica', 14))],
        [sg.Text('Password'), sg.InputText(key='password', password_char='*', font=('Helvetica', 14))],
        [sg.Button('Login', button_color=('white', 'navyblue'))],
        [sg.Text('Are you new?', background_color='navyblue', text_color='white'), sg.Text('Sign up now', font=('Helvetica', 12, 'underline'), text_color='blue', enable_events=True, key='Sign Up')]
    ]

    # Create the login window
    window = sg.Window('Login', layout, background_color='navyblue', size=(700, 180))

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
                    show_traveler_page(username)
                    break
                else:
                    sg.popup('Invalid username or password')
        if event == 'Sign Up':
            window.close()
            show_signup_page()
            break

    window.close()

# Function to show the signup page
def show_signup_page():
    layout = [
        [sg.Text('Sign Up', font=('Helvetica', 16), background_color='navyblue', text_color='white')],
        [sg.Text('Name', background_color='navyblue', text_color='white'), sg.InputText(key='name')],
        [sg.Text('Surname', background_color='navyblue', text_color='white'), sg.InputText(key='surname')],
        [sg.Text('Username', background_color='navyblue', text_color='white'), sg.InputText(key='username')],
        [sg.Text('Password', background_color='navyblue', text_color='white'), sg.InputText(key='password', password_char='*')],
        [sg.Button('Sign Up', button_color=('white', 'navyblue'))],
        [sg.Button('Back', button_color=('white', 'navyblue'))]
    ]

    window = sg.Window('Sign Up', layout, background_color='navyblue', size=(800, 500))

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'Back':
            window.close()
            show_login_page()
            break
        if event == 'Sign Up':
            name = values['name']
            surname = values['surname']
            username = values['username']
            password = values['password']

            # Validate that all inputs are provided
            if not name or not surname or not username or not password:
                sg.popup('All fields must be filled out.', font=('Helvetica', 14))
                continue
            
            try:
                con = sqlite3.connect('Project.db')
                cur = con.cursor()
                # Check if the username already exists
                cur.execute("SELECT username FROM User WHERE username = ?", (username,))
                if cur.fetchone():
                    sg.popup('Username already exists. Please choose a different username.', font=('Helvetica', 14))
                    continue

                # Insert the new user into the User table
                cur.execute("INSERT INTO User (username, password, name, surname) VALUES (?, ?, ?, ?)",
                            (username, password, name, surname))
                # Insert the new user into the Traveler table
                cur.execute("INSERT INTO Traveler (trusername) VALUES (?)", (username,))
                con.commit()
                sg.popup('Sign up successful! You can now log in.', font=('Helvetica', 14))
                window.close()
                show_login_page()
                break
            except Exception as e:
                sg.popup(f"Error occurred: {e}", font=('Helvetica', 14))
            finally:
                con.close()

    window.close()


if __name__ == "__main__":
    show_login_page()


    


    

    

    
