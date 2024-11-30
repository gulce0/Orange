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
                sg.popup('Tour created successfully', font=('Helvetica', 14))
                
            except Exception as e:
                print(f"Error occurred: {e}", flush=True)
            finally:
                con.close()
                print("Database connection closed", flush=True)
            window.close()
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
    
    window.close()
    display_all_tours_page()

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
        [sg.Text("All Tours in the System", font=('Helvetica', 16), background_color='navyblue', text_color='white' )],
        [sg.Table(values=tours, headings=["Tour ID", "Tour Name", "Starting Date", "Ending Date", "Maximum Capacity", "Itinerary", "Price"],justification='center', auto_size_columns=False, num_rows=min(len(tours), 10))],
        [sg.Button("Log Out")]
    ]


    window = sg.Window('All Tours', layout, background_color='navyblue')

    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED or event == "Log Out":
            sg.popup("Logged out successfully!")
            break

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





    


    

    

    
